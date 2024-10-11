import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.datasets import load_wine
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


load_data = load_wine()
df = pd.DataFrame(load_data.data, columns=load_data.feature_names)
df["target"] = load_data.target
print(df.head())
print(df.columns)

# 위 df를 이용하여 Linear Regression을 진행하고 모델을 평가하라.
# 계산을 위한 랜덤seed는 0으로 고정
np.random.seed(0)

x = df[df.columns[:-1]]
y = df['target']

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, shuffle=True)

model = LinearSVC()
model.fit(x_train, y_train)

print(model.coef_)
print(model.score(x_test, y_test))