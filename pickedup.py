import cozmo

def on_robot_picked_up(robot: cozmo.robot.Robot):
    if robot.is_picked_up:
        return True
    else:
        return False

# Connect to the robot and add the event handler
print(cozmo.run_program(on_robot_picked_up))
