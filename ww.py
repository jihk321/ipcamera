import re
import requests
from requests.auth import HTTPDigestAuth
import time,datetime
import paho.mqtt.client as mqtt
import asyncio

async def reconnection(mqtt) :
    mqtt_copy = mqtt
    loop = asyncio.get_event_loop()
    try :
        await loop.run_in_executor(mqtt_copy.reconnect())
        if mqtt.is_connected(): return mqtt_copy
    except : 
        print('false')
        return mqtt

client = mqtt.Client()

client.connect('localhost', 1883)
print(type(client))
client.loop_start()
time.sleep(1)

while True:
    time.sleep(1)
    ttt = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S')
    print(ttt)
    if client.is_connected() : 
        client.publish('/test', f'{datetime.datetime.now()}')
        time.sleep(1)
    else : 
        s = time.time()
        # client = asyncio.run(reconnection(client))
        client.connect_async('localhost', 1883)
        print(f'{time.time()- s}:.4f')