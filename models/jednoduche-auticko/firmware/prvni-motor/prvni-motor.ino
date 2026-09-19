#include <WiFiS3.h>
#include <ctype.h>
#include <string.h>
#include <stdio.h>

// První stolní test. Napájení a proud motoru musí být ověřeny před zapnutím.
constexpr uint8_t EN = 5, IN1 = 7, IN2 = 8;
const char SSID[] = "Auticko-test", PASSWORD[] = "auticko123"; // Veřejné demo heslo.
WiFiServer server(80);
bool ready = false;
bool apConfigured=false, networkAttempted=false;
uint32_t networkCheckedAt=0, tokenSequence=0;
char motorToken[33]="";
enum Request { INVALID, PAGE, TEST };
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
  char line[128];
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
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Test motoru</title>
<style>body{font:18px system-ui;max-width:32rem;margin:3rem auto;padding:1rem;line-height:1.5}
button{font:inherit;padding:.8rem 1rem;border-radius:.5rem;cursor:pointer}button:disabled{cursor:wait}</style>
<h1>První test motoru</h1><p>Jeden sekundový pulz vpřed. Potom se výstup vypne; motor může dobíhat.
Puštění tlačítka test nezkrátí.</p><button id="test">Test motoru na 1 sekundu</button>
<p id="result" role="status" aria-live="polite">Připraveno k jednomu testu.</p><script>
const button=document.getElementById('test'), result=document.getElementById('result');
let token='@TOKEN@';
button.addEventListener('click',async()=>{
  button.disabled=true;result.textContent='Čekám na dokončení testu…';
  const controller=new AbortController(), timer=setTimeout(()=>controller.abort(),6000);
  try {
    const reply=await fetch('/test',{method:'POST',headers:{'X-Motor-Test':'1','X-Motor-Token':token},body:'',
      cache:'no-store',signal:controller.signal});
    const body=await reply.text();
    if(!reply.ok || !/^TEST_OK:[0-9a-f]{32}$/.test(body)) throw new Error();
    token=body.slice(8);
    result.textContent='Sekundový pulz skončil. Výstup motoru je vypnutý.';
    button.disabled=false;
  } catch (_) {
    result.textContent='Výsledek nepotvrzen. Test mohl proběhnout. Ověř motor; další pokus až po novém otevření stránky.';
  } finally {clearTimeout(timer);}
});</script></html>)HTML";

void motorStop() {
  analogWrite(EN, 0); // L293D enable LOW: volný doběh, nikoli aktivní brzda.
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW); digitalWrite(LED_BUILTIN, LOW);
}
void motorPulse() {
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW); digitalWrite(LED_BUILTIN, HIGH);
  analogWrite(EN, 128);
  delay(1000); // Žádné WiFi/Serial I/O uvnitř pulzu; síť nesmí oddálit STOP.
  motorStop();
}

