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
  const button=makeButton(),left=makeButton(),right=makeButton(),center=makeButton();
  const result = { textContent: '' };
  const window = new Target();
  const document = Object.assign(new Target(), { hidden: false, getElementById: id => ({drive:button,left,right,center,result})[id] });
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
  return {button, left, right, center, result, document, window, requests,
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
    assert.equal(request.url,'/hold');assert.equal(request.options.headers['X-Control-Motor'],motor?'1':'0');
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
  console.log(`PASS ${cases} actual-inline-JavaScript browser scenarios; no hardware or network accessed`);
})().catch(error => {console.error(error);process.exitCode = 1;});
