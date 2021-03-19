# Video_Transfer
##RTSP영상을 저장하고 분석서버로 전송

### 실행파일 강제종료시 / 전원 off시 / 네트워크 끊겼을때 재접속시 이어진 시간 + 이어지는 프레임 전송필요

## video_recoding.py
채널 개수만큼 thread 동작 30분 단위 개별 녹화
무손실압축 옵션
마스킹 적용
if __name__ == '__main__': 부분에 open_t, close_t에 개점 시간 폐점시간 수정 후 사용 필

시간설정대로 작동 확인

## send_to_server.py
s3 서버로 Hmall/점코드/그룹 별로 저장
Tread로 채널 별 전송

## config.txt
dvr 정보 
