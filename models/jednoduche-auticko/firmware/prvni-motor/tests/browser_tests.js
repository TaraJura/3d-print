#!/usr/bin/env node
'use strict';
// Execute the actual inline browser program using deterministic DOM/fetch/timers.
// This exercises event semantics, not browser layout or a physical phone/network.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const source = fs.readFileSync(process.argv[2] || path.join(__dirname, '..', 'prvni-motor.ino'), 'utf8');
const html = source.match(/R"HTML\(([\s\S]*?)\)HTML"/)[1];
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1].replace('@TOKEN@', '0123456789abcdef0123456789abcdef');
const challenge = n => Number(n).toString(16).padStart(32, '0');
const flush = async () => { for (let i = 0; i < 20; ++i) await Promise.resolve(); };
class Target {
  constructor() { this.listeners = new Map(); }
  addEventListener(type, callback) {
    if (!this.listeners.has(type)) this.listeners.set(type, []);
    this.listeners.get(type).push(callback);
  }
  emit(type, values = {}) {
    const event = { isPrimary: true, button: 0, pointerId: 1, pointerType: 'mouse', repeat: false,
      preventDefault() {}, ...values };
    for (const callback of this.listeners.get(type) || []) callback(event);
  }
}
function runtime({honorAbort = true} = {}) {
  const makeButton=()=>Object.assign(new Target(), { disabled: false, dataset: {}, setPointerCapture() {} });
  const button=makeButton(),reverse=makeButton(),left=makeButton(),right=makeButton(),center=makeButton();
  const result = { textContent: '' };
  const window = new Target();
  const document = Object.assign(new Target(), { hidden: false, getElementById: id => ({drive:button,reverse,left,right,center,result})[id] });
  let now = 0, timerId = 0;
  const timers = new Map(), requests = [];
  const context = vm.createContext({document, window, AbortController,
    setTimeout(callback, ms) { const id = ++timerId; timers.set(id, {at: now + ms, callback}); return id; },
    clearTimeout(id) { timers.delete(id); },
    fetch(url, options) {
      return new Promise((resolve, reject) => {
        const request = {url, options, aborted: false,
          reply(body, ok = true) { resolve({ok, text: async () => body}); }, fail() { reject(new Error('network')); }};
        options.signal.addEventListener('abort', () => {request.aborted = true; if (honorAbort) reject(new Error('aborted'));});
        requests.push(request);
      });
    }
  });
  vm.runInContext(script, context, {filename: 'actual-firmware-inline.js'});
  return {button, reverse, left, right, center, result, document, window, requests,
    async emit(target, event, values) { this[target].emit(event, values); await flush(); },
    async advance(ms) {
      const end = now + ms;
      for (;;) {
        let nextId, next;
        for (const [id, item] of timers) if (item.at <= end && (!next || item.at < next.at)) {nextId = id; next = item;}
        if (!next) break;
        now = next.at; timers.delete(nextId); next.callback(); await flush();
      }
      now = end; await flush();
    },
    async respond(index, body, ok = true) {requests[index].reply(body, ok); await flush();}
  };
}
async function start(r, pointerType = 'mouse') {
  await r.emit('button', 'pointerdown', {pointerType});
  assert.equal(r.requests.length, 1); assert.equal(r.requests[0].url, '/arm');
  assert.equal(r.requests[0].options.headers['X-Motor-Press'], '1');
  await r.respond(0, 'ARM_OK:' + challenge(1));
  assert.equal(r.requests.length, 2); assert.equal(r.requests[1].url, '/hold');
  assert.equal(r.requests[1].options.headers['X-Motor-Challenge'], challenge(1));
  await r.respond(1, 'HOLD_OK:' + challenge(2));
  assert.equal(r.button.dataset.running, 'true');
}
let cases = 0;
async function test(name, work) {await work(); ++cases; console.log('PASS browser ' + name);}
(async () => {
  await test('load/click/secondary pointer do not start motor', async () => {
    const r = runtime(); assert.equal(r.requests.length, 0);
    await r.emit('button', 'click'); await r.emit('button', 'pointerdown', {isPrimary: false});
    await r.emit('button', 'pointerdown', {button: 2}); await r.advance(5000);
    assert.equal(r.requests.length, 0);
  });
  for (const pointerType of ['mouse', 'touch']) await test(pointerType + ' hold chain, release, next real press', async () => {
    const r = runtime(); await start(r, pointerType);
    await r.advance(19); assert.equal(r.requests.length, 2);
    await r.advance(1); assert.equal(r.requests.length, 3); assert.equal(r.requests[2].url, '/hold');
    assert.equal(r.requests[2].options.headers['X-Motor-Challenge'], challenge(2));
    await r.respond(2, 'HOLD_OK:' + challenge(3));
    await r.emit('window', 'pointerup'); assert.equal(r.requests[3].url, '/stop');
    assert.equal(r.button.dataset.running, 'false');
    await r.respond(3, 'STOP_OK'); await r.advance(2000); assert.equal(r.requests.length, 4);
    await r.emit('button', 'pointerdown', {pointerType});
    assert.equal(r.requests.length, 5); assert.equal(r.requests[4].url, '/arm');
    assert.equal(r.requests[4].options.headers['X-Motor-Press'], '2');
  });
  for (const [target, event] of [['window', 'pointercancel'], ['button', 'lostpointercapture'],
    ['window', 'blur'], ['window', 'pagehide'], ['window', 'offline'], ['document', 'visibilitychange']]) {
    await test(event + ' stops and requires new press', async () => {
      const r = runtime(); await start(r);
      if (event === 'visibilitychange') r.document.hidden = true;
      await r.emit(target, event); assert.equal(r.requests[2].url, '/stop'); assert.equal(r.button.dataset.running, 'false');
      await r.respond(2, 'STOP_OK'); await r.advance(2000); assert.equal(r.requests.length, 3);
      if (event === 'visibilitychange') {
        await r.emit('button', 'pointerdown'); assert.equal(r.requests.length, 3);
        r.document.hidden = false; await r.emit('document', event); assert.equal(r.requests.length, 3);
      }
    });
  }
  await test('unrelated pointer release does not stop current hold', async () => {
    const r = runtime(); await start(r); await r.emit('window', 'pointerup', {pointerId: 999});
    assert.equal(r.requests.length, 2); assert.equal(r.button.dataset.running, 'true');
    await r.emit('window', 'pointerup'); assert.equal(r.requests[2].url, '/stop');
  });
  await test('delayed ARM response after release never sends HOLD', async () => {
    const r = runtime({honorAbort: false}); await r.emit('button', 'pointerdown');
    await r.emit('window', 'pointerup'); assert.equal(r.requests[0].aborted, true); assert.equal(r.requests[1].url, '/stop');
    await r.respond(1, 'STOP_OK'); await r.respond(0, 'ARM_OK:' + challenge(1)); await r.advance(2000);
    assert.equal(r.requests.length, 2); assert.equal(r.button.dataset.running, 'false');
  });
  await test('delayed HOLD after release cannot schedule another heartbeat or show running', async () => {
    const r = runtime({honorAbort: false}); await start(r); await r.advance(20);
    await r.emit('window', 'pointerup'); assert.equal(r.requests[3].url, '/stop');
    await r.respond(3, 'STOP_OK'); await r.respond(2, 'HOLD_OK:' + challenge(3)); await r.advance(2000);
    assert.equal(r.requests.length, 4); assert.equal(r.button.dataset.running, 'false');
  });
  for (const mode of ['network', 'HTTP', 'bad-challenge', 'timeout']) await test(mode + ' failure stops without automatic retry', async () => {
    const r = runtime(); await start(r); await r.advance(20);
    if (mode === 'network') {r.requests[2].fail(); await flush();}
    if (mode === 'HTTP') await r.respond(2, 'rejected', false);
    if (mode === 'bad-challenge') await r.respond(2, 'HOLD_OK:wrong');
    if (mode === 'timeout') await r.advance(1200);
    assert.equal(r.requests[3].url, '/stop'); assert.equal(r.button.dataset.running, 'false');
    await r.respond(3, 'STOP_OK'); await r.advance(2000); assert.equal(r.requests.length, 4);
  });
  await test('failed STOP requires new press then recovers session without reload', async () => {
    const r = runtime(); await start(r); await r.emit('window', 'pointerup');
    r.requests[2].fail(); await flush(); await r.advance(2000);
    assert.equal(r.requests.length, 3); assert.equal(r.button.disabled, false);
    await r.emit('button', 'pointerdown'); assert.equal(r.requests.length, 4); assert.equal(r.requests[3].url, '/session');
    assert.equal(r.requests[3].options.method, 'POST');
    await r.respond(3, 'SESSION_OK:' + challenge(9)); assert.equal(r.requests[4].url, '/arm');
    assert.equal(r.requests[4].options.headers['X-Motor-Token'], challenge(9));
    await r.respond(4, 'ARM_OK:' + challenge(10)); await r.respond(5, 'HOLD_OK:' + challenge(11));
    assert.equal(r.button.dataset.running, 'true');
  });
  await test('error while still physically held requires release before new session', async () => {
    const r = runtime(); await start(r); await r.advance(20);r.requests[2].fail();await flush();
    await r.respond(3, 'STOP_OK'); await r.advance(2000);await r.emit('button', 'pointerdown');
    assert.equal(r.requests.length,4);await r.emit('window', 'pointerup');await r.emit('button', 'pointerdown');
    assert.equal(r.requests[4].url,'/session');
  });
  await test('release while recovery response pending cannot arm or run', async () => {
    const r = runtime({honorAbort:false});await start(r);await r.emit('window','pointerup');r.requests[2].fail();await flush();
    await r.emit('button','pointerdown');assert.equal(r.requests[3].url,'/session');await r.emit('window','pointerup');
    assert.equal(r.requests[4].url,'/stop');await r.respond(4,'STOP_OK');await r.respond(3,'SESSION_OK:'+challenge(9));
    await r.advance(2000);assert.equal(r.requests.length,5);assert.equal(r.button.dataset.running,'false');
  });
  for (const code of ['Space', 'Enter']) await test('keyboard ' + code + ' down/up and repeat suppression', async () => {
    const r = runtime(); await r.emit('button', 'keydown', {code}); assert.equal(r.requests[0].url, '/arm');
    await r.emit('button', 'keydown', {code, repeat: true}); assert.equal(r.requests.length, 1);
    await r.respond(0, 'ARM_OK:' + challenge(1)); await r.respond(1, 'HOLD_OK:' + challenge(2));
    await r.emit('window', 'keyup', {code}); assert.equal(r.requests[2].url, '/stop');
    await r.respond(2, 'STOP_OK'); await r.advance(2000); assert.equal(r.requests.length, 3);
  });
  const checkIntent=(request,motor,steer)=>{
    assert.equal(request.url,'/hold');assert.equal(request.options.headers['X-Control-Motor'],String(Number(motor)));
    assert.equal(request.options.headers['X-Control-Steer'],steer);
  };
  async function leftStart(r){
    await r.emit('left','pointerdown',{pointerId:11,pointerType:'touch'});
    assert.equal(r.requests[0].url,'/arm');await r.respond(0,'ARM_OK:'+challenge(1));
    checkIntent(r.requests[1],false,'left');await r.respond(1,'HOLD_OK:'+challenge(2));
    assert.equal(r.button.dataset.running,'false');
  }
  await test('steering alone and release never request motor power',async()=>{
    const r=runtime();await leftStart(r);await r.emit('window','pointerup',{pointerId:11});
    assert.equal(r.requests[2].url,'/stop');await r.respond(2,'STOP_OK');await r.advance(1000);
    assert.equal(r.requests.length,3);
  });
  await test('steering first, secondary touch drives; releasing drive preserves steering with motor0',async()=>{
    const r=runtime();await leftStart(r);
    await r.emit('button','pointerdown',{pointerId:22,pointerType:'touch',isPrimary:false});
    checkIntent(r.requests[2],true,'left');await r.respond(2,'HOLD_OK:'+challenge(3));
    await r.emit('window','pointerup',{pointerId:22});checkIntent(r.requests[3],false,'left');
    await r.respond(3,'HOLD_OK:'+challenge(4));assert.equal(r.button.dataset.running,'false');
    await r.emit('window','pointerup',{pointerId:11});assert.equal(r.requests[4].url,'/stop');
  });
  await test('drive first, secondary touch steers; steering release preserves motor and centers',async()=>{
    const r=runtime();await start(r,'touch');
    await r.emit('right','pointerdown',{pointerId:22,pointerType:'touch',isPrimary:false});
    checkIntent(r.requests[2],true,'right');await r.respond(2,'HOLD_OK:'+challenge(3));
    await r.emit('window','pointerup',{pointerId:22});checkIntent(r.requests[3],true,'center');
    await r.respond(3,'HOLD_OK:'+challenge(4));assert.equal(r.button.dataset.running,'true');
    await r.emit('window','pointerup');assert.equal(r.requests[4].url,'/stop');
  });
  await test('intent change during outstanding HOLD waits for nonce, never parallelizes HOLD',async()=>{
    const r=runtime();await start(r,'touch');await r.advance(20);assert.equal(r.requests.length,3);
    await r.emit('left','pointerdown',{pointerId:22,pointerType:'touch',isPrimary:false});
    await r.emit('window','pointerup',{pointerId:1});assert.equal(r.requests.length,3);
    await r.respond(2,'HOLD_OK:'+challenge(3));await r.advance(0);assert.equal(r.requests.length,4);
    checkIntent(r.requests[3],false,'left');assert.equal(r.requests[3].options.headers['X-Motor-Challenge'],challenge(3));
  });
  await test('center alone sends only STOP; center while driving retains drive but clears turn',async()=>{
    const r=runtime();await r.emit('center','click');assert.equal(r.requests[0].url,'/stop');
    await r.respond(0,'STOP_OK');assert.equal(r.requests.length,1);
    await r.emit('button','pointerdown',{pointerType:'touch'});assert.equal(r.requests[1].url,'/arm');
    await r.respond(1,'ARM_OK:'+challenge(1));await r.respond(2,'HOLD_OK:'+challenge(2));
    await r.emit('left','pointerdown',{pointerId:22,pointerType:'touch',isPrimary:false});
    checkIntent(r.requests[3],true,'left');await r.respond(3,'HOLD_OK:'+challenge(3));
    await r.emit('center','click');checkIntent(r.requests[4],true,'center');
    await r.respond(4,'HOLD_OK:'+challenge(4));await r.emit('window','pointerup',{pointerId:22});
    checkIntent(r.requests[5],true,'center');
  });
  await test('opposing steering touches request neutral until one releases',async()=>{
    const r=runtime();await leftStart(r);
    await r.emit('right','pointerdown',{pointerId:22,pointerType:'touch',isPrimary:false});
    checkIntent(r.requests[2],false,'center');await r.respond(2,'HOLD_OK:'+challenge(3));
    await r.emit('window','pointerup',{pointerId:11});checkIntent(r.requests[3],false,'right');
  });
  await test('arrow keys independently control motor and steering',async()=>{
    const r=runtime();await r.emit('window','keydown',{code:'ArrowLeft'});assert.equal(r.requests[0].url,'/arm');
    await r.emit('window','keydown',{code:'ArrowUp'});assert.equal(r.requests.length,1);
    await r.respond(0,'ARM_OK:'+challenge(1));checkIntent(r.requests[1],true,'left');
    await r.respond(1,'HOLD_OK:'+challenge(2));await r.emit('window','keyup',{code:'ArrowUp'});
    checkIntent(r.requests[2],false,'left');await r.respond(2,'HOLD_OK:'+challenge(3));
    await r.emit('window','keyup',{code:'ArrowLeft'});assert.equal(r.requests[3].url,'/stop');
  });
  for(const mode of ['cancel','network','blur','offline','hidden'])await test('combined controls '+mode+' invalidates both and never resumes held input',async()=>{
    const r=runtime();await leftStart(r);
    await r.emit('button','pointerdown',{pointerId:22,pointerType:'touch',isPrimary:false});
    await r.respond(2,'HOLD_OK:'+challenge(3));
    if(mode==='cancel')await r.emit('window','pointercancel',{pointerId:11});
    if(mode==='network'){await r.advance(20);r.requests[3].fail();await flush();}
    if(mode==='blur')await r.emit('window','blur');
    if(mode==='offline')await r.emit('window','offline');
    if(mode==='hidden'){r.document.hidden=true;await r.emit('document','visibilitychange');}
    const last=r.requests.length-1;assert.equal(r.requests[last].url,'/stop');
    await r.respond(last,'STOP_OK');await r.advance(1500);assert.equal(r.requests.length,last+1);
    assert.equal(r.button.dataset.running,'false');assert.equal(r.left.dataset.active,'false');
    assert.equal(r.button.dataset.active,'false');
  });
  async function reverseStart(r,pointerType='touch'){
    await r.emit('reverse','pointerdown',{pointerId:31,pointerType});
    assert.equal(r.requests[0].url,'/arm');await r.respond(0,'ARM_OK:'+challenge(1));
    checkIntent(r.requests[1],-1,'center');await r.respond(1,'HOLD_OK:'+challenge(2));
    assert.equal(r.button.dataset.running,'false');assert.equal(r.reverse.dataset.running,'true');
    assert.match(r.result.textContent,/vzad|couv/i);
  }
  for(const pointerType of ['mouse','touch'])await test('reverse '+pointerType+' hold, owner release and fresh press',async()=>{
    const r=runtime();
    await r.emit('reverse','click');await r.emit('reverse','pointerdown',{button:2});
    await r.emit('reverse','pointerdown',{pointerType:'mouse',isPrimary:false});
    assert.equal(r.requests.length,0);await reverseStart(r,pointerType);
    await r.emit('window','pointerup',{pointerId:999});assert.equal(r.requests.length,2);
    await r.advance(20);checkIntent(r.requests[2],-1,'center');
    assert.equal(r.requests[2].options.headers['X-Motor-Challenge'],challenge(2));
    await r.respond(2,'HOLD_OK:'+challenge(3));await r.emit('window','pointerup',{pointerId:31});
    assert.equal(r.requests[3].url,'/stop');assert.equal(r.reverse.dataset.running,'false');
    await r.respond(3,'STOP_OK');await r.advance(2000);assert.equal(r.requests.length,4);
    await r.emit('reverse','pointerdown',{pointerId:31,pointerType});
    assert.equal(r.requests[4].url,'/arm');assert.equal(r.requests[4].options.headers['X-Motor-Press'],'2');
  });
  await test('reverse ArrowDown and focused Space/Enter suppress repeat and release safely',async()=>{
    for(const code of ['ArrowDown','Space','Enter']){
      const r=runtime(),target=code==='ArrowDown'?'window':'reverse';
      await r.emit(target,'keydown',{code});assert.equal(r.requests[0].url,'/arm');
      await r.emit(target,'keydown',{code,repeat:true});assert.equal(r.requests.length,1);
      await r.respond(0,'ARM_OK:'+challenge(1));checkIntent(r.requests[1],-1,'center');
      await r.respond(1,'HOLD_OK:'+challenge(2));assert.equal(r.reverse.dataset.running,'true');
      await r.emit('window','keyup',{code});assert.equal(r.requests[2].url,'/stop');
      await r.respond(2,'STOP_OK');await r.emit(target,'keydown',{code,repeat:true});
      await r.advance(2000);assert.equal(r.requests.length,3);
      await r.emit(target,'keydown',{code});assert.equal(r.requests[3].url,'/arm');
    }
  });
  await test('reverse first keeps physical left/right directions and explicit center retains reverse',async()=>{
    for(const steer of ['left','right']){
      const r=runtime();await reverseStart(r);
      await r.emit(steer,'pointerdown',{pointerId:22,pointerType:'touch',isPrimary:false});
      checkIntent(r.requests[2],-1,steer);await r.respond(2,'HOLD_OK:'+challenge(3));
      await r.emit('center','click');checkIntent(r.requests[3],-1,'center');
      await r.respond(3,'HOLD_OK:'+challenge(4));assert.equal(r.reverse.dataset.running,'true');
      await r.emit('window','pointerup',{pointerId:22});checkIntent(r.requests[4],-1,'center');
      await r.respond(4,'HOLD_OK:'+challenge(5));await r.emit('window','pointerup',{pointerId:31});
      assert.equal(r.requests[5].url,'/stop');
    }
  });
  await test('steering first accepts secondary reverse touch and motor release retains steering',async()=>{
    const r=runtime();await leftStart(r);
    await r.emit('reverse','pointerdown',{pointerId:31,pointerType:'touch',isPrimary:false});
    checkIntent(r.requests[2],-1,'left');await r.respond(2,'HOLD_OK:'+challenge(3));
    await r.emit('window','pointerup',{pointerId:31});checkIntent(r.requests[3],0,'left');
    await r.respond(3,'HOLD_OK:'+challenge(4));assert.equal(r.reverse.dataset.running,'false');
    await r.emit('window','pointerup',{pointerId:11});assert.equal(r.requests[4].url,'/stop');
  });
  await test('opposite motor owners cancel touch, keyboard and mixed input; release/repeat never restarts',async()=>{
    const touch=(target,id)=>({target,event:'pointerdown',values:{pointerId:id,pointerType:'touch',isPrimary:id===1},release:'pointerup',up:{pointerId:id}});
    const key=code=>({target:'window',event:'keydown',values:{code},release:'keyup',up:{code}});
    const pairs=[[touch('button',1),touch('reverse',2)],[touch('reverse',1),touch('button',2)],
      [key('ArrowUp'),key('ArrowDown')],[key('ArrowDown'),key('ArrowUp')],[touch('reverse',1),key('ArrowUp')]];
    for(const [first,second] of pairs){
      const r=runtime();await r.emit(first.target,first.event,first.values);await r.respond(0,'ARM_OK:'+challenge(1));
      await r.respond(1,'HOLD_OK:'+challenge(2));await r.emit(second.target,second.event,second.values);
      assert.equal(r.requests.length,3);assert.equal(r.requests[2].url,'/stop');
      for(const control of ['button','reverse','left','right'])assert.equal(r[control].dataset.active,'false');
      assert.equal(r.button.dataset.running,'false');assert.equal(r.reverse.dataset.running,'false');
      await r.respond(2,'STOP_OK');
      // Both owners remain reserved until their actual release, including the conflicting owner.
      await r.emit(first.target,first.event,first.values);await r.emit(second.target,second.event,second.values);
      if(second.event==='keydown')await r.emit(second.target,second.event,{...second.values,repeat:true});
      await r.advance(2000);assert.equal(r.requests.length,3);
      await r.emit('window',first.release,first.up);await r.advance(100);assert.equal(r.requests.length,3);
      await r.emit('window',second.release,second.up);await r.advance(100);assert.equal(r.requests.length,3);
      await r.emit(second.target,second.event,second.values);assert.equal(r.requests[3].url,'/arm');
    }
  });
  await test('conflict invalidates delayed ARM, HOLD_OK and HOLD_REARM even after a fresh press',async()=>{
    for(const replyType of ['ARM_OK','HOLD_OK','HOLD_REARM']){
      const r=runtime({honorAbort:false});await r.emit('button','pointerdown',{pointerType:'touch'});
      let old=0;
      if(replyType!=='ARM_OK'){
        await r.respond(0,'ARM_OK:'+challenge(1));await r.respond(1,'HOLD_OK:'+challenge(2));
        await r.advance(20);old=2;
      }
      await r.emit('reverse','pointerdown',{pointerId:2,pointerType:'touch',isPrimary:false});
      assert.equal(r.requests[old].aborted,true);const stopped=r.requests.length-1;
      assert.equal(r.requests[stopped].url,'/stop');await r.respond(stopped,'STOP_OK');
      await r.emit('window','pointerup',{pointerId:1});await r.emit('window','pointerup',{pointerId:2});
      await r.emit('reverse','pointerdown',{pointerId:2,pointerType:'touch'});
      const fresh=r.requests.length-1;assert.equal(r.requests[fresh].url,'/arm');
      await r.respond(old,replyType==='HOLD_REARM'?replyType:replyType+':'+challenge(7));await r.advance(20);
      assert.equal(r.requests.length,fresh+1);assert.equal(r.button.dataset.running,'false');assert.equal(r.reverse.dataset.running,'false');
      await r.respond(fresh,'ARM_OK:'+challenge(8));checkIntent(r.requests[fresh+1],-1,'center');
      assert.equal(r.requests[fresh+1].options.headers['X-Motor-Challenge'],challenge(8));
      await r.respond(fresh+1,'HOLD_OK:'+challenge(9));assert.equal(r.reverse.dataset.running,'true');
    }
  });
  await test('HOLD_REARM cancels the original hold and elapsed time cannot restart it',async()=>{
    const r=runtime();await r.emit('reverse','pointerdown',{pointerId:31,pointerType:'touch'});
    await r.respond(0,'ARM_OK:'+challenge(1));checkIntent(r.requests[1],-1,'center');
    await r.respond(1,'HOLD_REARM');assert.equal(r.requests[2].url,'/stop');
    assert.equal(r.button.dataset.running,'false');assert.equal(r.reverse.dataset.running,'false');
    assert.equal(r.reverse.dataset.active,'false');await r.respond(2,'STOP_OK');
    assert.match(r.result.textContent,/Změna směru: pusť ovladače a stiskni znovu\./);
    await r.emit('reverse','pointerdown',{pointerId:31,pointerType:'touch'});
    await r.advance(2000);assert.equal(r.requests.length,3);
    await r.emit('window','pointerup',{pointerId:31});await r.advance(300);assert.equal(r.requests.length,3);
    await r.emit('reverse','pointerdown',{pointerId:31,pointerType:'touch'});
    assert.equal(r.requests[3].url,'/arm');assert.equal(r.requests[3].options.headers['X-Motor-Press'],'2');
    await r.respond(3,'ARM_OK:'+challenge(2));checkIntent(r.requests[4],-1,'center');
    await r.respond(4,'HOLD_OK:'+challenge(3));assert.equal(r.reverse.dataset.running,'true');
  });
  await test('an early new press receiving REARM again must be released; key repeat never retries',async()=>{
    const r=runtime();await r.emit('window','keydown',{code:'ArrowDown'});
    await r.respond(0,'ARM_OK:'+challenge(1));await r.respond(1,'HOLD_REARM');await r.respond(2,'STOP_OK');
    await r.emit('window','keyup',{code:'ArrowDown'});assert.equal(r.requests.length,3);
    await r.emit('window','keydown',{code:'ArrowDown'});assert.equal(r.requests[3].url,'/arm');
    await r.respond(3,'ARM_OK:'+challenge(2));await r.respond(4,'HOLD_REARM');
    assert.equal(r.requests[5].url,'/stop');await r.respond(5,'STOP_OK');
    await r.emit('window','keydown',{code:'ArrowDown',repeat:true});await r.advance(2000);
    assert.equal(r.requests.length,6);assert.equal(r.reverse.dataset.running,'false');
    await r.emit('window','keyup',{code:'ArrowDown'});assert.equal(r.requests.length,6);
    await r.emit('window','keydown',{code:'ArrowDown'});assert.equal(r.requests[6].url,'/arm');
    assert.equal(r.requests[6].options.headers['X-Motor-Press'],'3');
  });
  await test('REARM with a held steering owner blocks fresh motor presses until every owner releases',async()=>{
    const r=runtime();await leftStart(r);
    await r.emit('reverse','pointerdown',{pointerId:31,pointerType:'touch',isPrimary:false});
    checkIntent(r.requests[2],-1,'left');await r.respond(2,'HOLD_REARM');
    assert.equal(r.requests[3].url,'/stop');await r.respond(3,'STOP_OK');
    await r.emit('window','pointerup',{pointerId:31});assert.equal(r.requests.length,4);
    // The old left contact is still physically held; a different, genuinely new motor contact is blocked.
    await r.emit('reverse','pointerdown',{pointerId:32,pointerType:'touch',isPrimary:false});
    await r.advance(2000);assert.equal(r.requests.length,4);assert.equal(r.reverse.dataset.running,'false');
    await r.emit('window','pointerup',{pointerId:32});await r.emit('window','pointerup',{pointerId:11});
    await r.advance(300);assert.equal(r.requests.length,4);
    await r.emit('reverse','pointerdown',{pointerId:33,pointerType:'touch'});
    assert.equal(r.requests[4].url,'/arm');await r.respond(4,'ARM_OK:'+challenge(3));
    checkIntent(r.requests[5],-1,'center');
  });
  await test('contacts rejected during conflict latch or pending STOP must also release before rearming',async()=>{
    const touch=(target,id)=>({target,event:'pointerdown',values:{pointerId:id,pointerType:'touch',isPrimary:id===1},release:'pointerup',up:{pointerId:id}});
    const key=(target,code)=>({target,event:'keydown',values:{code},release:'keyup',up:{code}});
    const sequences=[
      [touch('button',1),touch('reverse',2),touch('button',3),touch('reverse',4)],
      [key('window','ArrowUp'),key('window','ArrowDown'),key('button','Space'),key('reverse','Enter')],
      [touch('button',1),key('window','ArrowDown'),key('window','ArrowUp'),touch('reverse',4)]
    ];
    for(const pendingStop of [false,true])for(const [first,second,third,fourth] of sequences){
      const r=runtime();await r.emit(first.target,first.event,first.values);await r.respond(0,'ARM_OK:'+challenge(1));
      await r.respond(1,'HOLD_OK:'+challenge(2));await r.emit(second.target,second.event,second.values);
      assert.equal(r.requests[2].url,'/stop');if(!pendingStop)await r.respond(2,'STOP_OK');
      await r.emit('window',first.release,first.up);await r.emit(third.target,third.event,third.values);
      if(pendingStop)assert.equal(r.button.disabled,true);
      await r.emit('window',second.release,second.up);await r.emit(fourth.target,fourth.event,fourth.values);
      assert.equal(r.requests.length,3);if(pendingStop)await r.respond(2,'STOP_OK');
      await r.advance(2000);assert.equal(r.requests.length,3);assert.equal(r.reverse.dataset.running,'false');
      await r.emit('window',third.release,third.up);await r.advance(300);assert.equal(r.requests.length,3);
      await r.emit('window',fourth.release,fourth.up);await r.advance(300);assert.equal(r.requests.length,3);
      await r.emit(fourth.target,fourth.event,fourth.values);assert.equal(r.requests[3].url,'/arm');
      await r.respond(3,'ARM_OK:'+challenge(3));checkIntent(r.requests[4],-1,'center');
    }
  });
  await test('second contact on the same forward button cannot be forgotten or transfer motor ownership',async()=>{
    const r=runtime();await start(r,'touch');
    await r.emit('button','pointerdown',{pointerId:2,pointerType:'touch',isPrimary:false});assert.equal(r.requests.length,2);
    await r.emit('window','pointerup',{pointerId:1});assert.equal(r.requests[2].url,'/stop');
    await r.respond(2,'STOP_OK');await r.advance(300);assert.equal(r.requests.length,3);
    await r.emit('reverse','pointerdown',{pointerId:3,pointerType:'touch',isPrimary:false});
    assert.equal(r.requests.length,4);assert.equal(r.requests[3].url,'/stop');
    await r.respond(3,'STOP_OK');await r.advance(2000);assert.equal(r.requests.length,4);
    await r.emit('window','pointerup',{pointerId:2});assert.equal(r.requests.length,4);
    await r.emit('window','pointerup',{pointerId:3});assert.equal(r.requests.length,4);
    await r.emit('reverse','pointerdown',{pointerId:4,pointerType:'touch'});assert.equal(r.requests[4].url,'/arm');
    await r.respond(4,'ARM_OK:'+challenge(3));checkIntent(r.requests[5],-1,'center');
  });
  await test('reverse failure retains its owner and recovery requires release plus new press',async()=>{
    for(const mode of ['network','timeout']){
      const r=runtime();await reverseStart(r);await r.advance(20);
      if(mode==='network'){r.requests[2].fail();await flush();}else await r.advance(1200);
      assert.equal(r.requests[3].url,'/stop');await r.respond(3,'STOP_OK');
      await r.emit('reverse','pointerdown',{pointerId:31,pointerType:'touch'});await r.advance(2000);
      assert.equal(r.requests.length,4);assert.equal(r.reverse.dataset.running,'false');
      await r.emit('window','pointerup',{pointerId:31});assert.equal(r.requests.length,4);
      await r.emit('reverse','pointerdown',{pointerId:31,pointerType:'touch'});assert.equal(r.requests[4].url,'/session');
    }
  });
  console.log(`PASS ${cases} actual-inline-JavaScript browser scenarios; no hardware or network accessed`);
})().catch(error => {console.error(error);process.exitCode = 1;});
