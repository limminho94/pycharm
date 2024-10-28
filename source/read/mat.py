import cv2
import mat.pyplot as plt  # pyplot 모듈 임포트

image = cv2.imread("images/matplot.jpg", cv2.IMREAD_COLOR)  # 영상 읽기
if image is None: raise Exception("영상파일 읽기 에러")  # 예외처리

rows, cols = image.shape[:2]  # 영상 크기 정보
rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # 컬러 공간변환
gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # 명암도 영상 변환

fig = plt.figure(num=1, figsize=(3,4))  # 그림 생성
plt.imshow(image), plt.title("figure1- original(bgr)")  # 그림표시 및 제목
plt.axis('off'), plt.tight_layout()  # 축 없음, 여백 없음

fig = plt.figure(figsize=(6,4))  # 그림 생성
plt.suptitle("figure2- pyplot image display")  # 전체 제목 지정
plt.subplot(1,2,1), plt.imshow(rgb_img)  # 서브 플롯 그림
plt.axis([0, cols, rows, 0]), plt.title("rgb color")  # 축 범위, 서브 플롯 제목
plt.subplot(1,2,2), plt.imshow(gray_img, cmap='gray')  # 서브 플롯 그림, 명암도로 표시
plt.title("gray_img2")

plt.show()  # 전체 그림 띄우기