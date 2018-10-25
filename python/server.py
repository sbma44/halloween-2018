#!/usr/bin/env python3

import socket
import random
import socketserver
import os
import asyncio
import websockets
import pystache

INTERVAL = 5.0
MAC_LOOKUP = {
    'abcdefgh': 1
}


if __name__ == "__main__":
    
    FX = os.listdir('./fx')
    print('found fx files: {}'.format(' '.join(FX)))

    sockets = {}
    async def register(websocket, path):
        print("connection!")
        try:
            async for m in websocket:
                print("got MAC {}".format(m))
                sockets[m] = websocket
        finally:
            await(unregister(websocket))

    async def unregister(websocket):
        target_mac = None
        for mac in sockets:
            if sockets[mac] == websocket:
                target_mac = mac
        if target_mac is not None:
            del dockets[target_mac]

    async def tic():
        sent_something = False
        with open('application.lua') as f:
            fx = ';'.join(f.readlines())

        if len(sockets):
            to_send = [] # queue up (websocket, msg) tuples
            for mac in sockets:
                vars = {
                    'offset': MAC_LOOKUP.get(mac, 0),
                    'r': random.randint(0, 255),
                    'g': random.randint(0, 255),
                    'b': random.randint(0, 255),
                    'delay': 0
                }
                to_send.append((sockets[mac], pystache.render(fx, vars)))
            await asyncio.wait([ws.send(msg) for (ws, msg) in to_send])

        await asyncio.sleep(INTERVAL)
        asyncio.ensure_future(tic())

    asyncio.get_event_loop().run_until_complete(websockets.serve(register, '0.0.0.0', 8765))

    asyncio.ensure_future(tic())

    asyncio.get_event_loop().run_forever()