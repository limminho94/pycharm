import pydobot
import socket
import cv2
import numpy as np
import struct
import torch
from keras import device

# 로봇팔 초기 위치 설정
x1, y1, z1 = 235, 0, 118

def machine_setting():
    global device
    port = 'COM5'
    device = pydobot.Dobot(port=port, verbose=True)
    device.move_to(x1, y1, z1, 0)
    device.wait(500)

def move_test():
    x1 = 180
    y1 = 0
    z1 = -10

    device.move_to(x1, y1, z1, 0)
    device.wait(2000)
    device.suck(True)
    print("로봇팔 흡입성공")
    z1 += -40
    device.move_to(x1, y1, z1, 0)
    device.suck(False)
    print("로봇팔 흡입끝")

    x1, y1, z1 = 235, 0, 118
    device.move_to(x1, y1, z1,0)

def receive_frame(client_socket):
    data = b''
    payload_size = struct.calcsize("L")
    while len(data) < payload_size:
        data += client_socket.recv(4096)

    # 이미지 크기 정보 추출
    packed_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("L", packed_size)[0]

    # 이미지 데이터 수신
    while len(data) < msg_size:
        data += client_socket.recv(4096)

    # 수신된 데이터를 이미지로 변환
    frame_data = data[:msg_size]
    frame = np.frombuffer(frame_data, dtype=np.uint8)
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    print("프레임:", frame)
    return frame

# YOLOv5 모델 불러오기
model = torch.hub.load('ultralytics/yolov5', 'custom', path='C:/Users/lms116/PycharmProjects/pycharm/yolov5/runs/train/exp6/weights/best.pt', force_reload=True, device='cpu')

# 서버 설정
server_ip = '10.10.20.116'
server_port = 12345
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip, server_port))
server_socket.listen(5)
print(f"서버가 {server_ip},{server_port}에서 대기 중입니다...")

# 클라이언트 연결 대기
client_socket, addr = server_socket.accept()
print(f"클라이언트 연결됨: {addr}")

# 로봇팔 초기 세팅
machine_setting()

# 데이터 처리 반복문
while True:
    frame = receive_frame(client_socket)
    if frame is not None:
        # YOLOv5 객체 탐지 수행
        results = model(frame)

        # 탐지 결과 표시 및 로봇팔 동작
        for obj in results.pred[0]:
            x1, y1, x2, y2, conf, cls = obj[:6]
            label = f"{model.names[int(cls)]} {conf:.2f}"
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # 신뢰도가 0.3 이상인 경우 로봇팔 동작
            if conf > 0.3:
                move_test()

        # 화면 출력
        cv2.imshow("window", frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    else:
        print("이미지 수신 실패")

# 연결 종료
client_socket.close()
server_socket.close()
cv2.destroyAllWindows()
