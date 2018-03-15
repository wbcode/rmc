/*

TAKE A MIN TO READ THIS!

rmc controller using mqtt to controll two raspberry pi:s that I use as display screens for twitch/youtube/photo:s etc.

NOTE: I manged to use some pins that will not allow you to upload the code to the arudino while it's connected to all the accessories. 

NOTE: Replace the mac address, client ip and server ip for the mqtt.

License: Beerware, Wineware or Whiskeyware

https://github.com/wbcode/rmc

*/

#include <SPI.h>
//#include <UIPEthernet.h> /*You can use a ENC28J60 module but it will be unstable, frezzening the arudino anything from startup to 2 days*/
#include <Ethernet.h>
#include <PubSubClient.h>
#include <SSD1306Ascii.h>
#include <SSD1306AsciiSpi.h>


/*
 * SCLK : SCK, CLK.
 * MOSI : SIMO, SDO, DO, DOUT, SO, MTSR.
 * MISO : SOMI, SDI, DI, DIN, SI, MRST.
 * SS : nCS, CS, CSB, CSN, nSS, STE, SYNC.
 */


/* Connecting things up
 *  OLED  ETH  165   ARD    POT1    POT2  BTN1  BTN2
 *  VCC   X     X    3.3V     X       X     X     X
 *  GRD   GRD  GRD   GRD     GRD     GRD   GRD   GRD  
 *  CS    X     X    9        X       X     X     X
 *  X     SS    X    10       X       X     X     X
 *  X     RST   X    RST      X       X     X     X
 *  RST   X     X    8        X       X     X     X
 *  DO    CK    X    13       X       X     X     X
 *  D1    MO    X    11       X       X     X     X
 *  X     MI    X    12       X       X     X     X
 *  DC    X     X    7        X       X     X     X
 *  X     X     1    2        X       X     X     X
 *  X     X     2    5        X       X     X     X
 *  X     X     9    4        X       X     X     X
 *  X     X    15    3        X       X     X     X
 *  X    VCC   VCC   5V      VCC     VCC   VCC   VCC
 *  X     X     X    A0      OTA      X     X     X
 *  X     X     X    A1       X      OTA    X     X
 *  X     X     X    A2       X       X    OTA    X
 *  X     X     X    A3       X       X     X    OTA
 */


// pin definitions
#define OLED_DC   7 
#define OLED_CS   9 /* SS */
#define OLED_CLK  13 /*SCLK*/
#define OLED_DATA 11 /*MOSI*/
#define OLED_RST   8
#define ETH_CS 10 /*SS*/

#define HC165_L 2 /* pin 1*/
#define HC165_CLK_E 3 /* pin 15*/
#define HC165_DIN 4 /* pin 9*/
#define HC165_CLK 5 /* pin 2*/




// Update these with values suitable for your hardware/network.
byte mac[]    = {  0xDE, 0xEA, 0xBA, 0xFE, 0xFE, 0xED };
/*server and client ip moved from here to save global memory*/

SSD1306AsciiSpi oled;

unsigned long unixtime = 0;
unsigned long gotunixtime = 0;
unsigned long last_clock = 0;
unsigned long lasttimerequest = 0;
unsigned long time_texted = 0;
boolean updatetime = false;
boolean texted = false;
byte lastdigA2= HIGH;
byte lastdigA3= HIGH;
int volumeR, volumeL=0;
byte lastbyte =0;

void callback(char* topic, byte* payload, unsigned int length) {
  char p[length];
  memcpy(p,(char *) payload, length);
  if (!strcmp(topic,"/pi/m/c/time")) {
     gotunixtime = millis();
     last_clock = gotunixtime;
     unixtime = strtoul(p,NULL,10);
     updatetime=true;
     oled_display_time();
  } else if (!strcmp(topic,"/pi/m/c/text")) {
      texted = true;
      time_texted =  millis();
      oled.clear(0,127,0,0);
      oled.setCursor((123 - (length*5))/2,0);
      oled.println(p);
  }    
  //free(p);
}

EthernetClient ethClient;
PubSubClient client;

long lastReconnectAttempt = 0;

boolean reconnect() {
  if (client.connect("controller")) {;
    client.subscribe("/pi/m/c/#");
    delay(2500); //needed to be able to get the time
    client.publish("/pi/m/s/time","now");
    // ... and resubscribe
  }
  return client.connected();
}

void oled_display_time() {
     unsigned long t,m,h,s =0;
     char st[9] = {'\0'};
     t=unixtime + ((last_clock-gotunixtime)/1000);
     s = t % 60;
     t /=60;
     m = t % 60;
     t /=60;
     h = t % 24;
     sprintf(st,"%02lu:%02lu:%02lu",h,m,s);
     //oled.set1X();
     oled.setCursor(28,3);
     oled.println("- WORLDRULER -");
     oled.setCursor(46,4);
     oled.println(st);
     sprintf(st,"L: %3d %%\0",volumeL);
     oled.setCursor(0,7);
     oled.print(st);
     oled.setCursor(80,7); 
     sprintf(st,"R: %3d %%\0",volumeR);
     oled.print(st);
}

