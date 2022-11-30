#!/usr/bin/python3

import paho.mqtt.client as mqtt
import configparser
import os
import re
import logging
import argparse

version="0.10 python3"

# command line args
parser = argparse.ArgumentParser(description='Client for the Remote MQTT command application, aka the rmc')
parser.add_argument('-c', '--config', default='/home/pi/rmc/client/rmc.conf', nargs='?', help='Configuration file location, default: /home/pi/rmc/client/rmc.conf')
parser.add_argument('-V', '--version', action='store_true', help='Show the version of rmc')

args = parser.parse_args()

# show version
if args.version is True :
  print("rmc version: "+version)
  quit()

# we need config file or we will die
if os.path.isfile(args.config) is False:
  print("Config file doesn't exist, exiting.")
  quit()

# Config file
config = configparser.ConfigParser(allow_no_value=True)
config.read(args.config)

# Setup logging
log = logging.getLogger('rmc')
hdlr = logging.FileHandler(config.get('general','log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr)
log.setLevel(logging.DEBUG)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(self, client, userdata, rc):
  log.info("Connected to "+ config.get('general','server') +":" +config.get('general','port') +" with result code "+str(rc))
  # Subscribing in on_connect() means that if we lose the connection and
  # reconnect then subscriptions will be renewed.
  for k,v in config.items("subscribe") :
    self.subscribe(k)
    log.info("Subscribing to: "+k)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
  log.debug("Message recived on topic:"+str(msg.topic)+" with msg: "+msg.payload.decode())
  entity = str(msg.topic).split('/')[4]
  p = msg.payload.decode().strip().split(' ')

  #youtube special to move from browser to tv mode, find a way to do this in a better way... dont hard code values...

  if entity == "www" and p[0] == "start"  and config.get('specials','youtube_tv') == 'true':
    r = re.compile(r"https:\/\/www.youtube.com\/watch\?v=(.*)")
    for i in range(1,len(p)) :
      m = r.search(p[i])
      if m is not None :
        #p[i] = "https://www.youtube.com/tv#/watch?v="+m.group(1)
        p[i] = "https://www.youtube.com/embed/"+m.group(1)+"?autoplay=1"
   #end youtube special ,maybe move this to function if there will be many off these... or create hooks...

 #youtube special to move from browser to tv mode, find a way to do this in a better way... dont hard code values...
  if entity == "www" and p[0] == "start"  and config.get('specials','twitch_tv') == 'true':
    r = re.compile(r"https://www.twitch.tv/(.*)")
    for i in range(1,len(p)) :
      m = r.search(p[i])
      if m is not None :
      #p[i] = "https://www.youtube.com/tv#/watch?v="+m.group(1)
        p[i] = "http://twitchtheater.tv/"+m.group(1)
 #end youtube special ,maybe move this to function if there will be many off these... or create hooks...
  #macro special get the line and fill the incomming messages

  if entity == "macro" and config.has_option('macro',p[0]):
    p[0] = config.get('macro',p[0])
    sc = str(config.get('commands',p[0])).split(':')
    log.debug("Macro: " +p[0] )
    entity = sc[0]
    p[0] = sc[1]

   #end macro special


  r = re.compile(r"(\w+):(\w+):([\s*|\w*]+):(.*)")
  for k,v in config.items("commands") :
    m = r.search(v)
    if entity == m.group(1) and p[0] == m.group(2):
        text = m.group(3)
        cmd = m.group(4)
        if len(p) > 1 : #find an replace all $1 $2 etc with command from mqtt payload
            for i in range(1,len(p)) :
                cmd = cmd.replace('$$'+str(i),p[i])
                log.debug("Replacing $$"+str(i)+" with " + p[i])
        os.system(cmd)
        client.publish(config.get('general','text_topic'),text)
        log.info("Executing: "+ cmd)



client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

log.debug("Connecting to mqtt server ip: "+ config.get('general','server') +" port :" +config.get('general','port') )
client.connect(config.get('general','server'), port=int(config.get('general','port')),keepalive=int(config.get('general','keepalive')))

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
