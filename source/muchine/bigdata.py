import numpy as np


# x1 = np.add(1,2)
# print(x1)
#
#
# x2 = np.add([1],[2])
# print(x2)
#
#
# x3 = np.add([[1]],[[2]])
# print(x3)
#
#
# x4 = np.add([[1,2]], [[3], [4]])
# print(x4)
#
#
# x5 = np.array([[1,2]]) + np.array([[3], [4]])
# print(x5)
#
#
# print([1] + [2])


x1 = np.zeros(4)
print(x1)


x2 = np.ones((1,4), dtype=np.int32)
print(x2)


x3 = np.arange(1, 9, dtype="int64").reshape((2,4))
print(x3)
print(x3[0])
print(x3[0][0])
print(x3[0][1:3])
print(np.sum(x3))
print(np.mean(x3))
print(np.var(x3))
print(np.max(x3))
print(np.argmax(x3))

