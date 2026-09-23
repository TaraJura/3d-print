#pragma once
#include "WiFiS3.h"
inline bool pwmBeginSucceeds=true,pwmPulseSucceeds=true;
inline float pwmFrequency=0;
inline float servoFrequency=0;
inline uint16_t servoPulseUs=0;
inline int pwmBeginFailPin=-1, pwmPulseFailPin=-1;
struct ServoWrite {uint16_t pulse; uint32_t time; bool irq;};
inline std::vector<ServoWrite> servoWrites;
class PwmOut {
  int pin;
public:
  explicit PwmOut(int value):pin(value){}
  bool begin(float frequency,float duty=0){if(pin==5)pwmFrequency=frequency;else servoFrequency=frequency;
    if(!pwmBeginSucceeds || pin==pwmBeginFailPin)return false;
    return pulse_perc(duty);}
  bool pulse_perc(float duty){if(!pwmPulseSucceeds || pin==pwmPulseFailPin)return false;
    if(pin==9){servoPulseUs=uint16_t(duty*200.0f+0.5f);servoWrites.push_back({servoPulseUs,clockMs,inInterrupt});}
    analogWrite(pin,int(duty*255.0f/100.0f+0.5f));return true;}
  bool duty_cycle(float duty){return pulse_perc(duty);}
  void end(){analogWrite(pin,0);}
};
