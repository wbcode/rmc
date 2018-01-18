### TO DO
#### UPDATE THE READ ME

### The begining
Project for my two upcoming monitors connected to raspberry pi:s. That I can execute remote commands using mqtt.  <br/>

More details will come.


Yes, I'm not a python programmer so the once that know what they are doing will cry.

Yes, You can use this to execute commands that you shouldn't .ie wipe your system etc.


Plan is to add "Alexa" or "Okey Google" support to command the monitors.



### On rasberry:
```
pip install paho-mqtt
sudo apt install xdotool
```

### MQTT
Add websocket listerner to mosquitto:
```
cat /etc/mosquitto/conf.d/websocket.conf
```
```
listener 1883
listener 1884
protocol websockets
```

### Add service for client
```
cd rmc
chmod 755 rmc.py
sudo cp lib/systemd/system/rmc.service /lib/systemd/system
sudo systemctl enable rmc.service 
sudo systemctl start rmc
```

### Add service for server
cd rmc
chmod 755 rmc.py
sudo cp lib/systemd/system/rmcserver.service /lib/systemd/system
sudo systemctl enable rmcserver.service
sudo systemctl start rmc
```

