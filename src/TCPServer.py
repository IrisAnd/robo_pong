#!/usr/bin/env python
 
import socket


TCP_IP = ""                         # Standard loopback interface address (localhost)
TCP_PORT = 5005                     # Port to listen on (non-privileged ports are > 1023)
BUFFER_SIZE = 1024                  # Normally 1024, but we want fast response

# create and bind socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
print("Socket opened ...")

# start listening for incoming connections
s.listen()
print("Server is listening ...")
 
conn, addr = s.accept()
print('Connection address:', addr)
while True:
    data = conn.recv(BUFFER_SIZE)
    if not data:
        break
    print("received data:", data)
    conn.send(data)  # echo
conn.close()
