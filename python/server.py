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

class SpotifyHolder(object):    
    def __init__(self, filename='spotify_creds.json', mock=False):
        SPOTIFY_SCOPES = [
            'user-read-playback-state',
            'user-read-currently-playing',
            'playlist-read-private',
            'user-library-read'
        ]
        with open(filename) as f:
            creds = json.load(f)
        token = spotipy.util.prompt_for_user_token(creds.get('user'),' '.join(SPOTIFY_SCOPES), creds.get('client_id'), client_secret=creds.get('client_secret'), redirect_uri='http://localhost')
        self.sp = spotipy.Spotify(auth=token)
        self.calls = []

        
    def get_track(self):
        self.calls.append(time.time())
        self.calls = [c for c in self.calls if (time.time() - c < 60.0)]
        return self.sp.current_user_playing_track()

    def recent_call_count(self):
        return len(self.calls)

def log(l):
    print('[{}] {}'.format(datetime.datetime.now().isoformat(), l))

if __name__ == "__main__":
    
    DEBUG = '--debug' in sys.argv
    OFFLINE = '--offline' in sys.argv

    if DEBUG:
        log('*** DEBUG MODE ***')
        #FX = [f for f in os.listdir('./fx') if f.split('.')[-1] == 'lua']
        FX = ['bak/debug.lua']
    else:
        FX = [f for f in os.listdir('./fx') if f.split('.')[-1] == 'lua']
    log('found fx files: {}'.format(' '.join(FX)))

    sockets = {}
    global meta
    meta = { 'LAST_SEND': 0, 'index': 0 }
    TIC_INTERVAL = 1.0
    MAC_LOOKUP = [
        '5c:cf:7f:53:d8:b0', #A
        '5c:cf:7f:53:d9:16', #B
        '5c:cf:7f:53:d6:1c', #C
        '5c:cf:7f:53:d8:ab', #D
        '5c:cf:7f:53:d3:fe', #E
        '5c:cf:7f:53:d6:f0', #F
    ]
    CYCLE_DELAY = 10.0
    sem = asyncio.Semaphore(1)    

    # set up spotify API object
    sp = SpotifyHolder()

    # connection handler
    async def register(websocket, path):
        global meta
        try:
            async for m in websocket:
                log("connection from {}".format(m))
                already_present = m in sockets
                sockets[m] = websocket
                meta['LAST_CONNECTION'] = time.time()
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

        time_since_connection = time.time() - meta.get('LAST_CONNECTION', time.time())
        if (OFFLINE or len(sockets) == 6 or time_since_connection > 30) and (meta.get('LAST_SEND') == 0 or (meta.get('last_track_name') != meta.get('track_name'))):

            # dumb cycle through fx
            rand = meta['index']
            selected = FX[meta['index']]
            
            # no rainbows before midnight
            if not DEBUG and datetime.datetime.now().hour > 6:
                while 'rainbow' in FX[meta['index']]:
                    meta['index'] = (meta['index'] + 1) % len(FX)
                    selected = FX[meta['index']]

            # no cycling bars until thriller
            if not DEBUG and not meta.get('thriller', False):
                while 'bars' in FX[meta['index']]:
                    meta['index'] = (meta['index'] + 1) % len(FX)
                    selected = FX[meta['index']]

            meta['index'] = (meta['index'] + 1) % len(FX)

            # no thriller until it's time
            if 'thriller' in meta['track_name'].lower():
                selected = 'thriller.lua'
                meta['thriller'] = True
            else:
                while 'thriller' in FX[meta['index']]:
                    meta['index'] = (meta['index'] + 1) % len(FX)
                    selected = FX[meta['index']]

            log("sending {}".format(selected))
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
            
            if not OFFLINE:
                await asyncio.wait([ws.send(msg) for (ws, msg) in to_send])        

            if OFFLINE or sent_something:
                meta['LAST_SEND'] = time.time()

        # refresh spotify info
        remaining = 10.0        
        track = sp.get_track()
        meta['last_track_name'] = meta.get('track_name')
        if track:
            if track.get('is_playing'):
                meta['track_name'] = track.get('item', {}).get('name')
                remaining = min(remaining, (track.get('item', {}).get('duration_ms') - track.get('progress_ms')) / 1000.0)
                if meta.get('last_track_name') != meta.get('track_name'):
                    remaining = 0.01
            else:
                meta['track_name'] = 'N/A'
                if meta['LAST_SEND'] == 0: # don't hammer the API every second if we are starting w/ nothing playing
                    meta['LAST_SEND'] = time.time()
        if meta['LAST_SEND'] == 0:
            remaining = 1

        # only schedule the next tic if one hasn't been called during processing this one
        log('current track: {}, last track: {}, spotify calls in last 60s: {}, waiting {}s'.format(meta.get('track_name', 'N/A'), meta.get('last_track_name', 'N/A'), sp.recent_call_count(), remaining))        
        await asyncio.sleep(remaining)
        meta['task'] = asyncio.ensure_future(tic())

    asyncio.get_event_loop().run_until_complete(websockets.serve(register, '0.0.0.0', 8765))

    asyncio.ensure_future(tic())

    asyncio.get_event_loop().run_forever()
