# import the necessary packages
from collections import deque
import numpy as np
import cv2
import time
import sys
import csv
import os
import ball_trajectory_estimation as bte
import ball_detection as bd
import catching_point_calculation as cpc
import pyrealsense2 as rs

def main():

    # create new csv file to save results
    try:
        os.remove('data.csv')
    except:
        print("No data file found, creating new one")
    file = open('data.csv', mode = 'a')
    writer = csv.writer(file,delimiter=',', quotechar=' ')
    writer.writerow(["time", "point"])
    
    # Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
    out = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (640,480))

    # Startup realsense pipeline
    pipeline = rs.pipeline()

    #Create a config and configure the pipeline to stream
    #  different resolutions of color and depth streams
    
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 60)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 60)

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
        
    # initialize variables for trajectory calculation
    buffer_len = 30 #number of points that will be taken into account for trajectory calculation
    pts = deque(maxlen=buffer_len)
    camera_pts = deque(maxlen=buffer_len)
    time_vec = deque(maxlen=buffer_len)
    tic = time.time()
    none_count = 0

    # Declare depth filters
    dec_filter = rs.decimation_filter()  # Decimation - reduces depth frame density
    spat_filter = rs.spatial_filter()  # Spatial    - edge-preserving spatial smoothing
    hole_filling = rs.hole_filling_filter()
    temp_filter = rs.temporal_filter()  # Temporal   - reduces temporal noise

    depth_to_disparity = rs.disparity_transform(True)
    disparity_to_depth = rs.disparity_transform(False)

    # loop for video
    while True:
        
        # Wait for frames from realsense
        frames = pipeline.wait_for_frames()
        # Align the depth frame to color frame
        aligned_frames = align.process(frames)

        # Get aligned frames
        aligned_depth_frame = aligned_frames.get_depth_frame() # aligned_depth_frame is a 640x480 depth image
        color_frame = aligned_frames.get_color_frame()

        # Filter aligned depth frame
        #aligned_depth_frame = dec_filter.process(aligned_depth_frame)
        aligned_depth_frame = depth_to_disparity.process(aligned_depth_frame)
        aligned_depth_frame = spat_filter.process(aligned_depth_frame)
        aligned_depth_frame = temp_filter.process(aligned_depth_frame)
        aligned_depth_frame = disparity_to_depth.process(aligned_depth_frame)
        aligned_depth_frame = hole_filling.process(aligned_depth_frame)

        # Get images to work on
        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Validate that both frames are valid
        if not aligned_depth_frame or not color_frame:
            print('Frame is none')
            continue

        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        
        # Detect the orange ball and return image with results
        ball_image,center = bd.fast_ball_detection(color_image,(pts or [None])[-1])

        
        
        # update the points queue
        if center is not None :
            
            #get depth from depth_image and append to center, append the current center to the points list
            depth = depth_image[center[0],center[1]]

            center.append(depth)
            camera_pts.append(center)

            # Transform point from camera coordinates to robot coordinate frame
            center_world = bte.transform_to_world(center)
            pts.append(center_world)

            #append current time to time vector
            toc = time.time()
            time_vec.append(toc-tic)

            #write the time and detected point to csv output file
            writer.writerow([toc, center]) # TODO this center should be in robot coordinates

        else:
            none_count = none_count+1

        #if no points were detected for some time (10 frames), reset the point vector and polynomial calculation
        if none_count >10:
            pts.clear()
            time_vec.clear()
            none_count = 0

        # if more then x ball positions were detected, calculate the trajectory estimation
        if(len(pts) > 10):

            params_x,params_y,params_z = bte.estimate_trajectory(np.asarray(pts), np.asarray(time_vec))

            catch_point = cpc.get_catching_point(params_x,params_y,params_z)

            #TODO: Send catching point to robot

            # calculate future points for ball from the estimated polynomial parameters and draw them
            future_points = bte.get_future_points_3D(params_x,params_y,params_z,tic,time.time(),5)
            for point in future_points.transpose():
                
                camera_point = bte.transform_to_camera(point)
                cv2.drawMarker(ball_image, tuple(camera_point.astype(int)[:2]), (255, 0, 0) ,cv2.MARKER_CROSS,10)

        # loop over the set of tracked points to draw the balls past movement
        for i in range(1, len(camera_pts)):

            # compute the thickness of the line and
            # draw the connecting lines
            thickness = int(np.sqrt(buffer_len / float(i + 1)) * 2.5)
            cv2.line(ball_image, tuple(camera_pts[i - 1][:2]), tuple(camera_pts[i][:2]), (0, 0, 255), thickness)

        # Display results
        cv2.imshow("Result image", ball_image)
        #out.write(ball_image)
        key = cv2.waitKey(1) & 0xFF

        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break

    # close all windows
    cv2.destroyAllWindows()

    


if __name__ == '__main__':
    main()