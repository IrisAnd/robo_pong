#!/usr/bin/env python
#  
import socket
 
 
TCP_IP = '10.38.197.195'#'127.0.0.1'  # Standard loopback interface address (localhost)
TCP_PORT = 5005         # Port to listen on (non-privileged ports are > 1023)
BUFFER_SIZE = 1024
MESSAGE = 'Hello'

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#it calls only connect() and immediately sends data to the server.
    print('startconnect')
    s.connect((TCP_IP, TCP_PORT))
    print('startsend')
    s.send(MESSAGE.encode())
    data = s.recv(BUFFER_SIZE)
#s.close()

print("received data:", repr(data))