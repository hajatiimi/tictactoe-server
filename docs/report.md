# REPORT FOR DISTRIBUTED SYSTEMS TASK 1

Project team

* Jani Takkinen
* Aleksi Toivanen
* Tuomas Toivonen


## Introduction

The description for the course task was the design and implementation
of a distributed system running on, at minimum, three nodes. One of
the example applications to implement was a game. We decided to do
exactly that and selected TicTacToe as the game to implement.

Reason for selecting a rather simple game like TicTacToe was to allow
us to focus on the actual networking and distribution parts of the
application rather than on the implementation of the game mechanics.

We decided to implement the game as a reasonably straightforward
client-server architecture. For the game mechanics, we need to
maintain a single source of truth as to which of the positions on the
grid have been played and by which of the players. Keeping this source
of truth on a server application was an architecturally safe
choice. The clients as the players of the game will also need to
maintain an in-memory copy of the game grid in order to decide which
of the grid positions to play when it is their turn.

We also did two separate implementations of the client to make sure
that the client-server protocol is defined well enough.


## Considerations of the design and implementation

### Networking

We decided to use TCP/IP for communications and implement a simple
human-readable ASCII protocol. Networking for the TCP clients did not
present challenges. For the server, we experimented with three
different multiprocessing and networking paradigms.

First implementation draft forked a separate process to handle each of
the clients. For this, e.g. the file system or some other database
would have been needed to maintain the grids of the ongoing games. The
two processes handling the two clients playing a single game would
have used this file or database as the source of truth. Using a
database seemed overkill for the scope of this exercise and reading
and writing a shared file with appropriate locking seemed a bit
lacking in elegance.

Second implementation draft was implemented using multi-threading
instead of forking separate threads. Difference in a threaded version
compared to forking was to allow easy use of shared variables to
maintain shared state between two threads handling players of a
game. Locking challenges with a threaded version would remain.

Finally, in the current implementation asynchronous I/O is used
instead of forking or threading. The Python equivalent of the C
select(2) is used to monitor multiple TCP sockets for incoming data. A
message is read from a socket that becomes available for reading, and
the actions indicated by the message are performed synchronously. As
the individual actions are simple and fast, there's no need for the
type of asynchronity provided by forking or threading. No locking
challenges are present as we only have one process (or thread)
accessing or modifying the variables that hold the states of the
games.


### Protocol

The [protocol](protocol-example.txt) used between the server and
clients is a simple protocol relying on an underlying streamed
transport - in this case TCP. Framing of messages in the stream is
done by a simple newline, '\n'. Character set used is vanilla ASCII.

The protocol paradigm is query-response. However, queries and
responses can be initiated by both the server or the client at
different points of the protocol exchange. Each query-response is
synchronous: a query must be followed by a response before the next
query.

In the protocol each query or response is delimited by a
newline. Within a query or response, the string is to be tokenised by
a single space character. The first token in a query describes the
action. The first token in a response is acknowledgement. For example,
query "GAME-JOIN" is responded to with "GAME-JOIN-ACK". Each query or
response can contain zero or more parameters, delimited also by a
space.


## Missing features and improvement suggestions

* We have not implemented a formal specification for the
  protocol. Nevertheless, even with the informal protocol example
  document we were able to implement a server and two clients
  independently. We thus consider the protocol to be sufficiently well
  defined and documented as it is (for the purposes of this course
  task).

* We did not run the server and clients on separate physical or
  virtual machines. We considered sufficient distribution to be
  achieved by implementing the distributed system with three processes
  running on a single host and communicating over TCP. Splitting the
  processes on three separate hosts would not (materially) change the
  logic of the implementation or add this exercise.