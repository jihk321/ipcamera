import socket, requests
from requests.auth import HTTPDigestAuth
import cv2
import numpy as np
import time, os, datetime
import torch
import asyncio
import paho.mqtt.client as mqtt

ip = ['221.159.47.49:10183', '192.168.0.45']
url = 'http://' + ip[1] + '/stw-cgi'
page = ['/system.cgi?', '/eventsources.cgi?']

login_info = ['admin', 'goback2022']
# param = {'msubmenu' : 'date',
#             'action' : 'view'}

# param = {'msubmenu' : 'videoanalysis',
#             'action' : 'view', 'Channel' : 0}

param = {'msubmenu' : 'peoplecount',
            'action' : 'view'}

res = requests.get(url= url+page[0], params=param, auth=HTTPDigestAuth('admin', 'goback2022') )
# print(res.content)

device_info = requests.get(url= url+page[0], params= {'msubmenu' : 'deviceinfo', 'action' : 'view'} , auth= HTTPDigestAuth(login_info[0], login_info[1])).text
device_info = device_info.split('\r\n')
del device_info[-1]
device_data, device_values = [],[]
for i in device_info :
    pair = i.split('=')
    device_data.append(pair[0])
    device_values.append(pair[1])

device_info = dict(zip(device_data,device_values))


print(device_info)

async def save_img(file,img):
    cv2.imwrite(file,img)
    await asyncio.sleep(1)
    
def mqtt_publish():
    client = mqtt.Client()
    client.connect('localhost', 1883)
    client.loop_start()

    return client
def load_model():
    model = torch.hub.load(r'C:\Users\goback\Downloads\yolov5-master\yolov5-master', 'custom', path='h3.pt', source='local',force_reload=True)
    model.conf = 0.6
    return model

def event_end():
    e = False
    
    # while e == False:
    res = requests.get(url = url+page[0], params= {'msubmenu': 'eventlog', 'action':'view', 'Type' : 'MotionDetection'}, auth= HTTPDigestAuth(login_info[0], login_info[1])).text
    total = res.split('\r\n')
    del total[-1]

    total = total[0].split('=')[1]

    check = int(total)%2
    # if int(total)%2 == 0: 
        # print(int(total)%2)
    #     e = True
    return check

def writevideo(ip,id,pw):
    e = 1

    currentTime = datetime.datetime.now()
    os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;udp'
    video_capture = cv2.VideoCapture(f'rtsp://{id}:{pw}@{ip}/profile2/media.smp')
    fps = 1
    
    fileName = str(currentTime.strftime('%Y-%m-%d %H %M %S'))
    path = r'C:\Users\goback\Documents\ipcamera' + f'\\{fileName}.mp4'

    fourcc = cv2.VideoWriter_fourcc(*'h264')
    # width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    # height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # out = cv2.VideoWriter(path, fourcc, fps, (width,height))

    print('writevideo', datetime.datetime.now())
    tok = 0
    while True :
        # video_capture = cv2.VideoCapture(f'rtsp://{id}:{pw}@{ip}/profile2/media.smp')
        ret, frame = video_capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_RGBA2GRAY)

        tick = datetime.datetime.today().second
        
        # out.write(gray)
        result = model(gray)
        if result.xyxy[0].shape[0] > 0 :
            # result.save(save_dir= r'C:\Users\goback\Documents\result')
            
            results = result.pandas().xyxy[0][['name','xmin','ymin','xmax','ymax']]

            # print(f'{now_time}_{human_num}_{device_name}')
            for num, i in enumerate(results.values):
                cv2.putText(frame, i[0], ((int(i[1]), int(i[2]))), cv2.FONT_HERSHEY_SIMPLEX, 2,(0, 0, 255), 3)
                cv2.rectangle(frame, (int(i[1]), int(i[2])), (int(i[3]), int(i[4])), (0, 0, 255), 3)
            
            if tick > tok : 
                save_path = r'C:\Users\goback\Documents\result'
                save_name = str(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')) + '.jpg' 
                saves = save_path + '\\' + save_name 
                cv2.imwrite(saves, gray)

                human_num = result.xyxy[0].shape[0]
                now_time = datetime.datetime.now()
                device_name = device_info['DeviceName']
                mq.publish('/test', f'{now_time}_{human_num}_{device_name}', 1)

                tok = tick 
        
        if tok >= 59 : tok == 0 # 0~60초  
        # print(result)
        cv2.imshow("Frame", frame)

        k = cv2.waitKey(1) & 0xff
        if k == 27: break

        # e = event_end()
    video_capture.release()
    # out.release()
    cv2.destroyAllWindows()

def event_check() :
    path = r'C:\Users\goback\Documents\ftp'
    # video_capture = cv2.VideoCapture(f'rtsp://{id}:{pw}@{ip}/profile2/media.smp', cv2.CAP_FFMPEG)
    pre_num = len(os.listdir(path))
    # print(pre_num)
    now_num = pre_num

    while now_num == pre_num :
        now_num = len(os.listdir(path))
        # print(f'이전 : {pre_num} 현재 : {now_num}')
        # time.sleep(0.3)
    
    print('event_check', datetime.datetime.now())
    e = os.listdir(path)[-1].split('_')
    
def event(ip,id,pw):
    c = event_end()
    while c != 1 :
        print(c)
        c = event_end()
    print('event_check', datetime.datetime.now())
    

model = load_model()

mq = mqtt_publish()
# event('192.168.0.45','admin','goback2022')
# event_check('192.168.0.45','admin','goback2022')
# event_end()
writevideo('192.168.0.45','admin','goback2022')


mq.loop_stop()
mq.disconnect()