import os
import pandas as pd
import matplotlib.pyplot as plt


def load_csv(name:str) -> pd.DataFrame:
    try:
        df = pd.read_csv(name, encoding="cp949")
        print(f"'{os.path.basename(name)}'이 로드되었습니다.")
        return df
    except FileNotFoundError as e:
        print("해당 파일이 존재하지 않습니다.")
        return pd.DataFrame("[[]]")


m = []
f = []

df = load_csv("../data/gender/gender.csv")
# print(df.columns)
name = input('지역이름검색 : ')
for index, row in df.iterrows():
    if name in row[0]:
        for i in row[3:104]:
            f.append(-int(i))
        for i in row[106:]:
            m.append(int(i))
        break


plt.style.use('ggplot')
plt.figure(figsize=(10,5))
plt.title('area gender percent')
plt.barh(range(101), m, label='male')
plt.barh(range(101), f, label='female')
plt.legend()
plt.show()
