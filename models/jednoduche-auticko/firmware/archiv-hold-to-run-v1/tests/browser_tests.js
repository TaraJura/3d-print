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
  const button = Object.assign(new Target(), { disabled: false, dataset: {}, setPointerCapture() {} });
  const result = { textContent: '' };
  const window = new Target();
  const document = Object.assign(new Target(), { hidden: false, getElementById: id => id === 'drive' ? button : result });
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
  return {button, result, document, window, requests,
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
    await r.advance(99); assert.equal(r.requests.length, 2);
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
    const r = runtime({honorAbort: false}); await start(r); await r.advance(100);
    await r.emit('window', 'pointerup'); assert.equal(r.requests[3].url, '/stop');
    await r.respond(3, 'STOP_OK'); await r.respond(2, 'HOLD_OK:' + challenge(3)); await r.advance(2000);
    assert.equal(r.requests.length, 4); assert.equal(r.button.dataset.running, 'false');
  });
  for (const mode of ['network', 'HTTP', 'bad-challenge', 'timeout']) await test(mode + ' failure stops without automatic retry', async () => {
    const r = runtime(); await start(r); await r.advance(100);
    if (mode === 'network') {r.requests[2].fail(); await flush();}
    if (mode === 'HTTP') await r.respond(2, 'rejected', false);
    if (mode === 'bad-challenge') await r.respond(2, 'HOLD_OK:wrong');
    if (mode === 'timeout') await r.advance(1200);
    assert.equal(r.requests[3].url, '/stop'); assert.equal(r.button.dataset.running, 'false');
    await r.respond(3, 'STOP_OK'); await r.advance(2000); assert.equal(r.requests.length, 4);
  });
  await test('failed STOP keeps button disabled until page reload', async () => {
    const r = runtime(); await start(r); await r.emit('window', 'pointerup');
    r.requests[2].fail(); await flush(); await r.advance(2000);
    await r.emit('button', 'pointerdown'); assert.equal(r.requests.length, 3); assert.equal(r.button.disabled, true);
  });
  for (const code of ['Space', 'Enter']) await test('keyboard ' + code + ' down/up and repeat suppression', async () => {
    const r = runtime(); await r.emit('button', 'keydown', {code}); assert.equal(r.requests[0].url, '/arm');
    await r.emit('button', 'keydown', {code, repeat: true}); assert.equal(r.requests.length, 1);
    await r.respond(0, 'ARM_OK:' + challenge(1)); await r.respond(1, 'HOLD_OK:' + challenge(2));
    await r.emit('window', 'keyup', {code}); assert.equal(r.requests[2].url, '/stop');
    await r.respond(2, 'STOP_OK'); await r.advance(2000); assert.equal(r.requests.length, 3);
  });
  console.log(`PASS ${cases} actual-inline-JavaScript browser scenarios; no hardware or network accessed`);
})().catch(error => {console.error(error);process.exitCode = 1;});
