import statemachine
import uuid


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
        print('PlayerState:connect')
        self.model.sock.send(b'GAME-READY\n')

    def on_win(self):
        print('PlayerState:win')
        self.model.sock.send(b'GAME-WON WON\n')

    def on_lose(self):
        print('PlayerState:lose')
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
