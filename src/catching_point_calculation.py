import numpy as np
from sympy.solvers import solve
from sympy import Symbol


def get_intersection_time(params_x,params_y,params_z):
    t = Symbol('t')
    r_out = 600
    r_in = 300
    T_mat_poly = np.array([t*t,t,1])#.transpose()
    print(T_mat_poly)
    T_mat_lin = np.array([t,1] )#.transpose()
    print(T_mat_lin)

    # TODO: solve this equation for t
    t = solve((params_x*T_mat_lin)^2+(params_y*T_mat_poly)^2+(params_z*T_mat_lin)^2-r_out^2, t)

    return t

def get_catching_point(params_x,params_y,params_z,t):

    T_mat_poly = np.array([t*t,t,1])#.transpose()
    T_mat_lin = np.array([t,1])#.transpose()

    x =  params_x*T_mat_lin
    y = params_y*T_mat_poly 
    z = params_z*T_mat_lin

    return (x,y,z)

def check_boundaries(point):

    if point[0]<0 and point[2]>0:
        return True
    else:
        return False


def main():
    params_x = np.array([2,4])
    print(params_x)
    params_y = np.array([1,5,6])
    params_z = np.array([5,7])

    t = get_intersection_time(params_x,params_y,params_z)
    print(t)

if __name__ == "__main__":
    main()
