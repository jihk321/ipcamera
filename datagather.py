import cv2, datetime, pafy
import torch 

model = torch.hub.load(r'C:\Users\goback\Downloads\yolov5-master\yolov5-master', 'custom', path='h7.pt', source='local',force_reload=True)
model.conf = 0.5

url = 'https://youtu.be/3aas-RT7Ul8'
video = pafy.new(url)
best = video.getbest(preftype='mp4')
video_capture = cv2.VideoCapture(best.url)

video_capture.set(cv2.CAP_PROP_FRAME_WIDTH,960)
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT,540)
video_capture.set(cv2.CAP_PROP_POS_FRAMES,10)

tok = 0
while True :
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
            human_num = result.xyxy[0].shape[0]
            now_time = datetime.datetime.now()

            save_path = r'C:\Users\goback\Documents\result'
            save_name = str(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')) + '_' + str(human_num) + '.jpg' 
            saves = save_path + '\\' + save_name 
            cv2.imwrite(saves, gray)

            # acc = result.pandas().xyxy[0][['confidence']].values
            # print(str(acc*100))
            tok = tick 
            # print(time.time() - start)
    
    if tok >= 59 : tok = 0 # 0~60초  
    # print(result)
    frame = cv2.resize(frame, dsize=(0,0), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    cv2.imshow("Frame", frame)

    k = cv2.waitKey(1) & 0xff
    if k == 27: break

    # e = event_end()
video_capture.release()
# out.release()
cv2.destroyAllWindows()