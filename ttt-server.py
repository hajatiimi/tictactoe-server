#!/usr/bin/python3

import selectors
import socket

from manager import Manager
from player import Player

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
    player = Player(sock)
    sock.send(b'GAME-JOIN-ACK ' + bytes(player.uuid, 'ascii') + b'\n')
    manager.add_new_player(player)

def handle_game_ready_ack(sock, *args):
    assert not args, "No arguments expected for GAME-READY-ACK"
    print("GAME-READY-ACK called:", args)
    # FIXME: We should have a state transition here!


HANDLERS[b'GAME-JOIN'] = handle_game_join
HANDLERS[b'GAME-READY-ACK'] = handle_game_ready_ack

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
