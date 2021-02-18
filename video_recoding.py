# -*- coding: utf-8 -*-
import numpy as np
import cv2
import time
import os

import sys
import datetime
import pandas as pd
from urllib.request import urlopen
import platform

class video_recode:
    
    def __init__(self):
        print('Recoding program start')
        o_sys = platform.system()
        if o_sys == 'Windows':
            self.opt = '-n'
        else:
            self.opt = '-c'
            
        self.start_time = []
        self.fr_count = 0
    # dvr 정보 취득(기번/ip)    
    def get_dvr_info(self):#, idx):
        df = pd.read_csv('./config.txt')
        self.dvr_num = df.loc[0, 'dvr_num']#[idx, 'dvr_num']
        self.dvr_ip = df.loc[0, 'dvr_ip']#[idx, 'dvr_ip']
        self.dvr_ch = df.loc[0, 'dvr_ch']#[idx, 'dvr_ip'] 
        
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
            
    def working_hours(self):
        now_t = datetime.datetime.now()
        open_t = datetime.datetime(now_t.year, now_t.month, now_t.day, 9,0,0)
        close_t = datetime.datetime(now_t.year, now_t.month, now_t.day, 22,0,0)
        
        if open_t < now_t:
            if close_t > now_t:
                return True
            else:
                return False
            
    def start_log(self, v_file_name):
       
        recode_log = pd.read_csv(self.log_path)
        idx = len(recode_log) - 1    
        recode_log.loc[idx] = [self.start_time[0], self.dvr_num, self.dvr_ch, v_file_name, 'rec_start', self.fr_count, None, None]
        recode_log.to_csv(self.log_path, index = False)
        
    def masking(self, frame):
      
        height, width, channel = frame.shape
        # blur_img = np.zeros((height, width), np.uint8)
        for y in range(0, height):
            for x in range(0, width):
                
                
                b = frame.item(y, x, 0)
                g = frame.item(y, x, 1)
                r = frame.item(y, x, 2)
                b = b*x
                g = g*x
                r = r*x
               # print(x, b,g,r)
                
                frame.itemset(y, x, 0, b)
                frame.itemset(y, x, 1, g)
                frame.itemset(y, x, 2, r)
             
        return frame
    
    '''        
    def last_file_check(self):
        recode_log = pd.read_csv(self.log_path)
        idx = len(recode_log) - 1
        last_filename =  
        last_filefr = 
    '''        
    
            
    
    # 로그 파일 생성     
    def make_log(self):
        recode_log = pd.DataFrame(index = range(0, 0), 
                          columns = ['time', 'dvr_num', 'dvr_ch', 'file_name', 'happened', 'rec_frame', 'send_frame', 'error'])

        self.now = datetime.datetime.now()
        self.today = self.now.strftime('%Y%m%d')
        self.log_path = './log/' + str(self.dvr_num) + '/' + self.today + '.csv'
        if not os.path.exists('./log/'):
            os.mkdir('./log/')
        if not os.path.exists('./log/' + str(self.dvr_num)):
            os.mkdir('./log/' + str(self.dvr_num))    
        # 로그 파일 없으면 생성
        if not os.path.exists(self.log_path):    
            recode_log.to_csv(self.log_path, index = False)
    
            
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
    
    def recoding_video(self):
        acc = 'qtumai'
        pw = 'qtumai123456'
        print('rtsp://' + acc + ':' + pw + '@' + self.dvr_ip + ':554/' + self.dvr_ch)
        cap = cv2.VideoCapture('rtsp://' + acc + ':' + pw + '@' + self.dvr_ip + ':554/' + self.dvr_ch)
        #cap = cv2.VideoCapture('rtsp://qtumai:qtumai123456@192.168.0.59:554/stream_ch00_1')
        width = int(cap.get(3))
        height = int(cap.get(4))
        print(str(width) + 'x' + str(height))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        video_codec = cv2.VideoWriter_fourcc(*'DIVX')
        
        #start = time.time()
        
        v_file_name = str(self.log_time().strftime('%H%M'))
        video_file = os.path.join(self.name, v_file_name + ".avi")
        video_writer = cv2.VideoWriter(video_file, video_codec, fps, (width, height))
        
        
        try:
            # 녹화 루프 시작
            print('start_time', self.log_time())
            while cap.isOpened():
                self.fr_count += 1
                self.start_time.append(datetime.datetime.now())
                self.start_log(v_file_name)
                ret, frame = cap.read()
              
                # 마스킹
                '''
                try:
                    frame = self.masking(frame)
                except AttributeError as e:
                    print(e)
                    pass
                '''
                
                # 캡쳐 됨
                if ret == True:
                    
                    # 영업시간 종료시간파일까지 녹화 되면 종료 
                    if v_file_name == '2231':
                        break
                    
                    # 녹화길이 설정 / 900frame 1분 / 15fps
                    if self.fr_count == 900:
                        #start = time.time()                
                        #now = datetime.datetime.now()
                        v_file_name = self.log_time().strftime('%H%M')
                        video_file = os.path.join(self.name, v_file_name + ".avi")
                        print("Capture video saved location : {}".format(video_file))
                        video_writer = cv2.VideoWriter(video_file, video_codec, fps, (width, height))
                        
                        #종료 로그작성
                        recode_log = pd.read_csv(self.log_path)
                        idx = len(recode_log)
                        recode_log.loc[idx] = [self.log_time(), self.dvr_num, self.dvr_ch, v_file_name, 'rec_finish', self.fr_count, None, None]
                        recode_log.to_csv(self.log_path, index = False)
                        print('finish_time', self.start_time[-1])
                        
                        self.start_time = []
                        self.fr_count = 0
                        print('start_time', self.log_time())
                        
                        
                    
                    #프레임 로그 작성 
                    recode_log = pd.read_csv(self.log_path)
                    idx = len(recode_log)
                    recode_log.loc[idx - 1, 'rec_frame'] = self.fr_count
                    #print(fr_count)
                    recode_log.to_csv(self.log_path, index = False)
                    
                    # Write the frame to the current video writer
                    video_writer.write(frame)
                
                # 로컬환경 일땐 gateway ping check로 변경
                # 캡쳐 안됨    
                else:
                    # 인터넷 연결 이상시 체크 후 로그 작성
                    online = self.check_internet()
                    if online == False:
                        netstat = self.check_network()
                        recode_log = pd.read_csv(self.log_path)
                        idx = len(recode_log)
                        # offline
                        recode_log.loc[idx] = [self.log_time(), self.dvr_num, self.dvr_ch, self.now.strftime('%H%M'), 'rec_disconnect', self.fr_count, None, netstat]
                        recode_log.to_csv(self.log_path, index = False)
                        break
             
            cap.release()
        except KeyboardInterrupt as e:
  
            cap.release()
            sys.exit()           
            
main = video_recode()

while True:
    if main.working_hours() == True:
        main.get_dvr_info()
        main.make_log()
        main.make_save_path()
        main.recoding_video()
    
    else:
        time.sleep(10)
      
                