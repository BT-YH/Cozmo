import numpy as np
from PIL import Image, ImageChops
import cv2

sum = np.sum([5, 3])
print(sum) # should be 8



img1 = Image.open("./images/rotation_330.jpeg")
img1 = np.array(img1)

img2 = Image.open("./images/rotation_345.jpeg")
img2 = np.array(img2)

'''
print(img2)

dimensions1 = img1.astype("float").shape
print(dimensions1)


img2 = cv2.resize(img2, (dimensions1[1], dimensions1[0]))
dimensions2 = img2.astype("float").shape
print(dimensions2)

err = np.sum((img1.astype("float") - img2.astype("float")) ** 2)
err /= dimensions1[0] * dimensions1[1] * dimensions1[2]
print(err)
'''

img3 = ImageChops.difference(img1, img2);
img3 = np.array(img3)
cv2.imwrite("./test.jpeg", img3)

print(ImageChops.difference(img1, img2))