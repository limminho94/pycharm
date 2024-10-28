import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.datasets import load_iris
import seaborn as sns
import matplotlib.pyplot as plt


load_data = load_iris()
df = pd.DataFrame(load_data.data, columns=load_data.feature_names)
df["target"] = load_data.target
print(df.head())

sns.pairplot(df[df.columns[:-1]])
plt.show()
exit()

train_x, test_x, train_y, test_y = train_test_split(df[df.columns[:-1]], df["target"], test_size=0.2, shuffle=True)

model = LinearSVC()
model.fit(train_x, train_y)

print(model.coef_)
print(model.score(test_x, test_y))