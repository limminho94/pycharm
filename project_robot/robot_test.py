import pydobot
import socket
import cv2
import numpy as np
import struct
import torch

# 로봇팔 초기 위치 설정
x1, y1, z1 = 235, 0, 118

def machine_setting():
    global device
    port = 'COM5'
    device = pydobot.Dobot(port=port, verbose=True)
    device.move_to(x1, y1, z1, 0)
    device.wait(500)

def move_to_object(x_center, y_center, z_base):
    # 물체의 중심 좌표에 로봇팔을 이동시키기
    # 예: 물체의 중심에 로봇팔을 이동시킬 때 z_base는 물체가 놓인 높이에 맞춰서 설정
    device.move_to(x_center, y_center, z_base, 0)
    device.wait(500)

def receive_frame(client_socket):
    data = b''  # 이미지 데이터
    header = struct.calcsize("L")
    while len(data) < header:
        data += client_socket.recv(4096)

    # 이미지 크기 정보 추출
    length = data[:header]
    data = data[header:]
    img = struct.unpack("L", length)[0]

    # 이미지 데이터 수신
    while len(data) < img:
        data += client_socket.recv(4096)

    # 수신된 데이터를 이미지로 변환
    frame_data = data[:img]
    frame = np.frombuffer(frame_data, dtype=np.uint8)
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
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

            # 물체 중심 좌표 계산
            object_center_x = (x1 + x2) / 2
            object_center_y = (y1 + y2) / 2

            # 물체의 중심을 로봇팔이 움직일 좌표로 변환
            # 예를 들어, 카메라의 화면 크기를 기준으로 비율로 변환
            # 카메라 해상도가 640x480이라고 가정할 때
            camera_width = 640
            camera_height = 480

            # 물체의 중심을 3D 좌표로 변환 (단순 예시: 비율 변환)
            # 실제 환경에서는 카메라의 시야각, 물체의 크기 등을 고려해야 함
            x_center = (object_center_x / camera_width) * 800  # 로봇팔의 x 좌표 범위 (예시 0 ~ 300)
            y_center = (object_center_y / camera_height) * 600  # 로봇팔의 y 좌표 범위 (예시 0 ~ 200)

            # 로봇팔 이동
            move_to_object(x_center, y_center)

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
