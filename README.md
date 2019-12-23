# RoboPong 
Final Project for Robotics Class 

### General To Do: 
* camera calibration 
* connect image processing laptop to robot controlling PC: 
	* [TESTING] proof of concept: send coordinates from laptop to PC and let robot move to those coordinates (see Run Remote ArmControl below)
	* [DEBUGGING]
* ball trajectory prediction: 
	* validate calculated trajectory by visualization 
* include air friction 

### How to

#### Run Remote ArmControl
1. go to Final Project > Group 15 > Remote ArmControl > ArmControl 
2. open Project file
3. run main.cpp
4. connect to robot (press this red button in robot program)
5. check console for server message: Server listening…
6. make sure that someone observes the robot and keeps the stop button
7. run TCPClient.py (Client sends array with coordinates to C++ server on ITRI PC and those coordinates are given to MOVP)
Now, the robot should move to the coordinates specified in TCPCleint.py.
(backup in github/src with name: TCP_remote_arm_control.cpp)

## Protocol 

#### 12/21/2019 – Gregor, Jakob
* TCP: 
	* [SOLVED] issue: now, strings, int arrays, etc can be read on server
	* [PREPARED] POC: integrated TCP into ArmControl 

#### 12/20/2019 - Iris, Gregor, Clarissa
* ProofOfConcept in 2D läuft
* Vorbereitung Kalibierung: Code in python für x,y, depth Werte, JupyterLab Solver
* Frame Rate optimierung
* erste Tests Werfen: Problem -> wenn Ball zu schnell, keine Erkennung (FrameRate Optimierung)
##### next steps:
* 3D Trajektorie schätzen
* string versenden (Idee in Array versenden)
* Vorbereitung: Fangpunkt --> Robot Arbeitsraum definieren (Kugel), Schnittpunkt mit Trajektorie


#### 12/19/2019 – Iris, Gregor, Jakob 
* trajectory: ball detected, position output by webcam (w/o depth) and trajectory calculated with translated Israeli code (presumably, to be tested) 
* TCP connection between our laptop (pyhton) and Robot PC (C++): message sent and echoed 
	* issue: on server, only length of transferred data could be read, not string itself (proper conversion must be found) 
	* TCPClient.py: ITRI PC IP address and port updated 
	* TCPServer.cpp: Windows Winsock TCP/IP Server example code (most recent version is on ITRI PC only) 

#### 12/18/2019 – Iris, Clarissa, Jakob
* RealSense: runs on Clarissa’s (Linux) and Jakob’s (Windows) laptop 
* ball detection: got pixel and depth information from RealSense 
* trajectory: Israeli matlab code was transleted to python (not tested yet) 
* TCP Server Client: sent String message from Clarissa’s laptop (client) to Jakob’s laptop (server) and back 
* ask TA for folding ruler
