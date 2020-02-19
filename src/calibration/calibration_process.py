## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2017 Intel Corporation. All Rights Reserved.

#####################################################
##              Align Depth to Color               ##
#####################################################

# First import the library
import pyrealsense2 as rs
# Import Numpy for easy array manipulation
import numpy as np
# Import OpenCV for easy image rendering
import cv2
import time
import sys
import argparse
from collections import deque
from ball_detection import detect_ball


def grab_contours(cnts):
    # if the length the contours tuple returned by cv2.findContours
    # is '2' then we are using either OpenCV v2.4, v4-beta, or
    # v4-official
    if len(cnts) == 2:
        cnts = cnts[0]

    # if the length of the contours tuple is '3' then we are using
    # either OpenCV v3, v4-pre, or v4-alpha
    elif len(cnts) == 3:
        cnts = cnts[1]

    # otherwise OpenCV has changed their cv2.findContours return
    # signature yet again and I have no idea WTH is going on
    else:
        raise Exception(("Contours tuple must have length 2 or 3, "
                         "otherwise OpenCV changed their cv2.findContours return "
                         "signature yet again. Refer to OpenCV's documentation "
                         "in that case"))

    # return the actual contours array
    return cnts


# camera_matrix = np.array([[-0.34250764,  1.59272568,  0.0229035 ],
#  [ 2.72670532, -0.68577947, -0.50570559],
#  [-0.3261723,  -1.39798248,  0.5276124 ]])

camera_matrix = np.array([[ 1.17387918e-02,  9.06677568e-01, -8.19763438e-01,  1.61342946e+03],
 [ 2.98177269e+00,  3.59008659e-01,  3.71671350e-02, -1.06108133e+03],
 [ 1.62125309e-02, -2.82591617e+00, -2.35226662e-01,  1.48935144e+03],
 [-8.67361738e-19,  8.40256684e-19, -1.08420217e-19,  1.00000000e+00]])

print(camera_matrix)
try:
    os.remove('calibration.txt')
except:
    print("No data file found, creating new one")

filehandle = open('calibration.txt', 'a')


# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
#HSV
orangeLower = (10, 170, 120)
orangeUpper = (20, 255, 255)

# Create a pipeline
pipeline = rs.pipeline()

#Create a config and configure the pipeline to stream
#  different resolutions of color and depth streams
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
profile = pipeline.start(config)

# Getting the depth sensor's depth scale (see rs-align example for explanation)
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
print("Depth Scale is: " , depth_scale)

# We will be removing the background of objects more than
#  clipping_distance_in_meters meters away
clipping_distance_in_meters = 1 #1 meter
clipping_distance = clipping_distance_in_meters / depth_scale

# Declare depth filters
dec_filter = rs.decimation_filter()  # Decimation - reduces depth frame density
spat_filter = rs.spatial_filter()  # Spatial    - edge-preserving spatial smoothing
hole_filling = rs.hole_filling_filter()
temp_filter = rs.temporal_filter()  # Temporal   - reduces temporal noise

depth_to_disparity = rs.disparity_transform(True)
disparity_to_depth = rs.disparity_transform(False)


# Create an align object
# rs.align allows us to perform alignment of depth frames to others frames
# The "align_to" is the stream type to which we plan to align depth frames.
align_to = rs.stream.color
align = rs.align(align_to)

# Streaming loop
try:
    while True:
        # Get frameset of color and depth
        frames = pipeline.wait_for_frames()
        # frames.get_depth_frame() is a 640x360 depth image

        # Align the depth frame to color frame
        aligned_frames = align.process(frames)

        # Get aligned frames
        aligned_depth_frame = aligned_frames.get_depth_frame() # aligned_depth_frame is a 640x480 depth image
        color_frame = aligned_frames.get_color_frame()

        
        # Validate that both frames are valid
        if not aligned_depth_frame or not color_frame:
            continue

        # Filter aligned depth frame
        #aligned_depth_frame = dec_filter.process(aligned_depth_frame)
        aligned_depth_frame = depth_to_disparity.process(aligned_depth_frame)
        aligned_depth_frame = spat_filter.process(aligned_depth_frame)
        aligned_depth_frame = temp_filter.process(aligned_depth_frame)
        aligned_depth_frame = disparity_to_depth.process(aligned_depth_frame)
        aligned_depth_frame = hole_filling.process(aligned_depth_frame)
        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        #color_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)

        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        # Remove background - Set pixels further than clipping_distance to grey
        # then we have reached the end of the video
        if color_image is None:
            print('Frame is none')
            break

        calib_point,radius = detect_ball(color_image)
        print(calib_point)

        if calib_point is not None:
            depth = depth_image[calib_point[1],calib_point[0]]
            center_3D = [calib_point[0],calib_point[1],depth]
            #depth_new = aligned_depth_frame.get_distance(calib_point[0],calib_point[1])
            print("depth: " + str(depth))
            # print("depthnew: " + str(depth_new))
            world_coordinate= np.dot(camera_matrix,np.array([calib_point[0], calib_point[1], depth,1]))
            print("World coordinate: ",world_coordinate)

            cv2.circle(color_image, (calib_point[0], calib_point[1]), 5, (0, 0, 255), -1)
            

            #cv2.circle(depth_colormap, calib_point, 5, (0, 0, 255), -1)
        else:
            print("Point not in image")
        # cv2.imshow('depth Image', depth_image)
        # cv2.imshow('color image', color_image)
        
        #bg_removed = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)
        
        
        images = np.hstack((color_image, depth_colormap))
        cv2.namedWindow('Align Example', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Align Example', images)
        cv2.imshow('Depth Image', depth_image)

        key = cv2.waitKey()


        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break

        if key == ord("s"):
            print("Saving point: ", center_3D)
            for listitem in center_3D:
                filehandle.write('%s ' % listitem)
            
            # get Robot coordinates here
            # for item in robot_position:
            #     filehandle.write('%s ' % item)
            filehandle.write('\n')
finally:
    filehandle.close()
    pipeline.stop()