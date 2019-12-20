# RoboPong 
Final Project for Robotics Class 

### General To Do: 
* camera calibration 
* connect image processing laptop to robot controlling PC: 
	* issue: on server, only length of transferred data could be read, not string itself (proper conversion must be found) 
	* proof of concept: send coordinates from laptop to PC and let robot move to those coordinates 
* ball trajectory prediction: 
	* validate calculated trajectory by visualization 
* include air friction 

## Protocol 

#### 12/20/2019 - Iris, Gregor, Clarissa
* ProofOfConcept in 2D läuft
* Vorbereitung Kalibierung: Code in python für x,y, depth Werte, JupyterLab Solver
* Frame Rate optimierung
* erste Tests Werfen: Problem -> wenn Ball zu schnell, keine Erkennung (FrameRate Optimierung)
##### next steps:
* 3D Trajectorie schätzen
* string versenden (Idee in Array versenden)
* Vorbereitung: Fangpunkt --> Robot Arbeitsraum definieren (Kugel), Schnittpunkt mit Trajectorie


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
