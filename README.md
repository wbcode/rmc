Rroject for my two upcoming monitors connected to raspberry pi:s. That I can execute remote commands. More details will come.

Yes, I'm not a python programmer so the once that know what they are doing will cry.
Yes, You can use this to execute commands that you shouldn't .ie wipe your system etc.





On rasberry:
pip install paho-mqtt
sudo apt install xdotool

Add websocket listerner to mosquitto:
cat /etc/mosquitto/conf.d/websocket.conf
listener 1883
listener 1884
protocol websockets
