#include <WiFiS3.h>
#include <ctype.h>
#include <string.h>

// První stolní test. Napájení a proud motoru musí být ověřeny před zapnutím.
constexpr uint8_t EN = 5, IN1 = 7, IN2 = 8;
const char SSID[] = "Auticko-test", PASSWORD[] = "auticko123"; // Veřejné demo heslo.
WiFiServer server(80);
bool ready = false;
enum Request { INVALID, PAGE, TEST };
Request readRequest(WiFiClient &client); // Explicitně kvůli Arduino generování prototypů.
const char HTML[] = R"HTML(<!doctype html><html lang="cs"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Test motoru</title>
<style>body{font:18px system-ui;max-width:32rem;margin:3rem auto;padding:1rem;line-height:1.5}
button{font:inherit;padding:.8rem 1rem;border-radius:.5rem;cursor:pointer}button:disabled{cursor:wait}</style>
<h1>První test motoru</h1><p>Jeden sekundový pulz vpřed. Potom se výstup vypne; motor může dobíhat.
Puštění tlačítka test nezkrátí.</p><button id="test">Test motoru na 1 sekundu</button>
<p id="result" role="status" aria-live="polite">Připraveno k jednomu testu.</p><script>
const button=document.getElementById('test'), result=document.getElementById('result');
button.addEventListener('click',async()=>{
  button.disabled=true;result.textContent='Čekám na dokončení testu…';
  const controller=new AbortController(), timer=setTimeout(()=>controller.abort(),6000);
  try {
    const reply=await fetch('/test',{method:'POST',headers:{'X-Motor-Test':'1'},body:'',
      cache:'no-store',signal:controller.signal});
    if(!reply.ok || await reply.text()!=='TEST_OK') throw new Error();
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

// Mobilní prohlížeče běžně posílají delší User-Agent a Accept hlavičky.
// Příjem zůstává omezený; po celou dobu je motor vypnutý.
constexpr size_t MAX_HTTP_LINE = 1024, MAX_HTTP_BYTES = 8192;
constexpr uint32_t HTTP_READ_TIMEOUT_MS = 3000;
Request readRequest(WiFiClient &client) {
  // Jedno spojení současně: buffer mimo malý zásobník UNO R4.
  static char line[MAX_HTTP_LINE+1]; size_t length=0, bytes=0;
  bool first=true, cr=false, host=false, zeroLength=false, trigger=false;
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
        return host && (request==PAGE || (zeroLength && trigger)) ? request : INVALID;
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
void respond(WiFiClient &client, bool ok, const char *type, const char *body) {
  client.print(ok ? "HTTP/1.1 200 OK\r\n" : "HTTP/1.1 400 Bad Request\r\n");
  client.print("Connection: close\r\nCache-Control: no-store\r\nX-Frame-Options: DENY\r\nContent-Type: ");
  client.print(type); client.print("\r\nContent-Length: "); client.print(strlen(body));
  client.print("\r\n\r\n"); client.print(body);
}
void setup() {
  pinMode(EN,OUTPUT); pinMode(IN1,OUTPUT); pinMode(IN2,OUTPUT); pinMode(LED_BUILTIN,OUTPUT);
  analogWriteResolution(8); motorStop();
  if (WiFi.status()==WL_NO_MODULE) return;
  WiFi.config(IPAddress(192,168,4,1));
  if (WiFi.beginAP(SSID,PASSWORD)!=WL_AP_LISTENING) { motorStop(); return; }
  delay(10000); // AP příprava podle oficiálního příkladu; motor zůstává vypnutý.
  server.begin(); ready=true;
}
void loop() {
  if (!ready) { motorStop(); delay(50); return; }
  const int status=WiFi.status();
  if (status!=WL_AP_LISTENING && status!=WL_AP_CONNECTED) { motorStop(); ready=false; return; }
  WiFiClient client=server.available(); if (!client) return;
  const Request request=readRequest(client);
  if (request==TEST) {
    motorPulse(); // Úplný validní POST; odpověď výhradně po STOP.
    respond(client,true,"text/plain; charset=utf-8","TEST_OK");
  } else if (request==PAGE) respond(client,true,"text/html; charset=utf-8",HTML);
  else { motorStop(); respond(client,false,"text/plain; charset=utf-8","Neplatny nebo neuplny pozadavek."); }
  client.stop(); // Jeden požadavek na spojení, žádné opakování ani automatický restart.
}
