import cv2
import os, datetime

class capture():
    def __init__(self,ip,id,pw,rport,):
        self.ip = ip
        self.id = id
        self.pw = pw
        self.rport = rport
        self.url = f'rtsp://{id}:{pw}@{ip}:{rport}/cam0_0'
        # self.url = f'rtsp://{self.id}:{self.pw}@{self.ip}:{self.rport}/profile2/media.smp'
    def video(self):
        cap = cv2.VideoCapture(self.url)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = 15
        print(width,height,fps)

        t = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.avi'
        if not os.path.isdir('C:\Video') : os.mkdir('C:\Video')
        path = os.path.join('C:\Video',t)
        out = cv2.VideoWriter(path, fourcc, fps, (width,height))

        while True:
            _, frame = cap.read()
            out.write(frame)
            
            frame = cv2.resize(frame, dsize=(0,0), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            cv2.imshow('recoding',frame)

            k = cv2.waitKey(1) & 0xff
            if k == 27: break

        cap.release()
        out.release()
        cv2.destroyAllWindows()

test = capture('192.168.0.48','root','root','554')
# test = capture('192.168.0.45','admin','goback2022','554')
test.video()