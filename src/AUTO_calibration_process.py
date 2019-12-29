# License: Apache 2.0. See LICENSE file in root directory.
# Copyright(c) 2017 Intel Corporation. All Rights Reserved.

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


def getBallPositionXYD(pipeline):

    # Declare depth filters
    # dec_filter = rs.decimation_filter()  # Decimation - reduces depth frame density
    # Spatial    - edge-preserving spatial smoothing
    spat_filter = rs.spatial_filter()
    hole_filling = rs.hole_filling_filter()
    temp_filter = rs.temporal_filter()  # Temporal   - reduces temporal noise

    depth_to_disparity = rs.disparity_transform(True)
    disparity_to_depth = rs.disparity_transform(False)

    # Create an align object
    # rs.align allows us to perform alignment of depth frames to others frames
    # The "align_to" is the stream type to which we plan to align depth frames.
    align_to = rs.stream.color
    align = rs.align(align_to)

    camera_coordinate = np.zeros(3)

    # Streaming loop
    i = 0
    try:
        while i < 5:
            # Get frameset of color and depth
            frames = pipeline.wait_for_frames()
            # frames.get_depth_frame() is a 640x360 depth image

            # Align the depth frame to color frame
            aligned_frames = align.process(frames)

            # Get aligned frames
            # aligned_depth_frame is a 640x480 depth image
            aligned_depth_frame = aligned_frames.get_depth_frame()
            color_frame = aligned_frames.get_color_frame()

            # Validate that both frames are valid
            if not aligned_depth_frame or not color_frame:
                continue

            # Filter aligned depth frame
            #aligned_depth_frame = dec_filter.process(aligned_depth_frame)
            aligned_depth_frame = depth_to_disparity.process(
                aligned_depth_frame)
            aligned_depth_frame = spat_filter.process(aligned_depth_frame)
            aligned_depth_frame = temp_filter.process(aligned_depth_frame)
            aligned_depth_frame = disparity_to_depth.process(
                aligned_depth_frame)
            aligned_depth_frame = hole_filling.process(aligned_depth_frame)
            depth_image = np.asanyarray(aligned_depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # Remove background - Set pixels further than clipping_distance to grey
            # then we have reached the end of the video
            if color_image is None:
                print('Frame is none')
                break

            calib_point, radius = detect_ball(color_image)
            if calib_point:
                if calib_point[1] <= depth_image.shape[0] and calib_point[0] <= depth_image.shape[1]:

                    depth = depth_image[calib_point[1], calib_point[0]]
                    camera_coordinate = [calib_point[0], calib_point[1], depth]
                    print("depth: " + str(depth))
                    print("Camera coordinate: ", camera_coordinate)

                else:
                    print("Point not in image")

                cv2.circle(
                    color_image, (int(calib_point[0]), int(
                        calib_point[1])), 5, (0, 0, 255), -1)
                depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(
                    depth_image, alpha=0.3), cv2.COLORMAP_JET)

                cv2.circle(
                    depth_colormap, (int(calib_point[0]), int(
                        calib_point[1])), 5, (0, 0, 255), -1)
                images = np.hstack((color_image, depth_colormap))
                cv2.namedWindow('Align Example', cv2.WINDOW_AUTOSIZE)
                cv2.imshow('Align Example', images)
                cv2.imshow('Depth Image', depth_image)

                # only proceed if the radius meets a minimum size
                if radius > 10:
                    # draw the circle and centroid on the color_image,
                    # then update the list of tracked points
                    cv2.circle(color_image, (int(calib_point[0]), int(
                        calib_point[1])), int(radius), (0, 255, 255), 2)
                    cv2.circle(color_image, (int(calib_point[0]), int(
                        calib_point[1])), 5, (0, 0, 255), -1)
            else:
                print("No calib point found")

            # show the color_image to our screen
            cv2.imshow("color_image", color_image)
            i += 1

    finally:
        pipeline.stop()

    return camera_coordinate
