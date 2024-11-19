import sys

import cv2
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

# 영상 출력 반복 스레드
class Thread(QThread):
    changePixmap = pyqtSignal(QImage, np.ndarray)
    recordVideo = pyqtSignal(QImage)
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
        self.cap.release()

# Qt 창
class CCTV(QMainWindow):
    def __init__(self):
        super(CCTV, self).__init__()
        # UI 초기화
        self.initUI()
        # 영상 출력 반복 스레드
        self.th = Thread(self)

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


# 메인: Qt창 시작
if __name__ == "__main__":
    app = QApplication(sys.argv)
    cctv = CCTV()
    cctv.show()
    app.exec_()