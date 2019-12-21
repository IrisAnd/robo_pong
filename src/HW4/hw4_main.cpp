#undef UNICODE

#define WIN32_LEAN_AND_MEAN

#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>

#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include <string>
#include <sstream>

#include <stack>
#include <math.h>       /* atan2 */

#include "opencv.hpp"
// Need to link with Ws2_32.lib
#pragma comment (lib, "Ws2_32.lib")

#define DEFAULT_BUFLEN 512
#define DEFAULT_PORT "4000"
#define PI 3.1415926

using namespace std;
using namespace cv;

int sendCommand(char* sendbuf, SOCKET& ClientSocket)
{
	cout << "Sending Command: " << sendbuf << endl;
	int SendResult = 0;
	int ReceiveResult = 0;
	char recvbuf[512];
	int counter = 0;
	int RoundThreshold = 1000;

	//Send Command to Robot Arm
	SendResult = send(ClientSocket, sendbuf, strlen(sendbuf)+1, 0 );

    if (SendResult == SOCKET_ERROR)
	{
		cout<< "send failed with error: " << WSAGetLastError() << endl;
		closesocket(ClientSocket);
		WSACleanup();
		return 1;
	}

	Sleep(100);

	do
	{
		ReceiveResult = recv(ClientSocket, recvbuf, 512, 0);
		counter++;
	}while(ReceiveResult == 0 && counter < RoundThreshold);

	if(counter > RoundThreshold)
	{
		cout << "Respond Time Out" << endl;
		return 1;
	}
	else
	{
		if(!strcmp(recvbuf,"ERR"))
		{
			cout << "Invalid Command" << endl;
			return 1;
		}
	}

	return 0;
}

std::vector<cv::Mat> find_image_segments_grayscale(cv::Mat& WorkImage){

  
  cvtColor(WorkImage,WorkImage,COLOR_BGR2GRAY);
  // Noise reduction with 3x3 Gaussian Filter
	cv::GaussianBlur(WorkImage, WorkImage, cv::Size(3, 3), 0, 0);

	// Thresholding with t = 140
	cv::threshold(WorkImage, WorkImage, 150, 255, cv::THRESH_BINARY);

	// Opening: removes small objects from the foreground
	cv::erode(WorkImage, WorkImage, cv::Mat());
	cv::dilate(WorkImage, WorkImage, cv::Mat());


	//Implementing the Region Growing Algorithm from lecture slides
	
	// segment index
	int i = 0;

	// Duplicate the working image to save segment "islands" marked with segment index
	cv::Mat ComImage = WorkImage.clone();

	// declare Vector for saving images with single segments
	std::vector<cv::Mat> VecSegImages;

	std::cout << "Now using Region Growing to find segments" << std::endl;
	
	//iterate over image rows and lines
	for (int ko = 0; ko < ComImage.rows; ko++)
	{
		for (int jo = 0; jo < ComImage.cols; jo++)
		{
			if (ComImage.at<uchar>(ko, jo) == 255) {
				// new segment found
				i = i + 1; 

				//Create new empty image to exclusively save the current segment
				cv::Mat SegImage = cv::Mat::zeros(cv::Size(ComImage.cols, ComImage.rows), CV_8U);

				// create pixel stack and push current segment pixel
				std::stack<cv::Point> pixstack;
				pixstack.push(cv::Point(ko, jo));
				
				// mark current segment with segment index
				ComImage.at<uchar>(ko, jo) = i;

				// mark current segment with max intensity
				SegImage.at<uchar>(ko, jo) = 255;

				// depth-first search in neighbourhood for segment member pixels
				while (!pixstack.empty()) {
					
					// get coordinates of upper stack entry and pop
					int k = pixstack.top().x;
					int j = pixstack.top().y;
					pixstack.pop();

					if (ComImage.at<uchar>(k, j + 1) == 255)
					{
						ComImage.at<uchar>(k, j + 1) = i;
						SegImage.at<uchar>(k, j + 1) = 255;
						pixstack.push(cv::Point(k, j + 1));
					}

					if (k > 1 && ComImage.at<uchar>(k - 1, j) == 255)
					{
						ComImage.at<uchar>(k - 1, j) = i;
						SegImage.at<uchar>(k - 1, j) = 255;
						pixstack.push(cv::Point(k - 1, j));
					}

					if (j > 1 && ComImage.at<uchar>(k, j - 1) == 255)
					{
						ComImage.at<uchar>(k, j - 1) = i;
						SegImage.at<uchar>(k, j - 1) = 255;
						pixstack.push(cv::Point(k, j - 1));
					}

					if (ComImage.at<uchar>(k + 1, j) == 255)
					{
						ComImage.at<uchar>(k + 1, j) = i;
						SegImage.at<uchar>(k + 1, j) = 255;
						pixstack.push(cv::Point(k + 1, j));
					}

				}
				VecSegImages.push_back(SegImage);
			}
		}
	}
	std::cout << "Found " << i << " objects" << std::endl;

  return VecSegImages;

}

