# -*- coding: utf-8 -*-
import numpy as np
import cv2
import time
import os
import random
import sys
import datetime

now = datetime.datetime.now()
today = now.strftime('%Y%m%d')
print(today)

# 저장 디렉토리 생성 YYYYmmdd
name = os.path.join(os.getcwd(), str(today))
print("ALl logs saved in dir:", name)
if not os.path.exists(name):
    os.mkdir(name)

# video input / output 사양
cap = cv2.VideoCapture('rtsp://qtumai:qtumai123456@192.168.0.59:554/stream_ch00_1')
width = int(cap.get(3))
height = int(cap.get(4))
print(str(width) + 'x' + str(height))
fps = cap.get(cv2.CAP_PROP_FPS)
video_codec = cv2.VideoWriter_fourcc(*'DIVX')

cur_dir = os.getcwd()

# 껍데기파일 생성
start = time.time()
video_file = os.path.join(name, now.strftime('%H%M') + ".avi")
video_writer = cv2.VideoWriter(video_file, video_codec, fps, (width, height))

# 녹화 루프 시작
while cap.isOpened():
    start_time = time.time()
    ret, frame = cap.read()
    if ret == True:
        #cv2.imshow("frame", frame)
        if time.time() - start > 60:
            start = time.time()
            
            now = datetime.datetime.now()
            video_file = os.path.join(name, now.strftime('%H%M') + ".avi")
            print("Capture video saved location : {}".format(video_file))
            video_writer = cv2.VideoWriter(video_file, video_codec, fps, (width, height))
            
        # Write the frame to the current video writer
        video_writer.write(frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break
    
cap.release()
#cv2.destroyAllWindows()
