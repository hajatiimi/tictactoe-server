import statemachine
import uuid
import logging

logger = logging.getLogger(__name__)

class PlayerState(statemachine.StateMachine):
    from statemachine import State

    unconnected = State('Unconnected', initial=True)
    connected = State('Connected')
    won = State('Won')
    lost = State('Lost')    

    connect = unconnected.to(connected)
    win = connected.to(won)
    lose = connected.to(lost)

    def on_connect(self):
        logging.info("Player {}: PlayerState:connect".format(self.model.uuid))
        # FIXME: Hardwired grid size used here!
        # FIXME: Hardwired player 'UUID' used here!
        if self.model.is_starting_player:
            starting_player_id = self.model.uuid
        else:
            starting_player_id = "someone else"
        self.model.sock.send("GAME-READY 3 3 {}\n".format(starting_player_id).encode())

    def on_win(self):
        logging.info("Player {}: PlayerState:win".format(self.model.uuid))
        self.model.sock.send(b'GAME-WON WON\n')

    def on_lose(self):
        logging.info("Player {}: PlayerState:lose".format(self.model.uuid))
        self.model.sock.send(b'GAME-WON LOST\n')
        
class Player(object):
    """
    Represents a single connected client, that is, "The Player
    of Games". The player's state is controlled throgh an FSM.
    """
    state_machine_name = PlayerState

    def __init__(self, player_sock):
        self.state = 'unconnected'
        
        self.sock = player_sock
        self.uuid = str(uuid.uuid4())

        self.fsm = PlayerState(self)
        self.is_starting_player = False

    def make_starting_player(self):
        self.is_starting_player = True
