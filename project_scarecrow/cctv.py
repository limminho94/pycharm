import sys
import cv2
import torch
import serial
import socket
import threading
import time
import warnings
import pathlib
from enum import Enum
from queue import Queue
from datetime import datetime

warnings.filterwarnings("ignore", category=FutureWarning)
pathlib.PosixPath = pathlib.WindowsPath


class ACT(Enum):
    CCTVCONNECT = 4
    VIEWCCTV = 5
    CCTVCHECK = 6
    CCTVSTOP = 7
    LOGIMG = 10
    CCTVIMG = 11


# Server Configuration
HOST = '10.10.20.105'  # 서버 IP
PORT = 12345  # 서버 포트

# YOLOv5 Configuration
model_path = 'C:/Users/lms115/PycharmProjects/pythonProject2/yolov5/runs/GOGO/weights/best.pt'
model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=True)
TRACKABLE_CLASSES = ['person', 'birds', 'wild_boar', 'gorani']

# Arduino Configuration
try:
    arduino = serial.Serial('COM3', 9600, timeout=1, write_timeout=5)
    time.sleep(3)
except serial.SerialException as e:
    print(f"Arduino connection error: {e}")
    sys.exit()

# Webcam Configuration
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open webcam.")
    sys.exit()


# Socket Initialization
try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print("서버 소켓 연결 성공")
except socket.error as e:
    print(f"서버 연결 실패: {e}")
    sys.exit()


# Data Receiver Thread
class DataReceiverThread(threading.Thread):
    def __init__(self, parent):
        super().__init__()
        self.working = True
        self.parent = parent

    def stop(self):
        self.working = False

    def run(self):
        try:
            while self.working:
                header = b""
                header_size = 128
                while len(header) < header_size:
                    serv_data = client_socket.recv(header_size - len(header))
                    if not serv_data:
                        print("서버 연결이 종료되었습니다.")
                        return
                    header += serv_data

                if len(header) != 128:
                    print("잘못된 헤더 크기 수신")
                    continue

                parts = header.decode('utf-8').strip('\0').split('/')
                if len(parts) != 3:
                    print("잘못된 헤더 형식 수신")
                    continue

                act_type = int(parts[0])
                sender_id = parts[1]
                data_length = int(parts[2])

                body = b""
                while len(body) < data_length:
                    serv_data = client_socket.recv(data_length - len(body))
                    if not serv_data:
                        raise ConnectionError("서버 연결이 종료되었습니다.")
                    body += serv_data

                msg = body.decode('utf-8')
                #print(f"서버에서 받은 메시지: {msg}")

                if act_type == ACT.VIEWCCTV.value:
                    self.parent.send_images = True
                elif act_type == ACT.CCTVSTOP.value:
                    self.parent.send_images = False
        except Exception as e:
            print("서버 데이터 수신 오류:", e)
        finally:
            print("데이터 수신 스레드 종료")


