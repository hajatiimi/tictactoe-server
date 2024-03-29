"""
Game mechanics implementation for TicTacToe
on a 3x3 grid. Handles player turns and checking
if a player won.
"""

import logging

from player import Player

logger = logging.getLogger(__name__)

class Game(object):
    """Class to manage a single TicTacToe game."""

    # FIXME: Supports now only 3x3 grid.
    ROWS = 3
    COLUMNS = 3

    def __init__(self, player_one=None, player_two=None):
        """
        Takes two tuples, one for each player. Both tuples should
        have two elements with [0] as the player's sock and [1] as
        the player's UUID.
        """
        assert player_one is not None
        assert player_two is not None

        self.player_one = player_one
        self.player_two = player_two

        logger.info("New game started: {}={} {}={}".format(
            player_one.sock.fileno(), player_one.uuid,
            player_two.sock.fileno(), player_two.uuid,
        ))

        self.turn = 'one'  # READY PLAYER ONE!
        self.turn_seq = None
        self.grid = []
        for r in range(self.ROWS):
            self.grid.append([])
            for c in range(self.COLUMNS):
                self.grid[r].append(None)

        self.player_one.make_starting_player()
        self.player_one.fsm.connect()
        self.player_two.fsm.connect()

    def get_current_player_by_sock(self, sock):
        player = None

        if self.player_one.sock == sock:
            player = self.player_one
        if self.player_two.sock == sock:
            player = self.player_two

        assert player is not None, "No player found for the sock"

        return player

    def get_other_player_by_sock(self, sock):
        player = None

        if self.player_one.sock == sock:
            player = self.player_two
        if self.player_two.sock == sock:
            player = self.player_one

        assert player is not None, "No player found for the sock"

        return player

    def do_we_have_a_winner(self):
        """Do what it says on the tin."""
        WINNERS = (
            ((0,0),(0,1),(0,2)),
            ((1,0),(1,1),(1,2)),
            ((2,0),(2,1),(2,2)),
            ((0,0),(1,0),(2,0)),
            ((0,1),(1,1),(2,1)),
            ((0,2),(1,2),(2,2)),
            ((0,0),(1,1),(2,2)),
            ((0,2),(1,1),(2,0)),
        )

        for x, y, z in WINNERS:
            if self.grid[x[0]][x[1]] == self.grid[y[0]][y[1]] == self.grid[z[0]][z[1]] == '1':
                return 'one'

        for x, y, z in WINNERS:
            if self.grid[x[0]][x[1]] == self.grid[y[0]][y[1]] == self.grid[z[0]][z[1]] == '2':
                return 'two'

        return None

    def run_turn(self, sock, turn_seq=None, row=None, column=None):
        """
        Handle one turn with a player (client) submitting
        row and column where they want to play. Checks if
        the player won the game and then switches the turn
        to the other player.
        """
        assert turn_seq is not None
        assert row is not None
        assert column is not None
        assert row >= 1 and row <= self.ROWS
        assert column >= 1 and column <= self.COLUMNS

        self.turn_seq = turn_seq

        player = self.get_current_player_by_sock(sock)
        other_player = self.get_other_player_by_sock(sock)

        logger.info("[Client {}] Running turn {} for {}".format(sock.fileno(), self.turn_seq, self.turn))
        logger.info("[Client {}] Client is player one: {}".format(sock.fileno(), player == self.player_one))
        logger.info("[Client {}] Client is player two: {}".format(sock.fileno(), player == self.player_two))

        if self.turn == 'one':
            assert player == self.player_one
            self.grid[row-1][column-1] = '1'
        if self.turn == 'two':
            assert player == self.player_two
            self.grid[row-1][column-1] = '2'

        logger.info("[Client {}] Grid after turn: {}".format(sock.fileno(), self.grid))

        winner = self.do_we_have_a_winner()
        if winner is not None:
            if winner == 'one':
                self.player_one.fsm.win()
                self.player_two.fsm.lose()
            if winner == 'two':
                self.player_two.fsm.won()
                self.player_one.fsm.lose()

        if self.turn == 'one':
            self.turn = 'two'
        elif self.turn == 'two':
            self.turn = 'one'
        else:
            assert False, "out of turn!"

        logger.info("[Client {}] Set next player to {}".format(sock.fileno(), self.turn))

        # Send TURN-ACK to the current player.
        self.write(sock, "TURN-ACK {}".format(self.turn_seq))

        # Send the TURN data to the other player.
        self.write(other_player.sock, "TURN {} {} {}".format(self.turn_seq, row, column))

    def write(self, sock, data):
        """
        Send the given data to the given socket. The data can be a 'str'
        and will be encoded to a 'bytes' for sending on the wire. A '\n'
        is automatically added.
        """
        # FIXME: Duplicated code from ttt-server.py
        logger.info("[Client {}] Sending data: {}".format(sock.fileno(), data))
        data = data + "\n"
        sock.send(data.encode())
