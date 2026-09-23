#pragma once
// Host-only substitutes. No USB, socket, or physical output is accessed.
#include <algorithm>
#include <cstdint>
#include <functional>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>
#define LED_BUILTIN 13
#define OUTPUT 1
#define HIGH 1
#define LOW 0
#define WL_NO_MODULE 255
#define WL_AP_LISTENING 7
#define WL_AP_CONNECTED 8
inline uint32_t clockMs=0;
inline int enabled=0, ioWhileOn=0, ioInInterrupt=0, pins[20]={};
inline bool inInterrupt=false;
inline unsigned int interruptDepth=0;
inline void (*clockTick)()=nullptr;
inline void (*onMotorEnable)()=nullptr;
inline std::vector<long> randomValues;
inline size_t randomAt=0;
inline int randomCalls=0;
struct PinWrite {int pin,value;uint32_t time;};
inline std::vector<PinWrite> writes;
inline void io(){if(enabled)++ioWhileOn;if(inInterrupt)++ioInInterrupt;}
inline unsigned long millis(){return clockMs;}
inline void delay(unsigned long ms){
  while(ms--){++clockMs;if(clockTick&&!interruptDepth)clockTick();}
}
inline void noInterrupts(){++interruptDepth;}
inline void interrupts(){if(interruptDepth)--interruptDepth;}
inline void pinMode(int pin,int){if(pin!=5&&pin!=7&&pin!=8&&pin!=9&&pin!=13)throw std::runtime_error("unexpected output pin");}
inline int digitalRead(int pin){return pins[pin]?HIGH:LOW;}
inline void analogWriteResolution(int){}
inline void digitalWrite(int pin,int value){pinMode(pin,1);pins[pin]=value;if(pin==5)enabled=value;writes.push_back({pin,value,clockMs});}
inline void analogWrite(int pin,int value){digitalWrite(pin,value);if(pin==5){enabled=value;if(value&&onMotorEnable)onMotorEnable();}}
inline long random(long maximum){
  io();++randomCalls;
  const long value=randomAt<randomValues.size()?randomValues[randomAt++]:0x12345678L;
  return value<0?value:value%maximum;
}
// One-shot delays mimic blocking AT operations; timer callbacks still execute.
struct MockDelays {
  uint32_t connected=0, available=0, read=0, print=0, write=0, stop=0, serial=0;
};
inline MockDelays blocked;
inline void blockOnce(uint32_t &ms){const auto amount=ms;ms=0;delay(amount);}
struct MockSerial {
  std::string output,input; size_t at=0; unsigned long baud=0;
  void begin(unsigned long b){io();baud=b;}
  int available(){io();blockOnce(blocked.serial);return int(input.size()-at);}
  int read(){io();return at<input.size()?static_cast<unsigned char>(input[at++]):-1;}
  size_t write(uint8_t *data,size_t size){io();blockOnce(blocked.serial);output.append(reinterpret_cast<char *>(data),size);return size;}
};
inline MockSerial Serial;
struct IPAddress {
  uint8_t octets[4];
  IPAddress(int a,int b,int c,int d):octets{uint8_t(a),uint8_t(b),uint8_t(c),uint8_t(d)}{}
  uint8_t operator[](size_t i)const{return octets[i];}
};
struct ClientState {std::string input,output;size_t at=0;bool alive=true;int writeCalls=0,printCalls=0;uint32_t next=0,gap=0;};
struct WiFiClient {
  std::shared_ptr<ClientState> state;
  WiFiClient()=default;
  WiFiClient(std::string text,unsigned long gap=0):state(std::make_shared<ClientState>()){
    state->input=text;state->gap=gap;state->next=clockMs;
  }
  bool connected(){io();blockOnce(blocked.connected);return state&&state->alive;}
  int available(){io();blockOnce(blocked.available);return state&&int32_t(clockMs-state->next)>=0?int(state->input.size()-state->at):0;}
  int read(){io();blockOnce(blocked.read);if(!state||state->at>=state->input.size())return -1;state->next=clockMs+state->gap;return static_cast<unsigned char>(state->input[state->at++]);}
  void print(const char *s){++state->printCalls;io();blockOnce(blocked.print);state->output+=s;}
  void print(size_t n){++state->printCalls;io();blockOnce(blocked.print);state->output+=std::to_string(n);}
  size_t write(const uint8_t *data,size_t size){++state->writeCalls;io();blockOnce(blocked.write);state->output.append(reinterpret_cast<const char *>(data),size);return size;}
  void stop(){io();blockOnce(blocked.stop);if(state)state->alive=false;}
  operator bool(){return bool(state)&&state->alive;}
};
struct WiFiServer {
  WiFiClient pending;
  bool started=false,beginSucceeds=true;
  int beginCalls=0;
  WiFiServer(int){}
  void begin(){io();++beginCalls;started=beginSucceeds;}
  operator bool()const{return started;}
  WiFiClient available(){io();WiFiClient c=pending;pending=WiFiClient();return c;}
};
struct MockWiFi {
  int state=WL_AP_LISTENING;
  int statusCalls=0,firmwareCalls=0,ipCalls=0,configCalls=0,beginCalls=0;
  std::vector<int> statusSequence;size_t statusAt=0;
  std::vector<unsigned long> statusDelays;size_t statusDelayAt=0;
  int status(){
    io();++statusCalls;
    if(statusDelayAt<statusDelays.size())delay(statusDelays[statusDelayAt++]);
    return statusAt<statusSequence.size()?statusSequence[statusAt++]:state;
  }
  void config(IPAddress){io();++configCalls;}
  int beginAP(const char*,const char*){io();++beginCalls;return state;}
  const char *firmwareVersion(){io();++firmwareCalls;return "mock-0.4.1";}
  IPAddress localIP(){io();++ipCalls;return IPAddress(192,168,4,1);}
};
inline MockWiFi WiFi;
