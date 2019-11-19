#!/usr/bin/python3

import selectors
import socket

from manager import Manager

sel = selectors.DefaultSelector()

HANDLERS = {}
manager = Manager()

def accept(sock, mask):
    conn, addr = sock.accept()
    print("New client connection {} from {}".format(conn, addr))
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)

def read(conn, mask):
    data = conn.recv(1024)
    print("data type:", type(data))
    print("length data:", len(data))
    if data:
        cmd = data.split()
        if cmd[0] in HANDLERS:
            HANDLERS[cmd[0]](conn, *cmd[1:])
        else:
            conn.send(b'ERROR\n')
    else:
        print("Closing connection")
        sel.unregister(conn)
        conn.close()

def handle_game_join(sock, *args):
    assert not args, "No arguments expected for GAME-JOIN"
    print("GAME-JOIN called:", args)
    player_uuid = manager.add_new_player(sock)
    sock.send(b'GAME-JOIN-ACK ' + bytes(player_uuid.encode('ascii')) + b'\n')

HANDLERS[b'GAME-JOIN'] = handle_game_join

if __name__ == '__main__':

    HOST = 'localhost'
    PORT = 8282

    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(False)
    sock.bind((HOST, PORT))
    sock.listen(100)
    sel.register(sock, selectors.EVENT_READ, accept)

    while True:
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)
