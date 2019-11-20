#!/usr/bin/python3

import selectors
import socket
import logging

from manager import Manager
from player import Player

# Set up logging to stdout at DEBUG level
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

sel = selectors.DefaultSelector()

HANDLERS = {}
manager = Manager()

# FIXME: Framing is missing!
# buffers = {}

# FIXME: BUG! We can have only one game running!
game = None

def accept(sock, mask):
    conn, addr = sock.accept()
    logger.info("[Client {}] Connection from {}:{}".format(conn.fileno(), addr[0], addr[1]))
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)


def read(sock, mask):
    data = sock.recv(1024).decode('ascii').strip()
    logger.info("[Client {}] Received data: {}".format(sock.fileno(), data))
    if data:
        cmd = data.split()
        if cmd[0] in HANDLERS:
            HANDLERS[cmd[0]](sock, *cmd[1:])
        else:
            sock.send(b'ERROR\n')
    else:
        logger.info("[Client {}] Closing connection".format(sock.fileno()))
        sel.unregister(sock)
        sock.close()


def handle_game_join(sock, *args):
    global game  # FIXME: ugly!
    assert not args, "No arguments expected for GAME-JOIN"
    logger.info("[Client {}] GAME-JOIN called: {}".format(sock.fileno(), args))
    player = Player(sock)
    sock.send(b'GAME-JOIN-ACK ' + bytes(player.uuid, 'ascii') + b'\n')
    game = manager.add_new_player(player)


def handle_game_ready_ack(sock, *args):
    assert not args, "No arguments expected for GAME-READY-ACK"
    logger.info("[Client {}] GAME-READY-ACK called: {}".format(sock.fileno(), args))
    # FIXME: We should have a state transition here!


def handle_turn(sock, *args):
    global game  # FIXME: ugly!
    assert len(args) == 3, "Expected three arguments for TURN"
    logger.info("[Client {}] TURN called: {}".format(sock.fileno(), args))
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

    logger.info("Server listening on {}:{}".format(host, port))

    while True:
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)
