import numpy as np
import cv2
# 3D Robo frame (mm)
Robo1 = [-221.63,449.19,-108.02]
Robo2 = [57.03,296.45,504.09]
Robo3 = [377.84,545.41,-0.86]
Robo4 = [437.44,124.65,481.03]
Robo5 = [713.23,187.79,80.57]
Robo6 = [596.38,-196.88,58.72]
Robo7 = [542.61,-365.15,293.54]
Robo8 = [211.25,-427.34,487.84]
Robo9 = [694.05,-4.92,223.01]
Robo10 = []
Robo11 = []
Robo12 = []
Robo13 = []

# 3D Camera frame (px: (x,y,z))
Cam1 = [444,312,2406] # green block
Cam2 = [417,176,2084] # red block
Cam3 = [497,348,1911] # blue block
Cam4 = [351,191,1747]
Cam5 = [401,354,1529]
Cam6 = [247,356,1671]
Cam7 = [185,252,1753]
Cam8 = [184,170,1952]
Cam9 = [321,301,1549]
Cam10 =[]
Cam11 =[]
Cam12 =[]
Cam13 =[]



A_list = []
bx_list = []
by_list = []
bz_list = []


# open file and read the content in a list
# with open('calibration.txt', 'r') as filehandle:
#     for line in filehandle:
#         # remove linebreak which is the last character of the string
#         point_string = line[:-1]
#         point = [int(x) for x in point_string.split()] 

#         bx_list.append(point[0])
#         by_list.append(point[1])
#         bz_list.append(point[2])
#         #A_list.append([point[3],point[4],point[5]])

cam_points = []

for i in np.arange(1,10):
    robo_point = eval('Robo' + str(i))
    A_list.append(robo_point)

    point = eval('Cam' + str(i))
    cam_points.append(point)
    bx_list.append(point[0])
    by_list.append(point[1])
    bz_list.append(point[2])

# Transform list to numpy array for further processing
#print(A_list)
#print(cam_points)
A = np.array(A_list)
bx = np.asarray(bx_list)
by = np.asarray(by_list)
bz = np.asarray(bz_list)
cam = np.array(cam_points)



#A = np.array([Robo1,Robo2,Robo3])

#bx = np.array([Cam1[0], Cam2[0], Cam3[0]])
#xi = np.linalg.solve(A, bx)
xi= np.linalg.lstsq(A, bx, rcond=None)[0]
#print(xi)
# check if solution is correct
#print("Result: " + str(np.allclose(np.dot(A, xi), bx)))

#for d e f does not work for variables, we have to use it with our measured values as in the example above

#by = np.array([Cam1[1], Cam2[1], Cam3[1]])
#xii = np.linalg.solve(A, by)

xii = np.linalg.lstsq(A, by, rcond=None)[0]
#print((xii))

# check if solution is correct
#print("Result: " + str(np.allclose(np.dot(A, xii), by)))

#for g h i does not work for variables, we have to use it with our measured values as in the example above
#bz = np.array([Cam1[2], Cam2[2], Cam3[2]])
#xiii = np.linalg.solve(A, bz)

xiii = np.linalg.lstsq(A, bz, rcond=None)[0]
#print(xiii)

# check if solution is correct
#print("Result: " + str(np.allclose(np.dot(A, xiii), bz)))


#Find the rotation and translation vectors.
# ret,rvecs, tvecs = cv.solvePnP(objp, corners2, mtx, dist)
#project 3D points to image plane
# imgpts, jac = cv.projectPoints(axis, rvecs, tvecs, mtx, dist)




TrafoMatrix = np.array([xi, xii, xiii])
print("Camera Matrix:")
print(TrafoMatrix)
print()
print("Inverse Camera Matrix:")
invTrafoMatrix = np.linalg.inv(TrafoMatrix)
print(invTrafoMatrix)