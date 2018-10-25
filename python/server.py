#!/usr/bin/env python3

import json
import random
import os
import math
import time
import asyncio
import websockets
import pystache
import spotipy, spotipy.util

if __name__ == "__main__":
    
    FX = os.listdir('./fx')
    print('found fx files: {}'.format(' '.join(FX)))

    sockets = {}
    global meta
    meta = { 'LAST_SEND': 0, 'index': 0 }
    TIC_INTERVAL = 1.0
    MAC_LOOKUP = {
        'abcdefgh': 1
    }
    CYCLE_DELAY = 10.0

    SPOTIFY_SCOPES = [
        'user-read-playback-state',
        'user-read-currently-playing',
        'playlist-read-private',
        'user-library-read'
    ]

    with open('spotify_creds.json') as f:
        creds = json.load(f)
    token = spotipy.util.prompt_for_user_token(creds.get('user'),' '.join(SPOTIFY_SCOPES), creds.get('client_id'), client_secret=creds.get('client_secret'), redirect_uri='http://localhost')
    sp = spotipy.Spotify(auth=token)

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
        global meta

        if len(sockets) and ((time.time() - meta['LAST_SEND']) > CYCLE_DELAY):
            
            rand = meta['index']
            meta['index'] = (meta['index'] + 1) % len(FX)
            print("sending {}".format(FX[rand]))
            with open('fx/{}'.format(FX[rand])) as f:
                fx = ';'.join([x for x in f.readlines() if len(x.strip()) > 0])
            
            to_send = [] # queue up (websocket, msg) tuples
            for mac in sockets:
                vars = {
                    'offset': MAC_LOOKUP.get(mac, 0),
                    'r': random.randint(0, 255),
                    'g': random.randint(0, 255),
                    'b': random.randint(0, 255),
                    'wait_until': 0
                }
                to_send.append((sockets[mac], pystache.render(fx, vars)))
                sent_something = True
            await asyncio.wait([ws.send(msg) for (ws, msg) in to_send])

            if sent_something:
                meta['LAST_SEND'] = time.time()

        print("tic!")

        track = sp.current_user_playing_track()
        remaining = (track.get('item', {}).get('duration_ms') - track.get('progress_ms')) / 1000.0

        print('waiting {} seconds'.format(remaining))

        await asyncio.sleep(remaining)
        asyncio.ensure_future(tic())

    asyncio.get_event_loop().run_until_complete(websockets.serve(register, '0.0.0.0', 8765))

    asyncio.ensure_future(tic())

    asyncio.get_event_loop().run_forever()