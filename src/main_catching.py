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
from TCPClient import TCPClient
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D



def visualization(xs,ys,zs,xs_pred, ys_pred, zs_pred,cp):

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(xs, ys, zs, s= 30, label = "real")
    ax.plot(xs_pred, ys_pred, zs_pred, label = "pred")
    if cp:
        ax.scatter(cp[0],cp[1],cp[2],s= 30, label = "catch_point")

    # Draw sphere
    r = 550 #radius
    q = 2
    p = 0.5
    u, v = np.mgrid[0:q*np.pi:20j,0:p*np.pi:10j]
    x = r * np.cos(u) * np.sin(v)
    y = r * np.sin(u) * np.sin(v)
    z = r * np.cos(v)
    ax.plot_wireframe(x, y, z, color = "grey")
    ax.scatter([0],[0],[0],s= 30, label = "Robot Base")

    ax.set_xlim(-100,3000)
    ax.set_ylim(-1000,1000)
    ax.set_zlim(0,1000)


    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.legend()
    plt.savefig("Result.png", dpi = 150, bbox_inches = 'tight')
    fig.show()
    input("Press key to close")

def main():

    # create new csv file to save results
    # try:
    #     os.remove('data.csv')
    # except:
    #     print("No data file found, creating new one")
    # file = open('data.csv', mode = 'a')
    # writer = csv.writer(file,delimiter=',', quotechar=' ')
    # writer.writerow(["time", "point"])

    # Open TCP connection to robot
    #client = TCPClient()
    
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

    # Declare depth filters
    dec_filter = rs.decimation_filter()  # Decimation - reduces depth frame density
    spat_filter = rs.spatial_filter()  # Spatial    - edge-preserving spatial smoothing
    hole_filling = rs.hole_filling_filter()
    temp_filter = rs.temporal_filter()  # Temporal   - reduces temporal noise

    depth_to_disparity = rs.disparity_transform(True)
    disparity_to_depth = rs.disparity_transform(False)

    # initialize variables for trajectory calculation
    buffer_len = 30 #number of points that will be taken into account for trajectory calculation
    pts = deque(maxlen=buffer_len)
    camera_pts = deque(maxlen=buffer_len)
    time_vec = deque(maxlen=buffer_len)
    tic = time.time()
    tic_frame = None
    none_count = 0

    preditcion_store = []
    points_store = []
    catch_point = []

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
        center,radius = bd.detect_ball(color_image)

        # update the points queue
        if center is not None :
            
            #get depth from depth_image and append to center, append the current center to the points list
            depth = depth_image[center[1],center[0]]
            if not tic_frame:
                tic_frame = time.time()
            center.append(depth)
            camera_pts.append(center)

            # Transform point from camera coordinates to robot coordinate frame
            center_world = bte.transform_to_world(center)
            pts.append(center_world)
            points_store.append(center_world)

            #append current time to time vector
            toc = time.time()
            time_vec.append(toc-tic)

            #write the time and detected point to csv output file
            #writer.writerow([toc, center_world]) # TODO this center should be in robot coordinates
            

        else:
            none_count = none_count+1
        #toc_frame = time.time()
        #print("Detection_time: ",toc_frame-tic_frame)


        #if no points were detected for some time (10 frames), reset the point vector and polynomial calculation
        if none_count >10:
            pts.clear()
            camera_pts.clear()
            time_vec.clear()
            none_count = 0

        # if more then x ball positions were detected, calculate the trajectory estimation
        if(len(pts) > 7):
            toce = time.time()
            params_x,params_y,params_z = bte.estimate_trajectory(np.asarray(pts), np.asarray(time_vec))

            catch_point = cpc.get_catching_point(params_x,params_y,params_z)


            #Send catching point to robot
            if catch_point is not None:
                #client.send_message(np.round(catch_point,2))
                print("Processing time:",(time.time()-toce))
                print("Sent point: ",np.round(catch_point,2))
                catch_point_camera = bte.transform_to_camera(catch_point)
                cv2.drawMarker(color_image, tuple(catch_point_camera.astype(int)[:2]), (0, 255, 0) ,cv2.MARKER_CROSS,10)

            # calculate future points for ball from the estimated polynomial parameters and draw them
            print("Tic frame: ", tic_frame)
            print("Time now: ", time.time)
            future_points = bte.get_future_points_3D(params_x,params_y,params_z,tic,time.time(),2)
            
            for point in future_points.transpose():
                preditcion_store.append(point)
                camera_point = bte.transform_to_camera(point)
                cv2.drawMarker(color_image, tuple(camera_point.astype(int)[:2]), (255, 0, 0) ,cv2.MARKER_CROSS,5)


            # loop over the set of tracked points to draw the balls past movement
            print("cam points: ", camera_pts)
            for i in range(1, len(camera_pts)):

                # compute the thickness of the line and
                # draw the connecting lines
                thickness = int(np.sqrt(buffer_len / float(i + 1)) * 2.5)
                #cv2.drawMarker(color_image, tuple(camera_pts[i - 1][:2]), tuple(camera_pts[i][:2]), (0, 0, 255), cv2.MARKER_CROSS,5)
                cv2.drawMarker(color_image, (camera_pts[i][0],camera_pts[i][1]), (0, 0, 255), cv2.MARKER_CROSS,10)
        
            break
        # Display results
        cv2.imshow("Result image", color_image)
        out.write(color_image)  # uncomment to save video
        key = cv2.waitKey(1) & 0xFF

        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break

    cv2.imshow("Result image", color_image)

    del points_store[0]    
    points_store = np.asarray(points_store)
    preditcion_store = np.asarray(preditcion_store)
    print("Catching point: ", catch_point)
    print("points: ", points_store)
    print('first: ', points_store[:,0])
    print('prediction: ',preditcion_store)
    
    visualization(points_store[:,0],points_store[:,1],points_store[:,2],preditcion_store[:,0],preditcion_store[:,1] , preditcion_store[:,2],catch_point)
    # close all windows
    cv2.destroyAllWindows()
   
   # client.close()

    


if __name__ == '__main__':
    main()