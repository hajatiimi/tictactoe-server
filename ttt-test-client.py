#!/usr/bin/python

# Test client for ttt-server. Doesn't do anything smart except tests a
# very basic flow of the game protocol. Useful for development and
# interactive testing of the server code.

import socket


HOST = "localhost"
PORT = 8282

def send(sock, data):
    print("SEND:", data)
    sock.sendall(bytes(data, "ascii") + b'\n')

def recv(sock):
    data = str(sock.recv(1024), "ascii").strip()
    print("RECV:", data)
    return data
    
# Create a socket: SOCK_STREAM == TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # Connect to server and send data
    sock.connect((HOST, PORT))

    send(sock, "GAME-JOIN")
    data = recv(sock)

    data = recv(sock)
    send(sock, "GAME-READY-ACK")