void readInput() {
  digitalWrite(HC165_L,LOW);
  delayMicroseconds(5);
  digitalWrite(HC165_L,HIGH);
  delayMicroseconds(5);
   
  digitalWrite(HC165_CLK,HIGH);
  digitalWrite(HC165_CLK_E,LOW);
  byte in = shiftIn(HC165_DIN, HC165_CLK,MSBFIRST);
  digitalWrite(HC165_CLK_E,HIGH);

  if (in!=lastbyte) {
    lastbyte=in;
    switch(in) {
      
      case B00000001:
         client.publish("/pi/m/1/macro","1");
      break;
      case B00000010: 
         client.publish("/pi/m/1/macro","2");
      break;
      case B00000100: 
         client.publish("/pi/m/1/macro","3");
      break;
      case B00001000: 
         client.publish("/pi/m/1/macro","4");
      break;
      case B00010000: 
         client.publish("/pi/m/2/macro","1");
      break;
      case B00100000: 
         client.publish("/pi/m/2/macro","2");
      break;
      case B01000000: 
         client.publish("/pi/m/2/macro","3");
      break;
      case B10000000: 
         client.publish("/pi/m/2/macro","4");
      break;
     }
    }
    byte digA2 = digitalRead(A2);
    byte digA3 = digitalRead(A3);
     
    if((digitalRead(A2) == LOW) && digA2 != lastdigA2) {
      client.publish("/pi/m/1/macro","5");
    }

    if((digitalRead(A3) == LOW) && digA3 != lastdigA3) {
      client.publish("/pi/m/2/macro","5");
    }
    lastdigA2 = digA2;
    lastdigA3 = digA3;
    
}

void readVolume() {
  int value = analogRead(A1);          
  value = map(value, 0, 1023, 0, 100);
  if (!(volumeR == value || volumeR+1 == value  || volumeR-1 == value )) {
    volumeR = value;
    char vcmd[8]= {"\0"};
    sprintf(vcmd,"set %d",volumeR);
    client.publish("/pi/m/2/volume",vcmd);
  }
  value = analogRead(A0);          
  value = map(value, 0, 1023, 0, 100);
  if (!(volumeL == value || volumeL+1 == value  || volumeL-1 == value )) {
    volumeL = value;
    char vcmd[8]= {"\0"};
    sprintf(vcmd,"set %d",volumeL);
    client.publish("/pi/m/1/volume",vcmd);
  }
}

void setup()
{

  pinMode(ETH_CS, OUTPUT); /*Make sure that SS on arduino is set to output*/
  pinMode(OLED_CS, OUTPUT);
  pinMode(HC165_L, OUTPUT);
  pinMode(HC165_CLK_E, OUTPUT);
  pinMode(HC165_DIN, INPUT);
  pinMode(HC165_CLK, OUTPUT);
  pinMode(A2, INPUT_PULLUP);
  pinMode(A3, INPUT_PULLUP);
  
 

  /* IP for server and client*/
  IPAddress ip(10, 10, 11, 43);
  IPAddress server(10, 10, 11, 101);

  oled.begin(&Adafruit128x64, OLED_CS, OLED_DC,OLED_RST);
  oled.setFont(Adafruit5x7);
  oled.clear();
  oled.println("Booting...");
 
  Ethernet.begin(mac, ip);
  
  oled.println(Ethernet.localIP());

  char cmac[18];
  sprintf(cmac, "%2X:%2X:%2X:%2X:%2X:%2X", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  
  oled.println(cmac);
  oled.setCursor(20,6);
  oled.print(".. by wbcode ..");
  delay(2500);

  client.setClient(ethClient);
  client.setServer(server, 1883);
  client.setCallback(callback);
  
  lastReconnectAttempt = 0;

  oled.clear();
  oled.setCursor(28,3);
  oled.println("- WORLDRULER -");
  //Serial.begin(115200);
}

void loop()
{
   
   long now = millis();
   
   if (!client.connected()) {
    if (now - lastReconnectAttempt > 5000) {
      lastReconnectAttempt = now;
      // Attempt to reconnect
      if (reconnect()) {
        lastReconnectAttempt = 0;
      }
    }
  } else {
    // Client connected
    client.loop();

      /*Clock update on oled*/
    if (( now - last_clock) > 1000 && gotunixtime !=0) {
      last_clock=millis();
      oled_display_time();
      if (texted && (millis()- time_texted > 5000)) {
        oled.clear(0,127,0,0);
      }
    }
    /*sync clock every min*/
    if(( now - gotunixtime) > 60000  && (now - lasttimerequest) > 5000 ) {
      client.publish("/pi/m/s/time","now");
      updatetime = false;
      lasttimerequest = now;
    }
    /*Check input but every 100ms*/
    if (( now - last_clock) > 100) {
      readVolume();
      readInput();
    }  
  } 
 
}
