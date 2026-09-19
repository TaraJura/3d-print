#include SKETCH_PATH
#include <cassert>
#include <iostream>
#include <utility>

const char TEST_TOKEN[]="0123456789abcdef0123456789abcdef";
#if EXPECT_MOBILE_REJECTED
const std::string TOKEN_HEADER;
#else
const std::string TOKEN_HEADER=std::string("X-Motor-Token: ")+TEST_TOKEN+"\r\n";
#endif

void resetRuntime() {
  clockMs=0;enabled=0;ioWhileOn=0;writes.clear();
  for(int &pin:pins)pin=LOW;
  onMotorEnable=nullptr;randomValues.clear();randomAt=0;randomCalls=0;
  WiFi=MockWiFi();Serial=MockSerial();server=WiFiServer(80);
  ready=true;server.started=true;
#if !EXPECT_MOBILE_REJECTED
  apConfigured=true;networkAttempted=false;networkCheckedAt=0;
  tokenSequence=0;snprintf(motorToken,sizeof(motorToken),"%s",TEST_TOKEN);
  snprintf(diagnosticFirmware,sizeof(diagnosticFirmware),"not-read");
  for(auto &octet:diagnosticIP)octet=0;
  diagnosticSetup="starting";diagnosticStatus=-1;diagnosticApStart=-1;
  diagnosticStatusAt=0;diagnosticSnapshotAt=0;diagnosticHttpAt=0;diagnosticStatusLogAt=0;
  diagnosticAccepted=0;diagnosticClosed=0;diagnosticHttpSeen=false;
  onMotorEnable=[](){assert(motorToken[0]=='\0');};
#endif
}

int pulseCount() {
  int starts=0;
  for(const auto &write:writes)if(write.pin==5&&write.value){assert(write.value==128);++starts;}
  return starts;
}

#if !EXPECT_MOBILE_REJECTED
std::string postWithToken(const std::string &token) {
  return "POST /test HTTP/1.1\r\nHost: 192.168.4.1\r\nContent-Length: 0\r\nX-Motor-Test: 1\r\nX-Motor-Token: "+token+"\r\n\r\n";
}

bool isToken(const std::string &token) {
  if(token.size()!=32)return false;
  for(char c:token)if(!((c>='0'&&c<='9')||(c>='a'&&c<='f')))return false;
  return true;
}

std::string responseBody(const WiFiClient &client) {
  const std::string &response=client.state->output;
  const auto split=response.find("\r\n\r\n");assert(split!=std::string::npos);
  const std::string body=response.substr(split+4);
  const auto length=response.find("Content-Length: ");assert(length!=std::string::npos);
  assert(std::stoul(response.substr(length+16))==body.size());
  return body;
}

WiFiClient serve(const std::string &request,bool ok) {
  WiFiClient client(request);server.pending=client;loop();
  assert(!client.state->alive);
  assert(client.state->output.find(ok?"HTTP/1.1 200":"HTTP/1.1 400")==0);
  assert(!enabled&&ioWhileOn==0);
  responseBody(client);
  return client;
}

std::string loadPage() {
  WiFiClient client=serve("GET / HTTP/1.1\r\nHost: 192.168.4.1\r\n\r\n",true);
  const std::string token=motorToken;assert(isToken(token));
  assert(responseBody(client).find(token)!=std::string::npos);
  return token;
}
#endif

