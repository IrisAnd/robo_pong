# USAGE
# python ball_tracking.py --video ball_tracking_example.mp4
# python ball_tracking.py

# import the necessary packages
from collections import deque
#from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
#import imutils
import time
import sys

import pyrealsense2 as rs


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

def parabel(pts):
	temp= None




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

#timestemp for parabel calc
time = [0]

# if a video path was not supplied, grab the reference
# to the webcam
#if not args.get("video", False):
#    vs = cv2.VideoCapture(0)

# otherwise, grab a reference to the video file
#else:
#   vs = cv2.VideoCapture(args["video"])
pipe = rs.pipeline()
profile = pipe.start()
# allow the camera or video file to warm up

#time.sleep(2.0)

# keep looping
while True:
	# grab the current frame
	#ret, frame = vs.read()
	frames = pipe.wait_for_frames()
	depth_frame = frames.get_depth_frame()
	color_frame = frames.get_color_frame()

	depth_image = np.asanyarray(depth_frame.get_data())
	color_image = np.asanyarray(color_frame.get_data())
	color_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
	


	#time = 

	# handle the frame from VideoCapture or VideoStream
	#print(type(frame))
	# if we are viewing a video and we did not grab a frame,
	# then we have reached the end of the video
	if color_image is None:
		print('Frame is none')
		break

	#cv2.imshow('frame', frame)
	# resize the frame, blur it, and convert it to the HSV
	# color space
	color_image = resize(color_image, width=600)
	blurred = cv2.GaussianBlur(color_image, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, orangeLower, orangeUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

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

		# only proceed if the radius meets a minimum size
		if radius > 10:
			# draw the circle and centroid on the color_image,
			# then update the list of tracked points
			cv2.circle(color_image, (int(x), int(y)), int(radius),
						(0, 255, 255), 2)
			cv2.circle(color_image, center, 5, (0, 0, 255), -1)

	# update the points queue
	pts.appendleft(center)
	
	'''parabel'''
	#pts in world xyz
	#parabel(pts,time)


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
	key = cv2.waitKey(1) & 0xFF

	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break


vs.release()

# close all windows
cv2.destroyAllWindows()
