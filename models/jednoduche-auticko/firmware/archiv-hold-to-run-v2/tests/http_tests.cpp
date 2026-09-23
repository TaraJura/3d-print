#include SKETCH_PATH
#include <cassert>
#include <iostream>
#include <utility>

const char TEST_TOKEN[]="0123456789abcdef0123456789abcdef";
const char TEST_CHALLENGE[]="fedcba9876543210fedcba9876543210";
const std::string GET_PAGE="GET / HTTP/1.1\r\nHost: 192.168.4.1\r\n\r\n";
const std::string TOKEN_HEADER=std::string("X-Motor-Token: ")+TEST_TOKEN+"\r\n";
unsigned scenarios=0;
void passed(const char *name){++scenarios;std::cout<<"PASS "<<name<<"\n";}

void resetRuntime(bool boot=true) {
  clockTick=nullptr;clockMs=0;enabled=0;ioWhileOn=0;ioInInterrupt=0;inInterrupt=false;interruptDepth=0;
  writes.clear();for(int &pin:pins)pin=LOW;
  onMotorEnable=nullptr;randomValues.clear();randomAt=0;randomCalls=0;blocked=MockDelays();
  timerBeginSucceeds=timerIrqSucceeds=timerOpenSucceeds=timerStartSucceeds=true;
  timerActive=false;timerAvailable=1;timerCallback=nullptr;timerLastMs=0;
  pwmBeginSucceeds=true;pwmPulseSucceeds=true;pwmFrequency=0;
  pwmReady=false;safetyReady=false;driveState=IDLE;leaseTicks=0;watchdogStops=0;armExpiries=0;runExpiries=0;stopReason=0;diagnosticRequestLogAt=0;challengeIssuedAt=0;holdChallenge[0]='\0';
  WiFi=MockWiFi();Serial=MockSerial();server=WiFiServer(80);
  ready=false;apConfigured=false;networkAttempted=false;networkCheckedAt=0;
  tokenSequence=0;motorToken[0]='\0';previousSessionToken[0]='\0';requestToken[0]='\0';lastPress=0;requestPress=0;requestChallenge[0]='\0';
  snprintf(diagnosticFirmware,sizeof(diagnosticFirmware),"not-read");
  for(auto &octet:diagnosticIP)octet=0;
  diagnosticSetup="starting";diagnosticStatus=-1;diagnosticApStart=-1;
  diagnosticStatusAt=0;diagnosticSnapshotAt=0;diagnosticHttpAt=0;diagnosticStatusLogAt=0;
  diagnosticAccepted=0;diagnosticClosed=0;diagnosticHttpSeen=false;
  if(boot){setup();assert(!enabled&&pins[7]==LOW&&pins[8]==LOW&&pins[13]==LOW);assert(ioInInterrupt==0);}
}

