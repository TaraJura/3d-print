#!/usr/bin/env node
'use strict';
// Real Chromium events/fetch over localhost HTTP, served by actual sketch logic
// in a persistent native C++ process. Arduino/WiFi/GPIO/timer remain mocks.
const assert=require('node:assert/strict'), fs=require('node:fs'), path=require('node:path');
const http=require('node:http'), readline=require('node:readline');
const {spawn,spawnSync}=require('node:child_process');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const here=__dirname, source=path.resolve(process.argv[2] || path.join(here,'..','prvni-motor.ino'));
const runtime=path.join(here,'..','.cache');fs.mkdirSync(runtime,{recursive:true});
const temporary=fs.mkdtempSync(path.join(runtime,'browser-http-'));
const binary=path.join(temporary,'driver');
const build=spawnSync('g++',['-std=c++17','-Wall','-Wextra','-Werror','-I',here,`-DSKETCH_PATH="${source}"`,
  '-DTEST_MAX_LINE=1024','-DTEST_MAX_BYTES=8192','-DTEST_DEADLINE=3000',path.join(here,'http_driver.cpp'),'-o',binary],{encoding:'utf8'});
if(build.status!==0){process.stderr.write(build.stderr);process.exit(1);}
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function until(check,label,timeout=3500){const end=Date.now()+timeout;while(Date.now()<end){if(await check())return;await sleep(10);}throw new Error('Timeout: '+label);}
let browser, passed=0;
async function fixture(options={}){
  const processDriver=spawn(binary,[],{stdio:['pipe','pipe','inherit']});
  let closed=false, state, pending=[], events=[], requests=[], lastClock=Date.now();
  readline.createInterface({input:processDriver.stdout}).on('line',line=>{
    const data=JSON.parse(line);state=data;events.push({...data,wall:Date.now()});const first=pending.shift();if(first)first.resolve(data);
  });
  processDriver.on('exit',code=>{if(!closed)for(const item of pending.splice(0))item.reject(new Error('Driver exit '+code));});
  function command(line){return new Promise((resolve,reject)=>{pending.push({resolve,reject});processDriver.stdin.write(line+'\n');});}
  const reset=await command('STATE');const baseline=reset.time;
  async function tick(){const now=Date.now(), elapsed=now-lastClock;lastClock=now;if(elapsed>0)await command('TICK '+elapsed);}
  const timer=setInterval(()=>{if(!closed)tick().catch(()=>{});},5);
  let dropStop=false, dropHold=false, dropSessionResponse=false, sequence=0;
  const server=http.createServer(async(req,res)=>{
    const n=sequence++, item={path:req.url,n,wall:Date.now(),raw:null,response:null};requests.push(item);
    if((dropStop&&req.url==='/stop')||(dropHold&&req.url==='/hold')){item.dropped=true;res.destroy();return;}
    const delays=options.delay ? options.delay(req.url,n) : {up:0,down:0};
    await sleep(delays.up||0);if(closed){res.destroy();return;}
    const headers={...req.headers,host:'192.168.4.1'};
    if(headers.origin)headers.origin='http://192.168.4.1';
    const raw=`${req.method} ${req.url} HTTP/1.1\r\n`+Object.entries(headers).map(([k,v])=>`${k}: ${v}\r\n`).join('')+'\r\n';item.raw=raw;
    await tick();const output=await command('REQUEST '+Buffer.from(raw).toString('hex'));
    const response=Buffer.from(output.responseHex,'hex').toString();item.response=response;item.after=output;
    if(dropSessionResponse&&req.url==='/session'){dropSessionResponse=false;res.destroy();return;}
    await sleep(delays.down||0);if(closed||res.destroyed)return;
    const boundary=response.indexOf('\r\n\r\n');
    if(boundary<0){res.destroy();return;}
    const first=response.slice(0,boundary).split('\r\n'), code=Number(first.shift().split(' ')[1]);
    for(const header of first){const at=header.indexOf(':');if(at>0)res.setHeader(header.slice(0,at),header.slice(at+1).trim());}
    res.writeHead(code);res.end(response.slice(boundary+4));
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const context=await browser.newContext({viewport:{width:390,height:844},hasTouch:true,isMobile:true});
  const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(`http://127.0.0.1:${server.address().port}/`);const button=page.locator('#drive');await button.waitFor();
  await page.evaluate(()=>{window.__pointerEvents=[];for(const name of ['pointerdown','pointerup','pointercancel','lostpointercapture'])
    window.addEventListener(name,e=>window.__pointerEvents.push({name,id:e.pointerId,target:e.target.id,primary:e.isPrimary}),true);});
  const rect=await button.boundingBox();await page.mouse.move(rect.x+rect.width/2,rect.y+rect.height/2);
  return {page,context,button,requests,events,errors,command,baseline,
    get state(){return state;},set dropStop(v){dropStop=v;},set dropHold(v){dropHold=v;},set dropSessionResponse(v){dropSessionResponse=v;},
    async down(){await page.mouse.down();},async up(){await page.mouse.up();},
    async raw(text){return command('REQUEST '+Buffer.from(text).toString('hex'));},
    async close(){closed=true;clearInterval(timer);await context.close();server.closeAllConnections();await new Promise(resolve=>server.close(resolve));processDriver.stdin.end();await new Promise(resolve=>processDriver.on('exit',resolve));}
  };
}
async function test(name,options,body){
  if(process.env.TEST_MATCH&&!name.includes(process.env.TEST_MATCH))return;
  const f=await fixture(options);try{await body(f);assert.deepEqual(f.errors,[]);++passed;console.log('PASS Chromium HTTP '+name);}
  catch(error){console.error('Failure diagnostics:',JSON.stringify({state:f.state,requests:f.requests.slice(-5),ui:await f.page.evaluate(()=>({owners,active,held,stopping,events:window.__pointerEvents}))}));throw error;}
  finally{await f.close();}
}
(async()=>{
  browser=await chromium.launch({headless:true,...(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE?{executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE}:{})});
  for(const roundtrip of [200,300,400])await test(`hold >2s with ${roundtrip}ms roundtrip +20ms browser pause`,{
    delay:(url)=>url==='/'?{up:0,down:0}:{up:Math.floor(roundtrip/3),down:roundtrip-Math.floor(roundtrip/3)}
  },async f=>{
    await f.down();await until(()=>f.state.motor>0,'initial motor');await sleep(2200);
    assert.equal(f.state.motor,128);assert.equal(f.state.watchdog,0);
    assert(f.requests.filter(r=>r.path==='/hold'&&r.after?.motor===128).length>=4);
    await f.up();await until(()=>f.state.motor===0,'released motor');
    const count=f.requests.filter(r=>r.path==='/hold').length;await sleep(650);assert.equal(f.state.motor,0);
    assert.equal(f.requests.filter(r=>r.path==='/hold').length,count);
  });
  await test('jittered response chain remains live then touch release stops',{delay:(url,n)=>url==='/'?{up:0,down:0}:{up:[30,60,90][n%3],down:[100,170,210][n%3]}},async f=>{
    const box=await f.button.boundingBox(), x=box.x+box.width/2,y=box.y+box.height/2;
    const cdp=await f.context.newCDPSession(f.page);
    await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y}]});
    await until(()=>f.state.motor>0,'touch start');await sleep(2300);assert.equal(f.state.motor,128);assert.equal(f.state.watchdog,0);
    await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await until(()=>f.state.motor===0,'touch release');
  });
  await test('release while ARM response pending cannot start motor',{delay:url=>url==='/arm'?{up:30,down:350}:{up:0,down:0}},async f=>{
    await f.down();await until(()=>f.requests.some(r=>r.path==='/arm'&&r.response),'ARM prepared');await f.up();await sleep(800);
    assert(!f.events.some(e=>e.motor));assert(!f.requests.some(r=>r.path==='/hold'));
  });
  await test('dropped STOP expires without retrigger, new press refreshes session',{delay:()=>({up:20,down:60})},async f=>{
    await f.down();await until(()=>f.state.motor>0,'initial motor');await sleep(250);f.dropStop=true;await f.up();
    await until(()=>f.state.motor===0,'watchdog after dropped STOP',1300);const stopped=f.state.time;
    await sleep(500);assert.equal(f.state.motor,0);assert(!f.events.some(e=>e.time>stopped&&e.motor));
    await until(async()=>!await f.button.isDisabled(),'button recovers',2500);
    const before=f.requests.length;f.dropStop=false;await f.down();await until(()=>f.state.motor>0,'new press after failure');
    assert(f.requests.slice(before).some(r=>r.path==='/session'));await f.up();await until(()=>f.state.motor===0,'final release');
  });
  await test('HOLD loss stops; connection recovery alone cannot restart',{delay:()=>({up:10,down:30})},async f=>{
    await f.down();await until(()=>f.state.motor>0,'initial motor');f.dropHold=true;
    await until(()=>f.state.motor===0,'loss stop',1500);
    // Restore transport while the physical mouse button is still DOWN.
    // Recovery alone must not emit another ARM/HOLD or restart the motor.
    const heldRequests=f.requests.filter(r=>r.path==='/arm'||r.path==='/hold').length;
    f.dropHold=false;await sleep(650);assert.equal(f.state.motor,0);
    assert.equal(f.requests.filter(r=>r.path==='/arm'||r.path==='/hold').length,heldRequests);
    await f.up();await until(async()=>!await f.button.isDisabled(),'release enables new press');await f.down();await until(()=>f.state.motor>0,'new press succeeds');
    await f.up();await until(()=>f.state.motor===0,'final stop');
  });
  await test('lost session response can retry on next press without token lockout',{delay:()=>({up:10,down:30})},async f=>{
    await f.down();await until(()=>f.state.motor>0,'first start');f.dropStop=true;await f.up();
    await until(()=>f.state.motor===0,'lost STOP expires');await until(async()=>!await f.button.isDisabled(),'release after failed STOP');
    f.dropStop=false;f.dropSessionResponse=true;await f.down();
    await until(()=>f.requests.some(r=>r.path==='/session'&&r.response),'session rotated with lost reply');
    await until(async()=>!await f.button.isDisabled(),'failed session/STOP complete');await f.up();await f.down();
    await until(()=>f.state.motor>0,'retry cached session starts');
    assert(f.requests.filter(r=>r.path==='/session').length>=2);
    await f.up();await until(()=>f.state.motor===0,'final stop');
  });
  await test('stale duplicate HOLD and earlier STOP do not cut a newer press',{},async f=>{
    await f.down();await until(()=>f.requests.some(r=>r.path==='/hold'&&r.response),'old hold');
    const old=f.requests.find(r=>r.path==='/hold').raw;await f.up();await until(()=>f.state.motor===0,'first stop');
    await until(async()=>!await f.button.isDisabled(),'next press ready');await f.down();await until(()=>f.state.motor>0,'second run');
    const oldStop=f.requests.find(r=>r.path==='/stop').raw;await f.raw(old);assert.equal(f.state.motor,128);await f.raw(oldStop);assert.equal(f.state.motor,128);
    await f.up();await until(()=>f.state.motor===0,'final stop');
  });
  for(const first of ['drive','left'])await test('real multitouch '+first+' first, independent release and safe stop',{},async f=>{
    const cdp=await f.context.newCDPSession(f.page),points={};
    for(const [id,name] of [[1,first],[2,first==='drive'?'left':'drive']]){
      const b=await f.page.locator('#'+name).boundingBox();points[name]={id,x:b.x+b.width/2,y:b.y+b.height/2};
    }
    const second=first==='drive'?'left':'drive';
    await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[points[first]]});
    await until(()=>first==='drive'?f.state.motor===128:f.state.steeringUs===1275,'first control');
    if(first==='left')assert.equal(f.state.motor,0);
    await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[points[first],points[second]]});
    await until(()=>f.state.motor===128&&f.state.steeringUs===1275,'motor+left from both fingers');
    // CDP touchEnd lists contacts being released, unlike touchStart/move.
    if(first==='left'){
      await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[points.drive]});
      await until(()=>f.state.motor===0&&f.state.steeringUs===1275,'motor released, steering stays');
    }else{
      await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[points.left]});
      await until(()=>f.state.motor===128&&f.state.steeringUs===1575,'steering released, motor stays');
    }
    await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
    await until(()=>f.state.motor===0&&f.state.steeringUs===1575,'both released');
  });
  await test('servo-only keyboard, explicit center, combined arrows and focus loss',{},async f=>{
    await f.page.keyboard.down('ArrowRight');await until(()=>f.state.steeringUs===1875,'right only');assert.equal(f.state.motor,0);
    await f.page.keyboard.down('ArrowUp');await until(()=>f.state.motor===128,'motor joins right');
    await f.page.locator('#center').click();await until(()=>f.state.steeringUs===1575,'explicit center');assert.equal(f.state.motor,128);
    await f.page.keyboard.up('ArrowRight');await f.page.keyboard.down('ArrowLeft');await until(()=>f.state.steeringUs===1275,'left');
    await f.page.evaluate(()=>window.dispatchEvent(new Event('blur')));
    await until(()=>f.state.motor===0&&f.state.steeringUs===1575,'blur clears both');
    const count=f.requests.length;await sleep(650);assert.equal(f.requests.length,count);
    await f.page.keyboard.up('ArrowLeft');await f.page.keyboard.up('ArrowUp');
  });
  await test('dropped STOP with both actuators returns motorOFF/neutral without new input',{},async f=>{
    await f.page.keyboard.down('ArrowUp');await f.page.keyboard.down('ArrowLeft');
    await until(()=>f.state.motor===128&&f.state.steeringUs===1275,'combined input');
    f.dropStop=true;await f.page.evaluate(()=>window.dispatchEvent(new Event('blur')));
    await until(()=>f.state.motor===0&&f.state.steeringUs===1575,'shared watchdog',1300);
    const stopped=f.state.time;await sleep(550);assert(!f.events.some(e=>e.time>stopped&&(e.motor||e.steeringUs!==1575)));
    await f.page.keyboard.up('ArrowUp');await f.page.keyboard.up('ArrowLeft');
  });
  const assertMotor=(state,direction)=>{
    assert.equal(state.motor,direction===0?0:128);assert.equal(state.motorDirection,direction);
    assert.equal(state.in1,direction===1?1:0);assert.equal(state.in2,direction===-1?1:0);
  };
  const controlRequests=f=>f.requests.filter(r=>r.path==='/arm'||r.path==='/hold').length;
  await test('reverse button holds opposite polarity and releases without retrigger',{},async f=>{
    const reverse=f.page.locator('#reverse'),box=await reverse.boundingBox();
    await f.page.mouse.move(box.x+box.width/2,box.y+box.height/2);await f.down();
    await until(()=>f.state.motorDirection===-1,'reverse button drives');assertMotor(f.state,-1);
    await sleep(650);assertMotor(f.state,-1);assert.equal(f.state.watchdog,0);
    assert(f.requests.some(r=>r.path==='/hold'&&/\r\nx-control-motor: -1\r\n/i.test(r.raw)));
    assert.equal(await reverse.getAttribute('data-running'),'true');
    assert.equal(await f.button.getAttribute('data-running'),'false');
    await f.up();await until(()=>f.state.motor===0,'reverse release');assertMotor(f.state,0);
    const count=controlRequests(f);await sleep(650);assert.equal(controlRequests(f),count);
  });
  for(const first of ['reverse','left'])await test('reverse multitouch '+first+' first preserves wheel direction and independent release',{},async f=>{
    const cdp=await f.context.newCDPSession(f.page),points={};
    const steer=first==='reverse'?'right':'left',second=first==='reverse'?steer:'reverse';
    for(const [id,name] of [[1,first],[2,second]]){
      const box=await f.page.locator('#'+name).boundingBox();points[name]={id,x:box.x+box.width/2,y:box.y+box.height/2};
    }
    const steeringUs=steer==='left'?1275:1875;
    await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[points[first]]});
    await until(()=>first==='reverse'?f.state.motorDirection===-1:f.state.steeringUs===steeringUs,'first reverse/steering control');
    if(first!=='reverse')assertMotor(f.state,0);
    await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[points[first],points[second]]});
    await until(()=>f.state.motorDirection===-1&&f.state.steeringUs===steeringUs,'reverse with unchanged wheel direction');assertMotor(f.state,-1);
    if(first==='reverse'){
      await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[points[steer]]});
      await until(()=>f.state.motorDirection===-1&&f.state.steeringUs===1575,'steering release retains reverse');assertMotor(f.state,-1);
    }else{
      await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[points.reverse]});
      await until(()=>f.state.motor===0&&f.state.steeringUs===steeringUs,'reverse release retains steering');assertMotor(f.state,0);
    }
    await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
    await until(()=>f.state.motor===0&&f.state.steeringUs===1575,'both reverse controls released');assertMotor(f.state,0);
  });
  await test('opposite motor touches cancel both; either release cannot restart and a fresh press can',{},async f=>{
    const cdp=await f.context.newCDPSession(f.page),points={};
    for(const [id,name] of [[1,'drive'],[2,'reverse']]){
      const box=await f.page.locator('#'+name).boundingBox();points[name]={id,x:box.x+box.width/2,y:box.y+box.height/2};
    }
    await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[points.drive]});
    await until(()=>f.state.motorDirection===1,'forward before touch conflict');assertMotor(f.state,1);
    await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[points.drive,points.reverse]});
    await until(()=>f.requests.some(r=>r.path==='/stop'&&r.response)&&f.state.motor===0,'touch conflict STOP');
    assertMotor(f.state,0);assert.equal(f.state.steeringUs,1575);
    await until(async()=>!await f.button.isDisabled(),'conflict STOP complete');
    const count=controlRequests(f);await sleep(300);assert.equal(controlRequests(f),count);
    await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[points.drive]});
    await sleep(100);assertMotor(f.state,0);assert.equal(controlRequests(f),count);
    await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
    await sleep(100);assertMotor(f.state,0);assert.equal(controlRequests(f),count);
    await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[points.reverse]});
    await until(()=>f.state.motorDirection===-1,'fresh reverse touch after conflict');assertMotor(f.state,-1);
    await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await until(()=>f.state.motor===0,'final reverse release');
  });
  await test('ArrowDown combines with steering and center, opposite arrow cancels until new keydown',{},async f=>{
    await f.page.keyboard.down('ArrowDown');await until(()=>f.state.motorDirection===-1,'ArrowDown reverse');assertMotor(f.state,-1);
    await f.page.keyboard.down('ArrowLeft');await until(()=>f.state.steeringUs===1275,'reverse left');assertMotor(f.state,-1);
    await f.page.locator('#center').click();await until(()=>f.state.steeringUs===1575,'reverse explicit center');assertMotor(f.state,-1);
    await f.page.keyboard.up('ArrowLeft');await f.page.keyboard.down('ArrowRight');
    await until(()=>f.state.steeringUs===1875,'reverse right stays right');assertMotor(f.state,-1);
    await f.page.keyboard.down('ArrowUp');await until(()=>f.state.motor===0&&f.state.steeringUs===1575,'opposite arrow conflict');
    await until(async()=>!await f.button.isDisabled(),'keyboard conflict STOP complete');
    const count=controlRequests(f);await f.page.keyboard.down('ArrowDown');await f.page.keyboard.down('ArrowUp');
    await f.page.keyboard.up('ArrowDown');await sleep(100);assert.equal(controlRequests(f),count);assertMotor(f.state,0);
    await f.page.keyboard.up('ArrowRight');await f.page.keyboard.up('ArrowUp');await sleep(300);
    assert.equal(controlRequests(f),count);assertMotor(f.state,0);
    await f.page.keyboard.down('ArrowUp');await until(()=>f.state.motorDirection===1,'new ArrowUp starts forward');assertMotor(f.state,1);
    await f.page.keyboard.up('ArrowUp');await until(()=>f.state.motor===0,'final arrow release');
  });
  // Delay HOLD replies so release can also race with the server's REARM response.
  const pauseReplyDelay=url=>({up:0,down:url==='/hold'?120:0});
  async function requestOppositeDuringPause(f){
    await f.page.keyboard.down('ArrowUp');await until(()=>f.state.motorDirection===1,'forward before direction pause');
    await f.page.keyboard.up('ArrowUp');await until(()=>f.state.motor===0,'actual OFF before reverse');
    await until(async()=>!await f.button.isDisabled(),'forward STOP complete');
    const stopped=f.requests.filter(r=>r.path==='/stop'&&r.after).at(-1).after.time;
    await f.page.keyboard.down('ArrowDown');
    await until(()=>f.requests.some(r=>r.path==='/hold'&&r.response?.includes('HOLD_REARM')),'reverse receives HOLD_REARM');
    const rejected=f.requests.find(r=>r.path==='/hold'&&r.response?.includes('HOLD_REARM'));
    assertMotor(rejected.after,0);assert.equal(rejected.after.state,0);
    assert(rejected.after.reversePauseMs>0&&rejected.after.reversePauseMs<=250);
    assert(rejected.after.time-stopped<250);assert.match(rejected.raw,/\r\nx-control-motor: -1\r\n/i);
    assert.equal(rejected.response.split('\r\n\r\n')[1],'HOLD_REARM');
    return {stopped,rejected};
  }
  await test('direction REARM stays OFF after 250ms and stale HOLD/ARM; only a fresh press can reverse',{delay:pauseReplyDelay},async f=>{
    const {stopped,rejected}=await requestOppositeDuringPause(f);
    await until(()=>f.requests.some(r=>r.path==='/stop'&&r.n>rejected.n&&r.response),'REARM causes STOP');
    await until(async()=>!await f.button.isDisabled(),'REARM STOP complete');
    assert.match(await f.page.locator('#result').textContent(),/Změna směru: pusť ovladače a stiskni znovu\./);
    const count=controlRequests(f);await f.command('TICK 300');
    assertMotor(f.state,0);assert.equal(f.state.reversePauseMs,0);assert.equal(controlRequests(f),count);
    const oldArm=f.requests.filter(r=>r.path==='/arm'&&r.n<rejected.n).at(-1);
    for(const old of [rejected,oldArm,rejected]){
      const output=await f.raw(old.raw);assertMotor(output,0);assert.equal(output.state,0);
      assert(!/ARM_OK:|HOLD_OK:/.test(Buffer.from(output.responseHex,'hex').toString()));
    }
    await f.page.keyboard.down('ArrowDown');await sleep(350);assertMotor(f.state,0);assert.equal(controlRequests(f),count);
    await f.page.keyboard.up('ArrowDown');await sleep(50);assert.equal(controlRequests(f),count);
    await f.page.keyboard.down('ArrowDown');await until(()=>f.state.motorDirection===-1,'fresh press after REARM');assertMotor(f.state,-1);
    const running=f.requests.find(r=>r.path==='/hold'&&r.after?.motorDirection===-1);
    assert(running.n>rejected.n);assert(running.after.time-stopped>=250);
    assert.notEqual(running.raw.match(/\r\nx-motor-press: ([0-9]+)\r\n/i)[1],rejected.raw.match(/\r\nx-motor-press: ([0-9]+)\r\n/i)[1]);
    await f.page.keyboard.up('ArrowDown');await until(()=>f.state.motor===0,'release after fresh reverse');
  });
  await test('release before REARM reply with dropped STOP never starts on timeout or stale reply',{delay:pauseReplyDelay},async f=>{
    await requestOppositeDuringPause(f);f.dropStop=true;await f.page.keyboard.up('ArrowDown');
    await until(()=>f.requests.some(r=>r.path==='/stop'&&r.dropped),'paused release STOP dropped');
    const count=controlRequests(f);await f.command('TICK 600');assertMotor(f.state,0);
    await sleep(650);assertMotor(f.state,0);assert.equal(controlRequests(f),count);
    f.dropStop=false;await until(async()=>!await f.button.isDisabled(),'failed STOP finished');
    await f.page.keyboard.down('ArrowDown');await until(()=>f.state.motorDirection===-1,'fresh press after paused release');
    assert(f.requests.some(r=>r.path==='/session'));assertMotor(f.state,-1);
    await f.page.keyboard.up('ArrowDown');await until(()=>f.state.motor===0,'final paused release');
  });
  await test('disabled button pointerdown during STOP preserves every rejected contact until release',{
    delay:url=>({up:0,down:url==='/stop'?1000:0})
  },async f=>{
    const cdp=await f.context.newCDPSession(f.page),points={};
    for(const [id,name] of [[1,'drive'],[2,'reverse'],[3,'drive'],[4,'reverse'],[5,'reverse']]){
      const box=await f.page.locator('#'+name).boundingBox();points[id]={id,x:box.x+box.width/2,y:box.y+box.height/2};
    }
    await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[points[1]]});
    await until(()=>f.state.motorDirection===1,'forward before pending STOP conflict');
    await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[points[1],points[2]]});
    await until(async()=>await f.button.isDisabled(),'STOP disables controls');
    await until(()=>f.state.motor===0,'conflict output OFF');
    await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[points[1]]});
    const driveDowns=await f.page.evaluate(()=>window.__pointerEvents.filter(e=>e.name==='pointerdown'&&e.target==='drive').length);
    assert.equal(await f.button.isDisabled(),true);
    await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[points[2],points[3]]});
    // This is a native CDP touch, not dispatchEvent on a mocked or enabled element.
    const recorded=await f.page.evaluate(()=>({
      downs:window.__pointerEvents.filter(e=>e.name==='pointerdown'&&e.target==='drive').length,
      contacts:[...contacts.drive],stopping
    }));
    assert.equal(recorded.downs,driveDowns+1,'Chromium must deliver pointerdown on the disabled drive button');
    assert.equal(recorded.stopping,true);assert.equal(recorded.contacts.length,1,'disabled contact must be tracked');
    await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[points[2]]});
    await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[points[3],points[4]]});
    await until(async()=>!await f.button.isDisabled(),'pending STOP completed');
    const held=await f.page.evaluate(()=>({drive:contacts.drive.size,reverse:contacts.reverse.size,rearmRequired}));
    assert.deepEqual(held,{drive:1,reverse:1,rearmRequired:true});
    const count=controlRequests(f);await sleep(300);assertMotor(f.state,0);assert.equal(controlRequests(f),count);
    await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[points[3]]});
    await sleep(100);assertMotor(f.state,0);assert.equal(controlRequests(f),count);
    await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
    await sleep(100);assert.equal(controlRequests(f),count);
    await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[points[5]]});
    await until(()=>f.state.motorDirection===-1,'new contact after all rejected contacts released');assertMotor(f.state,-1);
    await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await until(()=>f.state.motor===0,'final disabled-contact release');
  });
  await test('two real touches on forward retain the unowned contact and block reverse until all release',{},async f=>{
    const cdp=await f.context.newCDPSession(f.page),points={};
    for(const [id,name] of [[1,'drive'],[2,'drive'],[3,'reverse'],[4,'reverse']]){
      const box=await f.page.locator('#'+name).boundingBox();points[id]={id,x:box.x+box.width/2+(id===2?10:0),y:box.y+box.height/2};
    }
    await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[points[1]]});
    await until(()=>f.state.motorDirection===1,'first forward contact');
    await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[points[1],points[2]]});
    assert.equal(await f.page.evaluate(()=>contacts.drive.size),2);
    await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[points[1]]});
    await until(()=>f.state.motor===0,'owner release stops without contact handover');
    await until(async()=>!await f.button.isDisabled(),'owner release STOP complete');
    assert.equal(await f.page.evaluate(()=>contacts.drive.size),1);
    const count=controlRequests(f);
    await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[points[2],points[3]]});
    await until(async()=>await f.page.evaluate(()=>rearmRequired),'remaining forward contact conflicts with reverse');
    await until(async()=>!await f.button.isDisabled(),'second conflict STOP complete');
    await sleep(300);assert.equal(controlRequests(f),count);assertMotor(f.state,0);
    await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[points[2]]});
    await sleep(100);assert.equal(controlRequests(f),count);
    await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
    assert.equal(controlRequests(f),count);
    await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[points[4]]});
    await until(()=>f.state.motorDirection===-1,'new reverse after unowned contact release');assertMotor(f.state,-1);
    await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await until(()=>f.state.motor===0,'final same-button release');
  });
  await test('mobile UI has no overflow and screenshot is actual sketch page',{},async f=>{
    assert(await f.page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
    for(const id of ['drive','reverse','left','center','right']){
      const box=await f.page.locator('#'+id).boundingBox();assert(box.width>=44&&box.height>=44);
    }
    assert.equal(f.state.motor,0);assert.equal(f.state.steeringUs,1575);
    const image=path.resolve(here,'../../../../..','elektronika/auticko/nahled-ovladani-v3.png');
    await f.page.screenshot({path:image,fullPage:true});console.log('Screenshot:',image);
  });
  console.log(`PASS ${passed} real Chromium HTTP scenarios against actual persistent C++ sketch; hardware remains mocked`);
})().catch(e=>{console.error(e);process.exitCode=1;}).finally(async()=>{if(browser)await browser.close();fs.rmSync(temporary,{recursive:true,force:true});});
