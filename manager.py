import uuid

from game import Game

class Manager(object):
    """
    Manages the initialisation of TicTacToe games and keeps a record
    of the games in progress. A separate class, 'Game', is used to
    track each individual game.
    """
    def __init__(self):
        self.player_waiting = None

    def add_new_player(self, player):
        """
        A naive implementation for managing the initialisation of new
        games. If there's a player waiting, start a new game. If not,
        then just keep the player waiting until another player
        joins. Fails on any exception like the waiting player closing
        their connection before another player joins.
        """
        player_uuid = str(uuid.uuid4())

        if self.player_waiting is None:
            # No other player waiting.
            assert self.player_waiting is None
            self.player_waiting = player
            return None
        else:
            # Another player is already waiting, start a game.
            assert self.player_waiting is not None
            game = Game(
                player_one=self.player_waiting,
                player_two=player,
            )
            self.player_waiting = None
            return game