# Main CCTV Class
class CCTV:
    def __init__(self):
        self.send_images = False
        self.stop = False
        self.data_receiver_thread = DataReceiverThread(self)
        self.detection_count = {cls: 0 for cls in TRACKABLE_CLASSES}  # 객체 탐지 횟수
        self.last_detection_time = {cls: time.time() for cls in TRACKABLE_CLASSES}  # 마지막 탐지 시간
        self.alert_count = {cls: 0 for cls in TRACKABLE_CLASSES}  # 알림 카운트
        self.last_alert_time = {cls: 0 for cls in TRACKABLE_CLASSES}
        self.frame_queue = Queue(maxsize=1)
        self.lock = threading.Lock()

        self.alert_interval = 300
        self.search_mode = False
        self.search_direction = "LEFT"
        self.search_last_send_time = time.time()
        self.search_last_direction_change = time.time()
        self.search_interval = 1
        self.search_direction_change_interval = 20
        self.send_interval = 1.0
        self.last_send_time = time.time()
        self.connect_to_server()  # 서버와 연결
        self.start_receiving()

    def connect_to_server(self):
        try:
            act_type = ACT.CCTVCONNECT.value
            sender_id = '1'  # CCTV ID
            message = "connect".encode('utf-8')  # 서버로 보낼 연결 메시지
            self.send_data_to_server(act_type, sender_id, message)
            print("서버와 연결 성공")
        except Exception as e:
            print(f"서버 연결 오류: {e}")
            self.stop = True

    def send_data_to_server(self, act_type, sender_id, image_data=None):
        try:
            data_length = len(image_data) if image_data else 0
            header = f"{act_type}/{sender_id}/{data_length}".encode('utf-8')
            header = header.ljust(128, b'\0')

            if image_data:
                data = header + image_data
            else:
                data = header

            client_socket.sendall(data)
            #print(f"데이터 전송 완료: {data_length}바이트 전송")
        except Exception as e:
            print("서버 전송 오류:", e)

    def start_receiving(self):
        self.data_receiver_thread.start()

    def process_arduino_response(self, response):
        response = response.strip()
        if response:
            print(f"Arduino response: {response}")

    # read_frames: 프레임 읽기 및 큐 크기 처리
    def read_frames(self):
        while not self.stop:
            ret, frame = cap.read()
            if not ret:
                print("Cannot read frame.")
                self.stop = True
                break

            with self.lock:
                if self.frame_queue.full():  # 큐가 가득 차면 오래된 프레임 제거
                    self.frame_queue.get()
                self.frame_queue.put(frame)

            time.sleep(0.01)  # CPU 부하 방지

    def process_frame(self):
        # 추가: 탐지 실패 카운트 변수
        detection_fail_count = 0

        # 추가: 알림 카운트 딕셔너리 초기화
        alert_count = {cls: 0 for cls in TRACKABLE_CLASSES}

        # 추가: 서보 모터의 현재 각도와 제한 값 (Arduino와 동기화 필요)
        current_angle = {"x": 90, "y": 80}  # 초기 각도
        min_angle = {"x": 90, "y": 15}  # 최소 각도
        max_angle = {"x": 125, "y": 175}  # 최대 각도

        while not self.stop:
            with self.lock:
                if self.frame_queue.empty():
                    time.sleep(0.01)
                    continue
                frame = self.frame_queue.get()

            # YOLO 모델 추론
            results = model(frame)
            df = results.pandas().xyxy[0]
            df = df[df['name'].isin(TRACKABLE_CLASSES)]
            current_time = time.time()

            # 객체가 감지되지 않은 경우: 탐지 실패 카운트 증가
            if len(df) == 0:
                detection_fail_count += 1  # 탐지 실패 카운트 증가

                # 3회 이상 연속 탐지 실패 시 탐색 모드 활성화
                if detection_fail_count >= 10:
                    self.search_mode = True
                    if current_time - self.search_last_direction_change >= self.search_direction_change_interval:
                        self.search_direction = "RIGHT" if self.search_direction == "LEFT" else "LEFT"
                        self.search_last_direction_change = current_time
                        print(f"Changing search direction to: {self.search_direction}")

                    if current_time - self.search_last_send_time >= self.search_interval:
                        try:
                            arduino.write((self.search_direction + "\n").encode())
                            self.search_last_send_time = current_time
                        except serial.SerialTimeoutException as e:
                            print(f"Write timeout: {e}. Retrying...")
                else:
                    print(f"Detection failed {detection_fail_count} times.")  # 디버깅 출력

                continue

            # 객체가 감지된 경우: 탐지 실패 카운트 초기화 및 탐색 모드 종료
            detection_fail_count = 0  # 탐지 실패 카운트 초기화
            if self.search_mode:
                print("Object detected. Exiting search mode.")
                self.search_mode = False

            # 탐지된 객체 처리
            for _, row in df.iterrows():
                name = row['name']
                conf = row['confidence']

                if name in TRACKABLE_CLASSES and conf >= 0.3:
                    # 5초 이내 동일 객체 탐지 횟수 카운팅
                    if current_time - self.last_detection_time[name] <= 5:
                        self.detection_count[name] += 1
                    else:
                        self.detection_count[name] = 1

                    self.last_detection_time[name] = current_time

                    # 디버깅 출력: 객체 이름과 카운트 값
                    print(f"Object: {name}, Current Count: {self.detection_count[name]}")

                    # 탐지 횟수 10회 이상인 경우 알림 전송 및 카운트 누적
                    if self.detection_count[name] >= 10:
                        print(f"Alert: {name} detected 10 times within 5 seconds!")
                        try:
                            # BUZZ 신호 전송
                            arduino.write("BUZZ\n".encode())
                            print(f"BUZZ sent for {name}")

                            # 중복 알림 방지: 마지막 알림으로부터 5분 경과
                            if current_time - self.last_alert_time.get(name, 0) >= 300:
                                # PNG 이미지 캡처
                                _, image_data = cv2.imencode('.png', frame)
                                message = image_data.tobytes()

                                # 서버로 이미지와 알림 전송
                                sender_id = f"1,{name}"  # '1' + 객체 이름
                                self.send_data_to_server(ACT.LOGIMG.value, sender_id, message)
                                print(f"Alert and PNG image sent to server for {name}")

                                # 마지막 알림 시간 갱신
                                self.last_alert_time[name] = current_time

                            # 알림 카운트 증가
                            alert_count[name] += 1
                            if alert_count[name] == 3:
                                # FIRE 신호 전송
                                arduino.write("FIRE\n".encode())
                                print(f"FIRE signal sent for {name}!")
                                alert_count[name] = 0  # 알림 카운트 초기화

                            # 탐지 횟수 초기화
                            self.detection_count[name] = 0

                        except serial.SerialException as e:
                            print(f"Serial error while sending BUZZ/FIRE: {e}")

            # 가장 높은 신뢰도를 가진 객체 추적
            if len(df) > 0:
                highest_confidence = df.iloc[df['confidence'].idxmax()]
                obj_cx = int((highest_confidence['xmin'] + highest_confidence['xmax']) / 2) / frame.shape[1]
                obj_cy = int((highest_confidence['ymin'] + highest_confidence['ymax']) / 2) / frame.shape[0]

                # 화면 중앙 기준으로 객체 위치를 계산하여 방향 결정
                dx = 0.5 - obj_cx
                dy = 0.5 - obj_cy
                command = []
                if dx > 0.05 and current_angle["y"] + 5 <= max_angle["y"]:
                    command.append("LEFT")
                    current_angle["y"] += 5  # 각도 업데이트
                elif dx < -0.05 and current_angle["y"] - 5 >= min_angle["y"]:
                    command.append("RIGHT")
                    current_angle["y"] -= 5  # 각도 업데이트

                if dy > 0.05 and current_angle["x"] + 5 <= max_angle["x"]:
                    command.append("UP")
                    current_angle["x"] += 5  # 각도 업데이트
                elif dy < -0.05 and current_angle["x"] - 5 >= min_angle["x"]:
                    command.append("DOWN")
                    current_angle["x"] -= 5  # 각도 업데이트

                # 아두이노로 방향 명령 전송
                if current_time - self.last_send_time >= self.send_interval and command:
                    try:
                        arduino.write((" ".join(command) + "\n").encode())
                        print(f"Sent command to Arduino: {' '.join(command)}")
                        self.last_send_time = current_time
                    except serial.SerialTimeoutException as e:
                        print(f"Write timeout: {e}. Retrying...")


    def display_frame(self):
        while not self.stop:
            with self.lock:
                if self.frame_queue.empty():
                    continue
                frame = self.frame_queue.queue[0].copy()

            results = model(frame)
            df = results.pandas().xyxy[0]
            for _, row in df.iterrows():
                xmin, ymin, xmax, ymax = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
                label = f"{row['name']} {row['confidence']:.2f}"
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
                cv2.putText(frame, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            cv2.imshow("YOLO Detection", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                self.stop = True
                break

    # stream_thread: 서버로 스트림 데이터 전송
    def start_streaming(self):
        try:
            while not self.stop:
                if self.send_images:
                    with self.lock:
                        if self.frame_queue.empty():
                            time.sleep(0.01)
                            continue
                        frame = self.frame_queue.queue[0]  # 최신 프레임 가져오기

                    _, buffer = cv2.imencode('.jpg', frame)
                    image_data = buffer.tobytes()
                    self.send_data_to_server(ACT.CCTVIMG.value, '1', image_data)
                    time.sleep(0.1)  # 전송 주기
                else:
                    time.sleep(0.5)  # 스트림 비활성화 상태 대기
        except Exception as e:
            print(f"Stream thread error: {e}")

    def stop_streaming(self):
        if cap.isOpened():
            cap.release()
        self.data_receiver_thread.stop()
        self.data_receiver_thread.join()
        client_socket.close()
        print("연결 종료 및 리소스 정리 완료")


if __name__ == "__main__":
    cctv = CCTV()
    try:
        # 스레드 구성
        read_thread = threading.Thread(target=cctv.read_frames, daemon=True)
        process_thread = threading.Thread(target=cctv.process_frame, daemon=True)
        stream_thread = threading.Thread(target=cctv.start_streaming, daemon=True)  # start_streaming 추가

        # 스레드 시작
        read_thread.start()
        process_thread.start()
        stream_thread.start()

        cctv.display_frame()  # 디스플레이 실행
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # 종료 및 리소스 정리
        cctv.stop = True
        read_thread.join()
        process_thread.join()
        stream_thread.join()  # stream_thread 종료 대기
        cctv.stop_streaming()  # stop_streaming 호출로 리소스 정리 일괄 처리
        print("Program terminated.")