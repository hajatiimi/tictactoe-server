#!/usr/bin/python3

import selectors
import socket

sel = selectors.DefaultSelector()

def accept(sock, mask):
    conn, addr = sock.accept()
    print("New connection {} from {}".format(conn, addr))
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)

def read(conn, mask):
    data = conn.recv(1024)
    if data:
        print("Received data:", data)
        conn.send(data)
    else:
        print("Closing connection")
        sel.unregister(conn)
        conn.close()

HOST = 'localhost'
PORT = 8282

sock = socket.socket()
sock.bind(('localhost', 8181))
sock.listen(100)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)

while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)
