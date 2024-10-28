import os
import pandas as pd
import matplotlib.pyplot as plt
from PIL.ImageColor import colormap


def load_csv(name:str) -> pd.DataFrame:
    try:
        df = pd.read_csv(name, encoding="cp949")
        print(f"'{os.path.basename(name)}'이 로드되었습니다.")
        return df
    except FileNotFoundError as e:
        print("해당 파일이 존재하지 않습니다.")
        return pd.DataFrame("[[]]")


df = load_csv("../data/gender/gender.csv")
# print(df)

size = []

name = input('지역이름검색 : ')
for index, row in df.iterrows():
    if name in row[0]:
        m = 0
        f = 0
        for i in range(101):
            m += int(row[i+3])
            f += int(row[i+106])
        break
size.append(m)
size.append(f)

color = ['red', 'blue']

plt.pie(size, labels=['m', 'f'], autopct='%.1f%%', colors=color, startangle=90)
plt.title(' title name')
plt.show()

