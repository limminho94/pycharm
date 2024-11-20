import sys

import cv2
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import serial
import socket
import time

from PyQt5.uic.properties import QtGui
# c# 통신 연결
HOST = '10.10.20.105'  # 서버 IP
PORT = 12347  # 서버 포트
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# 아두이노 연결
# board = serial.Serial('COM3', 9600)

# 영상 출력 반복 스레드
class Thread(QThread):
    changePixmap = pyqtSignal(QImage, np.ndarray)
    working = True
    cap = None

    def run(self):
        # 0번 카메라 연결
        self.cap = cv2.VideoCapture(0)
        # 영상 가져오기 반복
        while self.working:
            # 카메라에서 영상 받기 (넘파이 배열)
            ret, frame = self.cap.read()
            # 영상이 없으면 종료
            if not ret:
                break

            # BGR -> RGB 변환
            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 영상의 세로, 가로, 채널수
            h, w, ch = rgbImage.shape
            bytes_per_line = ch * w

            # print(type(rgbImage.data))
            # print(rgbImage.data)
            # print(type(rgbImage))

            cvc = QImage(rgbImage.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.changePixmap.emit(cvc.scaled(640, 480, Qt.KeepAspectRatio), frame)

            # 전송할 데이터 준비
            type = '10'
            sender_id = "1"  # 클라이언트 ID
            msg = frame  # 보낼 메시지
            print("msg 값 :",msg)
            # 데이터를 '/ '로 구분하여 하나의 문자열로 합침
            data = f"{type}/{sender_id}/{msg}"
            print("보낼 데이터:", data)
            # 데이터를 바이트로 변환
            en_data = data.encode('utf-8')  # UTF-8로 인코딩
            # 서버로 실제 데이터 전송
            client_socket.sendall(en_data)
            print("보낸 데이터 : ", en_data)

            data = client_socket.recv(1024)
            msg = data.decode()  # 데이터를 출력한다.
            print('서버에서 온 데이터 : ', msg)

            # 연결 종료
            client_socket.close()
        self.cap.release()

# Qt 창
class CCTV(QMainWindow):
    def __init__(self):
        super(CCTV, self).__init__()
        # UI 초기화
        self.initUI()
        # 영상 출력 반복 스레드
        self.th = Thread(self)
        # 부저 클릭 시 경고음 재생
        # self.pushButton.clicked.connect(self.btn)
        # 부저 종료 클릭 시 경고음 종료
        # self.pushButton_2.clicked.connect(self.btn_stop)


    # UI 초기화 (영상 출력될 label 한 개, 시작버튼 한 개, 종료버튼 한 개)
    def initUI(self):
        # ui 파일 읽어오기
        loadUi('cctv.ui', self)


    # 시작 버튼 누름
    def cam_open(self):

        # 영상 읽어오기
        self.th.working = True
        self.th.changePixmap.connect(self.setImage)
        self.th.start()


    #  종료 버튼 누름
    def cam_close(self):
        # 영상 읽어오기
        self.th.working = False
        self.th.exec_()

    # label에 이미지 출력하기 함수
    def setImage(self, image):
        self.label_view.setPixmap(QPixmap.fromImage(image))

    # 부저 버튼 누름
    # def btn(self):
    #     board.write(b'1')
    #     pixmap = QPixmap('hesuabi.jpg')
    #     self.label_view.setPixmap(pixmap.scaled(640,800, Qt.KeepAspectRatio))

    # 부저 종료 버튼 누름
    # def btn_stop(self):
    #     board.write(b'0')

# 메인: Qt창 시작
if __name__ == "__main__":
    app = QApplication(sys.argv)
    cctv = CCTV()
    cctv.show()
    app.exec_()