int enableWrites(){int starts=0;for(const auto &w:writes)if(w.pin==5&&w.value){assert(w.value==128);++starts;}return starts;}
bool isToken(const std::string &s){if(s.size()!=32)return false;for(char c:s)if(!((c>='0'&&c<='9')||(c>='a'&&c<='f')))return false;return true;}
std::string request(const std::string &path,const std::string &token,uint32_t press,const std::string &challenge=""){
  std::string s="POST /"+path+" HTTP/1.1\r\nHost: 192.168.4.1\r\nContent-Length: 0\r\nX-Motor-Control: 1\r\nX-Motor-Token: "+token+"\r\nX-Motor-Press: "+std::to_string(press)+"\r\n";
  if(!challenge.empty())s+="X-Motor-Challenge: "+challenge+"\r\n";
  return s+"\r\n";
}
std::string sessionRequest(const std::string &token){return "POST /session HTTP/1.1\r\nHost: 192.168.4.1\r\nContent-Length: 0\r\nX-Motor-Control: 1\r\nX-Motor-Token: "+token+"\r\n\r\n";}
std::string responseBody(const WiFiClient &c){
  const auto &s=c.state->output;const auto split=s.find("\r\n\r\n");assert(split!=std::string::npos);
  const auto length=s.find("Content-Length: ");assert(length!=std::string::npos);
  const std::string body=s.substr(split+4);assert(std::stoul(s.substr(length+16))==body.size());return body;
}
WiFiClient serve(const std::string &text,bool ok=true,unsigned long gap=0){
  WiFiClient c(text,gap);server.pending=c;loop();
  if(c.state->alive||c.state->output.find(ok?"HTTP/1.1 200":"HTTP/1.1 400")!=0){
    std::cerr<<"Request: "<<text<<"Expected ok="<<ok<<" received: "<<c.state->output<<"\n";assert(false);
  }
  responseBody(c);assert(ioInInterrupt==0);
  if(text.rfind("POST ",0)==0)assert(c.state->writeCalls==1&&c.state->printCalls==0);
  return c;
}
std::string loadPage(){const auto c=serve(GET_PAGE);const std::string token=motorToken;assert(isToken(token));assert(responseBody(c).find(token)!=std::string::npos);assert(!enabled);return token;}
std::string arm(const std::string &token,uint32_t press){
  const auto body=responseBody(serve(request("arm",token,press)));assert(body.rfind("ARM_OK:",0)==0);const auto challenge=body.substr(7);assert(isToken(challenge));assert(!enabled);return challenge;
}
std::string hold(const std::string &token,uint32_t press,const std::string &challenge){
  const auto body=responseBody(serve(request("hold",token,press,challenge)));assert(body.rfind("HOLD_OK:",0)==0);const auto next=body.substr(8);assert(isToken(next)&&next!=challenge);assert(enabled==128&&pins[7]==HIGH&&pins[8]==LOW&&pins[13]==HIGH);return next;
}
void stop(const std::string &token,uint32_t press){assert(responseBody(serve(request("stop",token,press)))=="STOP_OK");assert(!enabled&&pins[7]==LOW&&pins[8]==LOW&&pins[13]==LOW);}
uint32_t firstOffAfter(size_t marker){for(size_t i=marker;i<writes.size();++i)if(writes[i].pin==5&&!writes[i].value)return writes[i].time;assert(false);return 0;}

