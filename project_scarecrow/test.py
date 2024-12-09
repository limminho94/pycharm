import sys
import cv2
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import socket
from enum import Enum


class ACT(Enum):
    LOGIN = 0
    SIGNUP = 1
    CCTVCONNECT = 2
    VIEWCCTV = 3
    CCTVSTOP = 4
    LOGIMG = 10
    CCTVIMG = 11



HOST = '10.10.20.105'  # 서버 IP
PORT = 12345  # 서버 포트

try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print("서버 연결 성공")
except socket.error as e:
    print(f"서버 연결 실패: {e}")
    sys.exit()


class Thread(QThread):
    changePixmap = pyqtSignal(QImage, np.ndarray)
    send_images = False
    working = True
    cap = None

    def create_header(self, act_type, sender_id, data_length):
        header = f"{act_type}/{sender_id}/{data_length}".encode('utf-8')
        header = header.ljust(128, b'\0')
        return header

    def send_data_to_server(self, act_type, sender_id, image_data=None):
        try:
            data_length = len(image_data) if image_data else 0
            header = self.create_header(act_type, sender_id, data_length)

            if image_data:
                data = header + image_data
            else:
                raise ValueError("Image data is required for act_type 10")

            client_socket.sendall(data)
            print(f"데이터 전송 완료: {data_length}바이트 전송")
        except Exception as e:
            print("서버 전송 오류:", e)

    def run(self):
        try:
            self.cap = cv2.VideoCapture(0)
            while self.working:
                ret, frame = self.cap.read()
                if not ret:
                    break

                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytes_per_line = ch * w

                cvc = QImage(rgbImage.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.changePixmap.emit(cvc.scaled(640, 480, Qt.KeepAspectRatio), frame)

                if self.send_images:
                    ret, buffer = cv2.imencode('.jpg', frame)  # 원본 화질로 이미지 인코딩
                    if ret:
                        image_data = buffer.tobytes()
                        self.send_data_to_server(ACT.CCTVIMG.value, '1', image_data)
        except Exception as e:
            print("웹캠 스레드 오류:", e)
        finally:
            if self.cap:
                self.cap.release()
            print("웹캠 스레드 종료")


class DataReceiverThread(QThread):
    receivedData = pyqtSignal(str)

    def __init__(self, parent_thread, parent=None):
        super().__init__(parent)
        self.working = True
        self.parent_thread = parent_thread

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
                print(f"서버에서 받은 메시지: {msg}")

                if act_type == ACT.CCTVCONNECT.value:
                    print("서버와 연결되었습니다.")
                elif act_type == ACT.VIEWCCTV.value:
                    print("CCTV 이미지 전송 요청 수신")
                    self.parent_thread.send_images = True
                elif act_type == ACT.CCTVSTOP.value:
                    print("CCTV 이미지 전송 중단 요청 수신")
                    self.parent_thread.send_images = False
        except Exception as e:
            print("서버 데이터 수신 오류:", e)
        finally:
            print("데이터 수신 스레드 종료")


class CCTV(QMainWindow):
    def __init__(self):
        super(CCTV, self).__init__()
        self.initUI()

        self.th = Thread(self)
        self.th.changePixmap.connect(self.setImage)

        self.data_receiver_thread = DataReceiverThread(self.th, self)
        self.data_receiver_thread.receivedData.connect(self.handle_received_data)

        self.cam_open()
        self.connect_to_server()

    def initUI(self):
        loadUi('cctv.ui', self)

    def connect_to_server(self):
        try:
            act_type = ACT.CCTVCONNECT.value
            sender_id = '1'
            message = "connect".encode('utf-8')
            self.th.send_data_to_server(act_type, sender_id, message)

            if not self.data_receiver_thread.isRunning():
                self.data_receiver_thread.start()

            print("서버와 연결 성공")
        except Exception as e:
            print("서버 연결 오류:", e)

    def cam_open(self):
        self.th.start()

    def cam_close(self):
        self.th.working = False
        self.th.quit()
        self.th.wait()
        self.data_receiver_thread.stop()
        self.data_receiver_thread.wait()

    def close_connection(self):
        client_socket.close()
        print("서버 연결 종료")

    def setImage(self, image, frame):
        self.label_view.setPixmap(QPixmap.fromImage(image))

    def handle_received_data(self, msg):
        print(f"서버에서 받은 메시지: {msg}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    cctv = CCTV()
    cctv.show()
    try:
        app.exec_()
    finally:
        cctv.cam_close()
        cctv.close_connection()