#!/usr/bin/python
#code needed to stitch images together 
import cv2
import imutils
import numpy as np


def run():
  print("\n\n\n!!!!! STITCH !!! \n\n\n\n")
  images = []
  #standardX, standardY = 500, 500
  for i in range(24):
    image = cv2.imread('./images/rotation_' + str((i * 15)) +'.jpeg')
    #if image is not None:
    images.append(image)

  stitcher = cv2.Stitcher_create()
  
  #(ret,pano) = stitcher.stitch(images[0], images[1])
  #cv2.imwrite('./Panorama.jpeg',pano)

  try:
    '''
    for i in range(2, 24):
      pano = cv2.imread('./Panorama.jpeg')
      (ret,pano) = stitcher.stitch(images[i], pano)
      cv2.imwrite('./Panorama.jpeg',pano)
    '''
    (ret,pano_0) = stitcher.stitch(images)
    #pano_0 = reshape(pano_0)
    #cv2.imshow(pano_0)
    cv2.imwrite('./Panorama_0.jpeg',pano_0)


    new_images = []
    for i in images[7:20]:
      new_images.append(i)
    (ret,pano_1) = stitcher.stitch(new_images)
    #pano_1 = reshape(pano_1)
    cv2.imwrite('./Panorama_1.jpeg',pano_1)

  except Exception as e:
    print(e)

def reshape(stitched):
  stitched = cv2.copyMakeBorder(stitched, 10, 10, 10, 10, cv2.BORDER_CONSTANT, (0, 0, 0))
  gray = cv2.cvtColor(stitched, cv2.COLOR_BGR2GRAY)
  thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)[1]
  cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  cnts = imutils.grab_contours(cnts)
  c = max(cnts, key=cv2.contourArea)
  
  mask = np.zeros(thresh.shape, dtype="uint8")
  (x, y, w, h) = cv2.boundingRect(c)
  cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)

  minRect = mask.copy()
  sub = mask.copy()

  while cv2.countNonZero(sub) > 0:
    minRect = cv2.erode(minRect, None)
    sub = cv2.subtract(minRect, thresh)

  cnts = cv2.findContours(minRect.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  cnts = imutils.grab_contours(cnts)
  c = max(cnts, key=cv2.contourArea)
  (x, y, w, h) = cv2.boundingRect(c)
  stitched = stitched[y:y + h, x:x + w]

  return stitched

run()