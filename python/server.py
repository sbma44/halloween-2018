#!/usr/bin/env python3

import socket
import random
import socketserver
import os
import asyncio
import websockets
import pystache

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        try:
            # self.request is the TCP socket connected to the client
            self.data = self.request.recv(1024).strip()
            print("{} wrote:".format(self.client_address[0]))
            print(self.data)
            # just send back the same data, but upper-cased
            self.request.sendall(self.data.upper())
        except:
            pass

class MyTCPServer(socketserver.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.allow_reuse_address = True
        self.socket.bind(self.server_address)

if __name__ == "__main__":
    
    if os.fork():
        HOST, PORT = "0.0.0.0", 10321

        # Create the server, binding to localhost on port 10321
        with MyTCPServer((HOST, PORT), MyTCPHandler) as server:
            # Activate the server; this will keep running until you
            # interrupt the program with Ctrl-C
            server.serve_forever()
    else:
        INTERVAL = 5.0

        sockets = set()
        meta = {}
        async def register(websocket, path):
            print("connection")
            sockets.add(websocket)
            try:
                async for m in websocket:
                    print('got message {}'.format(m))
            finally:
                await(unregister(websocket))

        async def unregister(websocket):
            sockets.remove(websocket)

        async def tic():
            sent_something = False
            with open('application.lua') as f:
                msg = pystache.render(';'.join(f.readlines()), { 'r': random.randint(0, 255), 'g': random.randint(0, 255), 'b': random.randint(0, 255) }) 

            if len(sockets):
                await asyncio.wait([s.send(msg) for s in sockets])
            await asyncio.sleep(INTERVAL)
            asyncio.ensure_future(tic())

        asyncio.get_event_loop().run_until_complete(websockets.serve(register, '0.0.0.0', 8765))
	
        asyncio.ensure_future(tic())

        asyncio.get_event_loop().run_forever()        
