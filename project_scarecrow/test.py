import sys
import cv2
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import socket
from enum import Enum

# 아두이노 연결
# board = serial.Serial('COM3', 9600)

class ACT(Enum):
    LOGIN = 0
    SIGNUP = 1
    CCTVCONNECT = 2
    LOGIMG = 10
    CCTVIMG = 11

# C# 서버와 통신
HOST = '10.10.20.105'  # 서버 IP
PORT = 12345  # 서버 포트
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# 영상 출력 반복 스레드
class Thread(QThread):
    changePixmap = pyqtSignal(QImage, np.ndarray)
    receivedData = pyqtSignal(str)  # 데이터 수신 후 UI 업데이트 위한 시그널

    working = True
    cap = None

    def create_header(self, act_type, sender_id, data_length):
        # 128바이트 고정 헤더 생성 (데이터 길이 포함)
        header = f"{act_type}/{sender_id}/{data_length}".encode('utf-8')
        header = header.ljust(128, b'\0')  # 패딩으로 128바이트 고정
        return header

    def send_data_to_server(self, act_type, sender_id, image_data=None):
        try:
            # 데이터 크기 계산
            data_length = len(image_data) if image_data else 0

            # 헤더 생성 (데이터 크기 포함)
            header = self.create_header(act_type, sender_id, data_length)

            # 데이터 준비
            if image_data:
                data = header + image_data  # 헤더 + 이미지 데이터
            else:
                raise ValueError("Image data is required for act_type 10")

            # 서버로 전송
            client_socket.sendall(data)
            print(f"데이터 전송 완료: {data_length}바이트 전송")


        except Exception as e:
            print("서버 전송 오류:", e)

    def run(self):
        self.cap = cv2.VideoCapture(0)
        while self.working:
            # 카메라에서 영상 받기 (넘파이 배열)
            ret, frame = self.cap.read()
            if not ret:
                break

            # BGR -> RGB 변환
            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgbImage.shape
            bytes_per_line = ch * w

            cvc = QImage(rgbImage.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.changePixmap.emit(cvc.scaled(640, 480, Qt.KeepAspectRatio), frame)

            # JPEG 인코딩
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                image_data = buffer.tobytes()
                # 데이터 전송 (act_type=10, sender_id='1', 이미지 데이터 포함)
                self.send_data_to_server(11, '1', image_data)

        self.cap.release()
        client_socket.close()

class DataReceiverThread(QThread):
    receivedData = pyqtSignal(str)  # 서버에서 받은 데이터를 UI로 전달하기 위한 시그널

    def __init__(self, parent=None):
        super().__init__(parent)
        self.working = True  # 스레드 작동 여부

    def stop(self):
        self.working = False

    def run(self):
        try:
            while self.working:
                # 헤더 수신
                header_size = 128
                header = b""
                while len(header) < header_size:
                    serv_data = client_socket.recv(header_size - len(header))
                    if not serv_data:
                        print("서버 연결이 종료되었습니다.")
                        return
                    header += serv_data

                # 헤더 파싱
                header_str = header.decode('utf-8').strip('\0')
                print(f"받은 헤더: {header_str}")

                parts = header_str.split('/')
                act_type = int(parts[0])  # 동작 타입
                sender_id = parts[1]  # 송신자 ID
                data_length = int(parts[2])  # 본문 데이터 길이

                # 본문 데이터 수신
                body = b""
                while len(body) < data_length:
                    serv_data = client_socket.recv(data_length - len(body))
                    if not serv_data:
                        raise ConnectionError("서버 연결이 종료되었습니다.")
                    body += serv_data
                    msg = body.decode('utf-8')
                    print(f"서버에서 받은 메시지: {msg}")
                    self.receivedData.emit(msg)

                # 데이터 처리 및 UI로 전달
                if act_type == ACT.CCTVIMG.value:
                    self.working = True


        except Exception as e:
            print("서버 데이터 수신 오류:", e)

class CCTV(QMainWindow):
    def __init__(self):
        super(CCTV, self).__init__()
        self.initUI()

        # 영상 출력 반복 스레드
        self.th = Thread(self)
        self.th.changePixmap.connect(self.setImage)  # 카메라 이미지 업데이트
        self.th.receivedData.connect(self.handle_received_data)  # 서버 데이터 처리

        # 데이터 수신을 위한 별도의 스레드
        self.data_receiver_thread = DataReceiverThread()
        self.data_receiver_thread.receivedData.connect(self.handle_received_data)  # 서버 데이터 처리

        # 최초 접속 시 서버 연결 및 수신 스레드 시작
        self.connect_to_server()
        self.cam_open()
    def connect_to_server(self):
        try:
            act_type = ACT.CCTVCONNECT.value  # 연결 요청 액션 타입
            sender_id = '1'
            message = "connect".encode('utf-8')

            # 서버로 연결 메시지 전송
            self.th.send_data_to_server(act_type, sender_id, message)

            # 데이터 수신 스레드 시작
            if not self.data_receiver_thread.isRunning():
                self.data_receiver_thread.start()

            print("서버와 연결 성공, 데이터 수신 스레드 시작")
        except Exception as e:
            print("서버 연결 및 데이터 수신 스레드 시작 오류:", e)

    # UI 초기화 (영상 출력될 label 한 개, 시작버튼 한 개, 종료버튼 한 개)
    def initUI(self):
        # ui 파일 읽어오기
        loadUi('cctv.ui', self)

    def cam_open(self):
        self.th.start()

    def cam_close(self):
        self.th.working = False
        self.th.quit()
        self.data_receiver_thread.stop()  # 데이터 수신 스레드 종료

    def setImage(self, image):
        self.label_view.setPixmap(QPixmap.fromImage(image))

    def handle_received_data(self, msg):
        print(f"서버에서 받은 메시지: {msg}")


# 메인: Qt창 시작
if __name__ == "__main__":
    app = QApplication(sys.argv)
    cctv = CCTV()
    cctv.show()
    app.exec_()