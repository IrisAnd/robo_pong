import numpy as np
from scipy.optimize import fsolve
import argparse
import time

# Following is the matlab code
# 
# function [New_Vector] = estimate_vector3(V,t,n)

# % estimate the track by m points using phisycs Neuton laws
# % the track will be parabolic in y axis use gravity in earth
# x=V(1,:);
# y=V(2,:);
# z=V(3,:);     
# m=length(t);

# dt=mean(diff(t));
# t = t - t(round(m/2));  % reduce condition number
# dt=dt/4;
# tt=t(m) + dt:dt: t(m) + n*dt;


# T1 = [t ;ones(1,length(t))];
# % T2 = [t.^2 ; t ;ones(1,length(t))];

# % TT1 = [tt ;ones(1,length(tt))];
# TT2 = [tt.^2 ; tt ;ones(1,length(tt))];

# % g = 9.8 m/s  ,   y=0.5 g t^2  ,y[cm]     theta=0.1rad between camera to the world
# a = 9800*cos(0.1);  
# arr_x =  x /T1;
# arr_y = (y-0.5*a*t.^2)/T1;
# arr_z =  z/T1;

# New_Vector = [[0,arr_x]; [0.5*a,arr_y] ; [0,arr_z]]*TT2;

# end

def estimate_trajectory_pixel (first_points, time):
    #params_x = np.array([Ax, Bx, Cx])
    #params_y = np.array([Ay, By, Cy])
    #params_z = np.array([Az, Bz, Cz])
    
    g = 9810 # mm/s^2

    T_mat = np.array([[t*t,t,1] for t in time]).transpose()
    T_mat_inv = np.linalg.pinv(T_mat)

    # In y-direction gravity should be considered, so second term is applied
    T_mat_y = T_mat
    T_mat_y[0]=T_mat_y[0]-g*T_mat_y[0]
    T_mat_y_inv = np.linalg.pinv(T_mat_y)
    

    params_x = first_points[:,0].dot(T_mat_inv)
    params_y = first_points[:,1].dot(T_mat_y_inv)
    #params_z = first_points[:,2].dot(T_mat_inv)

    return params_x,params_y



def estimate_trajectory (first_points, time):
    #params_x = np.array([Ax, Bx, Cx])
    #params_y = np.array([Ay, By, Cy])
    #params_z = np.array([Az, Bz, Cz])
    
    g = 9810 # mm/s^2

    T_mat = np.array([[t*t,t,1] for t in time]).transpose()
    T_mat_inv = np.linalg.pinv(T_mat)

    # In y-direction gravity should be considered, so second term is applied
    T_mat_y = T_mat
    T_mat_y[0]=T_mat_y[0]-g*T_mat_y[0]
    T_mat_y_inv = np.linalg.pinv(T_mat_y)
    print(T_mat_y)
    
    

    params_x = first_points[:,0].dot(T_mat_inv)
    params_y = first_points[:,1].dot(T_mat_y_inv)
    params_z = first_points[:,2].dot(T_mat_inv)

    return (params_x,params_y,params_z)

