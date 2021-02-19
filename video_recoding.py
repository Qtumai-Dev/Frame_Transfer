# -*- coding: utf-8 -*-
import cv2
import time
import os
import threading
import numpy as np
from PIL import Image

import sys
import datetime
import pandas as pd
from urllib.request import urlopen
import platform

class video_recode(threading.Thread):
    
    def __init__(self, dvr_num, dvr_ip, dvr_ch, open_t, close_t):
        threading.Thread.__init__(self, name = str(dvr_num) + '_' + str(dvr_ch))
        #self.name = str(dvr_num) + str(dvr_ch)
        self.dvr_num = dvr_num
        self.dvr_ip = dvr_ip
        self.dvr_ch = dvr_ch
        self.open_t = open_t
        self.close_t = close_t
        
        
        o_sys = platform.system()
        if o_sys == 'Windows':
            self.opt = '-n'
        else:
            self.opt = '-c'
            
        self.start_time = []
        self.fr_count = 0
        print('%s Recoding program start' %self.name)
        
    # 현재시간 리턴
    def log_time(self):
        self.n_time = datetime.datetime.now()
        return self.n_time
           
    # 인터넷 연결 확인
    def check_internet(self):
        try:
            urlopen('http://216.58.192.142', timeout = 1)
            print('conn internet')
            return True
        except:
            print('no internet')
            return False
        
    # 라우터 연결 확인    
    def check_router_conn(self):
        router = '192.168.0.1'
        response = os.system('ping ' + self.opt + ' 1 ' + router)
        if response == 0:
            self.net_stat = 'router_online'
            return self.net_stat
        else:
            self.net_stat = 'router_offline'
            return self.net_stat
    
    # DVR 연결 확인
    def check_dvr_conn(self):
        response = os.system('ping ' + self.opt + ' 1 ' + self.dvr_ip)
        if response == 0:
            self.net_stat = 'dvr_online'
            return self.net_stat
        else:
            self.net_stat = 'dvr_offline'
            return self.net_stat
        
    def check_network(self):
        netstat = self.check_dvr_conn()
        if netstat == 'dvr_offline':
            netstat1 = self.check_router_conn()
            if netstat1 == 'router_offline':
                return netstat1
            else:
                return netstat
    
    # 운영 시간 설정 필!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def working_hours(self):
        now_t = datetime.datetime.now()
        open_t = datetime.datetime(now_t.year, now_t.month, now_t.day, self.open_t[0], self.open_t[1], 0)
        close_t = datetime.datetime(now_t.year, now_t.month, now_t.day, self.close_t[0], self.close_t[1], 0)
        self.shutdown = close_t.strftime('%H%M')
        if open_t < now_t:
            if close_t > now_t:
                return True
            else:
                return False
            
    # 녹화 시작 로그작성        
    def start_log(self, v_file_name):
        self.recode_log = pd.read_csv(self.log_path)
        idx = self.log_len()   
        self.recode_log.loc[idx] = [self.log_time(), self.dvr_num, self.dvr_ch, v_file_name, 'rec_start', None, None, None]
        self.recode_log.to_csv(self.log_path, index = False)
    
    # 로그 인덱스 추출
    def log_len(self):
        recode_log = pd.read_csv(self.log_path)
        idx = len(recode_log) 
        return idx
    
    # 로그 파일 생성     
    def make_log(self):
        self.recode_log = pd.DataFrame(index = range(0, 0), 
                          columns = ['time', 'dvr_num', 'dvr_ch', 'file_name', 'happened', 'rec_frame', 'send_frame', 'error'])

        self.now = datetime.datetime.now()
        self.today = self.now.strftime('%Y%m%d')
        self.log_path = './log/' + str(self.dvr_num) + '_' + self.dvr_ch + '/' + self.today + '.csv'
        if not os.path.exists('./log/'):
            os.mkdir('./log/')
        if not os.path.exists('./log/' + str(self.dvr_num) + '_' + self.dvr_ch):
            os.mkdir('./log/' + str(self.dvr_num) + '_' + self.dvr_ch)    
        # 로그 파일 없으면 생성
        if not os.path.exists(self.log_path):    
            self.recode_log.to_csv(self.log_path, index = False)
    
    # 파일 저장 디렉토리 생성         
    def make_save_path(self):
        self.name = os.path.join(os.getcwd(), 'save_video', str(self.dvr_num), self.dvr_ch, str(self.today))
        print("All video saved in dir:", self.name)
        if not os.path.exists('./save_video/'):
            os.mkdir('./save_video/')
        if not os.path.exists('./save_video/' + str(self.dvr_num)):
            os.mkdir('./save_video/' + str(self.dvr_num))
        if not os.path.exists('./save_video/' + str(self.dvr_num) + '/' + self.dvr_ch):
            os.mkdir('./save_video/' + str(self.dvr_num) + '/' + self.dvr_ch)    
        if not os.path.exists(self.name):
            os.mkdir(self.name)
    
    def video_info(self):
        self.acc = 'qtumai'
        self.pw = 'qtumai123456'
        self.add = 'rtsp://' + self.acc + ':' + self.pw + '@' + self.dvr_ip + ':554/' + self.dvr_ch
        cap = cv2.VideoCapture(self.add)
        #cap = cv2.VideoCapture('rtsp://qtumai:qtumai123456@192.168.0.59:554/stream_ch00_1')
        self.width = int(cap.get(3))
        self.height = int(cap.get(4))
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.video_codec = cv2.VideoWriter_fourcc(*'DIVX')
        
        ret, frame = cap.read()
        self.hei, self.wid, self.channel = frame.shape
        
            
    def create_blur(self, hei, wid, channel):
        data = []
        for i in range(60):
            p1 = i * i
            p2 = i * i
            p3 = i * i
            item = [p1, p2, p3]
            data.append(item)
        _array = np.ones((hei, wid, 3), dtype=np.uint8)
        for col in range(hei):
            for row in range(wid):
                _array[col, row] = data[row % 60]
        blur_img = Image.fromarray(_array, 'RGB')
        return blur_img
    
    # 레코딩 설정 및 실행
    def recoding_video(self):
        # 영상 정보 설정 계정, 암호, 프레임 높이, 너비, 초당프레임, 코덱
        blur_img = self.create_blur(self.hei, self. wid, self.channel)
        cap = cv2.VideoCapture(self.add)
        
        # 저장 파일 세팅
        v_file_name = str(self.log_time().strftime('%H%M'))
        video_file = os.path.join(self.name, v_file_name + ".avi")
        video_writer = cv2.VideoWriter(video_file, self.video_codec, self.fps, (self.wid, self.hei))
        
        try:
            # 녹화 루프 시작
            print('start_time', self.log_time())
            self.start_log(v_file_name)
            self.recode_log.to_csv(self.log_path, index = False)
            
            while cap.isOpened():
                self.fr_count += 1
                self.start_time.append(datetime.datetime.now())
                ret, frame = cap.read()
                
                # 캡쳐 됨
                if ret == True:
                    # 영업시간 종료시간파일까지 녹화 되면 종료 ---- 시간확인!!!!!!!!!!!!! 
                    # 영상 저장 파일 이름 = HHMM
                    if v_file_name == self.shutdown:
                        print('now is not working hour')
                        break
                    
                    # 녹화길이 설정 / 900frame 1분 / 15fps
                    if self.fr_count == 900:
                        v_file_name = self.log_time().strftime('%H%M')
                        video_file = os.path.join(self.name, v_file_name + ".avi")
                        print("Capture video saved location : {}".format(video_file))
                        video_writer = cv2.VideoWriter(video_file, self.video_codec, self.fps, (self.wid, self.hei))
                        
                        #종료 로그작성
                        self.recode_log = pd.read_csv(self.log_path)
                        idx = self.log_len()
                        self.recode_log.loc[idx] = [self.log_time(), self.dvr_num, self.dvr_ch, v_file_name, 'rec_finish', self.fr_count, None, None]
                        self.recode_log.to_csv(self.log_path, index = False)
                        print('finish_time', self.start_time[-1])
                        
                        # 카운팅 초기화
                        self.start_time = []
                        self.fr_count = 0
                        
                        # 시작로그 작성
                        self.start_log(v_file_name) 
                        print('start_time', self.log_time())
                    
                    #프레임 로그 작성 
                    try:
                        self.recode_log = pd.read_csv(self.log_path)
                    except:
                        print(self.log_path)
                    idx = self.log_len()
                    self.recode_log.loc[idx - 1, 'rec_frame'] = self.fr_count
                    self.recode_log.to_csv(self.log_path, index = False)
                    
                    # Write the frame to the current video writer
                    result = frame + blur_img
                    video_writer.write(result)
                
                # 로컬환경 일땐 gateway ping check로 변경
                # 캡쳐 안됨    
                else:
                    # 인터넷 연결 이상시 체크 후 로그 작성
                    online = self.check_internet()
                    if online == False:
                        netstat = self.check_network()
                        self.recode_log = pd.read_csv(self.log_path)
                        idx = self.log_len()
                        # offline
                        self.recode_log.loc[idx] = [self.log_time(), self.dvr_num, self.dvr_ch, self.now.strftime('%H%M'), 'rec_disconnect', self.fr_count, None, netstat]
                        self.recode_log.to_csv(self.log_path, index = False)
                        break     
                    
            video_writer.release()
            cap.release()
        except KeyboardInterrupt as e:
            video_writer.release()
            cap.release()
            sys.exit() 
                     
    def run(self):
        while True:
            if self.working_hours() == True:
                print('now is working hour')
                #self.get_dvr_info()
                self.make_log()
                self.make_save_path()
                self.video_info()
                
                self.recoding_video()
                time.sleep(10)
            else:
                print('wait working hour')
                time.sleep(60)
        
 ################################## main ##################################            

if __name__ == '__main__':
    
    def get_dvr_info(idx):
        df = pd.read_csv('./config.txt')
        dvr_num = df.loc[idx, 'dvr_num']
        dvr_ip = df.loc[idx, 'dvr_ip']
        dvr_ch = df.loc[idx, 'dvr_ch'] 
        return dvr_num, dvr_ip, dvr_ch
    
    config = pd.read_csv('./config.txt')
 ################################## 영업시간 설정 ##################################
    open_t = (18,13)
    close_t = (18,15)

    for i in config.index:
        dvr_num, dvr_ip, dvr_ch = get_dvr_info(i)
        main = video_recode(dvr_num, dvr_ip, dvr_ch, open_t, close_t)
        main.start()
        time.sleep(5)
