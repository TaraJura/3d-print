#pragma once
// Náhrady API pouze pro hostové testy; žádný přístup k USB, síti ani motoru.
#include <cstdint>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>
#define LED_BUILTIN 13
#define OUTPUT 1
#define HIGH 1
#define LOW 0
#define WL_NO_MODULE 255
#define WL_AP_LISTENING 1
#define WL_AP_CONNECTED 2
inline unsigned long clockMs=0;
inline int enabled=0, ioWhileOn=0, pins[20]={};
struct PinWrite {int pin,value;unsigned long time;};
inline std::vector<PinWrite> writes;
inline void io(){if(enabled)++ioWhileOn;}
inline unsigned long millis(){return clockMs;}
inline void delay(unsigned long ms){clockMs+=ms;}
inline void pinMode(int pin,int){if(pin!=5&&pin!=7&&pin!=8&&pin!=13)throw std::runtime_error("unexpected pin");}
inline void analogWriteResolution(int){}
inline void digitalWrite(int pin,int value){pinMode(pin,1);pins[pin]=value;writes.push_back({pin,value,clockMs});}
inline void analogWrite(int pin,int value){digitalWrite(pin,value);if(pin==5)enabled=value;}
struct IPAddress {IPAddress(int,int,int,int){}};
struct ClientState {std::string input,output;size_t at=0;bool alive=true;unsigned long next=0,gap=0;};
struct WiFiClient {
  std::shared_ptr<ClientState> state;
  WiFiClient()=default;
  WiFiClient(std::string text,unsigned long gap=0):state(std::make_shared<ClientState>()){
    state->input=text;state->gap=gap;
  }
  bool connected(){io();return state&&state->alive;}
  int available(){io();return state&&clockMs>=state->next?int(state->input.size()-state->at):0;}
  int read(){io();if(!state||state->at>=state->input.size())return -1;state->next=clockMs+state->gap;return static_cast<unsigned char>(state->input[state->at++]);}
  void print(const char *s){io();state->output+=s;}
  void print(size_t n){io();state->output+=std::to_string(n);}
  void stop(){io();if(state)state->alive=false;}
  operator bool(){return bool(state)&&state->alive;}
};
struct WiFiServer {
  WiFiClient pending;
  WiFiServer(int){}
  void begin(){io();}
  WiFiClient available(){io();WiFiClient c=pending;pending=WiFiClient();return c;}
};
struct MockWiFi {
  int state=WL_AP_LISTENING;
  int status(){io();return state;}
  void config(IPAddress){io();}
  int beginAP(const char*,const char*){io();return state;}
};
inline MockWiFi WiFi;
