#include <WiFiS3.h>
#include <FspTimer.h>
#include <pwm.h>
#include <ctype.h>
#include <string.h>
#include <stdio.h>

// Motor v2 beze změny výkonu; nové řízení SG90 s malým zkušebním rozsahem.
const char BUILD_ID[] = "v3-steering-v3";
constexpr uint8_t EN = 5, IN1 = 7, IN2 = 8, STEER_PIN = 9;
constexpr uint16_t STEER_CENTER_US=1525, STEER_OFFSET_US=300;
constexpr int8_t STEER_SIGN=1; // Ověřit směr s odpojeným táhlem; ±300 us není změřený úhel.
const char SSID[] = "Auticko-test", PASSWORD[] = "auticko123"; // Veřejné demo heslo.
WiFiServer server(80);
bool ready = false;
bool apConfigured=false, networkAttempted=false;
uint32_t networkCheckedAt=0, tokenSequence=0;
char motorToken[33]="", previousSessionToken[33]="", requestToken[33]="";
enum Request { INVALID, PAGE, SESSION, ARM, HOLD, STOP };
enum DriveState { IDLE, ARMED, RUNNING };
constexpr uint32_t LEASE_MS=500, ARM_WAIT_MS=3000, TIMER_TICK_MS=5;
PwmOut motorPwm(EN);
PwmOut steeringPwm(STEER_PIN);
FspTimer safetyTimer;
volatile bool pwmReady=false, servoReady=false, safetyReady=false;
volatile uint16_t steeringPulseUs=STEER_CENTER_US;
bool requestMotor=true;
int8_t requestSteer=0;
volatile DriveState driveState=IDLE;
volatile uint16_t leaseTicks=0;
volatile uint32_t watchdogStops=0, armExpiries=0, runExpiries=0;
volatile uint8_t stopReason=0; // 0=start/local, 1=STOP, 2=ARM expiry, 3=RUN expiry, 4=network, 5=session, 6=PWM/RNG
uint32_t diagnosticRequestLogAt=0;
uint32_t lastPress=0, requestPress=0, challengeIssuedAt=0;
char holdChallenge[33]="", requestChallenge[33]="";
Request readRequest(WiFiClient &client); // Explicitně kvůli Arduino generování prototypů.
bool setSteering(int8_t direction);