void parserTests(){
  struct Case{std::string name,text;Request expected;unsigned long gap;};std::vector<Case> cases;
  const std::string base="POST /arm HTTP/1.1\r\nHost: 192.168.4.1\r\nContent-Length: 0\r\nX-Motor-Control: 1\r\n"+TOKEN_HEADER+"X-Motor-Press: 1\r\n";
  auto add=[&](std::string text,Request expected,unsigned long gap=0,std::string name=""){cases.push_back({name,text,expected,gap});};
  add(GET_PAGE,PAGE);add(base+"\r\n",ARM);
  add(base+"Origin: http://192.168.4.1\r\nContent-Type: text/plain;charset=UTF-8\r\n\r\n",ARM);
  add("POST /arm HTTP/1.1\r\nhOsT: 192.168.4.1:80\t\r\nCONTENT-length: 0\r\nX-MOTOR-CONTROL:\t1 \r\n"+TOKEN_HEADER+"X-Motor-Press: 1\r\n\r\n",ARM);
  for(const auto &line:{"GET /arm HTTP/1.1","GET /favicon.ico HTTP/1.1","POST /arm?run=1 HTTP/1.1","POST /arm HTTP/1.0","HEAD / HTTP/1.1","OPTIONS /arm HTTP/1.1","POST /arm HTTP/1.1 extra"})
    add(std::string(line)+"\r\nHost: 192.168.4.1\r\nContent-Length: 0\r\nX-Motor-Control: 1\r\n"+TOKEN_HEADER+"X-Motor-Press: 1\r\n\r\n",INVALID);
  add(base,INVALID);add(base+"\r",INVALID);add("POST /arm HTTP/1.1\nHost: 192.168.4.1\n\n",INVALID);
  for(const auto &line:{"Transfer-Encoding: chunked","Expect: 100-continue","Content-Length: 0","Host: 192.168.4.1","X-Motor-Control: 1","Origin: http://evil.example","Broken header"," Bad: value","Bad header: value"})add(base+line+"\r\n\r\n",INVALID);
  add(base+std::string("X:\0bad\r\n\r\n",11),INVALID);
  add(base+"X:"+std::string(TEST_MAX_LINE-2,'a')+"\r\n\r\n",ARM,0,"exact line limit");
  add(base+"X:"+std::string(TEST_MAX_LINE-1,'a')+"\r\n\r\n",INVALID,0,"line limit plus one");
  for(const auto &value:{"1","-1","00","+0","0, 0","0x0"})add("POST /arm HTTP/1.1\r\nHost: 192.168.4.1\r\nContent-Length: "+std::string(value)+"\r\nX-Motor-Control: 1\r\n"+TOKEN_HEADER+"X-Motor-Press: 1\r\n\r\n",INVALID);
  add("POST /arm HTTP/1.1\r\nHost: 192.168.4.1\r\nX-Motor-Control: 1\r\n"+TOKEN_HEADER+"X-Motor-Press: 1\r\n\r\n",INVALID);
  add("POST /arm HTTP/1.1\r\nHost: 192.168.4.1\r\nContent-Length: 0\r\n"+TOKEN_HEADER+"X-Motor-Press: 1\r\n\r\n",INVALID);
  add("POST /arm HTTP/1.1\r\nHost: other\r\nContent-Length: 0\r\nX-Motor-Control: 1\r\n"+TOKEN_HEADER+"X-Motor-Press: 1\r\n\r\n",INVALID);
  auto sized=[&](int n){std::string s=base;while(n-int(s.size())-2>130)s+="Z:"+std::string(124,'a')+"\r\n";s+="Z:"+std::string(n-int(s.size())-6,'a')+"\r\n\r\n";assert(int(s.size())==n);return s;};
  add(sized(TEST_MAX_BYTES),ARM,0,"exact total limit");add(sized(TEST_MAX_BYTES+1),INVALID,0,"total limit plus one");add(base+"\r\n",INVALID,100,"slow header timeout");
  assert(cases.size()==38);
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
  add(chromeGET,PAGE,0,"Chrome Android GET");add(safariGET,PAGE,0,"Safari iOS GET");add(chromePOST,ARM,0,"Chrome Android POST");add(safariPOST,ARM,0,"Safari iOS POST");
  add(chromeGET,PAGE,1,"fragmented Chrome GET");add(safariPOST,ARM,1,"fragmented Safari POST");
  add(get+chromeAccept+"\r\n\r\n",PAGE);add(get+safariUA+"\r\n\r\n",PAGE);
  add("GET / HTTP/1.1\r\nHost: 192.168.4.1\r\nContent-Length: 0\r\nX-Motor-Control: 1\r\n"+TOKEN_HEADER+"X-Motor-Press: 1\r\n\r\n",PAGE);
  for(const auto &line:{"Origin: null","X-Motor-Control: 0","X-Test: bad\rvalue","X-Test: value\r","X-Test: \xff"})add(base+line+"\r\n\r\n",INVALID);
  add("\r\n"+base+"\r\n",INVALID);assert(cases.size()==53);
  add(request("test",TEST_TOKEN,1),INVALID,0,"old pulse endpoint rejected");
  add(request("hold",TEST_TOKEN,1,TEST_CHALLENGE),HOLD);add(request("stop",TEST_TOKEN,1),STOP);
  for(const auto &value:{"0","00","01","-1","+1","1.0","0x1","4294967296","99999999999999999999999999","","1 2"}){
    std::string s=base;const auto start=s.find("X-Motor-Press: 1");s.replace(start,16,std::string("X-Motor-Press: ")+value+"\r");add(s+"\r\n",INVALID,0,"invalid press number");
  }
  add(request("arm",TEST_TOKEN,UINT32_MAX),ARM,0,"maximum press counter");
  for(const auto &header:{"X-Motor-Press: 1","x-motor-press: 2","X-Motor-Token: 0123456789abcdef0123456789abcdef"})add(base+header+"\r\n\r\n",INVALID);
  for(const auto &name:{"X-Motor-Press: 1\r\n","X-Motor-Token: 0123456789abcdef0123456789abcdef\r\n"}){std::string s=base;const auto at=s.find(name);assert(at!=std::string::npos);s.erase(at,std::string(name).size());add(s+"\r\n",INVALID);}
  for(const auto &token:{"","wrong","0123456789abcdef0123456789abcdeff"})add(request("arm",token,1),INVALID);
  add(request("hold",TEST_TOKEN,1),INVALID,0,"hold requires challenge");
  for(const auto &challenge:{"wrong","0123456789abcdef0123456789abcdeff","0123456789abcdef0123456789abcdef00","0123456789abcdeg0123456789abcdef0"})add(request("hold",TEST_TOKEN,1,challenge),INVALID);
  std::string duplicateChallenge=request("hold",TEST_TOKEN,1,TEST_CHALLENGE);duplicateChallenge.insert(duplicateChallenge.size()-2,std::string("X-Motor-Challenge: ")+TEST_CHALLENGE+"\r\n");add(duplicateChallenge,INVALID);
  add(sessionRequest(TEST_TOKEN),SESSION,0,"session request without press");
  add("GET /session HTTP/1.1\r\nHost: 192.168.4.1\r\n\r\n",INVALID);
  for(const auto &header:{"X-Motor-Control: 1\r\n","Content-Length: 0\r\n","X-Motor-Token: 0123456789abcdef0123456789abcdef\r\n"}){
    std::string missing=sessionRequest(TEST_TOKEN);const auto at=missing.find(header);missing.erase(at,std::string(header).size());add(missing,INVALID);
    std::string duplicate=sessionRequest(TEST_TOKEN);duplicate.insert(duplicate.size()-2,header);add(duplicate,INVALID);
  }
  unsigned n=0;
  for(const auto &c:cases){
    resetRuntime();snprintf(motorToken,sizeof(motorToken),"%s",TEST_TOKEN);const auto oldWrites=writes.size();const auto start=clockMs;
    WiFiClient client(c.text,c.gap);const auto got=readRequest(client);
    if(got!=c.expected){std::cerr<<"FAIL parser #"<<n<<" "<<c.name<<" expected="<<c.expected<<" got="<<got<<"\n"<<c.text;assert(false);}
    assert(writes.size()==oldWrites&&uint32_t(clockMs-start)<=TEST_DEADLINE);
    resetRuntime();snprintf(motorToken,sizeof(motorToken),"%s",TEST_TOKEN);
    const bool ok=c.expected!=INVALID&&c.expected!=HOLD;
    serve(c.text,ok,c.gap);assert(enableWrites()==0);++n;
  }
  std::cout<<"PASS "<<n<<" parser + "<<n<<" complete HTTP loop cases (no request alone starts motor)\n";
}

