#!/usr/bin/python

import paho.mqtt.client as mqtt
import ConfigParser
import os
import re
import logging
import argparse
import time

version="0.01"

# command line args
parser = argparse.ArgumentParser(description='Client for the Remote MQTT command application, aka the rmc')
parser.add_argument('-c', '--config', default='/home/pi/rmcserver/rmciserver.conf', nargs='?', help='Configuration file location, default: /home/pi/rmcserver/rmcserver.conf')
parser.add_argument('-V', '--version', action='store_true', help='Show the version of rmc')

args = parser.parse_args()

# show version
if args.version is True :
  print "rmc version: "+version
  quit()

# we need config file or we will die
if os.path.isfile(args.config) is False:
  print "Config file doesn't exist, exiting."
  quit()

# Config file
config = ConfigParser.ConfigParser(allow_no_value=True)
config.read(args.config)

# Setup logging
log = logging.getLogger('rmcserver')
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


  #push time in unix ttime

  if entity == "time" and p[0] == "now" :
    client.publish("/pi/m/c/time",int(time.time())+3600)


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

