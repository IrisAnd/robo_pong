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
#pragma comment(lib, "Ws2_32.lib")

#define DEFAULT_BUFLEN 512
#define DEFAULT_PORT "4000"
#define BUFLEN 4
#define PORT "27015"

using namespace std;
using namespace cv;

// connect to laptop and get integer array
void sendMessage(cv::Point3f Point, SOCKET &ClientSocket)
{
    int iSendResult;

    float coordinates[3];
    coordinates[0] = Point.x;
    coordinates[1] = Point.y;
    coordinates[2] = Point.z;
    char bytes_temp[4];

    for (int c = 0; c < 3; c++)
    {
        memcpy(bytes_temp, (unsigned char *)(&coordinates[c]), 4);

        iSendResult = send(ClientSocket, bytes_temp, sizeof(bytes_temp), 0);
        if (iSendResult == SOCKET_ERROR)
        {
            printf("send failed with error: %d\n", WSAGetLastError());
            closesocket(ClientSocket);
            WSACleanup();
        }
        printf("Bytes sent: %d\n", iSendResult);
    }
}

// send command to robot
int sendCommand(char *sendbuf, SOCKET &ClientSocket)
{
    cout << "Sending Command: " << sendbuf << endl;
    int SendResult = 0;
    int ReceiveResult = 0;
    char recvbuf[512];
    int counter = 0;
    int RoundThreshold = 1000;

    //Send Command to Robot Arm
    SendResult = send(ClientSocket, sendbuf, strlen(sendbuf) + 1, 0);

    if (SendResult == SOCKET_ERROR)
    {
        cout << "send failed with error: " << WSAGetLastError() << endl;
        closesocket(ClientSocket);
        WSACleanup();
        return 1;
    }

    Sleep(100);

    do
    {
        ReceiveResult = recv(ClientSocket, recvbuf, 512, 0);
        counter++;
    } while (ReceiveResult == 0 && counter < RoundThreshold);

    if (counter > RoundThreshold)
    {
        cout << "Respond Time Out" << endl;
        return 1;
    }
    else
    {
        if (!strcmp(recvbuf, "ERR"))
        {
            cout << "Invalid Command" << endl;
            return 1;
        }
    }

    return 0;
}

