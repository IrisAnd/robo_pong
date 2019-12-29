import numpy as np
from scipy.optimize import fsolve
import argparse
import time

camera_matrix = np.array([[ 5.68192779e-01,  1.95014068e+00, -7.38910498e-01,  1.81758340e+03],
 [ 4.63951488e+00,  2.17799140e-01,  1.03736906e-01, -1.79283182e+03],
 [-1.10971419e-01, -4.54328774e+00, -2.60702910e-01,  2.27763990e+03],
 [-2.60208521e-18, -1.73472348e-18, -3.79470760e-19,  1.00000000e+00]])
 
camera_matrix_inv = np.linalg.inv(camera_matrix)


def transform_to_world(point):

    world_coordinate= np.dot(camera_matrix,np.array([point[0], point[1], point[2],1]))

    return world_coordinate[0:3]

def transform_to_camera(point):

    camera_coordinate= np.dot(camera_matrix_inv,np.array([point[0], point[1], point[2],1]))
    return camera_coordinate



def estimate_trajectory_pixel (first_points, time):
    #params_x = np.array([Ax, Bx, Cx])
    #params_y = np.array([Ay, By, Cy])
    #params_z = np.array([Az, Bz, Cz])
    
    g = 9810 # mm/s^2

    T_mat = np.array([[t*t,t,1] for t in time]).transpose()
    T_mat_inv = np.linalg.pinv(T_mat)

    # In y-direction gravity should be considered, so second term is applied
    T_mat_y = T_mat
    #T_mat_y[0]=T_mat_y[0]-g*T_mat_y[0]
    #T_mat_y_inv = np.linalg.pinv(T_mat_y)
    

    params_x = first_points[:,0].dot(T_mat_inv)
    params_y = first_points[:,1].dot(T_mat_inv)
    #params_z = first_points[:,2].dot(T_mat_inv)

    return params_x,params_y



def estimate_trajectory(first_points, time):
    #params_x = np.array([Ax, Bx, Cx])
    #params_y = np.array([Ay, By, Cy])
    #params_z = np.array([Az, Bz, Cz])
    
    g = 9810 # mm/s^2

    T_mat_poly = np.array([[t*t,t,1] for t in time]).transpose()
    T_mat_lin = np.array([[t,1] for t in time]).transpose()
    
    T_mat_poly_inv = np.linalg.pinv(T_mat_poly)
    T_mat_lin_inv = np.linalg.pinv(T_mat_lin)

    # In y-direction gravity should be considered, so second term is applied
    #_mat_y = T_mat
    #T_mat_y[0]=T_mat_y[0]-g*T_mat_y[0]
    #T_mat_y_inv = np.linalg.pinv(T_mat_y)


    params_x = first_points[:,0].dot(T_mat_lin_inv)
    params_y = first_points[:,1].dot(T_mat_lin_inv)
    params_z = first_points[:,2].dot(T_mat_poly_inv)

    return params_x,params_y,params_z

def get_future_points_2D(params_x,params_y,tic,time_now,time_diff):
    times = np.arange(time_now-tic, time_now-tic+time_diff, 0.1)
    #print(times)
    x = params_x[0]*times*times+params_x[1]*times+params_x[2]
    y = params_y[0]*times*times+params_y[1]*times+params_y[2]
    return np.vstack((x,y))

def get_future_points_3D(params_x,params_y,params_z,tic,time_now,time_diff):
    times = np.arange(time_now-tic-time_diff, time_now-tic+time_diff, 0.01)
    #print(times)
    x = params_x[0]*times+params_x[1]
    y = params_y[0]*times+params_y[1]
    z = params_z[0]*times*times+params_z[1]*times+params_z[2]
    return np.vstack((x,y,z))

