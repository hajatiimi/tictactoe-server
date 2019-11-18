from game import Game

class Manager(object):
    """
    Manages the initialisation of TicTacToe games and keeps a record
    of the games in progress. A separate class, 'Game', is used to
    track each individual game.
    """
    def __init__(self):
        self.player_waiting_sock = None

    def add_new_player(self, sock):
        """
        A naive implementation for managing the initialisation of new
        games. If there's a player waiting, start a new game. If not,
        then just keep the player waiting until another player
        joins. Fails on any exception like the waiting player closing
        their connection before another player joins.
        """
        if self.player_waiting_sock is None:
            # No other player waiting.
            self.player_waiting_sock = sock
        else:
            # Another player is already waiting, start a game.
            game = Game((self.player_waiting_sock, sock))
            self.player_waiting_sock = None
