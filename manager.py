import uuid

from game import Game

class Manager(object):
    """
    Manages the initialisation of TicTacToe games and keeps a record
    of the games in progress. A separate class, 'Game', is used to
    track each individual game.
    """
    def __init__(self):
        self.player_waiting_sock = None
        self.player_waiting_uuid = None

    def add_new_player(self, player_sock):
        """
        A naive implementation for managing the initialisation of new
        games. If there's a player waiting, start a new game. If not,
        then just keep the player waiting until another player
        joins. Fails on any exception like the waiting player closing
        their connection before another player joins. Returns an UUID
        assigned to the player as an str.
        """
        player_uuid = str(uuid.uuid4())

        if self.player_waiting_sock is None:
            # No other player waiting.
            assert self.player_waiting_sock is None
            assert self.player_waiting_uuid is None
            self.player_waiting_sock = player_sock
            self.player_waiting_uuid = player_uuid
        else:
            # Another player is already waiting, start a game.
            assert self.player_waiting_sock is not None
            assert self.player_waiting_uuid is not None
            game = Game(
                player_one=(self.player_waiting_sock, self.player_waiting_uuid),
                player_two=(player_sock, player_uuid),
            )
            self.player_waiting_sock = None
            self.player_waiting_uuid = None

        return player_uuid
