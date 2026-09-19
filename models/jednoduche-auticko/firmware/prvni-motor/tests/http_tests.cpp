#include SKETCH_PATH
#include <cassert>
#include <iostream>
#include <utility>

int main() {
  struct Case {std::string name,text;Request expected;unsigned long gap;};
  std::vector<Case> cases;
  const std::string base="POST /test HTTP/1.1\r\nHost: 192.168.4.1\r\nContent-Length: 0\r\nX-Motor-Test: 1\r\n";
  auto add=[&](std::string text,Request expected,unsigned long gap=0,std::string name=""){cases.push_back({name,text,expected,gap});};
  add("GET / HTTP/1.1\r\nHost: 192.168.4.1\r\n\r\n",PAGE);
  add(base+"\r\n",TEST);
  add(base+"Origin: http://192.168.4.1\r\nContent-Type: text/plain;charset=UTF-8\r\n\r\n",TEST);
  add("POST /test HTTP/1.1\r\nhOsT: 192.168.4.1:80\t\r\nCONTENT-length: 0\r\nX-MOTOR-TEST:\t1 \r\n\r\n",TEST);
  for(const auto& line:{"GET /test HTTP/1.1","GET /favicon.ico HTTP/1.1","POST /test?run=1 HTTP/1.1","POST /test HTTP/1.0","HEAD / HTTP/1.1","OPTIONS /test HTTP/1.1","POST /test HTTP/1.1 extra"})
    add(std::string(line)+"\r\nHost: 192.168.4.1\r\nContent-Length: 0\r\nX-Motor-Test: 1\r\n\r\n",INVALID);
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
    add("POST /test HTTP/1.1\r\nHost: 192.168.4.1\r\nContent-Length: "+std::string(value)+"\r\nX-Motor-Test: 1\r\n\r\n",INVALID);
  add("POST /test HTTP/1.1\r\nHost: 192.168.4.1\r\nX-Motor-Test: 1\r\n\r\n",INVALID);
  add("POST /test HTTP/1.1\r\nHost: 192.168.4.1\r\nContent-Length: 0\r\n\r\n",INVALID);
  add("POST /test HTTP/1.1\r\nHost: other\r\nContent-Length: 0\r\nX-Motor-Test: 1\r\n\r\n",INVALID);
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
  add("GET / HTTP/1.1\r\nHost: 192.168.4.1\r\nContent-Length: 0\r\nX-Motor-Test: 1\r\n\r\n",PAGE,0,"GET with motor headers still cannot run motor");
  add(base+"Origin: null\r\n\r\n",INVALID);
  add(base+"X-Motor-Test: 0\r\n\r\n",INVALID);
  add(base+"X-Test: bad\rvalue\r\n\r\n",INVALID);
  add(base+"X-Test: value\r\r\n\r\n",INVALID);
  add(base+std::string("X-Test: \xff\r\n\r\n"),INVALID);
  add("\r\n"+base+"\r\n",INVALID);

  int total=0,loops=0;
  for(const auto& c:cases){
    clockMs=0;enabled=0;writes.clear();ioWhileOn=0;
    WiFiClient client(c.text,c.gap);auto got=readRequest(client);
    if(got!=c.expected){std::cerr<<"FAIL parser "<<total<<" "<<c.name<<" expected="<<c.expected<<" got="<<got<<"\n";return 1;}
    assert(writes.empty());assert(clockMs<=TEST_DEADLINE);
    if(!c.name.empty())std::cout<<"PASS parser "<<c.name<<": result="<<got<<" time="<<clockMs<<"ms\n";
    ++total;
    clockMs=0;enabled=0;writes.clear();ioWhileOn=0;ready=true;WiFi.state=WL_AP_LISTENING;
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
  clockMs=0;enabled=0;writes.clear();ioWhileOn=0;motorPulse();
  assert(clockMs==1000&&enabled==0&&pins[7]==LOW&&pins[8]==LOW&&pins[13]==LOW&&ioWhileOn==0);
  ready=false;WiFi.state=WL_NO_MODULE;setup();assert(!ready&&!enabled);
  ready=true;WiFi.state=77;loop();assert(!ready&&!enabled);
  std::cout<<"PASS "<<total<<" parser cases + "<<loops<<" full-loop cases; motor only on valid POST, 1000ms pulse, zero I/O during pulse, no replay, WiFi failures STOP.\n";
}
