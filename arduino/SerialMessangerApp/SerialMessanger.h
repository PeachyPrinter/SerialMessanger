#ifndef SerialMessanger_h
#define SerialMessanger_h

#include "Arduino.h"

class SerialMessanger
{
  public:
    SerialMessanger();
    SerialMessanger(byte *header,byte *footer,byte *hanshake);
    byte *header;
    byte *footer;
    byte *handshake;
    void sendMessage(byte *data);
    void readMessage();
  private:
    void init(byte *header,byte *footer,byte *hanshake);
};

#endif