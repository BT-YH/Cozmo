#!/usr/bin/python

#import take_picture as tp
from string import hexdigits
import cv2
import pandas as pd
import random
import cozmo
import pycozmo
from cozmo.util import degrees, distance_mm, speed_mmps
import numpy as np
from PIL import Image
import math 
from scipy import stats as st
from PIL import ImageChops

mm = 0

def main(robot: cozmo.robot):
    #tp.take_pictures(robot)
    #robot.add_event_handler(pycozmo.event.EvtRobotPickedUpChange, on_movement)
    monte_carlo_localize(robot)

def on_movement(robot: cozmo.robot.Robot, event, **kw):
    latest_image = robot.world.latest_image
    while latest_image is None:
      latest_image = robot.world.latest_image

    annotated = latest_image.annotate_image()
    if latest_image is not None:
      converted = annotated.convert()
      converted.save("latestImage", "JPEG", resolution=10)

# Arbitrary values, to model gaussian noise.
sensorVariance = 0.01
proportionalMotionVariance = 0.01

def monte_carlo_localize(robot: cozmo.robot.Robot):
  robot.set_head_angle((degrees(15))).wait_for_completed()
  robot.set_lift_height(0).wait_for_completed()
  robot.say_text("starting mcl").wait_for_completed()

  panoPixelArray = cv2.imread("Panorama_0.jpeg")
  panoPixelArray.astype("float")
  dimensions = panoPixelArray.shape
  width = dimensions[1]
  #hieght = dimensions[0]
  # Initialize cozmo camera
  robot.camera.image_stream_enabled = True
  pixelWeights = [] # predictions

  # Algorithm MCL Line 2
  # fill array with uniform values as starting predictions at initialize
  particles = []  # starts as randomized particles, aka guesses for where the robot is facing
  M = 100   # Number of particles
  i = 0     # Iterations

  dist = width // M
  f = dist
  while i < M:
    particles.append(f)
      # particles.append(random.randint(0, width))
    f += dist
    i += 1

  # Saves preliminary predictions to a dataframe
  pointFrame = pd.DataFrame(particles, columns=['particles'])
  
  i = 0
  while i < 10: # time steps is arbitrary
    # NEED TO calculate random movement
    # Rotate 10 degrees to right
    robot.turn_in_place(degrees(-10.0)).wait_for_completed()
    cv_cozmo_image2 = None
    latest_image = robot.world.latest_image
    while latest_image is None:
      latest_image = robot.world.latest_image

    annotated = latest_image.annotate_image()
    if latest_image is not None:
      converted = annotated.convert()
      converted.save("latestImage.jpeg", "JPEG", resolution=10)
    cozmo_image2 = latest_image.annotate_image(scale=None, fit_size=None, resample_mode=0)
    # Storing pixel RGB values in a 3D array
    cv_cozmo_image2 = np.array(cozmo_image2)

    # empty arrays that hold population number, and weight
    pixelPopulationNumber = []
    pixelWeights = []

    # empty that can hold new population, temp array list for the one above
    newParticles = []

    # Algorithm MCL Line 3
    for pose in particles:
      # Algorithm MCL Line 4
      newPose = sample_motion_model(pose, width, width / 36)
      # Algorithm MCL line 5:
      # map is [0, 1] interval space for movement, sensing distance from 0
      weight = measurement_model(cv_cozmo_image2, newPose) 
      #weight = weight if weight > 0 else 0.001

      # Algorithm MCL line 6:
      pixelWeights.append(weight)
      pixelPopulationNumber.append(newPose)

    # Compute probabilities (proportional to weights) and cumulative distribution function for sampling of next pose population
    # NOTE: This is the heart of weighted resampling that is _not_ given in the text pseudocode.
    # - first sum weights

    # sum all weight, create new array size M, calculate probability
    sum_weights = 0.0
    for pixel in pixelWeights:
      sum_weights += pixel
    probabilities = []

    for m in pixelWeights:
      probabilities.append(m / sum_weights)

    #Cumulative Distribution Function
    cdf = []
    sum_prob = 0

    for prob in probabilities:
        sum_prob += prob
        cdf.append(sum_prob)
    # cdf[len(probabilities)] = 1.0 last is always 1.0

   # redistribute population to newX

     #Algorithm MCL line 8:
   #resampling
    for m in range(M):
        p = random.uniform(0, 1)
        index = 0
        while p >= cdf[index]:
            index += 1
        newParticles.append(pixelPopulationNumber[index])
    particles = newParticles
    i += 1
    np_particles = np.array(particles)
    print("\n\n")
    print("guess: ")
    print(st.mode(np_particles))
    print("\n\n")

  newParticles.sort()

  # updating the CSV file with the original predictions and the newest predictions
  df = pd.DataFrame(newParticles, columns = ['newParticles'])
  df = df.join(pointFrame) # joins new predictions with original predictions
  df = df.sort_values(by=['newParticles'], ascending=False)
  df.to_csv("data/data.csv", index = False)


  robot.say_text("Finshing mcl").wait_for_completed()
  global mm
  mm = particles[find_groups(10, particles)]


