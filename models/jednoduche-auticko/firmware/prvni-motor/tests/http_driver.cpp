// Persistent process for real Chromium -> HTTP bridge -> actual firmware tests.
// The only transport is stdin/stdout. Timer and GPIO are host mocks.
#define HOST_DRIVER
#include "http_tests.cpp"
#include <sstream>
std::string hex(const std::string &s){
  const char *digits="0123456789abcdef";std::string out;
  for(unsigned char c:s){out+=digits[c>>4];out+=digits[c&15];}return out;
}
std::string unhex(const std::string &s){
  std::string out;for(size_t i=0;i+1<s.size();i+=2)out+=char(std::stoul(s.substr(i,2),nullptr,16));return out;
}
int main(){
  resetRuntime();
  for(std::string line;std::getline(std::cin,line);){
    std::istringstream input(line);std::string command,data,response;input>>command>>data;
    if(command=="RESET")resetRuntime();
    else if(command=="TICK")delay(std::stoul(data));
    else if(command=="REQUEST"){
      WiFiClient client(unhex(data));server.pending=client;loop();response=client.state->output;
    } else if(command=="WIFI")WiFi.state=std::stoi(data);
    else if(command=="LOOP")loop();
    else if(command!="STATE")return 2;
    std::cout<<"{\"time\":"<<clockMs<<",\"motor\":"<<enabled<<",\"steeringUs\":"<<servoPulseUs<<",\"state\":"<<int(driveState)
      <<",\"motorDirection\":"<<int(motorDirection)<<",\"in1\":"<<pins[7]<<",\"in2\":"<<pins[8]<<",\"reversePauseMs\":"<<reversePauseRemaining()
      <<",\"watchdog\":"<<watchdogStops<<",\"press\":"<<lastPress<<",\"responseHex\":\""<<hex(response)<<"\"}"<<std::endl;
  }
  return 0;
}
