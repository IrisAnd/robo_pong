import numpy as np
# 3D Robo frame (mm)
Robo1 = [0,415.94,339.15]
Robo2 = [-255.46,415.95,181.25]
Robo3 = [215.77,390.89,-138.67]
Robo4 = [197.75,24.8,643.90]
Robo5 = [223.49,-421.01,269.03]
Robo6 = [440.59,-387.41,-12.23]
Robo7 = [151.70,-340.45,510.66]
Robo8 = [228.76,144.81,208.80]
Robo9 = [573.34,-40.29,-38.7]

# # 3D Camera frame (px: (x,y,z))
# Cam1 = [453,240,1801] # green block
# Cam2 = [432,268,1911] # red block
# Cam3 = [448,407,1778] # blue block
# Cam4 = [309,101,2526]
# Cam5 = [128,267,2445]
# Cam6 = [134,407,2434]
# Cam7 = [160,155,1726]
# Cam8 = [370,300,1886]
# Cam9 = [285,452,2560]


A_list = []
bx_list = []
by_list = []
bz_list = []


# open file and read the content in a list
with open('calibration.txt', 'r') as filehandle:
    for line in filehandle:
        # remove linebreak which is the last character of the string
        point_string = line[:-1]
        point = [int(x) for x in point_string.split()] 

        bx_list.append(point[0])
        by_list.append(point[1])
        bz_list.append(point[2])
        #A_list.append([point[3],point[4],point[5]])


for i in np.arange(1,len(bx_list)+1):
    robo_point = eval('Robo' + str(i))
    A_list.append(robo_point)

  

# Transform list to numpy array for further processing
A = np.asarray(A_list)
bx = np.asarray(bx_list)
by = np.asarray(by_list)
bz = np.asarray(bz_list)



#A = np.array([Robo1,Robo2,Robo3])

#bx = np.array([Cam1[0], Cam2[0], Cam3[0]])
#xi = np.linalg.solve(A, bx)
xi = np.linalg.lstsq(A, bx, rcond=None)[0]
#print(xi)

# check if solution is correct
#print("Result: " + str(np.allclose(np.dot(A, xi), bx)))

#for d e f does not work for variables, we have to use it with our measured values as in the example above

#by = np.array([Cam1[1], Cam2[1], Cam3[1]])
#xii = np.linalg.solve(A, by)

xii = np.linalg.lstsq(A, by, rcond=None)[0]
#print(xii)

# check if solution is correct
#print("Result: " + str(np.allclose(np.dot(A, xii), by)))

#for g h i does not work for variables, we have to use it with our measured values as in the example above
#bz = np.array([Cam1[2], Cam2[2], Cam3[2]])
#xiii = np.linalg.solve(A, bz)

xiii = np.linalg.lstsq(A, bz, rcond=None)[0]
#print(xiii)

# check if solution is correct
#print("Result: " + str(np.allclose(np.dot(A, xiii), bz)))

TrafoMatrix = np.array([xi, xii, xiii])
print("Camera Matrix:")
print(TrafoMatrix)
print()
print("Inverse Camera Matrix:")
invTrafoMatrix = np.linalg.inv(TrafoMatrix)
print(invTrafoMatrix)