int main() {
  struct Case {std::string name,text;Request expected;unsigned long gap;};
  std::vector<Case> cases;
  const std::string base="POST /test HTTP/1.1\r\nHost: 192.168.4.1\r\nContent-Length: 0\r\nX-Motor-Test: 1\r\n"+TOKEN_HEADER;
  auto add=[&](std::string text,Request expected,unsigned long gap=0,std::string name=""){cases.push_back({name,text,expected,gap});};
  add("GET / HTTP/1.1\r\nHost: 192.168.4.1\r\n\r\n",PAGE);
  add(base+"\r\n",TEST);
  add(base+"Origin: http://192.168.4.1\r\nContent-Type: text/plain;charset=UTF-8\r\n\r\n",TEST);
  add("POST /test HTTP/1.1\r\nhOsT: 192.168.4.1:80\t\r\nCONTENT-length: 0\r\nX-MOTOR-TEST:\t1 \r\n"+TOKEN_HEADER+"\r\n",TEST);
  for(const auto& line:{"GET /test HTTP/1.1","GET /favicon.ico HTTP/1.1","POST /test?run=1 HTTP/1.1","POST /test HTTP/1.0","HEAD / HTTP/1.1","OPTIONS /test HTTP/1.1","POST /test HTTP/1.1 extra"})
    add(std::string(line)+"\r\nHost: 192.168.4.1\r\nContent-Length: 0\r\nX-Motor-Test: 1\r\n"+TOKEN_HEADER+"\r\n",INVALID);
  add(base,INVALID);add(base+"\r",INVALID);
  add("POST /test HTTP/1.1\nHost: 192.168.4.1\n\n",INVALID);
  add(base+"Transfer-Encoding: chunked\r\n\r\n",INVALID);
  add(base+"Expect: 100-continue\r\n\r\n",INVALID);
  add(base+"Content-Length: 0\r\n\r\n",INVALID);
  add(base+"Host: 192.168.4.1\r\n\r\n",INVALID);
  add(base+"X-Motor-Test: 1\r\n\r\n",INVALID);
  add(base+"Origin: http://evil.example\r\n\r\n",INVALID);
  add(base+"Broken header\r\n\r\n",INVALID);
  add(base+" Bad: value\r\n\r\n",INVALID);
  add(base+"Bad header: value\r\n\r\n",INVALID);
  add(base+std::string("X:\0bad\r\n\r\n",11),INVALID);
  add(base+"X:"+std::string(TEST_MAX_LINE-2,'a')+"\r\n\r\n",TEST,0,"exact line limit");
  add(base+"X:"+std::string(TEST_MAX_LINE-1,'a')+"\r\n\r\n",INVALID,0,"line limit plus one");
  for(const auto& value:{"1","-1","00","+0","0, 0","0x0"})
    add("POST /test HTTP/1.1\r\nHost: 192.168.4.1\r\nContent-Length: "+std::string(value)+"\r\nX-Motor-Test: 1\r\n"+TOKEN_HEADER+"\r\n",INVALID);
  add("POST /test HTTP/1.1\r\nHost: 192.168.4.1\r\nX-Motor-Test: 1\r\n"+TOKEN_HEADER+"\r\n",INVALID);
  add("POST /test HTTP/1.1\r\nHost: 192.168.4.1\r\nContent-Length: 0\r\n"+TOKEN_HEADER+"\r\n",INVALID);
  add("POST /test HTTP/1.1\r\nHost: other\r\nContent-Length: 0\r\nX-Motor-Test: 1\r\n"+TOKEN_HEADER+"\r\n",INVALID);
  auto sized=[&](int n){
    std::string s=base;
    while(n-int(s.size())-2>130)s+="Z:"+std::string(124,'a')+"\r\n";
    s+="Z:"+std::string(n-int(s.size())-6,'a')+"\r\n\r\n";
    assert(int(s.size())==n);return s;
  };
  add(sized(TEST_MAX_BYTES),TEST,0,"exact total limit");
  add(sized(TEST_MAX_BYTES+1),INVALID,0,"total limit plus one");
  add(base+"\r\n",INVALID,100,"slow header timeout");
  assert(cases.size()==38); // Původních 38 tříd případů, s aktuálními hranicemi.

  // Reprezentativní prohlížečové hlavičky, nikoli zachycení uživatelova telefonu.
  const std::string chromeUA="User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36";
  const std::string chromeAccept="Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7";
  const std::string safariUA="User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1";
  const std::string safariAccept="Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8";
  const std::string get="GET / HTTP/1.1\r\nHost: 192.168.4.1:80\r\nConnection: keep-alive\r\n";
  const std::string tail="Accept-Encoding: gzip, deflate\r\nAccept-Language: cs-CZ,cs;q=0.9,en;q=0.8\r\n\r\n";
  const std::string chromeGET=get+chromeUA+"\r\n"+chromeAccept+"\r\n"+tail;
  const std::string safariGET=get+safariUA+"\r\n"+safariAccept+"\r\n"+tail;
  const std::string chromePOST=base+chromeUA+"\r\n"+chromeAccept+"\r\nOrigin: http://192.168.4.1\r\n"+tail;
  const std::string safariPOST=base+safariUA+"\r\n"+safariAccept+"\r\nOrigin: http://192.168.4.1:80\r\n"+tail;
  const Request mobilePage=EXPECT_MOBILE_REJECTED?INVALID:PAGE;
  const Request mobileTest=EXPECT_MOBILE_REJECTED?INVALID:TEST;
  add(chromeGET,mobilePage,0,"Chrome Android GET (408 bytes)");
  add(safariGET,mobilePage,0,"Safari iOS GET (360 bytes)");
  add(chromePOST,mobileTest,0,"Chrome Android POST");
  add(safariPOST,mobileTest,0,"Safari iOS POST");
  add(chromeGET,mobilePage,1,"fragmented Chrome GET");
  add(safariPOST,mobileTest,1,"fragmented Safari POST");
  add(get+chromeAccept+"\r\n\r\n",mobilePage,0,"isolated Chrome Accept (143 chars)");
  add(get+safariUA+"\r\n\r\n",mobilePage,0,"isolated Safari User-Agent (147 chars)");
  add("GET / HTTP/1.1\r\nHost: 192.168.4.1\r\nContent-Length: 0\r\nX-Motor-Test: 1\r\n"+TOKEN_HEADER+"\r\n",PAGE,0,"GET with motor headers still cannot run motor");
  add(base+"Origin: null\r\n\r\n",INVALID);
  add(base+"X-Motor-Test: 0\r\n\r\n",INVALID);
  add(base+"X-Test: bad\rvalue\r\n\r\n",INVALID);
  add(base+"X-Test: value\r\r\n\r\n",INVALID);
  add(base+std::string("X-Test: \xff\r\n\r\n"),INVALID);
  add("\r\n"+base+"\r\n",INVALID);

  int total=0,loops=0;
  for(const auto& c:cases){
    resetRuntime();
    WiFiClient client(c.text,c.gap);auto got=readRequest(client);
    if(got!=c.expected){std::cerr<<"FAIL parser "<<total<<" "<<c.name<<" expected="<<c.expected<<" got="<<got<<"\n";return 1;}
    assert(writes.empty());assert(clockMs<=TEST_DEADLINE);
    if(!c.name.empty())std::cout<<"PASS parser "<<c.name<<": result="<<got<<" time="<<clockMs<<"ms\n";
    ++total;
    resetRuntime();
    WiFiClient served(c.text,c.gap);server.pending=served;loop();
    int starts=0;unsigned long on=0,off=0;
    for(const auto& w:writes){if(w.pin==5&&w.value){assert(w.value==128);++starts;on=w.time;}if(w.pin==5&&!w.value)off=w.time;}
    assert(starts==(c.expected==TEST?1:0));
    if(starts)assert(off-on==1000);
    assert(!enabled&&ioWhileOn==0&&!served.state->alive);
    assert(served.state->output.find(c.expected==INVALID?"HTTP/1.1 400":"HTTP/1.1 200")==0);
    if(c.expected==PAGE)assert(served.state->output.find("<!doctype html>")!=std::string::npos);
    if(c.expected==TEST)assert(served.state->output.find("TEST_OK")!=std::string::npos);
    const auto previous=writes.size();loop();assert(writes.size()==previous); // Spojení se nereplayuje.
    ++loops;
  }
  resetRuntime();onMotorEnable=nullptr;motorPulse();
  assert(clockMs==1000&&enabled==0&&pins[7]==LOW&&pins[8]==LOW&&pins[13]==LOW&&ioWhileOn==0);
  resetRuntime();ready=false;WiFi.state=WL_NO_MODULE;setup();assert(!ready&&!enabled);
  resetRuntime();ready=true;WiFi.state=77;loop();assert(!ready&&!enabled);
#if !EXPECT_MOBILE_REJECTED
  // Samostatné nonce případy: všechny původní HTTP třídy výše zůstávají zachované.
  const std::string withoutToken="POST /test HTTP/1.1\r\nHost: 192.168.4.1\r\nContent-Length: 0\r\nX-Motor-Test: 1\r\n";
  const std::vector<std::string> invalidTokens={
    withoutToken+"\r\n",
    postWithToken(""),postWithToken("wrong"),postWithToken(std::string(TEST_TOKEN).substr(1)),
    postWithToken(std::string(TEST_TOKEN)+"0"),
    withoutToken+TOKEN_HEADER+TOKEN_HEADER+"\r\n",
    withoutToken+TOKEN_HEADER+"x-motor-token: "+TEST_TOKEN+"\r\n\r\n"
  };
  for(const auto &text:invalidTokens){
    resetRuntime();WiFiClient client(text);assert(readRequest(client)==INVALID);
    assert(writes.empty());serve(text,false);assert(pulseCount()==0);
  }
  resetRuntime();motorToken[0]='\0';serve(postWithToken(TEST_TOKEN),false);assert(pulseCount()==0);
  resetRuntime();
  const std::string first=loadPage();assert(pulseCount()==0&&isToken(first));
  const auto firstResult=serve(postWithToken(first),true);
  const std::string second=responseBody(firstResult).substr(8);
  assert(responseBody(firstResult)=="TEST_OK:"+second&&isToken(second)&&second!=first);
  assert(pulseCount()==1&&second==motorToken);
  serve(postWithToken(first),false);assert(pulseCount()==1&&second==motorToken);
  const auto secondResult=serve(postWithToken(second),true);
  const std::string third=responseBody(secondResult).substr(8);
  assert(isToken(third)&&third!=second&&third==motorToken&&pulseCount()==2);
  serve(postWithToken(second),false);assert(pulseCount()==2);
  const std::string refreshed=loadPage();assert(refreshed!=third&&pulseCount()==2);
  serve(postWithToken(third),false);assert(pulseCount()==2);

  // Selhání TRNG ani vyčerpání čítače nesmí vydat oprávnění ke spuštění.
  for(size_t failed=0;failed<3;++failed){
    resetRuntime();randomValues={1,2,3};randomValues[failed]=-1;
    serve("GET / HTTP/1.1\r\nHost: 192.168.4.1\r\n\r\n",false);
    assert(!motorToken[0]&&pulseCount()==0);
    serve(postWithToken(TEST_TOKEN),false);assert(pulseCount()==0);
  }
  resetRuntime();tokenSequence=UINT32_MAX;
  serve("GET / HTTP/1.1\r\nHost: 192.168.4.1\r\n\r\n",false);
  assert(!motorToken[0]&&randomCalls==0&&pulseCount()==0);
  resetRuntime();randomValues={-1,2,3};
  assert(responseBody(serve(postWithToken(TEST_TOKEN),true))=="TEST_OK:");
  assert(!motorToken[0]&&pulseCount()==1); // Pulz skončil, nová autorizace nevznikla.
  serve(postWithToken(TEST_TOKEN),false);assert(pulseCount()==1);
  std::cout<<"PASS tokens: missing/wrong/duplicate rejected, consumed before pulse, response rotates token, replay rejected, page refresh invalidates old token, RNG failure fails closed.\n";

  // Jediný chybný dotaz nesmí vytvořit trvalý latch. Pending POST musí přežít
  // v mocku stejně jako v bridge; jeho zneplatnění tedy skutečně prověří token.
  for(int failedStatus:{WL_NO_MODULE,0,77}){
    resetRuntime();const std::string old=loadPage();
    WiFiClient queued(postWithToken(old));server.pending=queued;
    WiFi.statusSequence={failedStatus,WL_AP_CONNECTED};WiFi.statusAt=0;
    loop();
    assert(!ready&&!motorToken[0]&&!enabled&&pulseCount()==0&&queued.state->alive);
    const int failedQueries=WiFi.statusCalls;
    clockMs=networkCheckedAt+999;loop();assert(WiFi.statusCalls==failedQueries&&!ready);
    clockMs=networkCheckedAt+1000;loop();
    assert(ready&&WiFi.statusCalls==failedQueries+1&&!queued.state->alive);
    assert(queued.state->output.find("HTTP/1.1 400")==0&&pulseCount()==0);
    assert(WiFi.beginCalls==0&&WiFi.configCalls==0&&server.beginCalls==0);
    assert(!motorToken[0]);
    const std::string fresh=loadPage();assert(fresh!=old&&pulseCount()==0);
    serve(postWithToken(fresh),true);assert(pulseCount()==1&&ioWhileOn==0);
  }
  resetRuntime();
  const std::string beforeParseFailure=loadPage();
  WiFi.statusSequence={WL_AP_LISTENING,WL_NO_MODULE};WiFi.statusAt=0;
  serve(postWithToken(beforeParseFailure),false);
  assert(!ready&&!motorToken[0]&&pulseCount()==0); // Chyba po parseru, těsně před pulzem.
  clockMs=networkCheckedAt+1000;loop();assert(ready&&pulseCount()==0);
  serve(postWithToken(beforeParseFailure),false);assert(pulseCount()==0);
  serve(postWithToken(loadPage()),true);assert(pulseCount()==1);

  resetRuntime();const std::string beforeDelayedStatus=loadPage();
  WiFi.statusDelays={0,4000};WiFi.statusDelayAt=0;
  serve(postWithToken(beforeDelayedStatus),false);
  assert(ready&&!motorToken[0]&&pulseCount()==0&&clockMs==4000);
  serve(postWithToken(beforeDelayedStatus),false);assert(pulseCount()==0);
  serve(postWithToken(loadPage()),true);assert(pulseCount()==1);

  resetRuntime();ready=false;apConfigured=false;server.started=false;motorToken[0]='\0';
  WiFi.state=WL_NO_MODULE;setup();
  assert(!ready&&!apConfigured&&!server.started&&!motorToken[0]&&pulseCount()==0);
  assert(WiFi.beginCalls==0&&server.beginCalls==0);
  const int noModuleQueries=WiFi.statusCalls;
  WiFi.state=WL_AP_LISTENING;clockMs=999;loop();assert(WiFi.statusCalls==noModuleQueries);
  clockMs=1000;loop();
  assert(ready&&apConfigured&&server.started&&WiFi.beginCalls==1&&server.beginCalls==1);
  assert(clockMs==11000&&pulseCount()==0&&!motorToken[0]);
  serve(postWithToken(loadPage()),true);assert(pulseCount()==1);

  resetRuntime();ready=false;apConfigured=false;server.started=false;motorToken[0]='\0';
  server.beginSucceeds=false;setup();
  assert(!ready&&apConfigured&&!server.started&&server.beginCalls==1&&pulseCount()==0);
  assert(std::string(diagnosticSetup)=="server-begin-failed");
  server.beginSucceeds=true;clockMs=networkCheckedAt+999;loop();assert(server.beginCalls==1);
  clockMs=networkCheckedAt+1000;loop();
  assert(ready&&server.started&&server.beginCalls==2&&WiFi.beginCalls==1&&pulseCount()==0);
  serve(postWithToken(loadPage()),true);assert(pulseCount()==1);

  resetRuntime();ready=false;apConfigured=false;server.started=false;motorToken[0]='\0';
  WiFi.state=77;setup();assert(!ready&&!apConfigured&&WiFi.beginCalls==1);
  WiFi.state=WL_AP_LISTENING;clockMs=networkCheckedAt+1000;loop();
  assert(ready&&apConfigured&&WiFi.beginCalls==2&&server.beginCalls==1&&pulseCount()==0);
  std::cout<<"PASS recovery: transient 255/0/77 resumes without AP/server restart, retry bounded to 1s, queued old POST rejected, fresh GET+POST works, failed/slow post-parser status STOP, initial no-module/AP/server failure recovers.\n";

  // Diagnostika je UART bez čekání na monitor; snapshot přežije ztracený bootový log.
  resetRuntime();ready=false;apConfigured=false;server.started=false;motorToken[0]='\0';
  setup();assert(ready&&server.started&&Serial.baud==115200&&!enabled&&ioWhileOn==0);
  assert(Serial.output.find("boot=server-started fw=mock-0.6.0 ip=192.168.4.1")!=std::string::npos);
  Serial.output.clear();clockMs+=5000;loop();
  assert(Serial.output.find("boot=server-started")!=std::string::npos);
  assert(Serial.output.find("ready=1 server=1")!=std::string::npos);
  Serial.output.clear();clockMs+=1000;Serial.input="?";Serial.at=0;
  const int queries=WiFi.statusCalls+WiFi.firmwareCalls+WiFi.ipCalls;
  diagnosticPoll();assert(Serial.output.find("statusLast=")!=std::string::npos);
  assert(queries==WiFi.statusCalls+WiFi.firmwareCalls+WiFi.ipCalls); // Snapshot pouze z cache.
  Serial.output.clear();Serial.input=std::string(100,'?');Serial.at=0;diagnosticPoll();
  assert(Serial.at==8&&Serial.output.empty()); // Omezený příjem i frekvence vyžádaných zpráv.
  Serial.input.clear();Serial.at=0;WiFi.state=77;loop();
  assert(!ready&&!enabled&&Serial.output.find("STOP WiFi retry 77")!=std::string::npos);
  Serial.output.clear();WiFi.state=WL_AP_LISTENING;clockMs+=5000;
  const int beforeRecovery=WiFi.statusCalls;loop();
  assert(ready&&WiFi.statusCalls==beforeRecovery+1);
  assert(Serial.output.find("web-ready new-page-required")!=std::string::npos);
  Serial.output.clear();clockMs+=5000;diagnosticPoll();
  assert(Serial.output.find("ready=1")!=std::string::npos&&diagnosticStatus==WL_AP_LISTENING);
  assert(Serial.output.find(TEST_TOKEN)==std::string::npos);
  std::cout<<"PASS diagnostics: cached late snapshot, '?' rate limit, recovery reporting, no monitor wait, zero Serial/WiFi/RNG I/O during motor pulse.\n";
#endif
  std::cout<<"PASS "<<total<<" parser cases + "<<loops<<" full-loop cases; motor only on valid POST, 1000ms pulse, zero I/O during pulse, no replay, WiFi failures STOP.\n";
}
