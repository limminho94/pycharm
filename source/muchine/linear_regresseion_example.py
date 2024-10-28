from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import numpy as np


a = 0.2
u = 10 * np.random.normal(size=(500, ))

x = np.arange(1, 501)
y = a * x + u

plt.scatter(x, y)
plt.show()

x = x.reshape(-1, 1)
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, shuffle=True)

plt.scatter(x_train, y_train)
plt.scatter(x_test, y_test)
plt.show()
# exit()


model = LinearRegression()
model = model.fit(x_train, y_train)

print(model.coef_)
print(model.score(x_test, y_test))



