from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score

import pandas as pd

# 광물 데이터를 불러온다
df = pd.read_csv('../../data/sonar/sonar3.csv',header=None)
# print(df)

# 음파 관련 속성은 X, 광물의 종류는 y로 저장한다.
X = df.iloc[:,0:60]
y = df.iloc[:,60]

k = 5

kfold = KFold(n_splits=k, shuffle=True)

acc_score = []

def model_fn():
    model = Sequential()
    model.add(Dense(24, input_dim=60, activation='relu'))
    model.add(Dense(10, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    return model

for train_index, test_index in kfold.split(X):
    X_train, X_test = X.iloc[train_index,:], X.iloc[test_index,:]
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]

    model = model_fn()
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    history = model.fit(X_train, y_train, epochs=200, batch_size=10, verbose=0)

    accuracy = model.evaluate(X_test, y_test)[1]
    acc_score.append(accuracy)

avg_acc_score = sum(acc_score) / k

print('정확도: ', acc_score)
print('정확도 평균: ', avg_acc_score)


