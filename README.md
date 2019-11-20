# tictactoe-server

Server implementation for tic-tac-toe.

Usage: python3 client.py <bind-to-host> <bind-to-port>

## Running the client and server

First start the server and then the two clients. Make sure you have a
Python 3 environment. For the server, you need to have the packages
installed that are described in the 'requirements.txt' file. Using a
virtualenv is your friend here.

```
(cd tictactoe-server; python3 ttt-server.py localhost 8282)
(cd tictactoe-client-1; python3 client.py localhost 8282)
(cd tictactoe-client-2; python3 client.py localhost 8282)
```
