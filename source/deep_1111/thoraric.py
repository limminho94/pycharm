# 텐서플로 라이브러리 안에 있는 케라스 API에서 필요한 함수들을 불러온다
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# 데이터를 다루는 데 필요한 라이브러리를 불러온다
import numpy as np

# 깃허브에 준비된 데이터를 가져온다
# !git clone https://github.com/taehojo/data.git

# 준비된 수술 환자 데이터를 불러온다
Data_set = np.loadtxt("../../data/thorari/ThoraricSurgery3.csv", delimiter=",")


X = Data_set[:,0:16]    # 환자의 진찰 기록을 X로 지정한다
y = Data_set[:,16]      # 수술 1년 후 사망/생존 여부를 Y로 지정한다

# 딥러닝 모델의 구조를 결정한다
model = Sequential()
model.add(Dense(30, input_dim=16, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

# 딥러닝 모델을 실행한다
model.compile(loss='binary_crossentropy', optimizer='adam',metrics=['accuracy'])
history = model.fit(X, y, epochs=5, batch_size=16)