std::vector<cv::Mat> find_image_segments_color(cv::Mat& WorkImage){

  cvtColor(WorkImage,WorkImage,COLOR_BGR2HSV);
  cout<<"Converted to HSV"<<endl;
  // Noise reduction with 3x3 Gaussian Filter
  std::vector<cv::Mat> VecSegImages;
  cv::Mat image_blue, image_red, image_yellow;

  inRange(WorkImage, Scalar(0,80,80),Scalar(15,255,255),image_red);
  VecSegImages.push_back(image_red);

  inRange(WorkImage, Scalar(180,80,80),Scalar(270,255,255),image_blue);
  VecSegImages.push_back(image_blue);

  inRange(WorkImage, Scalar(40,80,80),Scalar(60,255,255),image_yellow);
  VecSegImages.push_back(image_yellow);

  for (unsigned int s = 0; s < VecSegImages.size(); s++)
  {
    
    
	  // Opening: removes small objects from the foreground
	  cv::erode(VecSegImages[s], VecSegImages[s], cv::Mat());
	  cv::dilate(VecSegImages[s], VecSegImages[s], cv::Mat());

    cv::imshow("SegImage", VecSegImages[s]);
    waitKey();
  }

  return VecSegImages;
}



void process_image(cv::Mat& Image, std::vector<cv::Point>& centroids, std::vector<double>& orientations){

  cv::Mat WorkImage = Image.clone();
  cv::Mat DispImage = Image.clone();
  std::vector<cv::Mat> VecSegImages = find_image_segments_grayscale(WorkImage);
  

	// Now, for every segment, extract the segment and calculate the moments based on this mask
	for (unsigned int s = 0; s < VecSegImages.size(); s++) {
		
		// find moments of the image
		cv::Moments m = cv::moments(VecSegImages[s], true);
		
		// centroid of segment
		cv::Point p(m.m10 / m.m00, m.m01 / m.m00); 

		// Principal Angle (radians)
		double theta = 0.5 * atan2(2 * m.mu11, m.mu20 - m.mu02);

		// calculate second point to visualize Principal Angle
		cv::Point p1 = cv::Point(p.x - 50 * cos(theta), p.y - 50 * sin(theta));
		
		// Output results
		std::cout << "Center and orientation of " << s + 1 << ". " << "object:" << std::endl;
		std::cout << p.x << " " << p.y << " " << theta / (2 * PI) * 360 << std::endl;
    centroids.push_back(p);
    orientations.push_back(theta);

		// insert centroid and principal angle line into working image
		cv::circle(DispImage, p, 5, cv::Scalar(128, 0, 0), -1);
		cv::line(DispImage, p, p1, cv::Scalar(128, 0, 0), 2);
	}

	// Show the working image with centroid as point and principal angle as line
	cv::imshow("WorkImage", DispImage);
	cv::waitKey();
}

Mat readCamera(bool video = true)
{
  VideoCapture cap(0);
  if ( !cap.isOpened() )  // if not success, exit program
  {
     cout << "Cannot access camera" << endl;
  }
  namedWindow("cam",1);
  Mat frame;
  if (!video)
  {
    ;
  }
  /*
  if (video)
  {
      while(true)
      {
          Mat frame;
          bool check = cap.read(frame); // read a new frame from video

          if (!check) //if not success, break loop
          {
              cout << "Cannot read the frame from video file" << endl;
              break;
          }
          //INSERT PROCESSING here
                    
          // Show Frame
          imshow("cam", frame);
          waitKey(33);
      }
  }
  */
  else
  {
      bool check = cap.read(frame); // read a new frame from video

      if (!check) //if not success, break loop
      {
         cout << "Cannot read the frame from video file" << endl;
      }
      //INSERT PROCESSING here
                         
      // Show Frame
      imshow("cam", frame);
  }
  return frame;
}

