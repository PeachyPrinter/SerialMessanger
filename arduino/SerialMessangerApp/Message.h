#ifndef Message_h
#define Message_h

#include "Arduino.h"

class Message
{
  public:
    short id();
    int length();
    getBytes(byte *bytes);
    setBytes(byte *bytes);
};

#endif