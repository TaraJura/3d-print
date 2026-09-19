#!/usr/bin/env node
'use strict';
// Real Chromium events/fetch over localhost HTTP, served by actual sketch logic
// in a persistent native C++ process. Arduino/WiFi/GPIO/timer remain mocks.
const assert=require('node:assert/strict'), fs=require('node:fs'), path=require('node:path');
const os=require('node:os'), http=require('node:http'), readline=require('node:readline');
const {spawn,spawnSync}=require('node:child_process');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const here=__dirname, source=path.resolve(process.argv[2] || path.join(here,'..','prvni-motor.ino'));
const temporary=fs.mkdtempSync(path.join(os.tmpdir(),'auticko-browser-http-'));
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
  const context=await browser.newContext({viewport:{width:420,height:850},hasTouch:true,isMobile:true});
  const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(`http://127.0.0.1:${server.address().port}/`);const button=page.locator('#drive');await button.waitFor();
  const rect=await button.boundingBox();await page.mouse.move(rect.x+rect.width/2,rect.y+rect.height/2);
  return {page,context,button,requests,events,errors,command,baseline,
    get state(){return state;},set dropStop(v){dropStop=v;},set dropHold(v){dropHold=v;},set dropSessionResponse(v){dropSessionResponse=v;},
    async down(){await page.mouse.down();},async up(){await page.mouse.up();},
    async raw(text){return command('REQUEST '+Buffer.from(text).toString('hex'));},
    async close(){closed=true;clearInterval(timer);await context.close();server.closeAllConnections();await new Promise(resolve=>server.close(resolve));processDriver.stdin.end();await new Promise(resolve=>processDriver.on('exit',resolve));}
  };
}
async function test(name,options,body){const f=await fixture(options);try{await body(f);assert.deepEqual(f.errors,[]);++passed;console.log('PASS Chromium HTTP '+name);}finally{await f.close();}}
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
  console.log(`PASS ${passed} real Chromium HTTP scenarios against actual persistent C++ sketch; hardware remains mocked`);
})().catch(e=>{console.error(e);process.exitCode=1;}).finally(async()=>{if(browser)await browser.close();fs.rmSync(temporary,{recursive:true,force:true});});
