#pragma once
#include "WiFiS3.h"
#define TIMER_MODE_PERIODIC 0
#define GPT_TIMER 0
struct timer_callback_args_t {};
inline bool timerBeginSucceeds=true,timerIrqSucceeds=true,timerOpenSucceeds=true,timerStartSucceeds=true;
inline bool timerActive=false;
inline int8_t timerAvailable=1;
inline uint32_t timerPeriodMs=5,timerLastMs=0;
inline void (*timerCallback)(timer_callback_args_t *)=nullptr;
inline void timerTick(){
  if(timerActive&&timerCallback&&uint32_t(clockMs-timerLastMs)>=timerPeriodMs){
    timerLastMs=clockMs;inInterrupt=true;timer_callback_args_t args;timerCallback(&args);inInterrupt=false;
  }
}
class FspTimer {
public:
  static int8_t get_available_timer(uint8_t &type,bool=false){type=0;return timerAvailable;}
  bool begin(uint8_t,uint8_t,uint8_t,float frequency,float,void (*callback)(timer_callback_args_t *),void * = nullptr){
    timerCallback=callback;timerPeriodMs=uint32_t(1000/frequency);timerLastMs=clockMs;clockTick=timerTick;return timerBeginSucceeds;
  }
  bool setup_overflow_irq(uint8_t=12){return timerIrqSucceeds;}
  bool open(){return timerOpenSucceeds;}
  bool start(){timerActive=timerStartSucceeds;return timerStartSucceeds;}
  bool stop(){timerActive=false;return true;}
  bool close(){timerActive=false;return true;}
};
