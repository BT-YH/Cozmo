from PIL import Image
import cv2
import os
import cozmo
import time
from cozmo.util import degrees
import random
import mcl
import stitching

#image_dict = {}

def take_pic(robot: cozmo.robot.Robot):
    action1 = robot.say_text("taking pictures", in_parallel=True)
    action2 = robot.set_lift_height(0, in_parallel=True)
    action3 = robot.set_head_angle((degrees(35)), in_parallel=True)
    action1.wait_for_completed()
    action2.wait_for_completed()
    action3.wait_for_completed()
    robot.camera.image_stream_enabled = True
    
    directory_name = 'images'
    if not os.path.exists(directory_name):
        os.mkdir(directory_name)
    
    degree_increment = 10
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
    
    action4 = robot.say_text("finished", in_parallel=True)
    action5 = robot.set_lift_height(1, in_parallel=True)
    action4.wait_for_completed()
    action5.wait_for_completed()
    
# Turns the robot a random amount simulating a kidnapping robot problem
def randomTurn(robot: cozmo.robot.Robot):
  # Enabling Cozmo Camera
  robot.camera.image_stream_enabled = True
  # Rotate a random degree
  deg = random.randint(0, 60)  
  robot.turn_in_place(degrees(deg + 60)).wait_for_completed()
    
  # Take a picture and save as "latestImage"
  latest_image = robot.world.latest_image
  annotated = latest_image.annotate_image()
  if latest_image is not None:
    converted = annotated.convert()
    converted.save("latestImage.jpeg", "JPEG", resolution=10)
  robot.say_text("Oh Noooooooo they kidnapped me").wait_for_completed()
  return deg

# Signals the program's completion
def madeItHome(robot: cozmo.robot.Robot):
  robot.say_text("Im hoooooooome").wait_for_completed()

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


# Initial set up for the panorama
cozmo.run_program(take_pic)

# Creates the panorama as Panorama.jpeg
stitching.run()
cozmo.run_program(fin_sti)
# 'Kidnaps' the cozmo by turning a random direction
degree = cozmo.run_program(randomTurn)

# Runs Monte Carlo algorithm 
cozmo.run_program(mcl.monte_carlo_localize)

cozmo.run_program(madeItHome)
