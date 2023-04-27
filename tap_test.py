
import cozmo
import asyncio


def sayGoodBye(robot: cozmo.robot.Robot):
    robot.say_text("Adieu!").wait_for_completed()

def my_ontap_handler(evt, *, obj, tap_count, **kwargs):
    cozmo.run_program(sayGoodBye)

async def cozmo_program(robot: cozmo.robot.Robot):

    robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)

    robot.world.wait_for_observed_light_cube(timeout=60)

    await cozmo.world.World.connect_to_cubes(robot)
    # Create a dispatcher and register an event handler for the EvtObjectTapped event
    dispatcher = cozmo.event.Dispatcher(robot, loop=asyncio.get_event_loop())
    # Connect to Cozmo and add a cube tap event listener
    dispatcher.add_event_handler(cozmo.objects.EvtObjectTapped, my_ontap_handler)
    while True:
        await asyncio.sleep(0)

# Start the program and wait for the cube to be tapped
#cozmo.run_program(cozmo_program)