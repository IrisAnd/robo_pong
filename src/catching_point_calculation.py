import numpy as np
import sympy as sym
from sympy.solvers import solve
from sympy import Symbol

def get_intersection_time(params_x,params_y,params_z):
    t = Symbol('t')
    r_out = 600
    r_in = 300
    T_mat_poly = np.array([t*t,t,1]).transpose()
    T_mat_lin = np.array([t,1]).transpose()

    equation = (np.dot(params_x[0], t) + params_x[1])**2 +(np.dot(params_y[0],t**2) + np.dot(params_y[1], t) + params_y[2])**2 + (np.dot(params_z[0], t) + params_z[1])**2 - r_out**2
    t = solve(equation ,t)

    #delete complex numbers
    print(type(t[2]))
   
    #need to find solution to delte complex numbers, problem data type is not a real complex number
    t = np.array([complex(item) for item in t])
    print(t)
    print(type(t[2]))
    temp =[]
    for i in t:
        if (i.imag == 0):
            print(i)
            temp.append(i)
    t = temp
    #should be postive, not right now because of dummy variables
    t = min(t) 

    print('t: ' + str(t))
    return t

def get_catching_point(params_x, params_y, params_z, t):
    
    T_mat_poly = np.array([t*t,t,1]).transpose()
    
    T_mat_lin = np.array([t,1]).transpose()
    x = np.dot(params_x, T_mat_lin)
    y = np.dot(params_y, T_mat_poly)
    z = np.dot(params_z, T_mat_lin)

    return (x,y,z)

def check_boundaries(point):
    #check that x < 0 and z >0
    print('point: ' + str(point))
    if point[0]<0 and point[2]>0:
        print('point: ' + str(point))
        return True
    else:
        return False


def main():
    params_x = np.array([2.,4.])
    params_y = np.array([1.,5.,6.])
    params_z = np.array([5.,7.])

    t = get_intersection_time(params_x,params_y,params_z)
  
    catch_point=get_catching_point(params_x,params_y,params_z,t)
    
    if check_boundaries(catch_point):
        print('move')


if __name__ == "__main__":
    main()
