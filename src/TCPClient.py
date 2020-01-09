#!/usr/bin/env python

import socket
import struct
import time
import cv2


class TCPClient:

    def __init__(self):
        # specify server IP
        self.TCP_IP = '10.38.236.84'        # ITRI PC: WLAN receiver IP
        # self.TCP_IP = '192.168.1.1'         # ITRI PC: LAN

        # Port to listen on (non-privileged ports are > 1023)
        self.TCP_PORT = 27015   # ITRI PC

        self.BUFFER_SIZE = 4
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print('start connect ...')
        self.s.connect((self.TCP_IP, self.TCP_PORT))
        print('connection successful')

    def close(self):
        self.s.close()

    def send_message(self, MESSAGE):

        # create list of bytes
        B_MESSAGE = []
        for number in MESSAGE:
            number = float(number)
            B_MESSAGE.append(bytearray(struct.pack("f", number)))

        for byte_array in B_MESSAGE:
            self.s.send(byte_array)

    # recieves and returns robot coordinate as 3 point byte array
    def recieve_message(self):
        data = self.s.recv(self.BUFFER_SIZE)
        return data


def main():
    client = TCPClient()
    DEFAULT_MESSAGE = [200.0, 400.0, 200.0]
    input("wait for input")
    client.send_message(DEFAULT_MESSAGE)


if __name__ == '__main__':
    main()
