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

def resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized


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

camera_matrix = np.array([[-0.63794924 , 2.08362029 , 0.02540786],[ 2.16947552 ,-1.10534136 ,-0.23741742],[-0.42861632 ,-0.45252261 , 0.27626879]])
camera_matrix = np.array([[-0.47068177,  1.65131359,  0.06589142],
 [ 2.11572391, -1.07885886, -0.22597733],
 [-0.37933887, -0.57711217,  0.27240474]])
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64, help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
#HSV
orangeLower = (10, 170, 70)
orangeUpper = (20, 255, 255)
pts = deque(maxlen=args["buffer"])



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

        print(depth_image.shape)
        print(color_image.shape)

        # Remove background - Set pixels further than clipping_distance to grey
        # then we have reached the end of the video
        if color_image is None:
            print('Frame is none')
            break

        #cv2.imshow('frame', frame)
        # resize the frame, blur it, and convert it to the HSV
        # color space
        #color_image = resize(color_image, width=600)
        blurred = cv2.GaussianBlur(color_image, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # construct a mask for the color "orange", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, orangeLower, orangeUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        #print(mask.shape)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = grab_contours(cnts)
        center = None

        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            
            #print("center: " + center)
            
            calib_point = center
            print("x: " + str(calib_point[0]))
            print("y: " + str(calib_point[1]))
            depth = depth_image[calib_point[0],calib_point[1]]
            print("depth: " + str(depth))
            world_coordinate= camera_matrix.dot(np.array([calib_point[0], calib_point[1], depth]).transpose())
            print("World coordinate: ",world_coordinate)
            # cv2.imshow('depth Image', depth_image)
            # cv2.imshow('color image', color_image)
            
            # Render images
            # Remove background - Set pixels further than clipping_distance to grey
            grey_color = 153
            depth_image_3d = np.dstack((depth_image,depth_image,depth_image)) #depth image is 1 channel, color is 3 channels
            #bg_removed = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)
            
            cv2.circle(color_image, center, 5, (0, 0, 255), -1)
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
            cv2.circle(depth_colormap, center, 5, (0, 0, 255), -1)
            images = np.hstack((color_image, depth_colormap))
            cv2.namedWindow('Align Example', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('Align Example', images)
            


            # only proceed if the radius meets a minimum size
            if radius > 10:
                # draw the circle and centroid on the color_image,
                # then update the list of tracked points
                cv2.circle(color_image, (int(x), int(y)), int(radius),
                            (0, 255, 255), 2)
                cv2.circle(color_image, center, 5, (0, 0, 255), -1)

        # update the points queue
        pts.appendleft(center)
        
        # loop over the set of tracked points
        for i in range(1, len(pts)):
            # if either of the tracked points are None, ignore
            # them
            if pts[i - 1] is None or pts[i] is None:
                continue

            # otherwise, compute the thickness of the line and
            # draw the connecting lines
            thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
            cv2.line(color_image, pts[i - 1], pts[i], (0, 0, 255), thickness)

        # show the color_image to our screen
        cv2.imshow("color_image", color_image)
        key = cv2.waitKey()

        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break
finally:
    pipeline.stop()