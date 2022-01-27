# RoboPong 
This is the code base for a final project for the robotics class at NTU, Taiwan. The objective is to detect a thrown table tennis ball via image processing and predict it's future trajectory. A robot arm is then controlled to move to a calculated catching point and catch the ball before it hits the ground.   

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
