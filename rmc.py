#!/usr/bin/python

import paho.mqtt.client as mqtt
import ConfigParser
import os
import re
import logging


# Config file
config = ConfigParser.ConfigParser(allow_no_value=True)
config.read("/home/pi/mqtt/rmc.conf")

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
  log.debug("Message recived on topic:"+msg.topic+" with msg: "+msg.payload)
  entity = msg.topic.split('/')[4]
  p = str(msg.payload).strip().split(' ')
  
  #youtube special to move from browser to tv mode
  if entity == "www" and p[0] == "start" :
    r = re.compile(r"https:\/\/www.youtube.com\/watch\?v=(\w+)")
    for i in range(1,len(p)) : 
	  m = r.search(p[i])
	  if m is not None :
	    p[i] = "https://www.youtube.com/tv#/watch?v="+m.group(1)
   #end youtube special ,maybe move this to function if there will be many off these... or create hooks...
    
    
  r = re.compile(r"(\w+):(\w+):(.*)")
  for k,v in config.items("commands") :
    m = r.search(v)
    if entity == m.group(1) and p[0] == m.group(2):
        cmd = m.group(3)
        if len(p) > 1 : #find an replace all $1 $2 etc with command from mqtt payload
		    for i in range(1,len(p)) : 
			    cmd = cmd.replace('$'+str(i),p[i])
			    log.debug("Replacing $"+str(i)+" with " + p[i])
		
        os.system(cmd)
        log.info("Executing: "+ cmd)

		
		
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

log.debug("Connecting to mqtt server ip: "+ config.get('general','server') +" port :" +config.get('general','port') )
client.connect(config.get('general','server'), config.get('general','port'), int(config.get('general','port')))

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
