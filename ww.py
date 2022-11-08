import re
import requests
from requests.auth import HTTPDigestAuth

sources = ['rtsp://root:root@220.82.139.41:554/cam0_0','rtsp://admin:goback2022@192.168.0.45:554/profile2/media.smp']


for index, letter in enumerate(sources):
    if 'cam0_0' in letter : device_info ='lpr'
    else :
        letter = letter.split('//')[1].split('/')[0]
        id = letter.split(':')[0]
        pw = letter.split(':')[1].split('@')[0]
        ip = letter.split(':')[1].split('@')[1]
        port = letter.split(':')[2]
        urls = f'http://{ip}:{port}/stw-cgi/system.cgi?'
        device_info = requests.get(url=urls, params= {'msubmenu' : 'deviceinfo', 'action' : 'view'}, auth=HTTPDigestAuth(id,pw))
        if device_info.status_code == 200 or device_info.status_code == 201:
            device_info = device_info.text.split('\r\n')
            del device_info[-1]
            device_data, device_values = [],[]
            for i in device_info :
                pair = i.split('=')
                device_data.append(pair[0])
                device_values.append(pair[1])

            camera_device = dict(zip(device_data,device_values))
            device_info = camera_device['DeviceName']
    print(device_info)