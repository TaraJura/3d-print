#include <WiFiS3.h>
#include <FspTimer.h>
#include <pwm.h>
#include <ctype.h>
#include <string.h>
#include <stdio.h>

// Ovládání při držení. Zapojení zůstává stejné jako u prvního stolního testu.
const char BUILD_ID[] = "hold-to-run-v1";
constexpr uint8_t EN = 5, IN1 = 7, IN2 = 8;
const char SSID[] = "Auticko-test", PASSWORD[] = "auticko123"; // Veřejné demo heslo.
WiFiServer server(80);
bool ready = false;
bool apConfigured=false, networkAttempted=false;
uint32_t networkCheckedAt=0, tokenSequence=0;
char motorToken[33]="";
enum Request { INVALID, PAGE, ARM, HOLD, STOP };
enum DriveState { IDLE, ARMED, RUNNING };
constexpr uint32_t LEASE_MS=500, TIMER_TICK_MS=5, HEARTBEAT_MS=100;
PwmOut motorPwm(EN);
FspTimer safetyTimer;
volatile bool pwmReady=false, safetyReady=false;
volatile DriveState driveState=IDLE;
volatile uint16_t leaseTicks=0;
volatile uint32_t watchdogStops=0;
uint32_t lastPress=0, requestPress=0, challengeIssuedAt=0;
char holdChallenge[33]="", requestChallenge[33]="";
Request readRequest(WiFiClient &client); // Explicitně kvůli Arduino generování prototypů.

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
<style>body{font:18px system-ui;max-width:32rem;margin:3rem auto;padding:1rem;line-height:1.5}
button{font:inherit;padding:1.3rem 2rem;border-radius:.5rem;cursor:pointer;touch-action:none;user-select:none;-webkit-user-select:none}
button[data-running="true"]{background:#1d6845;color:white}button:disabled{cursor:wait}</style>
<h1>Ovládání autíčka</h1><p>Drž tlačítko pro pohon vpřed. Puštěním pohon vypneš; kola mohou dobíhat.
Při výpadku spojení se výstup vypne přibližně do 0,5 sekundy od poslední ověřené výzvy.</p>
<button id="drive" type="button">Držet pro jízdu vpřed</button>
<p id="result" role="status" aria-live="polite">Připraveno. Motor je vypnutý.</p><script>
const button=document.getElementById('drive'), result=document.getElementById('result');
const token='@TOKEN@';
let press=0, held=false, generation=0, pointer=null, keyboard=null, timer=null, pending=null, stopping=false;
const headers=(id,challenge)=>({'X-Motor-Control':'1','X-Motor-Token':token,'X-Motor-Press':String(id),
  ...(challenge?{'X-Motor-Challenge':challenge}:{})});
async function command(path,id,challenge) {
  const controller=new AbortController(); pending=controller;
  const deadline=setTimeout(()=>controller.abort(),1200);
  try {
    const reply=await fetch(path,{method:'POST',headers:headers(id,challenge),body:'',cache:'no-store',signal:controller.signal});
    const text=await reply.text();
    if(!reply.ok) throw new Error('request');
    return text;
  } finally {clearTimeout(deadline);if(pending===controller)pending=null;}
}
function stop(message='Pohon vypnutý. Pro další jízdu stiskni znovu.') {
  if(!held) return;
  held=false;generation++;pointer=null;keyboard=null;clearTimeout(timer);
  if(pending) pending.abort();
  button.dataset.running='false';button.disabled=true;stopping=true;
  result.textContent='Zastavuji…';
  // Jiný HTTP request: STOP může předběhnout čekající ARM/HOLD. Server si pamatuje číslo stisku.
  const controller=new AbortController(), deadline=setTimeout(()=>controller.abort(),1500);
  fetch('/stop',{method:'POST',headers:headers(press),body:'',cache:'no-store',keepalive:true,signal:controller.signal})
    .then(async reply=>{if(!reply.ok || await reply.text()!=='STOP_OK')throw new Error();
      result.textContent=message;button.disabled=false;})
    .catch(()=>{result.textContent='Spojení přerušeno. Pohon se vypne časovačem. Pro další jízdu obnov stránku.';})
    .finally(()=>{clearTimeout(deadline);stopping=false;});
}
async function start() {
  if(held || stopping || button.disabled || document.hidden) return;
  held=true;const id=++press, gen=++generation;result.textContent='Připravuji jízdu…';
  try {
    const armed=await command('/arm',id);
    if(!held || gen!==generation) return;
    if(!/^ARM_OK:[0-9a-f]{32}$/.test(armed)) throw new Error();
    await heartbeat(armed.slice(7),id,gen);
  } catch (_) {if(held && gen===generation)stop('Jízda přerušena. Pro další pokus stiskni znovu.');}
}
async function heartbeat(challenge,id,gen) {
  if(!held || gen!==generation) return;
  try {
    const reply=await command('/hold',id,challenge);
    if(!held || gen!==generation) return;
    if(!/^HOLD_OK:[0-9a-f]{32}$/.test(reply))throw new Error();
    button.dataset.running='true';result.textContent='Pohon vpřed — puštěním zastavíš.';
    timer=setTimeout(()=>heartbeat(reply.slice(8),id,gen),100);
  } catch (_) {if(held && gen===generation)stop('Jízda přerušena. Pro další pokus stiskni znovu.');}
}
button.addEventListener('pointerdown',event=>{
  if(!event.isPrimary || event.button!==0 || held || stopping || button.disabled)return;
  event.preventDefault();pointer=event.pointerId;button.setPointerCapture(pointer);start();
});
window.addEventListener('pointerup',event=>{if(event.pointerId===pointer)stop();});
window.addEventListener('pointercancel',event=>{if(event.pointerId===pointer)stop();});
button.addEventListener('lostpointercapture',event=>{if(event.pointerId===pointer)stop();});
button.addEventListener('contextmenu',event=>event.preventDefault());
button.addEventListener('keydown',event=>{
  if(event.code!=='Space' && event.code!=='Enter')return;
  event.preventDefault();if(event.repeat || held || stopping || button.disabled)return;
  keyboard=event.code;start();
});
window.addEventListener('keyup',event=>{if(event.code===keyboard){event.preventDefault();stop();}});
window.addEventListener('blur',()=>stop());
window.addEventListener('pagehide',()=>stop());
window.addEventListener('offline',()=>stop());
document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
</script></html>)HTML";

