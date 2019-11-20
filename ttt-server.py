#!/usr/bin/python3

import selectors
import socket

from manager import Manager
from player import Player

sel = selectors.DefaultSelector()

HANDLERS = {}
manager = Manager()

# FIXME: Framing is missing!
# buffers = {}

# FIXME: BUG! We can have only one game running!
game = None

def accept(sock, mask):
    conn, addr = sock.accept()
    print("New client connection {} from {}".format(conn, addr))
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)

    
def read(sock, mask):
    data = sock.recv(1024).decode('ascii').strip()
    print("data:", data)
    print("length data:", len(data))
    if data:
        cmd = data.split()
        if cmd[0] in HANDLERS:
            HANDLERS[cmd[0]](sock, *cmd[1:])
        else:
            sock.send(b'ERROR\n')
    else:
        print("Closing connection")
        sel.unregister(sock)
        sock.close()

        
def handle_game_join(sock, *args):
    global game  # FIXME: ugly!
    assert not args, "No arguments expected for GAME-JOIN"
    print("GAME-JOIN called:", args)
    player = Player(sock)
    sock.send(b'GAME-JOIN-ACK ' + bytes(player.uuid, 'ascii') + b'\n')
    game = manager.add_new_player(player)
    print("game:", game)
    

def handle_game_ready_ack(sock, *args):
    assert not args, "No arguments expected for GAME-READY-ACK"
    print("GAME-READY-ACK called:", args)
    # FIXME: We should have a state transition here!

    
def handle_turn(sock, *args):
    global game  # FIXME: ugly!
    assert len(args) == 3, "Expected three arguments for TURN"
    print("TURN called:", args)
    print("game in turn:", game)
    game.run_turn(sock, int(args[1]), int(args[2]))
    
HANDLERS['GAME-JOIN'] = handle_game_join
HANDLERS['GAME-READY-ACK'] = handle_game_ready_ack
HANDLERS['TURN'] = handle_turn

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 3:
        print("Usage: {} <bind-to-host> <bind-to-port>".format(sys.argv[0]))
        sys.exit(1)

    host, port = sys.argv[1], int(sys.argv[2])

    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(False)
    sock.bind((host, port))
    sock.listen(100)
    sel.register(sock, selectors.EVENT_READ, accept)

    while True:
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)