void protocolTests(){
  resetRuntime();const auto token=loadPage();const auto armed=arm(token,1);delay(100);const auto next=hold(token,1,armed);
  const auto started=clockMs;delay(100);const auto renewed=hold(token,1,next);assert(renewed!=next);
  delay(300);assert(enabled);stop(token,1);assert(uint32_t(clockMs-started)==400);
  const int outputs=enableWrites();serve(request("hold",token,1,renewed),false);serve(request("arm",token,1),false);assert(enableWrites()==outputs);
  hold(token,2,arm(token,2));stop(token,2);passed("arm never moves; fresh challenge starts, heartbeat renews, stop latches, new press works");

  resetRuntime();const auto s=loadPage();stop(s,1);serve(request("arm",s,1),false);serve(request("hold",s,1,TEST_CHALLENGE),false);assert(!enabled&&enableWrites()==0);
  const auto c=arm(s,2);stop(s,2);serve(request("hold",s,2,c),false);assert(enableWrites()==0);passed("STOP before delayed ARM or first HOLD prevents later start");

  resetRuntime();const auto s2=loadPage();auto c2=arm(s2,1);auto c3=hold(s2,1,c2);const int started2=enableWrites();
  serve(request("hold",s2,1,c2),false);assert(enableWrites()==started2);
  // Duplicated/out-of-order heartbeats can stop the run but can never restart it.
  stop(s2,1);serve(request("hold",s2,1,c3),false);assert(!enabled&&enableWrites()==started2);
  passed("duplicate and in-flight heartbeat after STOP cannot restart");

  resetRuntime();const auto s3=loadPage();const auto a3=arm(s3,1);delay(500);serve(request("hold",s3,1,a3),false);assert(enableWrites()==0);
  serve(request("arm",s3,1),false);passed("expired ARM needs new real press");

  resetRuntime();const auto s4=loadPage();const auto live=hold(s4,1,arm(s4,1));const auto renewal=clockMs;const auto marker=writes.size();
  delay(510);assert(!enabled&&pins[7]==LOW&&pins[8]==LOW&&pins[13]==LOW);const auto cut=uint32_t(firstOffAfter(marker)-renewal);assert(cut>=500&&cut<=505);
  const int before=enableWrites();serve(request("hold",s4,1,live),false);assert(enableWrites()==before);serve(request("arm",s4,1),false);
  passed("independent IRQ cuts motor within 505 ms without loop or heartbeat; expired HOLD cannot renew");

  resetRuntime();const auto old=loadPage();const auto oldChallenge=hold(old,1,arm(old,1));const auto fresh=loadPage();assert(fresh!=old&&!enabled);
  serve(request("hold",old,1,oldChallenge),false);serve(request("arm",old,2),false);hold(fresh,1,arm(fresh,1));stop(fresh,1);
  passed("page refresh stops output and invalidates previous session");

  resetRuntime();const auto anchored=loadPage();const auto issuedChallenge=hold(anchored,1,arm(anchored,1));
  const auto issuedAt=clockMs;delay(300);hold(anchored,1,issuedChallenge);const auto lateMarker=writes.size();
  delay(210);assert(enabled);delay(300);assert(!enabled);assert(uint32_t(firstOffAfter(lateMarker)-issuedAt)==800);
  passed("fresh delayed heartbeat gets full 500ms lease from receipt, fixing double-RTT expiry");

  resetRuntime();const auto maximum=loadPage();stop(maximum,UINT32_MAX);serve(request("arm",maximum,1),false);serve(request("arm",maximum,UINT32_MAX),false);assert(enableWrites()==0);
  const auto newSession=loadPage();hold(newSession,1,arm(newSession,1));stop(newSession,1);passed("press counter never wraps within a session");

  resetRuntime();clockMs=UINT32_MAX-250;timerLastMs=clockMs;const auto wrap=loadPage();const auto wrapChallenge=hold(wrap,1,arm(wrap,1));const auto wrapStart=clockMs;const auto wrapMarker=writes.size();
  delay(510);assert(!enabled);assert(uint32_t(firstOffAfter(wrapMarker)-wrapStart)<=505);serve(request("hold",wrap,1,wrapChallenge),false);passed("watchdog deadline survives millis wraparound");
  for(unsigned gap:{200u,250u,300u,400u}){
    resetRuntime();const auto token=loadPage();auto nonce=hold(token,1,arm(token,1));
    for(int i=0;i<20;++i){delay(gap);nonce=hold(token,1,nonce);assert(enabled&&runExpiries==0);}
    stop(token,1);
  }
  passed("20 sustained heartbeat cycles each at 200/250/300/400ms intervals stay live");
  resetRuntime();const auto late=loadPage();const auto lateNonce=arm(late,1);delay(500);
  assert(driveState==ARMED&&!enabled&&armExpiries==0);serve(request("hold",late,1,lateNonce),false);assert(!enabled);
  resetRuntime();const auto expiry=loadPage();arm(expiry,1);delay(3010);assert(driveState==IDLE&&!enabled&&armExpiries==1);
  passed("ARM waits OFF up to 3000ms but first challenge remains bounded to 500ms");
  resetRuntime();const auto session=loadPage();const auto duplicate=arm(session,1);hold(session,1,duplicate);stop(session,1);
  const auto current=hold(session,2,arm(session,2));
  serve(request("hold",session,1,duplicate),false);assert(enabled);serve(request("arm",session,1),false);assert(enabled);
  serve(request("stop",session,1),true);assert(enabled);const auto starts=enableWrites();
  serve(request("hold",session,2,TEST_CHALLENGE),false);assert(enabled&&enableWrites()==starts);
  hold(session,2,current);stop(session,2);
  passed("obsolete STOP/ARM/HOLD and malformed requests cannot stop or renew newer press");

  resetRuntime();const auto releaseSession=loadPage();const auto inFlight=hold(releaseSession,1,arm(releaseSession,1));
  const auto releasedAt=clockMs;const auto releaseMarker=writes.size();delay(499);hold(releaseSession,1,inFlight);
  serve(request("hold",releaseSession,1,inFlight),false);assert(enabled);delay(510);assert(!enabled);
  const auto maximumRelease=uint32_t(firstOffAfter(releaseMarker)-releasedAt);assert(maximumRelease<=1000);
  passed("lost STOP plus last delayed in-flight HOLD still switches OFF within 1000ms of release");

}

