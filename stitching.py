#!/usr/bin/python
#code needed to stitch images together 
import cv2
def run():
  print("\n\n\n!!!!! STITCH !!! \n\n\n\n")
  images = []
  standardX, standardY = 500, 500
  for i in range(36):
    image = cv2.imread('./images/rotation_' + str((i * 10)) +'.jpeg')
    if image is not None:
      images.append(cv2.resize(image, (0,0), fx=standardX/image.shape[0], fy=standardY/image.shape[1]))

  stitcher = cv2.Stitcher_create()
  try:
    (ret,pano) = stitcher.stitch(images)
    cv2.imwrite('./Panorama.jpeg',pano)
  except Exception as e:
    print(e)

run()