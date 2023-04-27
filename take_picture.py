from PIL import Image
import cv2
import os
import cozmo
import time
from cozmo.util import degrees
import random
import mcl
import stitching
import histogram
import numpy as np


#image_dict = {}

mode = 0


def take_pic(robot: cozmo.robot.Robot):
    action1 = robot.say_text("taking pictures", in_parallel=True)
    action2 = robot.set_lift_height(0, in_parallel=True)
    action3 = robot.set_head_angle((degrees(15)), in_parallel=True)
    action1.wait_for_completed()
    action2.wait_for_completed()
    action3.wait_for_completed()
    robot.camera.image_stream_enabled = True
    
    directory_name = 'images'
    if not os.path.exists(directory_name):
        os.mkdir(directory_name)
    
    degree_increment = 15
    angle = 0
    
    while angle < 360:
        filename = directory_name +'/rotation_' + str(angle) + '.jpeg'
        #robot.say_text(str(int(angle/5))).wait_for_completed()
        latest_image = robot.world.latest_image
        while latest_image is None:
            print('Awaiting first comzo image...')
            time.sleep(1)
            latest_image = robot.world.latest_image

        if latest_image is not None:
            print('image = %s' % latest_image)
            annotated = latest_image.annotate_image()
            converted = annotated.convert()
            converted.save(filename, 'JPEG', resolution=10)
            #image_dict[angle/5] = cv2.cvtColor(cv2.imread(filename), cv2.COLOR_BGR2GRAY)
        
        #print(image_dict[angle%5].shape)
        robot.turn_in_place(degrees(degree_increment)).wait_for_completed()
        angle += degree_increment
    
    robot.say_text("finished").wait_for_completed()
    
# Turns the robot a random amount simulating a kidnapping robot problem
def randomTurn(robot: cozmo.robot.Robot):
  # Enabling Cozmo Camera
  robot.camera.image_stream_enabled = True
  # Rotate a random degree
  deg = random.randint(0, 360)  
  robot.turn_in_place(degrees(deg)).wait_for_completed()
    
  # Take a picture and save as "latestImage"
  latest_image = robot.world.latest_image
  annotated = latest_image.annotate_image()
  if latest_image is not None:
    converted = annotated.convert()
    converted.save("latestImage.jpeg", "JPEG", resolution=10)
  robot.say_text("Displaced").wait_for_completed()

# Signals the program's completion
def madeItHome(robot: cozmo.robot.Robot):
  global mode
  pano = cv2.imread('./Panorama_0.jpeg')
  home = cv2.imread('./images/rotation_0.jpeg')
  home = home[10:home.shape[1]-10, 10:home.shape[0]-10]

  width = pano.shape[1]
  
  res = cv2.matchTemplate(pano, home, cv2.TM_CCOEFF_NORMED)
  threshold = 0.5
  loc = np.where(res >= threshold)
  print(loc)
  home_start = sum(loc[1]) / len(loc[1])

  d = 360 * (mode - home_start) / width
  print()
  print(f"mode: {mode}")
  print(f"diff: {mode - home_start}")
  print(f"degree: {d}")
  print()

  a1 = robot.turn_in_place(degrees(d), in_parallel=True)
  a2 = robot.say_text("Done", in_parallel=True)
  a1.wait_for_completed()
  a2.wait_for_completed()


def rotato(robot: cozmo.robot.Robot):
  # Enabling Cozmo Camera
  robot.camera.image_stream_enabled = True
  # Rotate 5 degrees to the right
  robot.turn_in_place(degrees(5)).wait_for_completed()
    
  # Take a picture and save as "latestImage"
  latest_image = robot.world.latest_image
  annotated = latest_image.annotate_image()
  if latest_image is not None:
    converted = annotated.convert()
    converted.save("latestImage.jpeg", "JPEG", resolution=10)

def fin_sti(robot: cozmo.robot.Robot):
    robot.say_text("Stitched").wait_for_completed()


def on_robot_picked_up(robot: cozmo.robot.Robot):
    while (not robot.is_picked_up):
       time.sleep(.5)
       print("waiting")
       pass

    if (not robot.is_picked_up):
      latest_image = robot.world.latest_image

      while latest_image is None:
        latest_image = robot.world.latest_image
      annotated = latest_image.annotate_image()
      if latest_image is not None:
        converted = annotated.convert()
        converted.save("latestImage.jpeg", "JPEG", resolution=10)



''''''
# Initial set up for the panorama
cozmo.run_program(take_pic)

# Creates the panorama as Panorama.jpeg
stitching.run()
cozmo.run_program(fin_sti)
# 'Kidnaps' the cozmo by turning a random direction
# cozmo.run_program(randomTurn)
''''''

while True:
  cozmo.run_program(on_robot_picked_up)
# Runs Monte Carlo algorithm 
  cozmo.run_program(mcl.monte_carlo_localize)
  mode = mcl.mm
  cozmo.run_program(madeItHome)
  histogram.makeHistogram()