void sessionTests(){
  resetRuntime();const auto old=loadPage();hold(old,1,arm(old,1));
  const auto response=responseBody(serve(sessionRequest(old)));assert(response.rfind("SESSION_OK:",0)==0);
  const auto fresh=response.substr(11);assert(isToken(fresh)&&fresh!=old&&!enabled&&lastPress==0);
  hold(fresh,1,arm(fresh,1));const int starts=enableWrites();
  assert(responseBody(serve(sessionRequest(old)))==response);assert(enabled&&lastPress==1&&enableWrites()==starts);
  serve(request("arm",old,2),false);assert(enabled);
  passed("session rotation stops; repeated recovery request returns current session without cutting new run");

  const auto response2=responseBody(serve(sessionRequest(fresh)));const auto newest=response2.substr(11);
  assert(newest!=fresh&&!enabled);hold(newest,1,arm(newest,1));
  serve(sessionRequest(old),false);assert(enabled);assert(responseBody(serve(sessionRequest(fresh)))==response2);assert(enabled);
  stop(newest,1);passed("older session replay rejected; only immediately previous recovery token is idempotent");

  const auto page=loadPage();hold(page,1,arm(page,1));serve(sessionRequest(fresh),false);assert(enabled);stop(page,1);
  passed("normal page navigation clears recovery cache and fences old sessions");

  resetRuntime();const auto boot=responseBody(serve(sessionRequest(TEST_TOKEN)));const auto bootToken=boot.substr(11);
  assert(isToken(bootToken)&&!enabled);hold(bootToken,1,arm(bootToken,1));stop(bootToken,1);
  passed("new real press may acquire fresh session after boot without browser reload; session alone is OFF");

  resetRuntime();const auto first=loadPage();randomValues={-1};randomAt=0;serve(sessionRequest(first),false);assert(!enabled&&!motorToken[0]);
  randomValues.clear();randomAt=0;const auto retry=responseBody(serve(sessionRequest(first)));assert(isToken(retry.substr(11))&&!enabled);
  passed("session RNG failure is OFF and next explicit recovery request can succeed");
}