// UNO R4 WiFi Serial je UART přes ESP bridge: bool() vždy true, bez detekce monitoru.
// Krátký synchronní přenos při 115200; žádné čekání na monitor ani Serial.flush().
char diagnosticFirmware[24]="not-read";
uint8_t diagnosticIP[4]={0,0,0,0};
const char *diagnosticSetup="starting";
int diagnosticStatus=-1, diagnosticApStart=-1;
uint32_t diagnosticStatusAt=0, diagnosticSnapshotAt=0, diagnosticHttpAt=0;
uint32_t diagnosticStatusLogAt=0;
uint32_t diagnosticAccepted=0, diagnosticClosed=0;
bool diagnosticHttpSeen=false;
void diagnosticEvent(const char *event, long value) {
  char line[96];
  const int n=snprintf(line,sizeof(line),"DIAG %lu %s %ld\n",millis(),event,value);
  if (n>0 && n<int(sizeof(line))) Serial.write(reinterpret_cast<uint8_t *>(line),size_t(n));
}
void diagnosticPoll() {
  bool requested=false;
  for (uint8_t i=0;i<8 && Serial.available()>0;++i) if (Serial.read()=='?') requested=true;
  const uint32_t now=millis(), elapsed=uint32_t(now-diagnosticSnapshotAt);
  if (elapsed<5000 && !(requested && elapsed>=1000)) return;
  diagnosticSnapshotAt=now;
  char line[160];
  const int state=int(driveState);
  int detail=snprintf(line,sizeof(line),"DIAG build=%s safety=%d drive=%d ENread=%d IN1=%d IN2=%d watchdog=%lu\n",
    BUILD_ID,int(safetyReady),state,int(digitalRead(EN)),int(digitalRead(IN1)),int(digitalRead(IN2)),
    static_cast<unsigned long>(watchdogStops));
  if(detail>0 && detail<int(sizeof(line)))Serial.write(reinterpret_cast<uint8_t *>(line),size_t(detail));
  detail=snprintf(line,sizeof(line),"DIAG steeringReady=%d steeringUs=%u neutralUs=%u rangeUs=%u\n",
    int(servoReady),unsigned(steeringPulseUs),unsigned(STEER_CENTER_US),unsigned(STEER_OFFSET_US));
  if(detail>0 && detail<int(sizeof(line)))Serial.write(reinterpret_cast<uint8_t *>(line),size_t(detail));
  int counters=snprintf(line,sizeof(line),"DIAG armExpired=%lu runExpired=%lu stopReason=%u leaseMs=%u challengeAgeMs=%lu\n",
    static_cast<unsigned long>(armExpiries),static_cast<unsigned long>(runExpiries),unsigned(stopReason),
    unsigned(leaseTicks*TIMER_TICK_MS),static_cast<unsigned long>(uint32_t(millis()-challengeIssuedAt)));
  if(counters>0 && counters<int(sizeof(line)))Serial.write(reinterpret_cast<uint8_t *>(line),size_t(counters));
  int n=snprintf(line,sizeof(line),"DIAG %lu boot=%s fw=%s ip=%u.%u.%u.%u\n",
    millis(),diagnosticSetup,diagnosticFirmware,unsigned(diagnosticIP[0]),unsigned(diagnosticIP[1]),
    unsigned(diagnosticIP[2]),unsigned(diagnosticIP[3]));
  if (n>0 && n<int(sizeof(line))) Serial.write(reinterpret_cast<uint8_t *>(line),size_t(n));
  n=snprintf(line,sizeof(line),"DIAG ready=%d server=%d APstart=%d statusLast=%d ageMs=%lu HTTP=%lu closed=%lu\n",
    int(ready),int(bool(server)),diagnosticApStart,diagnosticStatus,
    static_cast<unsigned long>(uint32_t(now-diagnosticStatusAt)),
    static_cast<unsigned long>(diagnosticAccepted),static_cast<unsigned long>(diagnosticClosed));
  if (n>0 && n<int(sizeof(line))) Serial.write(reinterpret_cast<uint8_t *>(line),size_t(n));
}
const char HTML[] = R"HTML(<!doctype html><html lang="cs"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Ovládání autíčka</title>
<style>
*{box-sizing:border-box}body{font:17px system-ui;max-width:32rem;margin:0 auto;padding:1.25rem;line-height:1.5;color:#172a32;background:#f5f7f8}
h1{font-size:1.7rem;margin:.25rem 0}.label{color:#596b75;font-size:.85rem;margin:0 0 1.5rem}p{margin:.8rem 0}
button{font:inherit;font-weight:600;min-height:76px;padding:1rem .6rem;border:1px solid #bac9cf;border-radius:12px;color:inherit;background:#fff;cursor:pointer;touch-action:none;user-select:none;-webkit-user-select:none}
button:focus-visible{outline:3px solid #167bcb;outline-offset:3px}button:disabled{cursor:wait;opacity:.6}
#drive{width:100%;background:#174d3a;color:#fff;border-color:#174d3a;margin:.7rem 0 1.25rem;min-height:108px}
#drive[data-running="true"]{background:#267a55}.steering{display:grid;grid-template-columns:1fr 1fr 1fr;gap:.6rem}
button[data-active="true"]{background:#dceeff;border-color:#167bcb}.hint{font-size:.88rem;color:#50636e}
#result{background:#fff;border:1px solid #dce3e7;border-radius:12px;padding:1rem;min-height:82px;margin-top:1.4rem}
.warning{font-size:.83rem;padding-top:1rem;border-top:1px solid #dce3e7;color:#53636c}
</style>
<h1>Ovládání autíčka</h1><p class="label">Pohon vpřed · řízení SG90</p>
<p>Drž pro jízdu. Druhým prstem můžeš současně zatáčet.</p>
<button id="drive" type="button">↑<br>Držet pro jízdu vpřed</button>
<div class="steering" role="group" aria-label="Řízení">
<button id="left" type="button" aria-label="Držet doleva">←<br>Doleva</button>
<button id="center" type="button">Rovně</button>
<button id="right" type="button" aria-label="Držet doprava">→<br>Doprava</button>
</div>
<p class="hint">Doleva a doprava drž. Puštěním směru se řízení vrátí rovně. Samotné řízení motor nespustí.</p>
<p id="result" role="status" aria-live="polite">Připraveno. Motor je vypnutý, řízení rovně.</p>
<p class="warning">Zkušební malý rozsah řízení. Po zapnutí servo dostane povel na střed; první nastavení proveď bez připojeného táhla. Při výpadku se pohon vypne a řízení vrátí na střed. Ztracený povel může znamenat prodlevu až 1 s; kola mohou dobíhat.</p><script>
const button=document.getElementById('drive'), result=document.getElementById('result');
const controls={drive:button,left:document.getElementById('left'),right:document.getElementById('right')};
const centerButton=document.getElementById('center');
const owners={drive:null,left:null,right:null}, active={drive:false,left:false,right:false};
let token='@TOKEN@', sessionNeeded=false;
let press=0, held=false, generation=0, timer=null, pending=null, stopping=false, nonce=null, dirty=false;
const headers=(id,challenge)=>({'X-Motor-Control':'1','X-Motor-Token':token,'X-Motor-Press':String(id),
  ...(challenge?{'X-Motor-Challenge':challenge}:{})});
const intent=()=>({motor:active.drive,steer:active.left===active.right?'center':active.left?'left':'right'});
const anyActive=()=>Object.values(active).some(Boolean);
function paint(){for(const [name,control] of Object.entries(controls))control.dataset.active=String(active[name]);}
function disable(value){for(const control of [...Object.values(controls),centerButton])control.disabled=value;}
async function command(path,id,challenge,state) {
  const controller=new AbortController(); pending=controller;
  const deadline=setTimeout(()=>controller.abort(),1200);
  try {
    const fields=path==='/session'?{'X-Motor-Control':'1','X-Motor-Token':token}:headers(id,challenge);
    if(state)Object.assign(fields,{'X-Control-Motor':state.motor?'1':'0','X-Control-Steer':state.steer});
    const reply=await fetch(path,{method:'POST',headers:fields,body:'',cache:'no-store',signal:controller.signal});
    const text=await reply.text();if(!reply.ok)throw new Error('request');return text;
  } finally {clearTimeout(deadline);if(pending===controller)pending=null;}
}
function stop(message='Pohon vypnutý, řízení rovně. Pro další jízdu stiskni znovu.',failed=false,force=false) {
  if((!held && !force) || stopping)return;
  held=false;generation++;clearTimeout(timer);timer=null;nonce=null;
  for(const name of Object.keys(active))active[name]=false;paint();
  if(pending)pending.abort();if(failed)sessionNeeded=true;
  // Retain physical owners on error: a still-held touch/key cannot restart itself.
  button.dataset.running='false';disable(true);stopping=true;result.textContent='Zastavuji a vracím řízení rovně…';
  if(force && press===0)press=1;
  const controller=new AbortController(), deadline=setTimeout(()=>controller.abort(),1500);
  fetch('/stop',{method:'POST',headers:headers(press),body:'',cache:'no-store',keepalive:true,signal:controller.signal})
    .then(async reply=>{if(!reply.ok || await reply.text()!=='STOP_OK')throw new Error();result.textContent=message;})
    .catch(()=>{sessionNeeded=true;result.textContent='Spojení přerušeno. Časovač vypne pohon a vrátí řízení. Pusť ovladače a stiskni znovu.';})
    .finally(()=>{clearTimeout(deadline);stopping=false;disable(false);});
}
async function start() {
  if(held || stopping || button.disabled || document.hidden || !anyActive())return;
  held=true;nonce=null;const gen=++generation;result.textContent='Připravuji ovládání…';
  try {
    if(sessionNeeded) {
      const session=await command('/session');
      if(!held || gen!==generation)return;
      if(!/^SESSION_OK:[0-9a-f]{32}$/.test(session))throw new Error();
      token=session.slice(11);press=0;sessionNeeded=false;
    }
    const id=++press,armed=await command('/arm',id);
    if(!held || gen!==generation)return;
    if(!/^ARM_OK:[0-9a-f]{32}$/.test(armed))throw new Error();
    nonce=armed.slice(7);await heartbeat(id,gen);
  } catch(_){if(held && gen===generation)stop(undefined,true);}
}
async function heartbeat(id,gen) {
  if(!held || gen!==generation || !nonce || pending)return;
  const challenge=nonce,state=intent();nonce=null;dirty=false;
  try {
    const reply=await command('/hold',id,challenge,state);
    if(!held || gen!==generation)return;
    if(!/^HOLD_OK:[0-9a-f]{32}$/.test(reply))throw new Error();
    nonce=reply.slice(8);button.dataset.running=String(state.motor);
    result.textContent=(state.motor?'Pohon vpřed':'Motor vypnutý')+' · '+({left:'řízení doleva',center:'řízení rovně',right:'řízení doprava'}[state.steer])+'.';
    timer=setTimeout(()=>{timer=null;heartbeat(id,gen);},dirty?0:20);
  } catch(_){if(held && gen===generation)stop(undefined,true);}
}
function changed() {
  paint();if(!anyActive()){stop();return;}
  if(!held){start();return;}
  dirty=true;
  if(nonce && !pending){clearTimeout(timer);timer=null;heartbeat(press,generation);}
}
function begin(name,owner) {
  if(owners[name]!==null || stopping || controls[name].disabled || document.hidden)return;
  owners[name]=owner;active[name]=true;changed();
}
function release(owner) {
  let found=false;
  for(const name of Object.keys(owners))if(owners[name]===owner){owners[name]=null;active[name]=false;found=true;}
  if(found)changed();
}
for(const [name,control] of Object.entries(controls)) {
  control.addEventListener('pointerdown',event=>{
    if(event.button!==0 || (event.pointerType!=='touch' && !event.isPrimary) || owners[name]!==null || stopping || control.disabled || document.hidden)return;
    event.preventDefault();control.setPointerCapture(event.pointerId);begin(name,'p'+event.pointerId);
  });
  control.addEventListener('lostpointercapture',event=>release('p'+event.pointerId));
  control.addEventListener('contextmenu',event=>event.preventDefault());
  control.addEventListener('keydown',event=>{
    if(event.code!=='Space' && event.code!=='Enter')return;
    event.preventDefault();if(!event.repeat)begin(name,'k'+event.code);
  });
}
window.addEventListener('pointerup',event=>release('p'+event.pointerId));
// Cancellation may signal a system gesture: invalidate both controls together.
window.addEventListener('pointercancel',event=>{stop();release('p'+event.pointerId);});
window.addEventListener('keydown',event=>{
  const name={ArrowUp:'drive',ArrowLeft:'left',ArrowRight:'right'}[event.code];
  if(name){event.preventDefault();if(!event.repeat)begin(name,'k'+event.code);}
});
window.addEventListener('keyup',event=>{if(['Space','Enter','ArrowUp','ArrowLeft','ArrowRight'].includes(event.code)){event.preventDefault();release('k'+event.code);}});
centerButton.addEventListener('click',()=>{
  active.left=active.right=false;paint();
  if(anyActive())changed();else stop('Motor vypnutý, řízení rovně.',false,true);
});
function leave(){stop();for(const name of Object.keys(owners))owners[name]=null;}
window.addEventListener('blur',leave);window.addEventListener('pagehide',leave);
window.addEventListener('offline',()=>stop(undefined,true));
document.addEventListener('visibilitychange',()=>{if(document.hidden)leave();});
</script></html>)HTML";

// Volat jen v ISR nebo krátké kritické sekci. PWM je předem inicializované:
// žádná alokace, modem, čekání ani Serial. Směrové GPIO jdou LOW i při chybě PWM.
void motorOutputsOff() {
  if (pwmReady && !motorPwm.pulse_perc(0.0f)) {
    // Fail closed if the PWM peripheral ever refuses the OFF update.
    pinMode(EN,OUTPUT); digitalWrite(EN,LOW); pwmReady=false; safetyReady=false;
  }
  digitalWrite(IN1,LOW); digitalWrite(IN2,LOW); digitalWrite(LED_BUILTIN,LOW);
}
bool setSteering(int8_t direction) {
  if (!servoReady || direction < -1 || direction > 1) return false;
  const uint16_t pulse=STEER_CENTER_US + STEER_SIGN*int(direction)*STEER_OFFSET_US;
  if (!steeringPwm.pulse_perc(float(pulse)/200.0f)) {
    pinMode(STEER_PIN,OUTPUT); digitalWrite(STEER_PIN,LOW);
    servoReady=false; safetyReady=false; return false;
  }
  steeringPulseUs=pulse; return true;
}
void outputsOff() {
  motorOutputsOff();
  // Hardware50Hz PWM keeps producing the neutral pulse even if WiFi blocks.
  // A failed peripheral update disables all motion; LOW cannot promise centering.
  if (servoReady && !setSteering(0)) stopReason=6;
}
void motorStop() {
  noInterrupts(); driveState=IDLE; leaseTicks=0; outputsOff(); interrupts();
  holdChallenge[0]='\0';
}
void safetyTick(timer_callback_args_t *) {
  if (driveState!=IDLE && leaseTicks>0 && --leaseTicks==0) {
    if(driveState==ARMED){++armExpiries;stopReason=2;}else{++runExpiries;stopReason=3;}
    driveState=IDLE; outputsOff(); ++watchdogStops;
  }
}
bool initializeSafety() {
  // Reserve the PWM timer before asking for a separate, genuinely free timer.
  pwmReady=motorPwm.begin(490.0f,0.0f);
  if (!pwmReady) {pinMode(EN,OUTPUT); digitalWrite(EN,LOW); return false;}
  // Reserve D9 PWM too before allocating the independent5ms safety timer.
  // Startup commands the configured center; first set up without linkage.
  servoReady=steeringPwm.begin(50.0f,float(STEER_CENTER_US)/200.0f);
  if (!servoReady || !setSteering(0)) {
    pinMode(STEER_PIN,OUTPUT); digitalWrite(STEER_PIN,LOW); servoReady=false; return false;
  }
  uint8_t type=GPT_TIMER;
  const int8_t channel=FspTimer::get_available_timer(type);
  return channel>=0 && safetyTimer.begin(TIMER_MODE_PERIODIC,type,uint8_t(channel),
    1000.0f/TIMER_TICK_MS,0.0f,safetyTick) && safetyTimer.setup_overflow_irq(2) &&
    safetyTimer.open() && safetyTimer.start();
}

bool mintToken(char *destination) {
  destination[0]='\0';
  if (tokenSequence==UINT32_MAX) return false;
  // UNO R4 core 1.6.0 používá bez randomSeed() hardware TRNG, žádný analogový pin.
  const long a=random(0x7fffffffL), b=random(0x7fffffffL), c=random(0x7fffffffL);
  if (a<0 || b<0 || c<0) return false;
  ++tokenSequence;
  snprintf(destination,33,"%08x%08x%08x%08x",
    static_cast<unsigned>(a),static_cast<unsigned>(b),
    static_cast<unsigned>(c),static_cast<unsigned>(tokenSequence));
  return true;
}

bool mintMotorToken() { return mintToken(motorToken); }

bool applyArm(uint32_t press) {
  if (!safetyReady || press<=lastPress) return false;
  motorStop(); lastPress=press;
  if (!mintToken(holdChallenge)) return false;
  challengeIssuedAt=millis();
  noInterrupts(); leaseTicks=ARM_WAIT_MS/TIMER_TICK_MS; driveState=ARMED; interrupts();
  return true;
}
bool applyHold(uint32_t press, const char *challenge, bool motor, int8_t steer) {
  if (!safetyReady || press!=lastPress || !holdChallenge[0] || strcmp(challenge,holdChallenge)) return false;
  // Consume before any operation that could delay execution. A duplicate cannot renew.
  holdChallenge[0]='\0';
  const uint32_t issued=challengeIssuedAt;
  if (!mintToken(holdChallenge)) { motorStop(); stopReason=6; return false; }
  noInterrupts();
  const uint32_t age=uint32_t(millis()-issued);
  // ISR expiry is a latch: even a late valid packet cannot resurrect a stopped run.
  const bool valid=(driveState==ARMED || driveState==RUNNING) && age<LEASE_MS;
  if (valid) {
    leaseTicks=LEASE_MS/TIMER_TICK_MS; // One fresh packet grants a full lease; no double-RTT dependency.
    // Single-flight, one-use challenge expires after 500 ms. Lost STOP plus one
    // in-flight HOLD can extend physical release-to-OFF to at most 1000 ms.
    bool outputOk=setSteering(steer);
    if (outputOk && motor) {
      digitalWrite(IN1,HIGH); digitalWrite(IN2,LOW);
      outputOk=motorPwm.pulse_perc(128.0f*100.0f/255.0f);
      if (outputOk) digitalWrite(LED_BUILTIN,HIGH);
    } else {motorOutputsOff(); outputOk=outputOk && safetyReady;}
    if (outputOk) driveState=RUNNING; // Control lease may steer while motor is OFF.
    else { driveState=IDLE; leaseTicks=0; stopReason=6; outputsOff(); }
  }
  const bool running=valid && driveState==RUNNING;
  interrupts();
  if (!running) {motorStop(); return false;}
  challengeIssuedAt=millis();
  return true;
}
void applyStop(uint32_t press) {
  // Fence STOP before its ARM too, but never let an older press stop a newer one.
  if (press<lastPress) return;
  lastPress=press; motorStop(); stopReason=1;
}

bool networkReady() {
  if (ready && uint32_t(millis()-networkCheckedAt)<100) return true;
  if (!ready && networkAttempted && uint32_t(millis()-networkCheckedAt)<1000) return false;
  networkAttempted=true;
  int status=WiFi.status();
  networkCheckedAt=millis();
  if (!apConfigured && status!=WL_NO_MODULE) {
    motorStop(); motorToken[0]='\0';
    snprintf(diagnosticFirmware,sizeof(diagnosticFirmware),"%s",WiFi.firmwareVersion());
    WiFi.config(IPAddress(192,168,4,1));
    diagnosticApStart=WiFi.beginAP(SSID,PASSWORD); diagnosticEvent("AP-start",diagnosticApStart);
    apConfigured=diagnosticApStart==WL_AP_LISTENING;
    if (apConfigured) {
      delay(10000); // Stejná počáteční příprava AP; motor je vypnutý.
      status=WiFi.status();
    } else diagnosticSetup="ap-failed";
    networkCheckedAt=millis();
  }
  if (status!=diagnosticStatus && uint32_t(millis()-diagnosticStatusLogAt)>=1000) {
    diagnosticStatusLogAt=millis(); diagnosticEvent("WiFi-status",status);
  }
  diagnosticStatus=status; diagnosticStatusAt=millis();
  if (!apConfigured || (status!=WL_AP_LISTENING && status!=WL_AP_CONNECTED)) {
    motorStop(); motorToken[0]='\0';
    if (ready || strcmp(diagnosticSetup,"wifi-wait"))
      diagnosticEvent("STOP WiFi retry",status);
    ready=false; stopReason=4; diagnosticSetup="wifi-wait"; return false;
  }
  if (!server) {
    server.begin(); diagnosticEvent("server-begin",int(bool(server)));
    if (!server) {
      motorStop(); motorToken[0]='\0'; ready=false; diagnosticSetup="server-begin-failed"; return false;
    }
  }
  if (!ready) {
    // SERVEREND ve bridge 0.4.1 nečistí pending klienty. Starý POST blokuje token.
    // Při přechodné chybě zůstává běžící server zachován; žádný automatický pulz.
    motorToken[0]='\0'; ready=true; diagnosticSetup="server-started";
    const IPAddress ip=WiFi.localIP(); for (uint8_t i=0;i<4;++i) diagnosticIP[i]=ip[i];
    diagnosticEvent("web-ready new-page-required",0);
  }
  return true;
}

// Mobilní prohlížeče běžně posílají delší User-Agent a Accept hlavičky.
// Příjem zůstává omezený; motor hlídá nezávisle přerušení časovače.
constexpr size_t MAX_HTTP_LINE = 1024, MAX_HTTP_BYTES = 8192;
constexpr uint32_t HTTP_READ_TIMEOUT_MS = 3000;
Request readRequest(WiFiClient &client) {
  // Jedno spojení současně: buffer mimo malý zásobník UNO R4.
  static char line[MAX_HTTP_LINE+1]; size_t length=0, bytes=0;
  bool first=true, cr=false, host=false, zeroLength=false, trigger=false, token=false, press=false, challenge=false, origin=false;
  bool motorIntent=false, steerIntent=false;
  requestPress=0; requestChallenge[0]='\0'; requestToken[0]='\0';
  requestMotor=true; requestSteer=0; // Exact motor-onlyv2 protocol remains supported.
  Request request=INVALID; const uint32_t started=millis();
  while (uint32_t(millis()-started)<HTTP_READ_TIMEOUT_MS) {
    if (!client.connected()) return INVALID;
    if (!client.available()) { delay(1); continue; }
    int c=client.read(); if (c<0) continue;
    if (++bytes>MAX_HTTP_BYTES) return INVALID;
    if (c=='\r' && !cr) { cr=true; continue; }
    if (c=='\n' && cr) {
      cr=false; line[length]='\0';
      if (first) {
        if (!strcmp(line,"GET / HTTP/1.1")) request=PAGE;
        else if (!strcmp(line,"POST /session HTTP/1.1")) request=SESSION;
        else if (!strcmp(line,"POST /arm HTTP/1.1")) request=ARM;
        else if (!strcmp(line,"POST /hold HTTP/1.1")) request=HOLD;
        else if (!strcmp(line,"POST /stop HTTP/1.1")) request=STOP;
        else return INVALID;
        first=false;
      } else if (!length) {
        // A partial/invalid new intent must never fall back to legacy motor ON.
        if (motorIntent!=steerIntent || ((motorIntent || steerIntent) && request!=HOLD)) return INVALID;
        const bool sessionToken=token && (request==SESSION || (motorToken[0]&&!strcmp(requestToken,motorToken)));
        return host && (request==PAGE || (zeroLength && trigger && sessionToken && (request==SESSION || (press && (request!=HOLD || challenge))))) ? request : INVALID;
      } else {
        char *colon=strchr(line,':'); if (!colon || colon==line) return INVALID;
        for (char *p=line;p<colon;++p) {
          if (!isalnum((unsigned char)*p) && !strchr("!#$%&'*+-.^_`|~",*p)) return INVALID;
          *p=tolower((unsigned char)*p);
        }
        *colon='\0'; char *value=colon+1;
        while (*value==' ' || *value=='\t') ++value;
        char *end=value+strlen(value);
        while (end>value && (end[-1]==' ' || end[-1]=='\t')) *--end='\0';
        if (!strcmp(line,"host")) {
          if (host || (strcmp(value,"192.168.4.1") && strcmp(value,"192.168.4.1:80"))) return INVALID;
          host=true;
        } else if (!strcmp(line,"content-length")) {
          if (zeroLength || strcmp(value,"0")) return INVALID;
          zeroLength=true;
        } else if (!strcmp(line,"transfer-encoding") || !strcmp(line,"expect")) return INVALID;
        else if (!strcmp(line,"x-motor-control")) {
          if (trigger || strcmp(value,"1")) return INVALID;
          trigger=true;
        } else if (!strcmp(line,"x-motor-token")) {
          if (token || strlen(value)!=32) return INVALID;
          for(const char *p=value;*p;++p)if(!strchr("0123456789abcdef",*p))return INVALID;
          memcpy(requestToken,value,33);token=true;
        } else if (!strcmp(line,"x-motor-press")) {
          if (press || !*value || *value=='0') return INVALID;
          uint32_t number=0;
          for (const char *p=value;*p;++p) {
            if (*p<'0' || *p>'9' || number>(UINT32_MAX-uint32_t(*p-'0'))/10) return INVALID;
            number=number*10+uint32_t(*p-'0');
          }
          requestPress=number; press=true;
        } else if (!strcmp(line,"x-motor-challenge")) {
          if (challenge || strlen(value)!=32) return INVALID;
          for (const char *p=value;*p;++p) if (!strchr("0123456789abcdef",*p)) return INVALID;
          memcpy(requestChallenge,value,33); challenge=true;
        } else if (!strcmp(line,"x-control-motor")) {
          if (motorIntent || (strcmp(value,"0") && strcmp(value,"1"))) return INVALID;
          motorIntent=true; requestMotor=!strcmp(value,"1");
        } else if (!strcmp(line,"x-control-steer")) {
          if (steerIntent) return INVALID;
          if (!strcmp(value,"left")) requestSteer=-1;
          else if (!strcmp(value,"center")) requestSteer=0;
          else if (!strcmp(value,"right")) requestSteer=1;
          else return INVALID;
          steerIntent=true;
        } else if (!strcmp(line,"origin")) {
          if (origin || (strcmp(value,"http://192.168.4.1") && strcmp(value,"http://192.168.4.1:80"))) return INVALID;
          origin=true;
        }
      }
      length=0;
    } else {
      if (cr || (c<32 && c!='\t') || c>126 || length>=MAX_HTTP_LINE) return INVALID;
      line[length++]=char(c);
    }
  }
  return INVALID;
}
void responseHeaders(WiFiClient &client, bool ok, const char *type, size_t length) {
  // One modem send instead of a separate AT transaction for each header fragment.
  static char header[256]; // One client, outside the small UNO main stack.
  const int n=snprintf(header,sizeof(header),
    "HTTP/1.1 %s\r\nConnection: close\r\nCache-Control: no-store\r\nX-Frame-Options: DENY\r\nContent-Type: %s\r\nContent-Length: %u\r\n\r\n",
    ok ? "200 OK" : "400 Bad Request",type,unsigned(length));
  if(n>0 && n<int(sizeof(header)))client.write(reinterpret_cast<const uint8_t *>(header),size_t(n));
}
void respond(WiFiClient &client, bool ok, const char *type, const char *body) {
  // Short control responses use a single modem transaction (headers + body).
  static char packet[384]; // Never used from the ISR; one client at a time.
  const int n=snprintf(packet,sizeof(packet),
    "HTTP/1.1 %s\r\nConnection: close\r\nCache-Control: no-store\r\nX-Frame-Options: DENY\r\nContent-Type: %s\r\nContent-Length: %u\r\n\r\n%s",
    ok ? "200 OK" : "400 Bad Request",type,unsigned(strlen(body)),body);
  if(n>0 && n<int(sizeof(packet)))client.write(reinterpret_cast<const uint8_t *>(packet),size_t(n));
}
void respondPage(WiFiClient &client) {
  motorStop(); stopReason=5; lastPress=0; previousSessionToken[0]='\0';
  if (!mintMotorToken()) { respond(client,false,"text/plain; charset=utf-8","Test neni pripraven. Nacti stranku znovu."); return; }
  const char *marker=strstr(HTML,"@TOKEN@");
  responseHeaders(client,true,"text/html; charset=utf-8",strlen(HTML)-7+strlen(motorToken));
  client.write(reinterpret_cast<const uint8_t *>(HTML),size_t(marker-HTML));
  client.print(motorToken); client.print(marker+7);
}
void setup() {
  digitalWrite(EN,LOW); digitalWrite(IN1,LOW); digitalWrite(IN2,LOW);
  digitalWrite(STEER_PIN,LOW);
  pinMode(EN,OUTPUT); pinMode(IN1,OUTPUT); pinMode(IN2,OUTPUT); pinMode(STEER_PIN,OUTPUT); pinMode(LED_BUILTIN,OUTPUT);
  motorStop(); safetyReady=initializeSafety(); motorStop();
  Serial.begin(115200); diagnosticEvent(BUILD_ID,0);
  diagnosticEvent("safety-timer-ready",int(safetyReady));
  networkReady(); diagnosticPoll();
}
void loop() {
  diagnosticPoll();
  const uint32_t requestStarted=millis();
  if (!networkReady()) { motorStop(); delay(1); return; }
  WiFiClient client=server.available(); if (!client) {delay(1);return;}
  ++diagnosticAccepted;
  const Request request=readRequest(client);
  const uint32_t receivedAt=millis(), challengeAge=uint32_t(receivedAt-challengeIssuedAt);
  const int before=int(driveState);
  // No additional blocking modem call between validation and a lease grant.
  // networkReady() ran before reception; its delay is included below.
  bool ok=false;
  char reply[48]="Neplatny nebo stary pozadavek.";
  if (request==PAGE) respondPage(client);
  else if(request==SESSION) {
    // Only a new physical press after failure asks for this. It cannot move a motor.
    if(motorToken[0] && previousSessionToken[0] && !strcmp(requestToken,previousSessionToken)) {
      ok=true; // Lost response retry: reveal the same session, never stop a newer drive.
    } else if(!motorToken[0] || !strcmp(requestToken,motorToken)) {
      motorStop();stopReason=5;lastPress=0;
      memcpy(previousSessionToken,requestToken,33);ok=mintMotorToken();
    }
    if(ok)snprintf(reply,sizeof(reply),"SESSION_OK:%s",motorToken);
    respond(client,ok,"text/plain; charset=utf-8",reply);
  }
  else {
    const bool fresh=uint32_t(millis()-requestStarted)<HTTP_READ_TIMEOUT_MS;
    if (request==STOP) { applyStop(requestPress); ok=true; snprintf(reply,sizeof(reply),"STOP_OK"); }
    else if (fresh && request==ARM && applyArm(requestPress)) {
      ok=true;snprintf(reply,sizeof(reply),"ARM_OK:%s",holdChallenge);
    } else if (fresh && request==HOLD && applyHold(requestPress,requestChallenge,requestMotor,requestSteer)) {
      ok=true;snprintf(reply,sizeof(reply),"HOLD_OK:%s",holdChallenge);
    } // Invalid/obsolete requests cannot renew a lease or stop a newer press.
    respond(client,ok,"text/plain; charset=utf-8",reply);
  }
  client.stop(); ++diagnosticClosed;
  if(request!=HOLD || !ok || uint32_t(millis()-diagnosticRequestLogAt)>=1000) {
    diagnosticRequestLogAt=millis();
    const char *kind=request==PAGE?"PAGE":request==SESSION?"SESSION":request==ARM?"ARM":request==HOLD?"HOLD":request==STOP?"STOP":"INVALID";
    char line[160];
    const int n=snprintf(line,sizeof(line),"HTTP %s ok=%d press=%lu rxMs=%lu replyMs=%lu challengeAgeMs=%lu phase=%d->%d reason=%u\n",
      kind,int(ok),static_cast<unsigned long>(requestPress),static_cast<unsigned long>(receivedAt-requestStarted),
      static_cast<unsigned long>(uint32_t(millis()-receivedAt)),static_cast<unsigned long>(challengeAge),before,int(driveState),unsigned(stopReason));
    if(n>0&&n<int(sizeof(line)))Serial.write(reinterpret_cast<uint8_t *>(line),size_t(n));
  }
}
