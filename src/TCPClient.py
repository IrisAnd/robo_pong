#!/usr/bin/env python
#  
import socket
 
 
# specify server IP
TCP_IP = '10.38.236.84'           # ITRI PC: WLAN receiver IP
# TCP_IP = '10.38.197.195'          # Jakobs wlan ip
# TCP_IP = '127.0.0.1'              # Standard loopback interface address (localhost)

# Port to listen on (non-privileged ports are > 1023)
TCP_PORT = 27015                # ITRI PC
# TCP_PORT = 5005                 # Jakob Laptop

BUFFER_SIZE = 1024
# MESSAGE = "Hello World!"
MESSAGE = [200, 400, 50]
# MESSAGE = 1

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    # it calls only connect() and immediately sends data to the server
    print('start connect ...')

    s.connect((TCP_IP, TCP_PORT))
    print('start send ...')
    # s.send(MESSAGE.encode())
    s.send(bytearray(MESSAGE))
    # s.send(MESSAGE.to_bytes(1, byteorder='big'))
    data = s.recv(BUFFER_SIZE)

# s.close()

print("received data:", repr(data))