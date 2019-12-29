import numpy as np
import struct
import TCPClient
import AUTO_calibration_process
import time
import pyrealsense2 as rs

# Create a pipeline for camera
pipeline = rs.pipeline()

# Create a config and configure the pipeline to stream
#  different resolutions of color and depth streams
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
profile = pipeline.start(config)

# Getting the depth sensor's depth scale (see rs-align example for explanation)
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
print("Depth Scale is: ", depth_scale)

# connect with ITRI PC
client = TCPClient.TCPClient()

N_points = 20
Robo_list = []
Cam_list = []

i = 1   # counts points (0, 1, ..., N_points)
waiting_for_points = True

# wait for N_points robot points
while waiting_for_points:
    data = client.recieve_message()
    
    print("Length of data", len(data))

    # if data not empty
    if len(data) > 0:

        j = 0   # counts coordinates (0, 1, 2)
        waiting_for_coordinates = True
        coordinates = np.zeros(3)
        coordinates[j] = struct.unpack('f', data)[0]
        print(coordinates[j])
        print()

        j = 1
        # wait for 3 robot coordinates (X,Y,Z)
        while waiting_for_coordinates:
            
            data = client.recieve_message()
            if len(data) > 0:
                coordinates[j] = struct.unpack('f', data)[0]
                print(coordinates[j])
                print()

                j += 1    # one less coordinate left

            if j == 3:
                waiting_for_coordinates = False

        Robo_list.append(coordinates)
        print("Got point "+str(i)+" : "+str(coordinates))
        Cam_list.append(AUTO_calibration_process.getBallPositionXYD(pipeline))

        i += 1    # one less robot point left

    if i == N_points:
        waiting_for_points = False

# generate timestamp
timestr = time.strftime("%Y%m%d-%H%M%S")

# write robot coordinates to text file
with open('robot_coordinates_{}.txt'.format(timestr), 'w') as f:
    for coordinate in Robo_list:
        f.write("%s\n" % coordinate)

# write camera coordinates to text file
with open('camera_coordinates_{}.txt'.format(timestr), 'w') as f:
    for coordinate in Cam_list:
        f.write("%s\n" % coordinate)

# Robo Calibration points
np_robo_cali_points = np.array(Robo_list)
arm_cord = np.column_stack((np_robo_cali_points[:, 0:3], np.ones(np_robo_cali_points.shape[0]).T)).T
print(arm_cord)

# Cam Calibration points
np_cam_cali_points = np.array(Cam_list)
cam_cord = np.column_stack((np_cam_cali_points[:, 0:3], np.ones(np_cam_cali_points.shape[0]).T)).T
print(cam_cord)

# Compute Transformation matrices
image_to_arm = np.dot(arm_cord, np.linalg.pinv(cam_cord))
arm_to_image = np.linalg.pinv(image_to_arm)

# Print Results and Sanity Test
print("Finished")
print("Image to arm transform:\n", image_to_arm)
print("Arm to Image transform:\n", arm_to_image)
print()
print()

print("-------------------")
print("-------------------")
print("-------------------")
print("Sanity Test: Image_to_Arm")
print("-------------------")
print("-------------------")
print("-------------------")
print()
for ind, pt in enumerate(cam_cord.T):
    print("Spectated Camera Point:", np.array(pt)[0:3])
    # default_cali_point
    print("Expected Robo Point:", np_robo_cali_points[ind][0:3])
    print("Resulting Robo Point:", np.dot(image_to_arm, np.array(pt))[0:3])
    print("")

print("-------------------")
print("-------------------")
print("-------------------")
print("Sanity Test: Arm_to_Image")
print("-------------------")
print("-------------------")
print("-------------------")
print()
for ind, pt in enumerate(np_robo_cali_points):
    print("Spectated Robo Point:", np.array(pt)[0:3])
    print("Expected Camera Point:", cam_cord.T[ind][0:3])
    pt[3] = 1
    print("Resulting Camera Point:", np.dot(arm_to_image, np.array(pt))[0:3])
    print("")

# write inverse transformation matrix to text file
with open('inv_trafo_matrix_{}.txt'.format(timestr), 'w') as f:
    for row in image_to_arm.tolist():
        f.write("%s\n" % coordinate)