void blockingTests(){
  for(const auto &operation:{"status","connected","available","read","write","stop","serial"}){
    resetRuntime();const auto token=loadPage();const auto challenge=hold(token,1,arm(token,1));const auto start=clockMs;const auto marker=writes.size();
    const std::string op=operation;
    if(op=="status"){networkCheckedAt=clockMs-100;WiFi.statusDelays={1000};WiFi.statusDelayAt=0;}
    if(op=="connected")blocked.connected=1000;
    if(op=="available")blocked.available=1000;
    if(op=="read")blocked.read=1000;
    if(op=="write")blocked.write=1000;
    if(op=="stop")blocked.stop=1000;
    if(op=="serial")blocked.serial=1000;
    WiFiClient pending(request("hold",token,1,challenge));server.pending=pending;loop();
    assert(!enabled&&ioInInterrupt==0);const auto elapsed=uint32_t(firstOffAfter(marker)-start);assert(elapsed>=500&&elapsed<=505);
    const int starts=enableWrites();serve(request("hold",token,1,challenge),false);assert(enableWrites()==starts);
    std::cout<<"PASS blocking "<<operation<<": IRQ cutoff="<<elapsed<<" ms\n";
  }
  resetRuntime();const auto token=loadPage();hold(token,1,arm(token,1));const auto start=clockMs;const auto marker=writes.size();
  WiFiClient stalled("POST /hold HTTP/1.1\r\nHost: 192.168.4.1\r\n");server.pending=stalled;loop();assert(!enabled);assert(uint32_t(firstOffAfter(marker)-start)<=505);
  passed("partial or stalled HTTP cannot prolong motor lease");
}

