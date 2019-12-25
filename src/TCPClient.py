#!/usr/bin/env python
#  
import socket
import struct
import time

 
# specify server IP
TCP_IP = '10.38.236.84'           # ITRI PC: WLAN receiver IP
# TCP_IP = '10.38.197.195'          # Jakobs wlan ip
# TCP_IP = '127.0.0.1'              # Standard loopback interface address (localhost)

# Port to listen on (non-privileged ports are > 1023)
TCP_PORT = 27015                  # ITRI PC
# TCP_PORT = 5005                   # Jakob Laptop

BUFFER_SIZE = 4
MESSAGE = [200.0, 400.0, 50.0]

# create list of bytes
B_MESSAGE = []
for number in MESSAGE:
    number = float(number)
    B_MESSAGE.append(bytearray(struct.pack("f", number)))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print('start connect ...')
    s.connect((TCP_IP, TCP_PORT))
    print('start send ...')

    for byte_array in B_MESSAGE:
        s.send(byte_array)
        print('sent {}'.format(byte_array))

    data = "data"
    while data is not None:
        data = s.recv(BUFFER_SIZE)
        print("received data:", repr(data))
    s.close()