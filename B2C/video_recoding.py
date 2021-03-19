# -*- coding: utf-8 -*-
import subprocess

import time
import datetime
import os
import threading
import pandas as pd


'''
shop_code = 'kkakka001'
acc = 'qtumai'
passwd = 'qtumai123456'
ip = '192.168.0.59'
port = '554'
ch = 'stream_ch00_0'
add = 'rtsp://' + acc + ':' + passwd + '@' + ip + ':' + port + '/' + ch
save_path = './save_video/test.avi'
time = datetime.datetime.now()
file_name = '_' + shop_code + '_' + ch


cmd = 'ffmpeg.exe -y -i "' + add + '" -t 1800 -an "' + save_path +'"'
subprocess.check_output(cmd)
'''

class video_recoding(threading.Thread):
    
    def __init__(self, shop_code, acc, pw, ip, port, ch, open_t, close_t):
        threading.Thread.__init__(self)
        self.shop_code = shop_code
        self.acc = acc
        self.pw = pw
        self.ip = ip
        self.port = str(port)
        self.ch = str(ch)
        self.open_t = open_t
        self.close_t = close_t
    
    def get_rtsp_addr(self):
        #rtsp://admin:qtumai123456@192.168.1.111:554/cam/realmonitor?channel=1
        add = "rtsp://" + self.acc + ":" + self.pw + "@" + self.ip + ":" + self.port + "/\"" + self.ch + "\""
        #add = 'rtsp://' + self.acc + ':' + self.pw + '@' + self.ip + '/' + self.ch
        return add
    
    def get_save_path(self):
        save_path = os.path.join('/home/pi/workspace/stream', 'save_video')
        #save_path = './save_video'
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        return save_path
    
    def get_file_name(self):
        file_name = ''
        ntime = datetime.datetime.now()
        file_name = ntime.strftime('%Y%m%d%H%M%S%f')
        #file_name = file_name + '_' + self.shop_code + '_' + self.ch + '.avi'
        file_name = file_name + '_' + self.shop_code  + '.avi'
        return file_name
    
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
    
    def recode(self):
        add = self.get_rtsp_addr()
        save_path = self.get_save_path()
        
        while True:
            if self.working_hours() == True:
                file_name = self.get_file_name()
                #rtsp://admin:qtumai123456@192.168.1.111:554/cam/realmonitor?channel=1: Invalid data found when processing input
                #ffmpeg -y -hide_banner -rtsp_transport tcp -i rtsp://admin:qtumai123456@192.168.1.110:554/cam/realmonitor?channel=1&subtype=0 -t 1800 -an /home/pi/workspace/stream/save_video/20210313123108032940_JJIN-ch1_cam/realmonitor?channel=1&subtype=0.avi
                cmd ="ffmpeg -y -r 30 -stimeout 10000000 -hide_banner -rtsp_transport tcp -i %s -vcodec copy -t 1800 -an %s/%s" %(add, save_path, file_name)
                print(cmd)
                subprocess.check_output(cmd, shell=True, universal_newlines=True)
            else:
                print('Not working time')
                time.sleep(60)
            
    def run(self):
        
        while True:
            try:
                
                self.recode()
            except:
                pass
        
if __name__ == '__main__':
    def get_dvr_info(idx):
        df = pd.read_csv('/home/pi/workspace/stream/config.txt')
        #df = pd.read_csv('./config.txt')
        shop_code = df.loc[idx, 'shop_code']
        acc = df.loc[idx, 'acc']
        pw = df.loc[idx, 'pw']
        ip = df.loc[idx, 'dvr_ip']
        port = df.loc[idx, 'port']
        ch = df.loc[idx, 'dvr_ch'] 
       
        return shop_code, acc, pw, ip, port, ch
    
    config = pd.read_csv('/home/pi/workspace/stream/config.txt')
    #config = pd.read_csv('./config.txt')
    open_t = (0,0)
    close_t = (23,59)
    
    for i in config.index:
        shop_code, acc, pw, ip, port, ch = get_dvr_info(i)
        main = video_recoding(shop_code, acc, pw, ip, port, ch, open_t, close_t)
        main.start()
        time.sleep(0.01)
        
            
        
    
    
        
