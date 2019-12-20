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
import ball_trajectory_estimation as bte

#import pyrealsense2 as rs


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



def detect_ball(color_image):

    # define the lower and upper boundaries of the "green"
    # ball in the HSV color space, then initialize the
    # list of tracked points
    #HSV
    orangeLower = (10, 170, 70)
    orangeUpper = (20, 255, 255)


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

    '''parabel'''
    #pts in world xyz
    #parabel(pts,time)
    if center != None:
        center_numpy = [center[0],center[1]]
    else:
        center_numpy = None
    return color_image,center_numpy

def get_future_points_2D(params_x,params_y,tic,time_now,time_diff):
    times = np.arange(time_now-tic, time_now-tic+time_diff, 0.1)
    #print(times)
    x = params_x[0]*times*times+params_x[1]*times+params_x[2]
    y = params_y[0]*times*times+params_y[1]*times+params_y[2]
    return np.vstack((x,y))

def get_future_points_3D(params_x,params_y,params_z,tic,time_now,time_diff):
    times = np.arange(time_now-tic, time_now-tic+time_diff, 0.1)
    #print(times)
    x = params_x[0]*times*times+params_x[1]*times+params_x[2]
    y = params_y[0]*times*times+params_y[1]*times+params_y[2]
    z = params_z[0]*times*times+params_z[1]*times+params_z[2]
    return np.vstack((x,y,z))

def main():

    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("--webcam", action='store_true')
    args = ap.parse_args()

    # if a video path was not supplied, grab the reference
    # to the webcam
    if args.webcam == True:
        vs = cv2.VideoCapture(0)
        print("Webcam mode active")

    # otherwise, grab a reference to the video file
    else:
        pipe = rs.pipeline()
        profile = pipe.start()
    # allow the camera or video file to warm up

    #time.sleep(2.0)
    buffer_len = 20
    pts = deque(maxlen=buffer_len)
    time_vec = deque(maxlen=buffer_len)
    tic = time.time()
    none_count = 0
	# keep looping
    while True:
        # grab the current frame
        #ret, frame = vs.read()
        color_image = None
        
        if args.webcam == True:
            ret, color_image = vs.read()

        else:
            frames = pipe.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            color_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)

        # handle the frame from VideoCapture or VideoStream
        #print(type(frame))
        # if we are viewing a video and we did not grab a frame,
        # then we have reached the end of the video
        if color_image is None:
            print('Frame is none')
            break
        ball_image,center = detect_ball(color_image)
        ball_detected = False
        
        # show the color_image to our screen# update the points queue
        if center != None:
            pts.append(center)
            #print(len(pts))
            toc = time.time()
            time_vec.append(toc-tic)
            ball_detected = True
        else:
            none_count = none_count+1

        if none_count >10:
            pts.clear()
            time_vec.clear()
            none_count = 0



        #print(center)
        #print(pts)
        if(len(pts) > 5):
            params_x,params_y = bte.estimate_trajectory_pixel(np.asarray(pts), np.asarray(time_vec))
            #print(params_x)
            #print(params_y)
            future_points = get_future_points(params_x,params_y,tic,time.time(),5)
            #print(future_points)
            for point in future_points.transpose():
                #print(point)
                cv2.drawMarker(ball_image, tuple(point.astype(int)), (255, 0, 0) ,cv2.MARKER_CROSS,10)

        # loop over the set of tracked points
        for i in range(1, len(pts)):
            # if either of the tracked points are None, ignore
            # them
            if ball_detected != True:
                continue

            # otherwise, compute the thickness of the line and
            # draw the connecting lines
            thickness = int(np.sqrt(buffer_len / float(i + 1)) * 2.5)

            cv2.line(ball_image, tuple(pts[i - 1]), tuple(pts[i]), (0, 0, 255), thickness)


        cv2.imshow("color_image", ball_image)
        key = cv2.waitKey(1) & 0xFF

        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break

    vs.release()

    # close all windows
    cv2.destroyAllWindows()

    


if __name__ == '__main__':
    main()