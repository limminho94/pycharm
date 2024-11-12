# 필요한 라이브러리를 불러온다.
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 피마 인디언 당뇨병 데이터셋을 불러온다.
df = pd.read_csv('../../data/indians/pima-indians-diabetes3.csv')

# 0 ~ 4까지 행을 출력한다
# print(df.head(5))
# 당뇨환자 수
# print(df["diabetes"].value_counts())
# 정보별 특징
# print(df.describe())
# 각 항목별 상관관계
print(df.corr())

# 상관관계를 그래프로 표현
colormap = plt.cm.gist_heat # 그래프의 색상 구성을 정한다
plt.figure(figsize=(12,12)) # 그래프의 크기를 정한다

# 두 항목 간의 상관관계를 그래프로 출력
sns.heatmap(df.corr(), linewidths=0.1, vmax=0.5, cmap=colormap, linecolor='white', annot=True)
# plt.show()

# plasms, BMI 항목의 당뇨여부
plt.hist(x=[df.plasma[df.diabetes==0], df.plasma[df.diabetes==1]], bins=30, histtype='barstacked', label=['normal','diabetes'])
plt.legend()
plt.show()
plt.hist(x=[df.bmi[df.diabetes==0], df.bmi[df.diabetes==1]], bins=30, histtype='barstacked', label=['normal','diabetes'])
plt.legend()
plt.show()

