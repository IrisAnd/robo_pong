# RoboPong
Final Project for Robotics Class

## General To Do:
* camera calibration
* connect image processing laptop to robot controlling PC:
** issue: on server, only length of transferred data could be read, not string itself (proper conversion must be found)
** proof of concept: send coordinates from laptop to PC and let robot move to those coordinates
* ball trajectory prediction:
** validate calculated trajectory by visualization
** include air friction

## Protocol

<<<<<<< HEAD
### 12/19/2019 – Iris, Gregor, Jakob
* trajectory: ball detected, position output by webcam (w/o depth) and trajectory calculated with translated Israeli code (presumably, to be tested)
* TCP connection between our laptop (pyhton) and Robot PC (C++): message sent and echoed
** issue: on server, only length of transferred data could be read, not string itself (proper conversion must be found)
** TCPClient.py: ITRI PC IP address and port updated
** TCPServer.cpp: Windows Winsock TCP/IP Server example code (most recent version is on ITRI PC only)

### 12/18/2019 – Iris, Clarissa, Jakob
=======
### 13/18/2019
* RealSense: runs on Clarissa’s (Linux) and Jakob’s (Windows) laptop
* ball detection: got pixel and depth information from RealSense
* trajectory: Israeli matlab code was transleted to python (not tested yet)
* TCP Server Client:Sent a string message from Jakob's laptop (Python) to Roboter (C++). String message has to be decoded next.
* ask TA for folding ruler

### 12/18/2019
>>>>>>> f85ee9225dd5c832d608cc26c92875a374b0bc13
* RealSense: runs on Clarissa’s (Linux) and Jakob’s (Windows) laptop
* ball detection: got pixel and depth information from RealSense
* trajectory: start of translating Israeli matlab code to python
* TCP Server Client: sent String message from Clarissa’s laptop (client) to Jakob’s laptop (server) and back
* ask TA for folding ruler
