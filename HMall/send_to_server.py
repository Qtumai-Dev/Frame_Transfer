# -*- coding: utf-8 -*-
import paramiko
import pandas as pd
import os
import datetime
import glob
import threading
import time
import boto3
from botocore.exceptions import ClientError

class sendtoserver(threading.Thread):
    
    def __init__(self, dvr_num, dvr_ch, save_path):
       
        threading.Thread.__init__(self)
        self.dvr_num = str(dvr_num)
        self.dvr_ch = str(dvr_ch)
        self.server_path = save_path
        
    def setData(self):
        #self.now = datetime.datetime.now()
        #self.today = self.now.strftime('%Y%m%d')
        #self.work_dir = os.getcwd() + '/'
        self.local_path = os.path.join('/home/qtumai/workspace/stream/save_video/', self.dvr_num, self.dvr_ch)
        print('local_path : ', self.local_path)
        self.file_name = self.get_filename()
        
        self.access_key_id = "AKIAQXXRPHPXI4CQSHEX"
        self.secret_key = "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"
        self.bucket_name = "qtumaitest"
        while True:
            try:
                self.response = self.create_bucket(self.bucket_name)
                break
            except Exception as e:
                print(e)
                continue
        self.s3 = boto3.client("s3", aws_access_key_id = self.access_key_id, aws_secret_access_key = self.secret_key)
        
    def get_filelist(self):
        
        files = os.listdir(self.local_path)
        condition = self.local_path + '/*.mkv'
        files = glob.glob(condition)
        return files
    
    def send_sig(self, result):
        return result < datetime.datetime.now()
        
    def get_filename(self):
        
        self.files = ''
        self.file_name = ''
        self.files = self.get_filelist()
        
        for self.file_name in self.files:
            self.file_name = self.file_name.split('/')[-1]
            print(self.file_name)
            create_time = self.file_name[:12]
            year = create_time[:4]
            month = create_time[4:6]
            day = create_time[6:8]
            hour = create_time[8:10]
            _min = create_time[10:12]
            print(int(year), int(month), int(day), int(hour), int(_min))
            
            create_time = datetime.datetime(int(year), int(month), int(day), int(hour), int(_min))
            result = create_time + datetime.timedelta(seconds = 120)
            
            
            print(self.send_sig(result))
            
            if self.send_sig(result) == True:
                print('select file : ', self.file_name)
                break
                
            else:
                time.sleep(1)
                self.files = ''
                self.file_name = ''
                self.files = self.get_filelist()
                pass
      
        return self.file_name     
    #채널 분류
    def ch_classification(self):
        entrance = ['1']
        etc = ['2', '3']
        out = ['4']
        
        if self.dvr_ch in entrance:
            self.group = 'entrance'
            
        elif self.dvr_ch in etc:
            self.group = 'etc'
            
        elif self.dvr_ch in out:
            self.group = 'out'
        else:
            print(self.dvr_ch + '채널 설정확인')
            
    def delete_file(self):
        os.remove(self.local_path + '/' + self.file)
       
    def create_bucket(self, bucket_name):
        print("Creating a bucket..." + bucket_name)
        s3 = boto3.client("s3", aws_access_key_id = self.access_key_id, aws_secret_access_key = self.secret_key)
        try:
            response = s3.create_bucket(Bucket = bucket_name, CreateBucketConfiguration = {"LocationConstraint": "ap-northeast-2"})
            return response
        except ClientError as e:
            if e.response['Error']['Code'] == "BucketAlreadyOwnedByYou":
                print("Bucket already exists. skipping..")
            else:
                print("Unknown error, exit...")    
        
    def transfer(self):
        try:
            self.file = ''
            self.file = self.get_filename()
            self.shop_code = self.file.split('_')[1]
        
            print('file upload : ', self.file)
            print('file_path : ', self.local_path)
            self.s3.upload_file(self.local_path + '/' + self.file, self.bucket_name, 'HMALL/' + self.shop_code + '/' + self.group + '/' + self.file)
            print('upload finish : ', self.file)
            self.delete_file()
        except IndexError as e:
            print(e)
            time.sleep(10)
        
        
        
        
    '''
    def transfer(self):
        self.file = ''        
        self.transport = paramiko.transport.Transport(host, port)
        
        while True:
            try:
                self.file = self.get_filename()
                print('file_name : ', self.file)
                print(self.transport.getpeername())
                self.transport.connect(username = self.acc, password = self.pw)
                self.sftp = paramiko.SFTPClient.from_transport(self.transport)
                self.sftp.put(self.local_path + self.file, self.server_path + '/' + self.file)
                self.delete_file(self.file)
            except Exception as e:
                print('error : ', e)
                pass
            
            finally:
                self.sftp.close()
                self.transport.close()
                
                break
    '''         
    
    def run(self):
        
        while True:
            self.setData()
            self.ch_classification()
            #self.create_log(self.local_path)
            self.transfer() 
            
            time.sleep(0.5)
        
            
if __name__ == '__main__':
    
    def get_dvr_info(idx):
        df = pd.read_csv('/home/qtumai/workspace/stream/config.txt')
        dvr_num = df.loc[idx, 'dvr_num']
        dvr_ip = df.loc[idx, 'dvr_ip']
        dvr_ch = df.loc[idx, 'dvr_ch'] 
        shop_code = df.loc[idx, 'shop_code']
        return dvr_num, dvr_ch ,shop_code
   
                
    host = '175.197.68.67'
    port = 22
    acc = 'admin'
    pw = '@!Chaos123'
    config = pd.read_csv('/home/qtumai/workspace/stream/config.txt')
    save_path = '/homes/brooks/save_video/'
    
    for i in config.index:
        dvr_num, dvr_ch, shop_code = get_dvr_info(i)
        main = sendtoserver(dvr_num, dvr_ch, save_path)
        main.start()
        time.sleep(0.01)    
    '''    
    dvr_num, dvr_ch, shop_code = get_dvr_info(0)
    main = sendtoserver(dvr_num, dvr_ch, save_path)
    main.start()
    time.sleep(0.5)    
    '''
    