def sample_motion_model(xPixel, width, dist):
  # making variance proportional to magnitude of motion command
  newX = xPixel - dist + sample_normal_distribution(abs(dist * proportionalMotionVariance))
  if newX < 0 or newX > width:
    if newX < 0:
       return width + newX
    else:
       return newX - width
  else:
     return newX

# map in this case is [0, 1] allowable poses
def measurement_model(latestImage, particlePose):
    # Gaussian (i.e. normal) error, see https://en.wikipedia.org/wiki/Normal_distribution
    # same as p_hit in Figure 6.2(a), but without bounds. Table 5.2
  img = Image.open("./Panorama_0.jpeg")
  width, height = img.size
  #get the slice of the panorama that corresponds to the pixel
  image1 = slice(img, particlePose, 160, 160, height)
  image2 = latestImage
  #compare how similar/different they are using MSE

  cv2.imwrite("./image1.jpeg", image1)
  cv2.imwrite("./image2.jpeg", image2)

  image1 = Image.open("./image1.jpeg")
  image2 = Image.open("./image2.jpeg")

  diff = compare_images(image1, image2)
  print(f"diff: {diff}")
  #see Text Table 5.2, implementation of probability normal distribution
  result = (1.0 / math.sqrt(2 * math.pi * sensorVariance)) * math.exp(- (diff * diff) / (2 * sensorVariance))
  # print(f"Left: {(1.0 / math.sqrt(2 * math.pi * sensorVariance))} ")
  # print(f"Right: {math.exp(- (diff * diff) / (2 * sensorVariance)) }")
  print(f"Result:  {result}")
  print()
  return result

#see Text Table 5.4, implementation of sample normal distribution
def sample_normal_distribution(variance):
  b = math.sqrt(variance)
  sum = 0
  for i in range(12):
    sum += (random.random() + random.random() - 1) * b
  return sum / 2.0

# Compares images by pixels using Mean Squared Error formula
def compare_images(imageA, imageB):
  # See https://en.wikipedia.org/wiki/Mean_squared_error 
  '''
  dimensions = imageA.astype("float").shape
  width = dimensions[1]
  height = dimensions[0]
  err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
  # Dividing the values so they fit 
  err /= (width * height * dimensions[2]) ** 2
  # print(f"Error:  {err}")
  '''

  dif = ImageChops.difference(imageA, imageB)
  dif = np.array(dif)
  dimensions = dif.astype("float").shape
  width = dimensions[1]
  length = dimensions[0]
  height = dimensions[2]


  return 200 * np.mean(dif) / (width * length)

  #return err

# Creates a slice of the panorama to compare to latestImage
def slice(imgName, center, pixelLeft, pixelRight, height):
  # slice an image into parts height wide
  # initialize boundaries
  img = Image.open("./Panorama_0.jpeg")
  width, height = img.size
  left = center - pixelLeft
  right = center + pixelRight
  slice_width = pixelLeft + pixelRight

  # if we go out of bounds set the limit to be the bounds of the image
  if center < pixelLeft:
      left = 0
      right = 360
  if center > (width - pixelRight):
      right = width
      left = width - 360

  # newImgSize = dim(center - 20, center + 20)
  upper = 0

  lower = height
  # box with boundaries6
  bbox = (left, upper, right, lower)
  sliced_image = img.crop(bbox)
  cv_sliced = np.array(sliced_image)
  # save the slice

  cv2.imwrite("Sliced.jpeg", cv_sliced)
  return cv_sliced
  
def find_groups(diff, particles):
  groups = [[]] * len(particles)
  for i in range(len(particles)):
    groups[i].append(particles[i])
    for f in range(i+1, len(particles)):
        if (abs(particles[i] - particles[f]) < diff):
          groups[i].append(particles[f])
          groups[f].append(particles[i])

  max = 0
  max_index = -1
  for i in range(len(groups)):
    if len(groups[i]) > max:
      max = len(groups[i])
      print(f"Group Length: {max}")
      max_index = i
  return max_index
     
# TO-DO

  #locate in panorama if it has gone a full 360
  #if pixels then knowing what is the point where things cycle around is important
  #subtract that number of pixels to wrap it around

  #MCL motion model
  #update poses when cozmo turns during monte carlo localization
  #need to update pixels by how many pixels 10 would move you

  #Histogram
  #not seeing density around spikes

  #slice
  #needs to wrap around if at one end or the other

  #figure out units for panorama so that motion model
  #(which should be wrapping around)
  #turning in degrees but units should be pixels
  #can't wrap around until we know...
  #what we are calling pixel

  #something that would print out where it thinks it is at 
  #and where it is facing as a demonstration of localization


#cozmo.run_program(main)