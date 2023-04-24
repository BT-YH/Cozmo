import numpy as np
from PIL import Image, ImageChops
import cv2

pano = cv2.imread('./Panorama_0.jpeg')
home = cv2.imread('./images/rotation_0.jpeg')
 
cv2.imshow('home', home)
cv2.imshow('pano', pano)
cv2.waitKey(0)
 
home = home[10:home.shape[1]-10, 10:home.shape[0]-10]
 
cv2.imshow('home', home)
cv2.imshow('pano', pano)
cv2.waitKey(0)
 
w, h = pano.shape[:-1]
 
res = cv2.matchTemplate(pano, home, cv2.TM_CCOEFF_NORMED)
threshold = 0.7
loc = np.where(res >= threshold)
for pt in zip(*loc[::-1]):
    cv2.rectangle(pano, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
           
cv2.imwrite('result.jpeg', pano)

loc = sum(loc[1]) / len(loc)
print(loc)