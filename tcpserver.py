#!/usr/bin/python3

import socketserver
import threading

state = None
state_lock = threading.Condition()

class TTTRequestHandler(socketserver.StreamRequestHandler):
    
    def handle(self):
        global state
        with state_lock:
            print("New connection from {}:{} on thread {}".format(self.client_address[0], self.client_address[1], threading.current_thread().name))
            print("State before: {}".format(state))
            data = self.rfile.readline().strip()
            state = data
            self.wfile.write(data.upper())
            print("State after: {}".format(state))

class TTTServer(socketserver.ThreadingMixIn, socketserver.TCPServer):

    allow_reuse_address = True
        
if __name__ == "__main__":

    HOST = "localhost"
    PORT = 8181

    with TTTServer((HOST, PORT), TTTRequestHandler) as server:
        print("Ready to serve")
        server.serve_forever()

