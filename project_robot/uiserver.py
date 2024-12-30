import sys
import cv2
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QMovie
import mariadb
from _thread import *
import threading
import pandas as pd
import numpy as np
import socket
import torch
import warnings
import pathlib
from datetime import datetime
import os

warnings.filterwarnings("ignore", category=FutureWarning)
temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath

# 1. YOLOv5 모델 로드
# 학습된 모델 파일 경로 (예: best.pt)
model_path = r'C:\Users\lms113\Desktop\exp3\weights\best.pt'
model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=True)

# UI파일 연결
# 단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("Server_layout.ui")[0]

client_frames = {} # 프레임 저장하는 곳
addr_list = [] # 클라이언트 주소 리스트
lock = threading.Lock()  # 데이터 충돌방지
user_sockets = {}
event = None
record_count = 0

# DB 연결
try:
    conn = mariadb.connect(
        user="root",
        password="1234",
        host="10.10.20.117",
        port=3306,
        database="fire_system"
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

cur = conn.cursor()

# 데이터 정확히 수신 원하는 데이터의 크기가 될때까지 누적했다가 보여준다
def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf:
            return None
        buf += newbuf
        count -= len(newbuf)
    return buf

# 스레드 할당
def threaded(client_socket, addr):
    global client_frames, addr_list,event, record_count
    print(f'Connected by: {addr[0]}:{addr[1]}')
    addr_list.append(addr)
    print(addr_list)
    # header = recvall(client_socket, 256).decode().strip()
    while True:
        try:
            with lock:
                while event == "fire":
                    cur.execute(
                        "select fire_alram.FE, fire_alram.warehouse, fire_alram.first_action from fire_alram left join fire_record on fire_alram.warehouse = fire_record.warehouse order by fire_record.time desc limit 1")
                    res = cur.fetchall()  # 쿼리 실행 결과
                    FE_path = str(res[0][0])
                    image = cv2.imread(FE_path)

                    if not os.path.exists(FE_path):
                        print(f"이미지 경로가 잘못되었습니다: {FE_path}")
                    else:
                        # 이미지 읽기
                        image = cv2.imread(FE_path)
                        if image is None:
                            print("이미지를 읽을 수 없습니다. 파일이 손상되었거나 경로가 잘못되었습니다.")
                        else:
                            print("이미지를 성공적으로 불러왔습니다.")
                    _, buffer = cv2.imencode('.jpg', image)  # 이미지를 바이트 배열로 변환
                    byte_data = buffer.tobytes()
                    result = str(res[0][1]) + ";" + str(res[0][2])

                    image_path2 = f"../Data/fire_record/record_img{record_count-1}.jpg"
                    image2 = cv2.imread(image_path2)  # OpenCV로 이미지 읽기
                    _, buffer2 = cv2.imencode('.jpg', image2)  # 이미지를 바이트 배열로 변환
                    byte_data2 = buffer2.tobytes()

                    header1 = "Detect_img".ljust(16).encode()
                    header2 = "FE_img".ljust(16).encode()
                    header3 = "Detect_Msg".ljust(16).encode()

                    length1 = str(len(byte_data2)).ljust(16).encode()
                    length2 = str(len(byte_data)).ljust(16).encode()
                    length3 = str(len(result.encode())).ljust(16).encode()

                    data1 = byte_data2
                    data2 = byte_data
                    data3 = result.encode()
                    try:
                        user_sockets["24110123"].sendall(header1 + length1 + data1)  # sendall은 데이터 크기와 상관없이 모두 전송될 때까지 시도
                        print("result1 전송 성공")
                    except Exception as e:
                        print(f"전송 중 오류 발생: {e}")
                    try:
                        user_sockets["24110123"].sendall(header2 + length2 + data2)  # sendall은 데이터 크기와 상관없이 모두 전송될 때까지 시도
                        print("result2 전송 성공")
                    except Exception as e:
                        print(f"전송 중 오류 발생: {e}")
                    try:
                        user_sockets["24110123"].sendall(header3 + length3 + data3)  # sendall은 데이터 크기와 상관없이 모두 전송될 때까지 시도
                        print("result3 전송 성공")
                    except Exception as e:
                        print(f"전송 중 오류 발생: {e}")

                    event = None
                    break

            # 데이터 타입 헤더 수신
            header = recvall(client_socket, 16).decode().strip()
            # 이미지 데이터 수신
            if header == "IMG":
                length = recvall(client_socket, 16).decode().strip()
                # 데이터 크기를 정수로 변환
                length = int(length)
                data = recvall(client_socket, length)
                # 이미지를 디코딩
                np_data = np.frombuffer(data, dtype='uint8')
                decimg = cv2.imdecode(np_data, 1)

                with lock:  # 락걸어서 데이터끼리 충돌방지
                    client_frames[addr] = decimg
            # 텍스트 데이터 수신
            if header.strip().replace("\x00", "") == "Text":
                data = recvall(client_socket, 256).decode().strip().replace("\x00", "")
                print("Received text:", data)
                msg = data.split(';')
                print(msg)
                if msg[0].strip() == "LOGIN":
                    cur.execute(f'select id,pw from users where id = "{msg[1]}" and pw = "{msg[2]}"')  # 쿼리 바인드
                    res = cur.fetchall()
                    if res:
                        print("로그인 성공")
                        header = "Login".ljust(16).encode()
                        length = str(len("success")).ljust(16).encode()
                        client_socket.send(header + length + "success".encode())
                        user_sockets[msg[1]] = client_socket
                    else:
                        print("로그인 실패")
                        header = "Login".ljust(16).encode()
                        length = str(len("failed")).ljust(16).encode()
                        client_socket.send(header + length + "failed".encode())

                elif msg[0].strip() == "fire_record":
                    header = "Msg".ljust(16).encode()
                    cur.execute('select time,warehouse from fire_record order by time desc')
                    res = cur.fetchall()  # 쿼리 실행 결과
                    result = "|".join(f"{str(row[0])}/{str(row[1])}" for row in res)
                    length = str(len(result)).ljust(16).encode()
                    try:
                        client_socket.sendall(header + length + result.encode())  # sendall은 데이터 크기와 상관없이 모두 전송될 때까지 시도
                        print("전송 성공")
                    except Exception as e:
                        print(f"전송 중 오류 발생: {e}")

                elif msg[0].strip() == 'img_record':
                    cur.execute(f'select image_path from fire_record where time = "{msg[1]}"')
                    res = cur.fetchall()  # 쿼리 실행 결과
                    header = "Record_img".ljust(16).encode()

                    image_path = str(res[0][0]).strip()
                    # image_path = "../Data/fire_record/record_img0.jpg"
                    image = cv2.imread(image_path)  # OpenCV로 이미지 읽기
                    _, buffer = cv2.imencode('.jpg', image)  # 이미지를 바이트 배열로 변환
                    byte_data = buffer.tobytes()
                    length = str(len(byte_data)).ljust(16).encode()
                    try:
                        client_socket.sendall(header + length + byte_data)
                        print("img_record 전송 성공")
                    except Exception as e:
                        print(f"전송 중 오류 발생 : {e}")

        except Exception as e:
            print(f'Error: {e}')
            break

    # 클라이언트 연결 종료 시 저장된 프레임 제거
    with lock:
        if addr in client_frames:
            del client_frames[addr]
    client_socket.close()


# 메인 윈도우 클래스
class WindowClass(QMainWindow, form_class):
    # 초기화 메서드
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        gif_path = "../Data/No_Signal-MOS.gif"  # 기본 이미지 설정
        # wh1 ~ wh4 및 warehouse1 ~ warehouse4에 QMovie 설정
        self.wh1_movie = QMovie(gif_path)
        self.wh2_movie = QMovie(gif_path)
        self.wh3_movie = QMovie(gif_path)
        self.wh4_movie = QMovie(gif_path)
        self.warehouse1_movie = QMovie(gif_path)
        self.warehouse2_movie = QMovie(gif_path)
        self.warehouse3_movie = QMovie(gif_path)
        self.warehouse4_movie = QMovie(gif_path)

        ################ 이벤트
        self.wh1_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.combine1))
        self.wh2_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.combine2))
        self.wh3_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.combine3))
        self.wh4_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.combine4))
        self.all_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.allview))

        logo_pixmap = QPixmap("../Data/fire_logo.png") # 로고 이미지 설정
        self.logo1.setScaledContents(True)
        self.logo2.setScaledContents(True)
        self.logo3.setScaledContents(True)
        self.logo4.setScaledContents(True)
        self.logo5.setScaledContents(True)
        self.logo1.setPixmap(logo_pixmap)
        self.logo2.setPixmap(logo_pixmap)
        self.logo3.setPixmap(logo_pixmap)
        self.logo4.setPixmap(logo_pixmap)
        self.logo5.setPixmap(logo_pixmap)

        # QTimer를 사용해 프레임 업데이트
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frames)
        self.timer.start(1000)  # 30ms마다 업데이트

    def update_frames(self):
        global client_frames, event,client_socket,record_count

        now = datetime.now() # 현재 시간 추출
        with lock:
            frames = list(client_frames.values())
            # 첫 번째 웹캠
            if len(frames) > 0:

                frame1 = frames[0]
                frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)  # OpenCV는 BGR, PyQt는 RGB 사용

                # warehouse1 화면일 때와 wh1 화면일 때 크기 설정
                if self.stackedWidget.currentWidget() == self.combine1:
                    # warehouse1 화면일 때 크기
                    label_width = self.warehouse1.width()
                    label_height = self.warehouse1.height()
                else:
                    # wh1 화면일 때 크기
                    label_width = self.wh1.width()
                    label_height = self.wh1.height()

                resized_frame = cv2.resize(frame1, (label_width, label_height), interpolation=cv2.INTER_AREA)
                h, w, ch = resized_frame.shape
                bytes_per_line = ch * w
                qimg1 = QImage(resized_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                results = model(resized_frame)

                # 탐지 결과가 있는 경우에만 처리
                if results.pred[0].nelement() > 0:  # 결과가 있을 경우
                    for *box, conf, class_id in results.pred[0]:  # 탐지 결과
                        x1, y1, x2, y2 = map(int, box)  # 바운딩 박스 좌표
                        label = f'{model.names[int(class_id)]}: {conf:.2f}'  # 클래스 이름과 신뢰도
                        color = (0, 255, 0)  # 바운딩 박스 색상 (녹색)

                        # 바운딩 박스와 레이블 그리기
                        cv2.rectangle(resized_frame, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(resized_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                        # 클래스가 'fire'인 경우에만 처리
                        if model.names[int(class_id)] == 'fire':
                            if conf >= 0.5:
                                print("1창고 화재감지")  # 신뢰도(conf)가 0.5 이상일 때
                                fire_detect = []
                                recolor_frame = cv2.cvtColor(resized_frame, cv2.COLOR_RGB2BGR)
                                fire_detect.append(recolor_frame)
                                detect_time = now.strftime('%Y-%m-%d %H:%M:%S')
                                print("화재감지시간:" + detect_time)
                                #cv2.imshow("detect",fire_detect[0])
                                cv2.imwrite(f"../Data/fire_record/record_img{record_count}.jpg", fire_detect[0])
                                image_path = f"../Data/fire_record/record_img{record_count}.jpg"
                                log = detect_time + "\n1창고 화재감지" + "\n정확도:" + str(conf)
                                self.loglist.addItem(log)
                                # 데이터베이스에 저장
                                try:
                                    cur.execute("INSERT INTO fire_record (image_path, warehouse) VALUES (%s, %s)",(image_path, 'warehouse1'))
                                    conn.commit()
                                except mariadb.Error as e:
                                    print(f"DB 삽입 오류: {e}")
                                record_count = record_count + 1

                                event = "fire"

                            elif conf >= 0.3:
                                print("차수빈바보")  # 신뢰도(conf)가 0.3 이상 0.5 미만일 때
                            else:
                                print("신뢰도가 낮아 무시됩니다.")  # 신뢰도가 0.3 미만일 때

                self.wh1.setPixmap(QPixmap.fromImage(qimg1))
                self.warehouse1.setPixmap(QPixmap.fromImage(qimg1).copy())
            else:
                self.wh1.setScaledContents(True)
                self.warehouse1.setScaledContents(True)
                self.wh1.setMovie(self.wh1_movie)
                self.warehouse1.setMovie(self.warehouse1_movie)
                self.wh1_movie.start()
                self.warehouse1_movie.start()

            # 두 번째 웹캠
            if len(frames) > 1:
                frame2 = frames[1]
                frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)  # OpenCV는 BGR, PyQt는 RGB 사용
                # warehouse2 화면일 때와 wh2 화면일 때 크기 설정
                if self.stackedWidget.currentWidget() == self.combine2:
                    # warehouse2 화면일 때 크기
                    label_width = self.warehouse2.width()
                    label_height = self.warehouse2.height()
                else:
                    # wh1 화면일 때 크기
                    label_width = self.wh2.width()
                    label_height = self.wh2.height()
                resized_frame = cv2.resize(frame2, (label_width, label_height), interpolation=cv2.INTER_AREA)
                h, w, ch = resized_frame.shape
                bytes_per_line = ch * w
                qimg2 = QImage(resized_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                results = model(resized_frame)
                # 탐지 결과가 있는 경우에만 처리
                if results.pred[0].nelement() > 0:  # 결과가 있을 경우
                    for *box, conf, class_id in results.pred[0]:  # 탐지 결과
                        x1, y1, x2, y2 = map(int, box)  # 바운딩 박스 좌표
                        label = f'{model.names[int(class_id)]}: {conf:.2f}'  # 클래스 이름과 신뢰도
                        color = (0, 255, 0)  # 바운딩 박스 색상 (녹색)
                        # 바운딩 박스와 레이블 그리기
                        cv2.rectangle(resized_frame, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(resized_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                        # 클래스가 'fire'인 경우에만 처리
                        if model.names[int(class_id)] == 'fire':
                            if conf >= 0.5:
                                print("2창고 화재감지")  # 신뢰도(conf)가 0.5 이상일 때
                                fire_detect = []
                                recolor_frame = cv2.cvtColor(resized_frame, cv2.COLOR_RGB2BGR)
                                fire_detect.append(recolor_frame)
                                detect_time = now.strftime('%Y-%m-%d %H:%M:%S')
                                print("화재감지시간:" + detect_time)
                                # cv2.imshow("detect",fire_detect[0])
                                cv2.imwrite(f"../Data/fire_record/record_img{record_count}.jpg", fire_detect[0])
                                image_path = f"../Data/fire_record/record_img{record_count}.jpg"
                                log = detect_time + "\n2창고 화재감지" + "\n정확도:" + str(conf)
                                self.loglist.addItem(log)
                                # 데이터베이스에 저장
                                try:
                                    cur.execute("INSERT INTO fire_record (image_path, warehouse) VALUES (%s, %s)",
                                                (image_path, 'warehouse2'))
                                    conn.commit()
                                except mariadb.Error as e:
                                    print(f"DB 삽입 오류: {e}")
                                record_count = record_count + 1
                                event = "fire"
                            elif conf >= 0.3:
                                print("차수빈바보")  # 신뢰도(conf)가 0.3 이상 0.5 미만일 때
                            else:
                                print("신뢰도가 낮아 무시됩니다.")  # 신뢰도가 0.3 미만일 때
                self.wh2.setPixmap(QPixmap.fromImage(qimg2))
                self.warehouse2.setPixmap(QPixmap.fromImage(qimg2).copy())
            else:
                self.wh2.setScaledContents(True)
                self.warehouse2.setScaledContents(True)
                self.wh2.setMovie(self.wh2_movie)
                self.warehouse2.setMovie(self.warehouse2_movie)
                self.wh2_movie.start()
                self.warehouse2_movie.start()

            # 세 번째 웹캠
            if len(frames) > 2:
                frame3 = frames[2]
                frame3 = cv2.cvtColor(frame3, cv2.COLOR_BGR2RGB)  # OpenCV는 BGR, PyQt는 RGB 사용
                # warehouse2 화면일 때와 wh2 화면일 때 크기 설정
                if self.stackedWidget.currentWidget() == self.combine3:
                    # warehouse2 화면일 때 크기
                    label_width = self.warehouse3.width()
                    label_height = self.warehouse3.height()
                else:
                    # wh1 화면일 때 크기
                    label_width = self.wh3.width()
                    label_height = self.wh3.height()
                resized_frame = cv2.resize(frame3, (label_width, label_height), interpolation=cv2.INTER_AREA)
                h, w, ch = resized_frame.shape
                bytes_per_line = ch * w
                qimg3 = QImage(resized_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                results = model(resized_frame)
                # 탐지 결과가 있는 경우에만 처리
                if results.pred[0].nelement() > 0:  # 결과가 있을 경우
                    for *box, conf, class_id in results.pred[0]:  # 탐지 결과
                        x1, y1, x2, y2 = map(int, box)  # 바운딩 박스 좌표
                        label = f'{model.names[int(class_id)]}: {conf:.2f}'  # 클래스 이름과 신뢰도
                        color = (0, 255, 0)  # 바운딩 박스 색상 (녹색)
                        # 바운딩 박스와 레이블 그리기
                        cv2.rectangle(resized_frame, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(resized_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                        # 클래스가 'fire'인 경우에만 처리
                        if model.names[int(class_id)] == 'fire':
                            if conf >= 0.5:
                                print("3창고 화재감지")  # 신뢰도(conf)가 0.5 이상일 때
                                fire_detect = []
                                recolor_frame = cv2.cvtColor(resized_frame, cv2.COLOR_RGB2BGR)
                                fire_detect.append(recolor_frame)
                                detect_time = now.strftime('%Y-%m-%d %H:%M:%S')
                                print("화재감지시간:" + detect_time)
                                # cv2.imshow("detect",fire_detect[0])
                                cv2.imwrite(f"../Data/fire_record/record_img{record_count}.jpg", fire_detect[0])
                                image_path = f"../Data/fire_record/record_img{record_count}.jpg"
                                log = detect_time + "\n3창고 화재감지" + "\n정확도:" + str(conf)
                                self.loglist.addItem(log)
                                # 데이터베이스에 저장
                                try:
                                    cur.execute("INSERT INTO fire_record (image_path, warehouse) VALUES (%s, %s)",
                                                (image_path, 'warehouse3'))
                                    conn.commit()
                                except mariadb.Error as e:
                                    print(f"DB 삽입 오류: {e}")
                                record_count = record_count + 1
                                event = "fire"
                            elif conf >= 0.3:
                                print("차수빈바보")  # 신뢰도(conf)가 0.3 이상 0.5 미만일 때
                            else:
                                print("신뢰도가 낮아 무시됩니다.")  # 신뢰도가 0.3 미만일 때
                self.wh3.setPixmap(QPixmap.fromImage(qimg3))
                self.warehouse3.setPixmap(QPixmap.fromImage(qimg3).copy())
            else:
                self.wh3.setScaledContents(True)
                self.warehouse3.setScaledContents(True)
                self.wh3.setMovie(self.wh3_movie)
                self.warehouse3.setMovie(self.warehouse3_movie)
                self.wh3_movie.start()
                self.warehouse3_movie.start()

            # 네 번째 웹캠
            if len(frames) > 3:
                frame4 = frames[3]
                frame4 = cv2.cvtColor(frame4, cv2.COLOR_BGR2RGB)  # OpenCV는 BGR, PyQt는 RGB 사용
                # warehouse2 화면일 때와 wh2 화면일 때 크기 설정
                if self.stackedWidget.currentWidget() == self.combine4:
                    # warehouse2 화면일 때 크기
                    label_width = self.warehouse4.width()
                    label_height = self.warehouse4.height()
                else:
                    # wh1 화면일 때 크기
                    label_width = self.wh4.width()
                    label_height = self.wh4.height()
                resized_frame = cv2.resize(frame4, (label_width, label_height), interpolation=cv2.INTER_AREA)
                h, w, ch = resized_frame.shape
                bytes_per_line = ch * w
                qimg4 = QImage(resized_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                results = model(resized_frame)
                # 탐지 결과가 있는 경우에만 처리
                if results.pred[0].nelement() > 0:  # 결과가 있을 경우
                    for *box, conf, class_id in results.pred[0]:  # 탐지 결과
                        x1, y1, x2, y2 = map(int, box)  # 바운딩 박스 좌표
                        label = f'{model.names[int(class_id)]}: {conf:.2f}'  # 클래스 이름과 신뢰도
                        color = (0, 255, 0)  # 바운딩 박스 색상 (녹색)
                        # 바운딩 박스와 레이블 그리기
                        cv2.rectangle(resized_frame, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(resized_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                        # 클래스가 'fire'인 경우에만 처리
                        if model.names[int(class_id)] == 'fire':
                            if conf >= 0.5:
                                print("4창고 화재감지")  # 신뢰도(conf)가 0.5 이상일 때
                                fire_detect = []
                                recolor_frame = cv2.cvtColor(resized_frame, cv2.COLOR_RGB2BGR)
                                fire_detect.append(recolor_frame)
                                detect_time = now.strftime('%Y-%m-%d %H:%M:%S')
                                print("화재감지시간:" + detect_time)
                                # cv2.imshow("detect",fire_detect[0])
                                cv2.imwrite(f"../Data/fire_record/record_img{record_count}.jpg", fire_detect[0])
                                image_path = f"../Data/fire_record/record_img{record_count}.jpg"
                                log = detect_time + "\n4창고 화재감지" + "\n정확도:" + str(conf)
                                self.loglist.addItem(log)
                                # 데이터베이스에 저장
                                try:
                                    cur.execute("INSERT INTO fire_record (image_path, warehouse) VALUES (%s, %s)",
                                                (image_path, 'warehouse4'))
                                    conn.commit()
                                except mariadb.Error as e:
                                    print(f"DB 삽입 오류: {e}")
                                record_count = record_count + 1
                                event = "fire"
                            elif conf >= 0.3:
                                print("차수빈바보")  # 신뢰도(conf)가 0.3 이상 0.5 미만일 때
                            else:
                                print("신뢰도가 낮아 무시됩니다.")  # 신뢰도가 0.3 미만일 때
                self.wh4.setPixmap(QPixmap.fromImage(qimg4))
                self.warehouse4.setPixmap(QPixmap.fromImage(qimg4).copy())
            else:
                self.wh4.setScaledContents(True)
                self.warehouse4.setScaledContents(True)
                self.wh4.setMovie(self.wh4_movie)
                self.warehouse4.setMovie(self.warehouse4_movie)
                self.wh4_movie.start()
                self.warehouse4_movie.start()

# 서버 설정
HOST = '10.10.20.113'
PORT = 9999

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()

print('서버 시작')

if __name__ == "__main__":
    start_new_thread(lambda: [start_new_thread(threaded, server_socket.accept()) for _ in iter(int, 1)], ())
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()

server_socket.close()