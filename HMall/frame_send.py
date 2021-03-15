# -*- coding: utf-8 -*-
import cv2
import socket
import struct
import pickle
import time
import datetime
import os

# 서버 주소
ip = '192.168.0.69' 
port = 50001 

# 소켓 객체를 생성 및 연결
while True:
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        print('연결 성공')
        break
    except Exception as e:
        print('연결 실패 재시도')
        print(e)
        time.sleep(5)
        continue
   
while True:
    # file_list 불러오기
    now = datetime.datetime.now()
    today = now.strftime('%Y%m%d')
    
    file_path = os.path.join(os.getcwd(), str(today))
    file_list = os.listdir(file_path)
    full_path = file_path + '/' + file_list[0]
        
    # 동영상 선택
    cap = cv2.VideoCapture(full_path)
    print(full_path)
    
    # 크기 지정
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640) # 가로
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) # 세로
    
    # 인코드 파라미터
    # 캡쳐 품질 설정
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 100]
    
    #프레임전송
    while cap.isOpened():
        #fps에 따라 sleep 변경 필요
        time.sleep(0.066666667)
        ret, frame = cap.read() # 카메라 프레임 읽기
        
        if frame is None:
            break
   
        # 프레임 인코딩
        result, frame = cv2.imencode('.jpg', frame, encode_param)
           
        # 프레임을 직렬화화하여 binary file로 변환
        data = pickle.dumps(frame, 0) 
        size = len(data)
        # 프레임 크기 출력
        # print("Frame Size : ", size)
    
        # 데이터(프레임) 전송
        client_socket.sendall(struct.pack(">L", size) + data)
        
  
    # 메모리를 해제
    cap.release()
    
    # 전송 끝난 파일 삭제
    if os.path.isfile(full_path):
        os.remove(full_path)
    