// Volat jen v ISR nebo krátké kritické sekci. PWM je předem inicializované:
// žádná alokace, modem, čekání ani Serial. Směrové GPIO jdou LOW i při chybě PWM.
void outputsOff() {
  if (pwmReady && !motorPwm.pulse_perc(0.0f)) {
    // Fail closed if the PWM peripheral ever refuses the OFF update.
    pinMode(EN,OUTPUT); digitalWrite(EN,LOW); pwmReady=false; safetyReady=false;
  }
  digitalWrite(IN1,LOW); digitalWrite(IN2,LOW); digitalWrite(LED_BUILTIN,LOW);
}
void motorStop() {
  noInterrupts(); driveState=IDLE; leaseTicks=0; outputsOff(); interrupts();
  holdChallenge[0]='\0';
}
void safetyTick(timer_callback_args_t *) {
  if (driveState!=IDLE && leaseTicks>0 && --leaseTicks==0) {
    driveState=IDLE; outputsOff(); ++watchdogStops;
  }
}
bool initializeSafety() {
  // Reserve the PWM timer before asking for a separate, genuinely free timer.
  pwmReady=motorPwm.begin(490.0f,0.0f);
  if (!pwmReady) {pinMode(EN,OUTPUT); digitalWrite(EN,LOW); return false;}
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
  noInterrupts(); leaseTicks=LEASE_MS/TIMER_TICK_MS; driveState=ARMED; interrupts();
  return true;
}
bool applyHold(uint32_t press, const char *challenge) {
  if (!safetyReady || press!=lastPress || !holdChallenge[0] || strcmp(challenge,holdChallenge)) return false;
  // Consume before any operation that could delay execution. A duplicate cannot renew.
  holdChallenge[0]='\0';
  const uint32_t issued=challengeIssuedAt;
  if (!mintToken(holdChallenge)) { motorStop(); return false; }
  noInterrupts();
  const uint32_t age=uint32_t(millis()-issued);
  // ISR expiry is a latch: even a late valid packet cannot resurrect a stopped run.
  const bool valid=(driveState==ARMED || driveState==RUNNING) && age<LEASE_MS-TIMER_TICK_MS;
  if (valid) {
    leaseTicks=(LEASE_MS-age)/TIMER_TICK_MS; // Bound by the previous server challenge, not packet arrival.
    digitalWrite(IN1,HIGH); digitalWrite(IN2,LOW);
    if (motorPwm.pulse_perc(128.0f*100.0f/255.0f)) {
      driveState=RUNNING; digitalWrite(LED_BUILTIN,HIGH);
    } else { driveState=IDLE; leaseTicks=0; outputsOff(); }
  }
  const bool running=valid && driveState==RUNNING;
  interrupts();
  if (!running) {motorStop(); return false;}
  challengeIssuedAt=millis();
  return true;
}
void applyStop(uint32_t press) {
  // STOP arriving before ARM fences off that press too. A stale STOP can only stop.
  if (press>lastPress) lastPress=press;
  motorStop();
}

