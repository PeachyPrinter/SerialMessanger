#ifndef SerialMessanger_h
#define SerialMessanger_h

#include "Arduino.h"
@include "Message.h"

class SerialMessanger
{
  public:
    SerialMessanger();
    SerialMessanger(byte *header,byte *footer,byte *hanshake);
    byte *header;
    byte *footer;
    byte *handshake;
    void sendMessage(Message);
    Message readMessage();
    void registerMessageHandler(short messageId, int messageLength, handler)
  private:
    void init(byte *header,byte *footer,byte *hanshake);
};

#endif