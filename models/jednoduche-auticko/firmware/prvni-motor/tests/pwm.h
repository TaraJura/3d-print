#pragma once
#include "WiFiS3.h"
inline bool pwmBeginSucceeds=true,pwmPulseSucceeds=true;
inline float pwmFrequency=0;
class PwmOut {
  int pin;
public:
  explicit PwmOut(int value):pin(value){}
  bool begin(float frequency,float duty=0){pwmFrequency=frequency;pulse_perc(duty);return pwmBeginSucceeds;}
  bool pulse_perc(float duty){if(!pwmPulseSucceeds)return false;analogWrite(pin,int(duty*255.0f/100.0f+0.5f));return true;}
  bool duty_cycle(float duty){return pulse_perc(duty);}
  void end(){analogWrite(pin,0);}
};
