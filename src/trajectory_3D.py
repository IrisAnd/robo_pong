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
    # blur it, and convert it to the HSV
    # color space
    
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

    # Create an align object
    # rs.align allows us to perform alignment of depth frames to others frames
    # The "align_to" is the stream type to which we plan to align depth frames.
    align_to = rs.stream.color
    align = rs.align(align_to)
    
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

             # Align the depth frame to color frame
            aligned_frames = align.process(frames)

            # Get aligned frames
            aligned_depth_frame = aligned_frames.get_depth_frame() # aligned_depth_frame is a 640x480 depth image
            color_frame = aligned_frames.get_color_frame()

            # Validate that both frames are valid
            if not aligned_depth_frame or not color_frame:
                print('Frame is none')
                continue

            depth_image = np.asanyarray(aligned_depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            frames = pipe.wait_for_frames()


            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

        # handle the frame from VideoCapture or VideoStream
        #print(type(frame))
        # if we are viewing a video and we did not grab a frame,
        # then we have reached the end of the video
        
        ball_image,center = detect_ball(color_image)

        #get depth from depth_image and append to center
        depth = depth_image[center[0],center[1]]
        center.append(depth)
        print("Center: "+ str(center))

        ball_detected = False
        
        # show the color_image to our screen# update the points queue
        if center != None:
            pts.append(center)
            toc = time.time()
            time_vec.append(toc-tic)
            ball_detected = True
        else:
            none_count = none_count+1

        #if no points were detected for some time, reset the point vector and polynomial calculation
        if none_count >10:
            pts.clear()
            time_vec.clear()
            none_count = 0


        if(len(pts) > 5):
            params_x,params_y,params_z = bte.estimate_trajectory(np.asarray(pts), np.asarray(time_vec))
            print(params_x)
            print(params_y)
            print(params_z)
            future_points = get_future_points_3D(params_x,params_y,params_z,tic,time.time(),5)
            #print(future_points)
            for point in future_points.transpose():
                #print(point)
                cv2.drawMarker(ball_image, tuple(point.astype(int)[:2]), (255, 0, 0) ,cv2.MARKER_CROSS,10)

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