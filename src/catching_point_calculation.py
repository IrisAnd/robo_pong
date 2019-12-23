import numpy as np
import sympy as sym
from sympy.solvers import solve
from sympy import Symbol

def get_intersection_time(params_x,params_y,params_z):
    t = Symbol('t')
    r_out = 600
    r_in = 300
    T_mat_poly = np.array([t*t,t,1]).transpose()
    #print(T_mat_poly)
    T_mat_lin = np.array([t,1]).transpose()
    #print(T_mat_lin)
    # TODO: solve this equation for t
    #print(params_x[0])
    #print(params_y[2])
    #print(params_z)
   
    equation = (params_x[0] * t + params_x[1])**2 +(params_y[0]*t *t + params_y[1] * t + params_y[2])**2 + (params_z[0] * t + params_z[1])**2 - r_out**2
    t = solve(equation ,t)
    t = sym.simplify(t)
    #t = solve((params_x*T_mat_lin)^2+(params_y*T_mat_poly)^2+(params_z*T_mat_lin)^2-r_out^2, t)

    return t
def get_catching_point(params_x,params_y,params_z,t):
    x = []
    y = []
    z = []
    for point in t: 
        T_mat_poly = np.array([point*point,point,1]).transpose()
        T_mat_lin = np.array([point,1]).transpose()

        x.append(params_x*T_mat_lin)
        y.append(params_y*T_mat_poly )
        z.append(params_z*T_mat_lin)
    points = (x,y,z)
    return np.array(points)

def check_boundaries(points):
    for i in range(len(point)[0]):
        if point[0]<0 and point[2]>0:
            return True
        else:
            return False


def main():
    params_x = np.array([2.,4.])
    params_y = np.array([1.,5.,6.])
    params_z = np.array([5.,7.])

    t = get_intersection_time(params_x,params_y,params_z)
    print(t)

    catch_points=get_catching_point(params_x,params_y,params_z,t)
    print(np.array(catch_points).shape)  #(dim,anzahlpoits)
    print(len((catch_points)[0]) )

    #check_boundaries(catch_points)


if __name__ == "__main__":
    main()
