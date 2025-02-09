import numpy as np
import sympy as sym
from sympy.solvers import solve
from sympy import Symbol


def get_intersection_time(params_x, params_y, params_z):
    t = Symbol('t')
    r_out = 550
   
    equation = (np.dot(params_x[0], t) + params_x[1])**2 + (np.dot(params_y[0], t) + + params_y[1]
                                                            )**2 + (np.dot(params_z[0], t**2)+np.dot(params_z[1], t) + params_z[2])**2 - r_out**2
    t = solve(equation, t)

    # delete complex numbers
    # need to find solution to delete complex numbers, problem data type is not a real complex number
    t = np.array([complex(item) for item in t])
    temp = []
    for i in t:
        if (i.imag == 0):
            temp.append(i.real)
    t = temp
    if t:

        t = min(t)

        return t
    else:
        return None


def calc_catching_point(params_x, params_y, params_z, t):

    T_mat_poly = np.array([t*t, t, 1]).transpose()

    T_mat_lin = np.array([t, 1]).transpose()
    x = np.dot(params_x, T_mat_lin)
    y = np.dot(params_y, T_mat_lin)
    z = np.dot(params_z, T_mat_poly)

    return (x, y, z)


def check_boundaries(point):
    # check that x < 200 and z >0
    
    if point[0] > 200 and point[2] > 0:
        return True
    else:
        return False


def get_catching_point(params_x, params_y, params_z):

    t = get_intersection_time(params_x, params_y, params_z)
    print("t: ", t)
    if t is not None:
        catch_point = calc_catching_point(params_x, params_y, params_z, t)

        if check_boundaries(catch_point):
            print("catch point: ", catch_point)
            return catch_point
    else:
        print("No valid catching point found")
        return None


def main():
    params_x = np.array([2., 4.])
    params_y = np.array([1., 5., 6.])
    params_z = np.array([5., 7.])

    t = get_intersection_time(params_x, params_y, params_z)

    catch_point = calc_catching_point(params_x, params_y, params_z, t)

    if check_boundaries(catch_point):
        print('move')


if __name__ == "__main__":
    main()
