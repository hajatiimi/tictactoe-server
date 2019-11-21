#!/usr/bin/python3

"""
Main code for the TicTacToe server. Run from the command line with
parameters for server-host and server-port (where the server will
listen for connections).
"""

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

def write(sock, data):
    """
    Send the given data to the given socket. The data can be a 'str'
    and will be encoded to a 'bytes' for sending on the wire. A '\n'
    is automatically added.
    """
    logger.info("[Client {}] Sending data: {}".format(sock.fileno(), data))
    data = data + "\n"
    sock.send(data.encode())

def read(sock, mask):
    """
    Read data from the socket, tokenise, and invoke the correct handler
    method. read() is called by Python selectors when a socket becomes
    ready for reading.
    """
    data = sock.recv(1024).decode().strip()
    logger.info("[Client {}] Received data: {}".format(sock.fileno(), data))
    if data:
        cmd = data.split()
        if cmd[0] in HANDLERS:
            HANDLERS[cmd[0]](sock, *cmd[1:])
        else:
            write(sock, "ERROR")
    else:
        logger.info("[Client {}] Closing connection".format(sock.fileno()))
        sel.unregister(sock)
        sock.close()


def handle_game_join(sock, *args):
    global game  # FIXME: ugly!
    assert not args, "No arguments expected for GAME-JOIN"
    logger.info("[Client {}] GAME-JOIN called: {}".format(sock.fileno(), args))
    player = Player(sock)
    write(sock, "GAME-JOIN-ACK {}".format(player.uuid))
    game = manager.add_new_player(player)


def handle_game_ready_ack(sock, *args):
    assert not args, "No arguments expected for GAME-READY-ACK"
    logger.info("[Client {}] GAME-READY-ACK called: {}".format(sock.fileno(), args))
    # FIXME: We should have a state transition here!


def handle_turn(sock, *args):
    global game  # FIXME: ugly!
    assert len(args) == 3, "Expected three arguments for TURN"
    logger.info("[Client {}] TURN called: {}".format(sock.fileno(), args))
    game.run_turn(sock, args[0], int(args[1]), int(args[2]))


def handle_turn_ack(sock, *args):
    assert len(args) == 1, "Expected one argument for TURN-ACK"
    logger.info("[Client {}] TURN-ACK called: {}".format(sock.fileno(), args))
    # This is really a no-op. We could check the turn number for verification.


HANDLERS['GAME-JOIN'] = handle_game_join
HANDLERS['GAME-READY-ACK'] = handle_game_ready_ack
HANDLERS['TURN'] = handle_turn
HANDLERS['TURN-ACK'] = handle_turn_ack

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