int __cdecl main(void) 
{
    WSADATA wsaData;
    int iResult;

    SOCKET ListenSocket = INVALID_SOCKET;
    SOCKET ClientSocket = INVALID_SOCKET;

    struct addrinfo *result = NULL;
    struct addrinfo hints;

    int recvbuflen = DEFAULT_BUFLEN;
    
    // Initialize Winsock
    iResult = WSAStartup(MAKEWORD(2,2), &wsaData);
    if (iResult != 0) {
        printf("WSAStartup failed with error: %d\n", iResult);
        return 1;
    }

    ZeroMemory(&hints, sizeof(hints));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_protocol = IPPROTO_TCP;
    hints.ai_flags = AI_PASSIVE;

    // Resolve the server address and port
    iResult = getaddrinfo(NULL, DEFAULT_PORT, &hints, &result);
    if ( iResult != 0 ) {
        printf("getaddrinfo failed with error: %d\n", iResult);
        WSACleanup();
        return 1;
    }

    // Create a SOCKET for connecting to server
    ListenSocket = socket(result->ai_family, result->ai_socktype, result->ai_protocol);
    if (ListenSocket == INVALID_SOCKET) {
        printf("socket failed with error: %ld\n", WSAGetLastError());
        freeaddrinfo(result);
        WSACleanup();
        return 1;
    }

    // Setup the TCP listening socket
    iResult = bind( ListenSocket, result->ai_addr, (int)result->ai_addrlen);
    if (iResult == SOCKET_ERROR) {
        printf("bind failed with error: %d\n", WSAGetLastError());
        freeaddrinfo(result);
        closesocket(ListenSocket);
        WSACleanup();
        return 1;
    }

    freeaddrinfo(result);

    iResult = listen(ListenSocket, SOMAXCONN);
    if (iResult == SOCKET_ERROR) {
        printf("listen failed with error: %d\n", WSAGetLastError());
        closesocket(ListenSocket);
        WSACleanup();
        return 1;
    }

    // Accept a client socket
    ClientSocket = accept(ListenSocket, NULL, NULL);
    if (ClientSocket == INVALID_SOCKET) {
        printf("accept failed with error: %d\n", WSAGetLastError());
        closesocket(ListenSocket);
        WSACleanup();
        return 1;
    }

    // No longer need server socket
    closesocket(ListenSocket);
	
	//========== Add your code below ==========//
	

	// 1. Read the camera frames and open a window to show it.
    cv::Mat Image;
    Image = readCamera();

    cout << "Got File!" << endl;


	// 2. Segment the object(s) and calculate the centroid(s) and principle angle(s).
    std::vector<cv::Point> centroids;
    std::vector<double> principal_angles;
    process_image(Image,centroids, principal_angles);


	// 3. Use prespective transform to calculate the desired pose of the arm.
  // pixel to mm with camera matrix
  
	double pxTOmm = 740.0 / 1280.0;
	double z_init = 0.0;
	double z_ground = -200.0;
	double z_stack = -200.0;

	
	// TODO
	// 

	double x,y,z,x_stack,y_stack;
  	double a;
	for (int c = 0; c<3; c++){
		cout<<centroids[c]<<endl;
			
		//hand eye coordination
		// read centroids and transform from camera pixels to robot milimeters
		cv::Matx31f world_cord(centroids[c].x, centroids[c].y, 1);
		world_cord = camera_matrix.inv()*world_cord;
		world_cord *= z_world; //z_world defines unit, have to figure out with unit, seems that it is in mm without z_world

		// here still missing transfering image coordiante system to robot coordiante system, hand eye coordination

		x = world_cord[c].x
		y = world_cord[c].y
		x_stack = world_cord[1].x
		y_stack = world_cord[1].y

		/*x = 360.0 - centroids[c].x * pxTOmm;
		cout<<x<<endl;
		cout<<pxTOmm<<endl;
			y = 200.0 + centroids[c].y * pxTOmm;
			x_stack = 312 - centroids[1].x * pxTOmm;
			y_stack = 335 + centroids[1].y * pxTOmm;*/
		a = principal_angles[c];
		a = (a / (2.0*PI)) *360;
		cout<<a<<endl;
		//a=180; //for testing
		
			// Move arm to correct (x,y) position and orientation above block
		char command_init[80];
		char command_toGround[80];
		char command_closeGripper[80];
		char command_up[80];
		char command_center[80];
		char command_centerDown[80];
		char command_openGripper[80];
		
		sprintf(command_init, "MOVP %f %f %f 90 0 -%f", x, y , z_init, a);
		cout<<command_init<<endl;
		sendCommand(command_init, ClientSocket);
		Sleep(1000);
			// Move arm to ground
			/*sprintf(command_toGround, "MOVP %f %f %f 90 0 -%f", x, y , z_ground, a);
			sendCommand(command_toGround, ClientSocket);

			// grip block
			sprintf(closeGripper, "OUTPUT 48 ON");
			sendCommand(closeGripper, ClientSocket);
			Sleep(1000);

			// Move arm up again
			sprintf(command_up, "MOVP %f %f %f 90 0 -%f", x, y , z_init, a);
			sendCommand(command_up, ClientSocket);
			
			// Move arm to to stacking center (here position of first detected block) and rotate
			sprintf(command_center, "MOVP %f %f %f 90 0 180", x_stack, y_stack, z_init) ; 
			sendCommand(command_center, ClientSocket);

			// Move arm down to stack block
			spintf(command_centerDown,"MOVP %f %f %f 90 0 180", x_stack, y_stack, z_stack); // 300,350 = corner of working plane
			sendCommand(command_centerDown, ClientSocket);

			// put block blog on predefinde steacking place (here position of first detected block)
			char openGripper[] = "OUTPUT 48 OFF";
			sendCommand(openGripper, ClientSocket);
			Sleep(1000);

			// Move arm up again to start from there to next position
			sprintf(command_center, "MOVP %f %f %f 90 0 180", x_stack, y_stack, z_init); 
			sendCommand(command_center, ClientSocket);

			z_stack = z_stack + 30; // + 30mm for stacking next block on top of the first one
			*/
	}
	
	//========== Add your code above ==========//
	
	system("pause"); 
		
	// shutdown the connection since we're done
    iResult = shutdown(ClientSocket, SD_SEND);
    if (iResult == SOCKET_ERROR) {
        printf("shutdown failed with error: %d\n", WSAGetLastError());
        closesocket(ClientSocket);
        WSACleanup();
        return 1;
    }

    // cleanup
    closesocket(ClientSocket);
    WSACleanup();

    return 0;
}