int __cdecl main(void)
{

    //========== Robot Server ==========//
    WSADATA wsaData;
    int iResult;

    SOCKET ListenSocket = INVALID_SOCKET;
    SOCKET ClientSocket = INVALID_SOCKET;

    struct addrinfo *result = NULL;
    struct addrinfo hints;

    int recvbuflen = DEFAULT_BUFLEN;

    // Initialize Winsock
    iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (iResult != 0)
    {
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
    if (iResult != 0)
    {
        printf("getaddrinfo failed with error: %d\n", iResult);
        WSACleanup();
        return 1;
    }

    // Create a SOCKET for connecting to server
    ListenSocket = socket(result->ai_family, result->ai_socktype, result->ai_protocol);
    if (ListenSocket == INVALID_SOCKET)
    {
        printf("socket failed with error: %ld\n", WSAGetLastError());
        freeaddrinfo(result);
        WSACleanup();
        return 1;
    }

    // Setup the TCP listening socket
    iResult = bind(ListenSocket, result->ai_addr, (int)result->ai_addrlen);
    if (iResult == SOCKET_ERROR)
    {
        printf("bind failed with error: %d\n", WSAGetLastError());
        freeaddrinfo(result);
        closesocket(ListenSocket);
        WSACleanup();
        return 1;
    }

    freeaddrinfo(result);

    iResult = listen(ListenSocket, SOMAXCONN);
    if (iResult == SOCKET_ERROR)
    {
        printf("listen failed with error: %d\n", WSAGetLastError());
        closesocket(ListenSocket);
        WSACleanup();
        return 1;
    }

    // Accept a client socket
    ClientSocket = accept(ListenSocket, NULL, NULL);
    if (ClientSocket == INVALID_SOCKET)
    {
        printf("accept failed with error: %d\n", WSAGetLastError());
        closesocket(ListenSocket);
        WSACleanup();
        return 1;
    }

    // No longer need server socket
    closesocket(ListenSocket);

    //========== Camera Server ==========//

    WSADATA wsaData2;

    SOCKET ListenSocket2 = INVALID_SOCKET;
    SOCKET ClientSocket2 = INVALID_SOCKET;

    struct addrinfo *result2 = NULL;
    struct addrinfo hints2;

    int iResult2;

    // Initialize Winsock
    iResult2 = WSAStartup(MAKEWORD(2, 2), &wsaData2);
    if (iResult2 != 0)
    {
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
    if (iResult2 != 0)
    {
        printf("getaddrinfo failed with error: %d\n", iResult2);
        WSACleanup();
        //return 1;
    }

    // Create a SOCKET for connecting to server
    ListenSocket2 = socket(result2->ai_family, result2->ai_socktype, result2->ai_protocol);
    if (ListenSocket2 == INVALID_SOCKET)
    {
        printf("socket failed with error: %ld\n", WSAGetLastError());
        freeaddrinfo(result2);
        WSACleanup();
        //return 1;
    }
    printf("Socket created ...\n");

    // Setup the TCP listening socket
    iResult2 = bind(ListenSocket2, result2->ai_addr, (int)result2->ai_addrlen);
    if (iResult2 == SOCKET_ERROR)
    {
        printf("bind failed with error: %d\n", WSAGetLastError());
        freeaddrinfo(result2);
        closesocket(ListenSocket2);
        WSACleanup();
        //return 1;
    }

    freeaddrinfo(result2);

    iResult2 = listen(ListenSocket2, SOMAXCONN);
    if (iResult2 == SOCKET_ERROR)
    {
        printf("listen failed with error: %d\n", WSAGetLastError());
        closesocket(ListenSocket2);
        WSACleanup();
        //return 1;
    }
    printf("Server listening ...\n");

    // Accept a client socket
    ClientSocket2 = accept(ListenSocket2, NULL, NULL);
    if (ClientSocket2 == INVALID_SOCKET)
    {
        printf("accept failed with error: %d\n", WSAGetLastError());
        closesocket(ListenSocket2);
        WSACleanup();
        //return 1;
    }
    printf("Client accepted ...\n");

    // No longer need server socket
    closesocket(ListenSocket2);

    //========== Automated Calibration ==========//

    // ensure high variance in all axes and visibility of ball
    // define world coordinates for calibration
    cv::Point3f Point1 = (-0.01, 251.14, 208.73);
    cv::Point3f Point2 = (26.83, 188.36, 473.59);
    cv::Point3f Point3 = (71.17, 526.10, 18.00);
    cv::Point3f Point4 = (110.59, 429.92, 285.81);
    cv::Point3f Point5 = (65.65, 198.20, 435.28);
    cv::Point3f Point6 = (226.00, 477.19, -46.48);
    cv::Point3f Point7 = (206.72, 353.95, 339.27);
    cv::Point3f Point8 = (93.55, 109.99, 471.64);
    cv::Point3f Point9 = (418.05, 358.83, -27.28);
    cv::Point3f Point10 = (408.41, 234.29, 265.65);
    cv::Point3f Point11 = (201.19, 72.41, 456.05);
    cv::Point3f Point12 = (531.98, 88.46, 108.16);
    cv::Point3f Point13 = (438.18, -2.58, 308.79);
    cv::Point3f Point14 = (534.02, -105.82, 83.16);
    cv::Point3f Point15 = (423.42, -122.20, 305.81);
    cv::Point3f Point16 = (244.01, -93.70, 438.77);
    cv::Point3f Point17 = (478.41, -266.70, 61.52);
    cv::Point3f Point18 = (488.16, -71.63, 228.49);
    cv::Point3f Point19 = (302.37, -35.99, 417.84);
    cv::Point3f Point20 = (415.80, -343.60, 107.68);
    cv::Point3f Point21 = (182.87, -230.46, 423.33);
    cv::Point3f Point22 = (249.03, -433.05, 216.83);
    cv::Point3f Point23 = (116.02, -331.25, 388.71);

    // stack world coordinates to vector
    std::vector<cv::Point3f> world_coordinates;
    world_coordinates.stack(Point1);
    world_coordinates.stack(Point2);
    world_coordinates.stack(Point3);
    world_coordinates.stack(Point4);
    world_coordinates.stack(Point5);
    world_coordinates.stack(Point6);
    world_coordinates.stack(Point7);
    world_coordinates.stack(Point8);
    world_coordinates.stack(Point9);
    world_coordinates.stack(Point10);
    world_coordinates.stack(Point11);
    world_coordinates.stack(Point12);
    world_coordinates.stack(Point13);
    world_coordinates.stack(Point14);
    world_coordinates.stack(Point15);
    world_coordinates.stack(Point16);
    world_coordinates.stack(Point17);
    world_coordinates.stack(Point18);
    world_coordinates.stack(Point19);
    world_coordinates.stack(Point20);
    world_coordinates.stack(Point21);
    world_coordinates.stack(Point22);
    world_coordinates.stack(Point23);

    for (int c = 0; c < sizeof(world_coordinates); c++)
    {
        coordinates = world_coordinates[c];

        char command[80];
        // TODO: set gripper position to  catch position A B C
        sprintf(command, "MOVP %f %f %f 0 -60 180", coordinates.x, coordinates.y, coordinates.z);
        sendCommand(command, ClientSocket);

        Sleep(5000); // wait for robot to drive to position
        cout << "Moved to: " << coordinates.x << " " << coordinates.y << " " << coordinates.z << endl;
        sendMessage(coordinates, ClientSocket2);
        Sleep(2500); // wait for camera to save ball position
    }

    //========== Camera Server ==========//
    // shutdown the connection since we're done
    int iResult = shutdown(ClientSocket2, SD_SEND);
    if (iResult == SOCKET_ERROR)
    {
        printf("shutdown failed with error: %d\n", WSAGetLastError());
        closesocket(ClientSocket2);
        WSACleanup();
        //return 1;
    }

    // cleanup
    closesocket(ClientSocket2);
    WSACleanup();
    //=======================================//

    system("pause");

    // shutdown the Robot server connection since we're done
    iResult = shutdown(ClientSocket, SD_SEND);
    if (iResult == SOCKET_ERROR)
    {
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