void recoveryTests(){
  for(int status:{WL_NO_MODULE,0,77}){
    resetRuntime();const auto token=loadPage();const auto challenge=hold(token,1,arm(token,1));
    WiFiClient queued(request("hold",token,1,challenge));server.pending=queued;
    networkCheckedAt=clockMs-100;WiFi.statusSequence={status,WL_AP_CONNECTED};WiFi.statusAt=0;loop();assert(!ready&&!enabled&&!motorToken[0]&&queued.state->alive);
    const int calls=WiFi.statusCalls;delay(998);loop();assert(WiFi.statusCalls==calls);delay(2);loop();assert(ready&&!queued.state->alive&&!enabled);
    assert(queued.state->output.find("HTTP/1.1 400")==0);assert(WiFi.beginCalls==1&&server.beginCalls==1);
    const auto fresh=loadPage();assert(fresh!=token);hold(fresh,1,arm(fresh,1));stop(fresh,1);
  }
  passed("transient WiFi 255/0/77 stops; rate-limited recovery keeps server and rejects queued old session");
  resetRuntime(false);WiFi.state=WL_NO_MODULE;setup();assert(!ready&&!enabled&&WiFi.beginCalls==0);WiFi.state=WL_AP_LISTENING;delay(1000);loop();assert(ready&&!enabled);passed("missing module at startup can recover, never starts motor");
  resetRuntime(false);server.beginSucceeds=false;setup();assert(!ready&&!enabled);server.beginSucceeds=true;delay(1000);loop();assert(ready&&!enabled);passed("server start failure can recover without motion");
  resetRuntime(false);WiFi.state=77;setup();assert(!ready&&!enabled);WiFi.state=WL_AP_LISTENING;delay(1000);loop();assert(ready&&!enabled);passed("AP start failure can recover without motion");
  // A new boot cannot accept queued old messages even if USB/WiFi reconnect.
  resetRuntime();const auto previous=loadPage();const auto oldChallenge=hold(previous,1,arm(previous,1));
  resetRuntime();serve(request("hold",previous,1,oldChallenge),false);serve(request("arm",previous,2),false);assert(!enabled&&enableWrites()==0);passed("boot always OFF; old page cannot start before new page load");
}

void failureTests(){
  for(size_t failure=0;failure<3;++failure){resetRuntime();randomValues={1,2,3};randomValues[failure]=-1;serve(GET_PAGE,false);assert(!motorToken[0]&&enableWrites()==0);}
  resetRuntime();tokenSequence=UINT32_MAX;serve(GET_PAGE,false);assert(!motorToken[0]&&enableWrites()==0);passed("RNG failure or exhausted token counter cannot authorize motion");
  for(int fault=0;fault<6;++fault){
    resetRuntime(false);
    if(fault==0)pwmBeginSucceeds=false;
    if(fault==1)timerAvailable=-1;
    if(fault==2)timerBeginSucceeds=false;
    if(fault==3)timerIrqSucceeds=false;
    if(fault==4)timerOpenSucceeds=false;
    if(fault==5)timerStartSucceeds=false;
    setup();assert(!enabled&&enableWrites()==0);
    if(ready){const auto token=loadPage();serve(request("arm",token,1),false);}
    assert(!enabled&&enableWrites()==0);
  }
  passed("PWM or watchdog initialization failures fail closed");
  resetRuntime();const auto token=loadPage();randomValues={-1};randomAt=0;
  serve(request("arm",token,1),false);assert(!enabled);
  resetRuntime();const auto token2=loadPage();const auto challenge2=hold(token2,1,arm(token2,1));
  randomValues={-1};randomAt=0;serve(request("hold",token2,1,challenge2),false);assert(!enabled);
  passed("challenge RNG failure stops instead of running without next challenge");
  resetRuntime();const auto pwmToken=loadPage();const auto pwmChallenge=arm(pwmToken,1);
  pwmPulseSucceeds=false;serve(request("hold",pwmToken,1,pwmChallenge),false);assert(!enabled&&!safetyReady);
  resetRuntime();const auto offToken=loadPage();hold(offToken,1,arm(offToken,1));pwmPulseSucceeds=false;
  delay(510);assert(!enabled&&!safetyReady&&pins[7]==LOW&&pins[8]==LOW);
  passed("PWM update failure and failed PWM OFF use GPIO fallback, disallow further motion");
}
#ifndef HOST_DRIVER
int main(){parserTests();protocolTests();sessionTests();blockingTests();recoveryTests();failureTests();std::cout<<"PASS all host checks ("<<scenarios<<" named protocol/recovery/failure scenarios); no hardware accessed\n";}

#endif
