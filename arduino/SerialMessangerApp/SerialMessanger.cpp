#include "Arduino.h"
#include "SerialMessanger.h"

SerialMessanger::SerialMessanger()
{
  byte aheader[] = "HEAD";
  byte afooter[] = "FOOT";
  byte ahandshake[] = "";
  init(aheader,afooter,ahandshake);
}

SerialMessanger::SerialMessanger(byte *aheader, byte *afooter, byte *ahandshake)
{
  init(aheader,afooter,ahandshake);
}

void SerialMessanger::init(byte *aheader, byte *afooter, byte *ahandshake)
{
  header = aheader;
  footer = afooter;
  handshake = ahandshake;
}

void SerialMessanger::sendMessage(Message message)
{
    
}

Message SerialMessanger::recieveMessage()
{

}