from collections import deque
import numpy as np
import argparse
import cv2
import time
import sys


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

# check if a point lies within the image borders


def check_image_boundaries(image, point):
    if point[0] >= image.shape[0] or point[1] >= image.shape[1]:
        return False
    else:
        return True


def detect_ball(work_image):

    # define the lower and upper boundaries of the "orange"
    # ball in the HSV color space, then initialize the
    # list of tracked points

    # HSV
    orangeLower = (10, 120, 70)
    orangeUpper = (25, 255, 255)
    # orangeLower = (30, 100, 100)  # green
    # orangeUpper = (50, 255, 255)  # green

    #cv2.imshow('frame', frame)
    # blur it, and convert it to the HSV
    # color space
    #blurred = cv2.GaussianBlur(work_image, (11, 11), 0)
    hsv = cv2.cvtColor(work_image, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, orangeLower, orangeUpper)
    cv2.imshow('mask', mask)
    # higher number of iterations reduces fps a lot!
    mask = cv2.erode(mask, None, iterations=1)
    mask = cv2.dilate(mask, None, iterations=1)
    #cv2.imwrite('maskerode'+str(time.time)+'.png', mask)
    cv2.imshow('maskerode', mask)
    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = grab_contours(cnts)
    center = None
    radius = None

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

    # # If found center fullfills the requirements, return it as numpy array
    # center_numpy = None
    # if center != None and check_image_boundaries(work_image, center):
    #     center_numpy = [center[0],center[1]]

    if center is not None:
        return [center[0], center[1]], radius
    else:
        return None, None


# to up frame-rate, after first recognition of ball try to find it
# near the first occurence in the next frame
# def fast_ball_detection(color_image,center):
#     diff = 80
#     bounding_box = None


#     # This code is not used, as it made detection slower not faster :)
#     # if center is not None:

#     #     # Crop image but make sure cropping is done within image boundaries
#     #     x_min = center[0] - diff if center[0] - diff > 0 else 0
#     #     x_max = center[0] + diff if center[0] + diff < color_image.shape[0] else color_image.shape[0]
#     #     y_min = center[1] - diff if center[1] - diff > 0 else 0
#     #     y_max = center[1] + diff if center[1] + diff < color_image.shape[1] else color_image.shape[1]
#     #     crop_image = color_image[y_min:y_max,x_min:x_max]


#     #     bounding_box = (x_min, x_max, y_min, y_max)
#     #     #cv2.imshow("Crop image", crop_image)


#     return detect_ball(color_image, bounding_box)
