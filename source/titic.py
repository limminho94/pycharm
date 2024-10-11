import pandas as pd
import matplotlib.pyplot as plt


path = "../data/titanic/titanic.csv"
df = pd.read_csv(path, encoding="cp949")
size = []
# print(df)
# print(df.columns)
save_male = len(df[(df['Survived'] == 1) & (df['Sex'] == 'male')])
save_female = len(df[(df['Survived'] == 1) & (df['Sex'] == 'female')])
# print(save_male, save_female)

size.append(save_male)
size.append(save_female)
size.append(3)
print(size)
plt.title("survive gender")
plt.pie(size, labels=('male','female','hybrid') , autopct='%.1f%%', colors=('green','blue','pink'), startangle=90)
plt.show()