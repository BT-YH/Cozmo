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
    (ret,pano_0) = stitcher.stitch(images)
    cv2.imwrite('./Panorama_0.jpeg',pano_0)

  except Exception as e:
    print(e)

# run()