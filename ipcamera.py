import time
import requests
from requests.auth import HTTPDigestAuth
import cv2, datetime, os, asyncio
import numpy as np
import torch 
import paho.mqtt.client as mqtt

class detectmodel():
    def __init__(self) :
        self.model = torch.hub.load(r'C:\Users\goback\Downloads\yolov5-master\yolov5-master', 'custom', path='people.pt', source='local',force_reload=True)
        self.model.conf = 0.6
        self.model.classes = [0]

    def detection(self,img):
        result = self.model(img)
        return result
det = detectmodel()
class IpCamera:

    def __init__(self,ip, hport ,rport ,id, pw) :
        self.ip = ip
        self.id = id
        self.pw = pw
        self.hport = hport
        self.rport = rport
        self.url = f'http://{ip}:{hport}/stw-cgi/system.cgi?'
    
    def get_device(self):
        
        device_info = requests.get(url=self.url, params= {'msubmenu' : 'deviceinfo', 'action' : 'view'}, auth=HTTPDigestAuth(self.id,self.pw))
        if device_info.status_code == 200 or device_info.status_code == 201:
            device_info = device_info.text.split('\r\n')
            del device_info[-1]
            device_data, device_values = [],[]
            for i in device_info :
                pair = i.split('=')
                device_data.append(pair[0])
                device_values.append(pair[1])

            self.device_info = dict(zip(device_data,device_values))
            print(self.device_info['DeviceName'], 'Is Running~~~~')
        else : print('연결안됨')
        # print(self.device_info, 'running~')

        # return device_info

    def mqtt_publish(self):
        client = mqtt.Client()
        client.connect('localhost', 1883)
        client.loop_start()
        self.mq = client
        # return client

    # def save_img():

    def streaming(self,device):
        currentTime = datetime.datetime.now()
        os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;udp'
        if device == 'hanwha' : 
            video_capture = cv2.VideoCapture(f'rtsp://{self.id}:{self.pw}@{self.ip}:{self.rport}/profile2/media.smp')
            device_name = self.device_info['DeviceName']
        elif device == 'flex' : 
            video_capture = cv2.VideoCapture(f'rtsp://{self.id}:{self.pw}@{self.ip}:{self.rport}/cam0_0')
            device_name = 'lpr'

        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH,960)
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT,540)
        # video_capture.set(cv2.CAP_PROP_POS_FRAMES,30)
        fps = 1
        fileName = str(currentTime.strftime('%Y-%m-%d %H %M %S'))
        path = r'C:\Users\goback\Documents\ipcamera' + f'\\{fileName}.mp4'
        fourcc = cv2.VideoWriter_fourcc(*'h264')
        # width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        # height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # out = cv2.VideoWriter(path, fourcc, fps, (width,height))

        # print('running')
        tok = 0
        while True :
            try:
                ret, frame = video_capture.read()
                gray = cv2.cvtColor(frame, cv2.COLOR_RGBA2GRAY)
                img_copy = frame.copy()
            except: 
                print('이미지 없음 재접속')
                video_capture.release()
                time.sleep(2)
                video_capture = cv2.VideoCapture(f'rtsp://{self.id}:{self.pw}@{self.ip}:{self.rport}/profile2/media.smp')
                continue

            tick = datetime.datetime.today().second
        
            # out.write(gray)
            result = det.detection(gray)
            if result.xyxy[0].shape[0] > 0 :
                start = time.time()
                # result.save(save_dir= r'C:\Users\goback\Documents\result')
                
                results = result.pandas().xyxy[0][['name','xmin','ymin','xmax','ymax']]

                # print(f'{now_time}_{human_num}_{device_name}')
                for num, i in enumerate(results.values):
                    cv2.putText(frame, i[0], ((int(i[1]), int(i[2]))), cv2.FONT_HERSHEY_SIMPLEX, 2,(0, 0, 255), 3)
                    cv2.rectangle(frame, (int(i[1]), int(i[2])), (int(i[3]), int(i[4])), (0, 0, 255), 3)
                
                if tick > tok : 
                    human_num = result.xyxy[0].shape[0]
                    now_time = datetime.datetime.now()
                    
                    self.mq.publish('/test', f'{now_time},{human_num},{device_name}', 1)

                    save_path = r'C:\Users\goback\Documents\result'
                    save_name = str(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')) + '_' + str(human_num) 
                    saves = save_path + '\\' + save_name 
                    cv2.imwrite(saves + '.jpg', img_copy)
                    f = open(saves + '.txt' ,'w')
                    for index, data in enumerate(results.values):
                        text = f'{str(data[0])} {data[1]} {data[2]} {data[3]} {data[4]} \n'
                        f.write(text)
                    f.close()
                    # acc = result.pandas().xyxy[0][['confidence']].values
                    # print(str(acc*100))
                    tok = tick 
                    # print(time.time() - start)
            
            if tok >= 59 : tok = 0 # 0~60초  
            # print(result)
            frame = cv2.resize(frame, dsize=(0,0), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            cv2.imshow(device_name, frame)

            k = cv2.waitKey(1) & 0xff
            if k == 27: break

            # e = event_end()
        video_capture.release()
        # out.release()
        cv2.destroyAllWindows()
        print('exit')
        self.mq.loop_stop()
        self.mq.disconnect()

    def get_date(self):
        os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;udp'
        video_capture = cv2.VideoCapture(f'rtsp://{self.id}:{self.pw}@{self.ip}:{self.rport}/profile2/media.smp')

        tok = 0
        while True :
            try:
                ret, frame = video_capture.read()
                gray = cv2.cvtColor(frame, cv2.COLOR_RGBA2GRAY)
            except: 
                print('이미지 없음 재접속')
                video_capture.release()
                time.sleep(2)
                video_capture = cv2.VideoCapture(f'rtsp://{self.id}:{self.pw}@{self.ip}:{self.rport}/profile2/media.smp')
                continue

            tick = datetime.datetime.today().second
            
            if tick > tok : 
                save_path = r'C:\Users\goback\Documents\datas'
                save_name = str(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')) + '.jpg' 
                saves = save_path + '\\' + save_name 
                cv2.imwrite(saves, frame)
                tok = tick 

            if tok >= 59 : tok = 0 # 0~60초  
            # print(result)
            frame = cv2.resize(frame, dsize=(0,0), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            cv2.imshow(self.device_info['DeviceName'], frame)

            k = cv2.waitKey(1) & 0xff
            if k == 27: break

            # e = event_end()
        video_capture.release()
        # out.release()
        cv2.destroyAllWindows()
        print('exit')


from multiprocessing import Process

def cam1():
    first = IpCamera(ip='192.168.0.45', hport=80, rport=554 ,id='admin', pw='goback2022')
    first.get_device()
    first.mqtt_publish()
    first.streaming(device='hanwha')
def cam2():
    two = IpCamera(ip='221.159.47.49', hport=10183, rport=10557, id='admin', pw='goback@2021')
    two.get_device()
    two.mqtt_publish()
    two.streaming(device='hanwha')
def cam3():
    ss = IpCamera(ip='220.82.139.41', hport=80, rport=554, id='root', pw='root')
    ss.mqtt_publish()
    ss.streaming(device='flex')

def get_pic():
    g = IpCamera(ip='192.168.0.45', hport=80, rport=554 ,id='admin', pw='goback2022')
    g.get_device()
    g.get_date()

if __name__ == '__main__':
    p1 = Process(target=cam1)
    # p2 = Process(target=cam2)
    p3 = Process(target=cam3)
    p1.start()
    # p2.start()
    p3.start()

# r = requests.get(url='http://192.168.0.45:80/stw-cgi/system.cgi?', params= {'msubmenu' : 'deviceinfo', 'action' : 'view'}, auth=HTTPDigestAuth('admin','goback2022'))
