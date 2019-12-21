import numpy as np

def get_intersection_time(params_x,params_y,params_z):
    r_out = 600
    r_in = 300
    T_mat_poly = np.array([[t*t,t,1] for t in time]).transpose()
    T_mat_lin = np.array([[t,1] for t in time]).transpose()

    # TODO: solve this equation for t
    (params_x*T_mat_lin)^2+(params_y*T_mat_poly)^2+(params_z*T_mat_lin)^2-r_out^2

    return t

def get_catching_point(params_x,params_y,params_z,t):

    T_mat_poly = np.array([t*t,t,1]).transpose()
    T_mat_lin = np.array([t,1]).transpose()

    x =  params_x*T_mat_lin
    y = params_y*T_mat_poly 
    z = params_z*T_mat_lin

    return (x,y,z)

def check_boundaries(point):

    if point[0]<0 and point[2]>0:
        return True
    else:
        return False
