#!/usr/bin/env python3

import json
import datetime
import random
import os
import sys
import math
import time
import asyncio
import websockets
import pystache
import spotipy, spotipy.util

def get_playlist(sp):
    plo = sp.user_playlist(creds.get('user'), 'spotify:user:1216663148:playlist:63zBPWdtXyY1PUqz1qWA1Y')
    return [t['track']['name'] for t in plo['tracks']['items']]

if __name__ == "__main__":
    
    DEBUG = '--debug' in sys.argv

    if DEBUG:
        print('*** DEBUG MODE ***')
        #FX = ['debug.lua']
        FX = [f for f in os.listdir('./fx') if f.split('.')[-1] == 'lua']
    else:
        FX = [f for f in os.listdir('./fx') if f.split('.')[-1] == 'lua']
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

    PLAYLIST = get_playlist(sp)
    print('Found playlist tracks:')
    for t in PLAYLIST:
        print('    - {}'.format(t))

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

        if len(sockets) == 6:
            # dumb cycle through fx
            rand = meta['index']
            selected = FX[meta['index']]
            
            # no rainbows before midnight
            if datetime.datetime.now().hour > 6:
                while 'rainbow' in FX[meta['index']]:
                    meta['index'] = (meta['index'] + 1) % len(FX)
                    selected = FX[meta['index']]

            # no cycling bars until thriller
            if not meta.get('thriller', False):
                while 'bars' in FX[meta['index']]:
                    meta['index'] = (meta['index'] + 1) % len(FX)
                    selected = FX[meta['index']]

            meta['index'] = (meta['index'] + 1) % len(FX)

            # no thriller until it's time
            if 'thriller' in PLAYLIST[(meta['track_index'] + 1) % len(PLAYLIST)].lower():
                selected = 'thriller.lua'
                meta['thriller'] = True
            else:
                while 'thriller' in FX[meta['index']]:
                    meta['index'] = (meta['index'] + 1) % len(FX)
                    selected = FX[meta['index']]

            print("sending {}".format(selected))
            with open('fx/{}'.format(selected)) as f:
                fx = ''.join([x for x in f.readlines() if len(x.strip())])

            to_send = [] # queue up (websocket, msg) tuples
            # filter to individual mac(s) if called by connection handler (don't refresh all strands)
            mac_list = sockets.keys()
            if len(macs):
                mac_list = [m for m in mac_list if m in macs]

            # send queued messages
            stable_h = 0
            dice_roll = random.random()
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
                if datetime.datetime.now().hour < 22:
                    vars['stable_h'] = dice_roll < 0.5 and 17 or 290    
                if datetime.datetime.now().hour >= 22:
                    vars['stable_h'] = vars['offset'] % 2 == 0 and 17 or 290    
                if datetime.datetime.now().hour >= 23:
                    vars['stable_h'] = 0
                
                to_send.append((sockets[mac], pystache.render(fx, vars)))
                sent_something = True
            await asyncio.wait([ws.send(msg) for (ws, msg) in to_send])

            if sent_something:
                meta['LAST_SEND'] = time.time()

        # refresh spotify info
        remaining = 30.0
        if not DEBUG:
            track = sp.current_user_playing_track()
            meta['track_name'] = track.get('item', {}).get('name')
            try:
                meta['track_index'] = PLAYLIST.index(track_name)
            except:
                meta['track_index'] = 0
            if track and track.get('is_playing'):
                remaining = (track.get('item', {}).get('duration_ms') - track.get('progress_ms')) / 1000.0
            print('current track: {}'.format(meta['track_name'])
        if meta['LAST_SEND'] == 0:
            remaining = 1

        # only schedule the next tic if one hasn't been called during processing this one
        print('tic! waiting {} seconds...'.format(remaining))
        await asyncio.sleep(remaining)
        meta['task'] = asyncio.ensure_future(tic())

    asyncio.get_event_loop().run_until_complete(websockets.serve(register, '0.0.0.0', 8765))

    asyncio.ensure_future(tic())

    asyncio.get_event_loop().run_forever()
