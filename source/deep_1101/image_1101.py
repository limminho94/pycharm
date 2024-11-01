import cv2

img = cv2.imread("./data/pish.jpg")
print(img.shape)
print(img)

cv2.imshow("img", img)
cv2.waitKey(0)

