import numpy as np
from scipy.optimize import fsolve
import argparse
import time

camera_matrix = np.array([[-0.47068177,  1.65131359,  0.06589142],
 [ 2.11572391, -1.07885886, -0.22597733],
 [-0.37933887, -0.57711217,  0.27240474]])

camera_matrix_inv = np.linalg.inv(camera_matrix)


def transform_to_world(point):

    world_coordinate= camera_matrix.dot(np.array([point[0], point[1], point[2]]).transpose())
    return world_coordinate

def transform_to_camera(point):

    camera_coordinate= camera_matrix_inv.dot(np.array([point[0], point[1], point[2]]).transpose())
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
    params_y = first_points[:,1].dot(T_mat_poly_inv)
    params_z = first_points[:,2].dot(T_mat_lin_inv)

    return params_x,params_y,params_z

def get_future_points_2D(params_x,params_y,tic,time_now,time_diff):
    times = np.arange(time_now-tic, time_now-tic+time_diff, 0.1)
    #print(times)
    x = params_x[0]*times*times+params_x[1]*times+params_x[2]
    y = params_y[0]*times*times+params_y[1]*times+params_y[2]
    return np.vstack((x,y))

def get_future_points_3D(params_x,params_y,params_z,tic,time_now,time_diff):
    times = np.arange(time_now-tic, time_now-tic+time_diff, 0.01)
    #print(times)
    x = params_x[0]*times+params_x[1]
    y = params_y[0]*times*times+params_y[1]*times+params_y[2]
    z = params_z[0]*times+params_z[1]
    return np.vstack((x,y,z))

