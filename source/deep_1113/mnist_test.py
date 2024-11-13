import numpy as np
from keras.models import load_model
from PIL import Image

# 사전 학습된 모델 불러오기
model_path = './MNIST_CNN.keras'  # 경로를 알맞게 설정하세요
model = load_model(model_path)

# 이미지 로드 및 전처리
image_path = './2.jpg'  # 경로를 알맞게 설정하세요
image = Image.open(image_path).convert('L')  # 이미지를 흑백으로 변환
image = image.resize((28, 28))  # 크기를 28x28로 조정

# 색상 반전이 필요하다면 수행 (배경이 흰색이고 숫자가 검정일 때)
image_data = np.array(image)
image_data = 255 - image_data  # 색상 반전이 필요한 경우 수행
image_data = image_data / 255.0  # 데이터 정규화
image_data = image_data.reshape(1, 28, 28, 1)  # 모델에 맞게 데이터 형식 조정

# 예측 수행
prediction = model.predict(image_data)
predicted_class = np.argmax(prediction)  # 가장 높은 확률을 가진 클래스를 선택


print(f"Predicted class: {predicted_class}")