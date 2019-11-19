class Game(object):
    """Class to manage a single TicTacToe game."""

    def __init__(self, player_one=None, player_two=None):
        """
        Takes two tuples, one for each player. Both tuples should
        have two elements with [0] as the player's sock and [1] as
        the player's UUID.
        """
        assert player_one is not None
        assert player_two is not None

        print("New game started")
        self.player_one_sock = player_one[0]
        self.player_one_uuid = player_one[1]
        self.player_two_sock = player_two[0]
        self.player_two_uuid = player_two[1]
