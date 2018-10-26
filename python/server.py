#!/usr/bin/env python3

import json
import random
import os
import sys
import math
import time
import asyncio
import websockets
import pystache
import spotipy, spotipy.util

if __name__ == "__main__":
    
    DEBUG = '--debug' in sys.argv

    if DEBUG:
        print('*** DEBUG MODE ***')
        FX = ['debug.lua']
    else:
        FX = [f for f in os.listdir('./fx') if 'debug.lua' not in f]
    #FX = ['diamond.lua']
    print('found fx files: {}'.format(' '.join(FX)))

    sockets = {}
    global meta
    meta = { 'LAST_SEND': 0, 'index': 0 }
    TIC_INTERVAL = 1.0
    MAC_LOOKUP = [
        '5c:cf:7f:53:d8:ab', #D
        '5c:cf:7f:53:d6:f0', #F
        '5c:cf:7f:53:d8:b0', #A
        '5c:cf:7f:53:d6:1c', #C
        '5c:cf:7f:53:d9:16', #B
        '5c:cf:7f:53:d3:fe', #E
    ]
    CYCLE_DELAY = 10.0
    sem = asyncio.Semaphore(1)

    SPOTIFY_SCOPES = [
        'user-read-playback-state',
        'user-read-currently-playing',
        'playlist-read-private',
        'user-library-read'
    ]

    # set up spotify API object
    with open('spotify_creds.json') as f:
        creds = json.load(f)
    token = spotipy.util.prompt_for_user_token(creds.get('user'),' '.join(SPOTIFY_SCOPES), creds.get('client_id'), client_secret=creds.get('client_secret'), redirect_uri='http://localhost')
    sp = spotipy.Spotify(auth=token)

    # connection handler
    async def register(websocket, path):
        try:
            async for m in websocket:
                print("connection from {}".format(m))
                already_present = m in sockets
                sockets[m] = websocket
                if already_present:
                    await(tic((m,)))
        finally:
            await(unregister(websocket))

    # disconnection handler
    async def unregister(websocket):
        target_mac = None
        for mac in sockets:
            if sockets[mac] == websocket:
                target_mac = mac
        if target_mac is not None:
            del sockets[target_mac]

    # send messages on some interval
    async def tic(macs=[]):
        sent_something = False
        global meta

        if len(sockets):
            # dumb cycle through fx
            rand = meta['index']
            meta['index'] = (meta['index'] + 1) % len(FX)
            print("sending {}".format(FX[rand]))
            with open('fx/{}'.format(FX[rand])) as f:
                fx = ''.join([x for x in f.readlines() if len(x.strip())])
            
            to_send = [] # queue up (websocket, msg) tuples
            # filter to individual mac(s) if called by connection handler (don't refresh all strands)
            mac_list = sockets.keys()
            if len(macs):
                mac_list = [m for m in mac_list if m in macs]

            # send queued messages
            stable_h = random.randint(0, 360)
            for (i, mac) in enumerate(sorted(sockets.keys())):
                vars = {
                    'offset': MAC_LOOKUP.index(mac) if mac in MAC_LOOKUP else -1,
                    'r': random.randint(0, 255),
                    'g': random.randint(0, 255),
                    'b': random.randint(0, 255),
                    'h': random.randint(0, 360),
                    'stable_h': stable_h,
                    'wait_until': time.time() + 2.0
                }
                to_send.append((sockets[mac], pystache.render(fx, vars)))
                sent_something = True
            await asyncio.wait([ws.send(msg) for (ws, msg) in to_send])

            if sent_something:
                meta['LAST_SEND'] = time.time()

        # refresh spotify info
        remaining = 15.0
        if not DEBUG:
            track = sp.current_user_playing_track()
            if track:
                remaining = (track.get('item', {}).get('duration_ms') - track.get('progress_ms')) / 1000.0

        # only schedule the next tic if one hasn't been called during processing this one
        if not sem.locked():
            async with sem:
                print('tic! waiting {} seconds...'.format(remaining))
                await asyncio.sleep(remaining)
                meta['task'] = asyncio.ensure_future(tic())
        else:
            print('existing callback detected, avoiding duplication')

    asyncio.get_event_loop().run_until_complete(websockets.serve(register, '0.0.0.0', 8765))

    asyncio.ensure_future(tic())

    asyncio.get_event_loop().run_forever()