bool mintMotorToken() {
  motorToken[0]='\0';
  if (tokenSequence==UINT32_MAX) return false;
  // UNO R4 core 1.6.0 používá bez randomSeed() hardware TRNG, žádný analogový pin.
  const long a=random(0x7fffffffL), b=random(0x7fffffffL), c=random(0x7fffffffL);
  if (a<0 || b<0 || c<0) return false;
  ++tokenSequence;
  snprintf(motorToken,sizeof(motorToken),"%08x%08x%08x%08x",
    static_cast<unsigned>(a),static_cast<unsigned>(b),
    static_cast<unsigned>(c),static_cast<unsigned>(tokenSequence));
  return true;
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
// Příjem zůstává omezený; po celou dobu je motor vypnutý.
constexpr size_t MAX_HTTP_LINE = 1024, MAX_HTTP_BYTES = 8192;
constexpr uint32_t HTTP_READ_TIMEOUT_MS = 3000;
Request readRequest(WiFiClient &client) {
  // Jedno spojení současně: buffer mimo malý zásobník UNO R4.
  static char line[MAX_HTTP_LINE+1]; size_t length=0, bytes=0;
  bool first=true, cr=false, host=false, zeroLength=false, trigger=false, token=false;
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
        else if (!strcmp(line,"POST /test HTTP/1.1")) request=TEST;
        else return INVALID;
        first=false;
      } else if (!length) {
        return host && (request==PAGE || (zeroLength && trigger && token)) ? request : INVALID;
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
        else if (!strcmp(line,"x-motor-test")) {
          if (trigger || strcmp(value,"1")) return INVALID;
          trigger=true;
        } else if (!strcmp(line,"x-motor-token")) {
          if (token || !motorToken[0] || strcmp(value,motorToken)) return INVALID;
          token=true;
        } else if (!strcmp(line,"origin") && strcmp(value,"http://192.168.4.1") &&
                   strcmp(value,"http://192.168.4.1:80")) return INVALID;
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
  client.print(ok ? "HTTP/1.1 200 OK\r\n" : "HTTP/1.1 400 Bad Request\r\n");
  client.print("Connection: close\r\nCache-Control: no-store\r\nX-Frame-Options: DENY\r\nContent-Type: ");
  client.print(type); client.print("\r\nContent-Length: "); client.print(length);
  client.print("\r\n\r\n");
}
void respond(WiFiClient &client, bool ok, const char *type, const char *body) {
  responseHeaders(client,ok,type,strlen(body)); client.print(body);
}
void respondPage(WiFiClient &client) {
  if (!mintMotorToken()) { respond(client,false,"text/plain; charset=utf-8","Test neni pripraven. Nacti stranku znovu."); return; }
  const char *marker=strstr(HTML,"@TOKEN@");
  responseHeaders(client,true,"text/html; charset=utf-8",strlen(HTML)-7+strlen(motorToken));
  client.write(reinterpret_cast<const uint8_t *>(HTML),size_t(marker-HTML));
  client.print(motorToken); client.print(marker+7);
}
void setup() {
  pinMode(EN,OUTPUT); pinMode(IN1,OUTPUT); pinMode(IN2,OUTPUT); pinMode(LED_BUILTIN,OUTPUT);
  analogWriteResolution(8); motorStop();
  Serial.begin(115200); diagnosticEvent("BOOT",0);
  networkReady();
  diagnosticPoll();
}
void loop() {
  diagnosticPoll();
  const uint32_t requestStarted=millis();
  if (!networkReady()) { motorStop(); delay(1); return; }
  WiFiClient client=server.available(); if (!client) return;
  ++diagnosticAccepted;
  const bool trace=!diagnosticHttpSeen || uint32_t(millis()-diagnosticHttpAt)>=1000;
  if (trace) { diagnosticHttpSeen=true; diagnosticHttpAt=millis(); diagnosticEvent("HTTP accepted",diagnosticAccepted); }
  const Request request=readRequest(client);
  if (trace) diagnosticEvent(request==TEST ? "HTTP TEST" : request==PAGE ? "HTTP PAGE" : "HTTP INVALID",diagnosticAccepted);
  if (request==TEST) {
    motorToken[0]='\0'; // Jednorázový token spotřebovat před pulzem i před další kontrolou Wi-Fi.
    // AT dotazy mohou přesáhnout timeout parseru; opožděný požadavek už motor nespustí.
    if (networkReady() && uint32_t(millis()-requestStarted)<HTTP_READ_TIMEOUT_MS) {
      motorPulse(); // Úplný validní POST; odpověď výhradně po STOP.
      char reply[41]="TEST_OK:";
      if (mintMotorToken()) memcpy(reply+8,motorToken,sizeof(motorToken));
      respond(client,true,"text/plain; charset=utf-8",reply);
    } else respond(client,false,"text/plain; charset=utf-8","Spojeni se obnovuje. Nacti stranku znovu.");
  } else if (request==PAGE) respondPage(client);
  else { motorStop(); respond(client,false,"text/plain; charset=utf-8","Neplatny nebo neuplny pozadavek."); }
  if (trace) diagnosticEvent("HTTP response-returned",diagnosticAccepted);
  client.stop(); // Jeden požadavek na spojení, žádné opakování ani automatický restart.
  ++diagnosticClosed;
  if (trace) diagnosticEvent("HTTP closed",diagnosticClosed);
}
