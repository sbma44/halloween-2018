#!/usr/bin/env python3

import json
import socket
import random
import socketserver
import os
import time
import asyncio
import websockets
import pystache
import spotipy, spotipy.util

TIC_INTERVAL = 1.0
MAC_LOOKUP = {
    'abcdefgh': 1
}
LAST_SEND = 0
CYCLE_DELAY = 10.0

SPOTIFY_SCOPES = [
    'user-read-playback-state',
    'user-read-currently-playing',
    'playlist-read-private',
    'user-library-read'
]

if __name__ == "__main__":
    
    with open('spotify_creds.json') as f:
        creds = json.load(f)
    token = spotipy.util.prompt_for_user_token(creds.get('user'),' '.join(SPOTIFY_SCOPES), creds.get('client_id'), client_secret=creds.get('client_secret'), redirect_uri='http://localhost')
    sp = spotipy.Spotify(auth=token)

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

        if len(sockets) and ((time.time() - LAST_SEND) > CYCLE_DELAY):
            
            rand = floor((time.time() % floor(CYCLE_DELAY * len(FX)) / CYCLE_DELAY))
            with open('fx/{}'.format(FX[rand])) as f:
                fx = ';'.join(f.readlines())
            
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

            if sent_something:
                LAST_SEND = time.time()

        print("tic!")

        track = sp.current_user_playing_track()
        remaining = (track.get('item', {}).get('duration_ms') - track.get('progress_ms')) / 1000.0

        print('waiting {} seconds'.format(remaining))

        await asyncio.sleep(remaining)
        asyncio.ensure_future(tic())

    asyncio.get_event_loop().run_until_complete(websockets.serve(register, '0.0.0.0', 8765))

    asyncio.ensure_future(tic())

    asyncio.get_event_loop().run_forever()