#undef UNICODE

#define WIN32_LEAN_AND_MEAN

#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>

#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include <string>

#include "opencv.hpp"
// Need to link with Ws2_32.lib
#pragma comment (lib, "Ws2_32.lib")

#define DEFAULT_BUFLEN 512
#define DEFAULT_PORT "4000"

using namespace std;
using namespace cv;

// connect to laptop and get integer array
int* getMessage(int arrToBeFilled[]){
	
	//#include "stdafx.h"

	#define BUFLEN 1024
	#define PORT "27015"

    WSADATA wsaData2;
    int iResult2;

    SOCKET ListenSocket2 = INVALID_SOCKET;
    SOCKET ClientSocket2 = INVALID_SOCKET;

    struct addrinfo *result2 = NULL;
    struct addrinfo hints2;

    int iSendResult2;
    char recvbuf2[BUFLEN];
    int recvbuflen2 = BUFLEN;
    
    // Initialize Winsock
    iResult2 = WSAStartup(MAKEWORD(2,2), &wsaData2);
    if (iResult2 != 0) {
        printf("WSAStartup failed with error: %d\n", iResult2);
        //return 1;
    }

    ZeroMemory(&hints2, sizeof(hints2));
    hints2.ai_family = AF_INET;
    hints2.ai_socktype = SOCK_STREAM;
    hints2.ai_protocol = IPPROTO_TCP;
    hints2.ai_flags = AI_PASSIVE;

    // Resolve the server address and port
    iResult2 = getaddrinfo(NULL, PORT, &hints2, &result2);
    if ( iResult2 != 0 ) {
        printf("getaddrinfo failed with error: %d\n", iResult2);
        WSACleanup();
        //return 1;
    }

    // Create a SOCKET for connecting to server
    ListenSocket2 = socket(result2->ai_family, result2->ai_socktype, result2->ai_protocol);
    if (ListenSocket2 == INVALID_SOCKET) {
        printf("socket failed with error: %ld\n", WSAGetLastError());
        freeaddrinfo(result2);
        WSACleanup();
        //return 1;
    }
    printf("Socket created ...\n");

    // Setup the TCP listening socket
    iResult2 = bind( ListenSocket2, result2->ai_addr, (int)result2->ai_addrlen);
    if (iResult2 == SOCKET_ERROR) {
        printf("bind failed with error: %d\n", WSAGetLastError());
        freeaddrinfo(result2);
        closesocket(ListenSocket2);
        WSACleanup();
        //return 1;
    }

    freeaddrinfo(result2);

    iResult2 = listen(ListenSocket2, SOMAXCONN);
    if (iResult2 == SOCKET_ERROR) {
        printf("listen failed with error: %d\n", WSAGetLastError());
        closesocket(ListenSocket2);
        WSACleanup();
        //return 1;
    }
    printf("Server listening ...\n");

    // Accept a client socket
    ClientSocket2 = accept(ListenSocket2, NULL, NULL);
    if (ClientSocket2 == INVALID_SOCKET) {
        printf("accept failed with error: %d\n", WSAGetLastError());
        closesocket(ListenSocket2);
        WSACleanup();
        //return 1;
    }
    printf("Client accepted ...\n");

    // No longer need server socket
    closesocket(ListenSocket2);

	/*
	int sizeOfByteArray = 3;
    int* intArray = new int[sizeOfByteArray];
	*/

    // Receive until the peer shuts down the connection
    do {
        iResult2 = recv(ClientSocket2, recvbuf2, recvbuflen2,0);
        if (iResult2 > 0) {   								
			int arrLen = sizeof(arrToBeFilled);
			for (int i=0; i<arrLen; ++i){
				arrToBeFilled[i] = recvbuf2[i];
				//cout<<intArray[i]<<endl;
			}

        // Echo the buffer back to the sender
            iSendResult2 = send(ClientSocket2, recvbuf2, iResult2, 0 );
            if (iSendResult2 == SOCKET_ERROR) {
                printf("send failed with error: %d\n", WSAGetLastError());
                closesocket(ClientSocket2);
                WSACleanup();
                //return 1;
            }
            printf("Bytes sent: %d\n", iSendResult2);
        }
        else if (iResult2 == 0)
            printf("Connection closing...\n");
        else  {
            printf("recv failed with error: %d\n", WSAGetLastError());
            closesocket(ClientSocket2);
            WSACleanup();
            //return 1;
        }

    } while (iResult2 > 0);

    // shutdown the connection since we're done
    iResult2 = shutdown(ClientSocket2, SD_SEND);
    if (iResult2 == SOCKET_ERROR) {
        printf("shutdown failed with error: %d\n", WSAGetLastError());
        closesocket(ClientSocket2);
        WSACleanup();
        //return 1;
    }

    // cleanup
    closesocket(ClientSocket2);
    WSACleanup();

    return arrToBeFilled;
}

// send command to robot
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
	
	// 1. Read the int array with coordinates sent by remote laptop
	// for clarification see https://stackoverflow.com/questions/3473438/return-array-in-a-function

	int x, y, z;
	int arrToBeFilled[3];
	int *coordinates = getMessage(arrToBeFilled);
	x = coordinates[0];
	y = coordinates[1];
	z = coordinates[2];


	// 2. Move the robot to the specified coordinates
	char command[80];
	sprintf(command, "MOVP %f %f %f", x, y, z);
	sendCommand(command, ClientSocket);
	Sleep(1000);

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
