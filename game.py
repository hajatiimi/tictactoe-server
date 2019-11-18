class Game(object):
    """Class to manage a single TicTacToe game."""

    def __init__(self, player_socks):
        """
        player_socks should be a two-tuple of sockets for players
        one and two.
        """
        print("New game started")
        self.player_one_sock = player_socks[0]
        self.player_two_sock = player_socks[1]
