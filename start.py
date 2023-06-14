import carla
import random
import time
import threading

# Connect to the client and retrieve the world object
client = carla.Client('localhost', 2000)
world = client.get_world()
tm = client.get_trafficmanager()
settings = world.get_settings()
settings.synchronous_mode = True
settings.fixed_delta_seconds = 0.1
# After that, set the TM to sync mode
tm.set_synchronous_mode(True)
tm.set_hybrid_physics_mode(True)
# Retrieve the spectator object
spectator = world.get_spectator()

# Get the location and rotation of the spectator through its transform


# Set the spectator with an empty transform
spectator.set_transform(carla.Transform())

# Get the blueprint library and filter for the vehicle blueprints
vehicle_blueprints = world.get_blueprint_library().filter('*vehicle*')

# Get the map's spawn points
spawn_points = world.get_map().get_spawn_points()

# Spawn 50 vehicles randomly distributed throughout the map
# for each spawn point, we choose a random vehicle from the blueprint library
for i in range(0,50):
    world.try_spawn_actor(random.choice(vehicle_blueprints), random.choice(spawn_points))
    
ego_bp = world.get_blueprint_library().find('vehicle.lincoln.mkz_2020')

ego_bp.set_attribute('role_name', 'hero')

ego_vehicle = world.spawn_actor(ego_bp, random.choice(spawn_points))

# Create a transform to place the camera on top of the vehicle
camera_init_trans = carla.Transform(carla.Location(z=2))
camera_back_trans = carla.Transform(carla.Location(x=-2,z=2),carla.Rotation(yaw=180))
camera_frontL_trans = carla.Transform(carla.Location(y=-1,z=2),carla.Rotation(yaw=-55))
camera_frontR_trans = carla.Transform(carla.Location(y=1,z=2),carla.Rotation(yaw=55))
camera_backL_trans = carla.Transform(carla.Location(x=-1,y=-1,z=2),carla.Rotation(yaw=-110))
camera_backR_trans = carla.Transform(carla.Location(x=-1,y=1,z=2),carla.Rotation(yaw=110))
camera_top_trans = carla.Transform(carla.Location(z=10),carla.Rotation(pitch=270))

# We create the camera through a blueprint that defines its properties
camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')
camera_bp.set_attribute('image_size_x', '1600')
camera_bp.set_attribute('image_size_y', '900')
camera_bp.set_attribute('fov', '75')
# Set the time in seconds between sensor captures
camera_bp.set_attribute('sensor_tick', '0.1')
camera_bp.set_attribute('iso', '2000')
camera_bp.set_attribute('motion_blur_intensity', '0')
camera_bp.set_attribute('shutter_speed', '4000')

# We spawn the camera and attach it to our ego vehicle
cameraFL = world.spawn_actor(camera_bp, camera_frontL_trans, attach_to=ego_vehicle)
cameraFR = world.spawn_actor(camera_bp, camera_frontR_trans, attach_to=ego_vehicle)
cameraBL = world.spawn_actor(camera_bp, camera_backL_trans, attach_to=ego_vehicle)
cameraBR = world.spawn_actor(camera_bp, camera_backR_trans, attach_to=ego_vehicle)

camera_bp.set_attribute('fov', '120')
camera = world.spawn_actor(camera_bp, camera_init_trans, attach_to=ego_vehicle)
cameraB = world.spawn_actor(camera_bp, camera_back_trans, attach_to=ego_vehicle)
camera_bp.set_attribute('image_size_x', '1600')
camera_bp.set_attribute('image_size_y', '1800')
cameraT = world.spawn_actor(camera_bp, camera_top_trans, attach_to=ego_vehicle)

camera.listen(lambda image: image.save_to_disk('./out/%06d.png' % image.frame))
cameraB.listen(lambda image: image.save_to_disk('./outB/%06d.png' % image.frame))
cameraT.listen(lambda image: image.save_to_disk('./outT/%06d.png' % image.frame))
cameraFL.listen(lambda image: image.save_to_disk('./outFL/%06d.png' % image.frame))
cameraFR.listen(lambda image: image.save_to_disk('./outFR/%06d.png' % image.frame))
cameraBL.listen(lambda image: image.save_to_disk('./outBL/%06d.png' % image.frame))
cameraBR.listen(lambda image: image.save_to_disk('./outBR/%06d.png' % image.frame))

for vehicle in world.get_actors().filter('*vehicle*'):
    vehicle.set_autopilot(True)
#    tm.update_vehicle_lights(vehicle, True)

def set_spectator_location(world, vehicle, camera_transform):
    spectator = world.get_spectator()
    world_snapshot = world.wait_for_tick()

    # Get the state of the vehicle
    vehicle_transform = vehicle.get_transform()

    # Calculate the final transform of the spectator
    spectator_transform = carla.Transform(vehicle_transform.location + camera_transform.location, camera_transform.rotation)

    # Set the spectator's transform
    spectator.set_transform(spectator_transform)

# Create a camera transform
camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))

def update_spectator():
   while True:
    set_spectator_location(world, ego_vehicle, camera_transform)
    world.tick()

# Start a new thread that runs the update_spectator function
threading.Thread(target=update_spectator).start()

world.apply_settings(settings)
while True:
    world.tick()

#settings.synchronous_mode = False
#tm.set_synchronous_mode(False)
