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

class video_recode(threading.Thread):
    
    def __init__(self, shop_code, dvr_num, dvr_ip, dvr_ch, open_t, close_t):
        threading.Thread.__init__(self, name = str(dvr_num) + '_' + str(dvr_ch))
        #self.name = str(dvr_num) + str(dvr_ch)
        self.shop_code = shop_code
        self.dvr_num = dvr_num
        self.dvr_ip = dvr_ip
        self.dvr_ch = str(dvr_ch)
        self.open_t = open_t
        self.close_t = close_t
        self.start_time = []
        self.fr_count = 0
        
        print('%s Recoding program start' %self.name)
        
    # 현재시간 리턴
    def log_time(self):
        self.n_time = datetime.datetime.now()
        return self.n_time
           
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
    def get_file_name(self):
        file_name = ''
        ntime = datetime.datetime.now()
        file_name = ntime.strftime('%Y%m%d%H%M%S%f')
        #file_name = file_name + '_' + self.shop_code + '_' + self.ch + '.avi'
        file_name = file_name + '_' + self.shop_code + '_' + str(self.dvr_num) + '_' + self.dvr_ch
        return file_name
    
    
    # 파일 저장 디렉토리 생성         
    def make_save_path(self):
        #self.name = os.path.join(os.getcwd(), 'save_video', str(self.today) + '_' + self.shop_code + '_' + str(self.dvr_num) + '_' + self.dvr_ch)
        self.name = os.path.join('/home/qtumai/workspace/stream/save_video/', str(self.dvr_num), self.dvr_ch)
        print("All video saved in dir:", self.name)
        if not os.path.exists('/home/qtumai/workspace/stream/save_video/'):
            os.mkdir('/home/qtumai/workspace/stream/save_video/')
        if not os.path.exists('/home/qtumai/workspace/stream/save_video/' + str(self.dvr_num) + '/'):
            os.mkdir('/home/qtumai/workspace/stream/save_video/' + str(self.dvr_num) + '/')
        if not os.path.exists(self.name):
            os.mkdir(self.name)
        
    
    def video_info(self):
        #self.acc = 'admin'
        self.acc = 'qtumai'
        #self.pw = '4321'
        self.pw = 'qtumai123456'
        #self.add = 'rtsp://' + self.acc + ':' + self.pw + '@' + self.dvr_ip + ':4524/' + self.dvr_ch
        #self.add = 'rtsp://' + self.acc + ':' + self.pw + '@' + self.dvr_ip + ':554/' + self.dvr_ch
        self.add = 'rtsp://' + self.acc + ':' + self.pw + '@' + self.dvr_ip + ':554/' + 'stream_ch00_1'
        cap = cv2.VideoCapture(self.add)
        #cap = cv2.VideoCapture('rtsp://qtumai:qtumai123456@192.168.0.59:554/stream_ch00_1')
        self.width = int(cap.get(3))
        self.height = int(cap.get(4))
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.video_codec = cv2.VideoWriter_fourcc(*'FFV1')
        
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
    
   
    def recoding_video(self):
        
        while True:
            if self.working_hours() == True:
                print('working hour')
                break
            else:
                print('close time. 60sec wait')
                time.sleep(60)
                
        # 영상 정보 설정 계정, 암호, 프레임 높이, 너비, 초당프레임, 코덱                
        print(self.wid, self.hei)
        blur_img = self.create_blur(self.hei, self. wid, self.channel)
        cap = cv2.VideoCapture(self.add)
        
        # 저장 파일 세팅
        v_file_name = self.get_file_name()
        video_file = os.path.join(self.name, v_file_name + ".mkv")
        print('make_file')
        self.video_writer = cv2.VideoWriter(video_file, self.video_codec, self.fps, (self.wid, self.hei))
        self.fr_count = 0
        try:
            
            print('start_time', self.log_time())

            while cap.isOpened():
                
                self.fr_count += 1
                #print('fr_count : %i, fps : %i' %(self.fr_count, self.fps))
                      
                self.start_time.append(datetime.datetime.now())
                ret, frame = cap.read()
                
                # 캡쳐 됨
                if ret == True:
                                     
                    if self.fr_count == self.fps * 1800:
                        v_file_name = self.get_file_name()
                        video_file = os.path.join(self.name, v_file_name + ".mkv")
                        print("Capture video saved location : {}".format(video_file))
                        self.video_writer = cv2.VideoWriter(video_file, self.video_codec, self.fps, (self.wid, self.hei))

                        print('finish_time', self.start_time[-1])
                        
                        while True:
                            if self.working_hours() == True:
                                print('working hour')
                                break
                            else:
                                print('close time. 60sec wait')
                                time.sleep(60)
                        
                        
                        # 초기화
                        self.start_time = []
                        self.fr_count = 0
                        video_file = ''
                        print('start_time', self.log_time())
                    
                    
                    # Write the frame to the current video writer
                    result = frame + blur_img
                    self.video_writer.write(result)
                
                
                # 캡쳐 안됨    
                else:  
                    break     
                    
            self.video_writer.release()
            cap.release()
        except KeyboardInterrupt as e:
            self.video_writer.release()
            cap.release()
            sys.exit() 
                     
    def run(self):
        while True:
            
           
            #self.get_dvr_info()
            self.make_save_path()
            self.video_info()
            self.recoding_video()
            
                
            
        
 ################################## main start ##################################            

if __name__ == '__main__':
    
    def get_dvr_info(idx):
        df = pd.read_csv('/home/qtumai/workspace/stream/config.txt')
        dvr_num = df.loc[idx, 'dvr_num']
        dvr_ip = df.loc[idx, 'dvr_ip']
        dvr_ch = df.loc[idx, 'dvr_ch'] 
        shop_code = df.loc[idx, 'shop_code']
        return dvr_num, dvr_ip, dvr_ch ,shop_code
    
    config = pd.read_csv('/home/qtumai/workspace/stream/config.txt')
 ################################## 영업시간 설정 ##################################
    open_t = (10,30)
    close_t = (22,30)
    
    for i in config.index:
        dvr_num, dvr_ip, dvr_ch, shop_code = get_dvr_info(i)
        main = video_recode(shop_code, dvr_num, dvr_ip, dvr_ch, open_t, close_t)
        main.start()
        
    '''        
    dvr_num, dvr_ip, dvr_ch = get_dvr_info(1)
    main = video_recode(dvr_num, dvr_ip, dvr_ch, open_t, close_t)
    main.start()
    time.sleep(5)
    '''