bool networkReady() {
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
    ready=false; diagnosticSetup="wifi-wait"; return false;
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
  requestPress=0; requestChallenge[0]='\0';
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
        else if (!strcmp(line,"POST /arm HTTP/1.1")) request=ARM;
        else if (!strcmp(line,"POST /hold HTTP/1.1")) request=HOLD;
        else if (!strcmp(line,"POST /stop HTTP/1.1")) request=STOP;
        else return INVALID;
        first=false;
      } else if (!length) {
        return host && (request==PAGE || (zeroLength && trigger && token && press && (request!=HOLD || challenge))) ? request : INVALID;
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
          if (token || !motorToken[0] || strcmp(value,motorToken)) return INVALID;
          token=true;
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
  char header[256];
  const int n=snprintf(header,sizeof(header),
    "HTTP/1.1 %s\r\nConnection: close\r\nCache-Control: no-store\r\nX-Frame-Options: DENY\r\nContent-Type: %s\r\nContent-Length: %u\r\n\r\n",
    ok ? "200 OK" : "400 Bad Request",type,unsigned(length));
  if(n>0 && n<int(sizeof(header)))client.write(reinterpret_cast<const uint8_t *>(header),size_t(n));
}
void respond(WiFiClient &client, bool ok, const char *type, const char *body) {
  responseHeaders(client,ok,type,strlen(body)); client.print(body);
}
void respondPage(WiFiClient &client) {
  motorStop(); lastPress=0;
  if (!mintMotorToken()) { respond(client,false,"text/plain; charset=utf-8","Test neni pripraven. Nacti stranku znovu."); return; }
  const char *marker=strstr(HTML,"@TOKEN@");
  responseHeaders(client,true,"text/html; charset=utf-8",strlen(HTML)-7+strlen(motorToken));
  client.write(reinterpret_cast<const uint8_t *>(HTML),size_t(marker-HTML));
  client.print(motorToken); client.print(marker+7);
}
void setup() {
  digitalWrite(EN,LOW); digitalWrite(IN1,LOW); digitalWrite(IN2,LOW);
  pinMode(EN,OUTPUT); pinMode(IN1,OUTPUT); pinMode(IN2,OUTPUT); pinMode(LED_BUILTIN,OUTPUT);
  motorStop(); safetyReady=initializeSafety(); motorStop();
  Serial.begin(115200); diagnosticEvent(BUILD_ID,0);
  diagnosticEvent("safety-timer-ready",int(safetyReady));
  networkReady(); diagnosticPoll();
}
void loop() {
  diagnosticPoll();
  const uint32_t requestStarted=millis();
  if (!networkReady()) { motorStop(); delay(1); return; }
  WiFiClient client=server.available(); if (!client) return;
  ++diagnosticAccepted;
  const Request request=readRequest(client);
  // No additional blocking modem call between validation and a lease grant.
  // networkReady() ran before reception; its delay is included below.
  bool ok=false;
  char reply[48]="Neplatny nebo stary pozadavek.";
  if (request==PAGE) respondPage(client);
  else {
    const bool fresh=uint32_t(millis()-requestStarted)<HTTP_READ_TIMEOUT_MS;
    if (request==STOP) { applyStop(requestPress); ok=true; snprintf(reply,sizeof(reply),"STOP_OK"); }
    else if (fresh && request==ARM && applyArm(requestPress)) {
      ok=true;snprintf(reply,sizeof(reply),"ARM_OK:%s",holdChallenge);
    } else if (fresh && request==HOLD && applyHold(requestPress,requestChallenge)) {
      ok=true;snprintf(reply,sizeof(reply),"HOLD_OK:%s",holdChallenge);
    } else motorStop();
    respond(client,ok,"text/plain; charset=utf-8",reply);
  }
  client.stop(); ++diagnosticClosed;
}
