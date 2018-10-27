import json
import spotipy, spotipy.util
from spotipy.oauth2 import SpotifyClientCredentials

with open('spotify_creds.json') as f:
	creds = json.load(f)

SPOTIFY_SCOPES = [
	'user-read-playback-state',
	'user-read-currently-playing',
	'playlist-read-private',
	'user-library-read'
]

token = spotipy.util.prompt_for_user_token(creds.get('user'),' '.join(SPOTIFY_SCOPES), creds.get('client_id'), client_secret=creds.get('client_secret'), redirect_uri='http://localhost')
if token:
    sp = spotipy.Spotify(auth=token)
    #print(json.dumps(sp.current_user_playing_track(), indent=4))
    print(json.dumps(sp.user_playlist(creds.get('user'), 'spotify:user:1216663148:playlist:63zBPWdtXyY1PUqz1qWA1Y'), indent=4)) 
# {
#     "timestamp": 1540434393382,
#     "context": {
#         "external_urls": {
#             "spotify": "https://open.spotify.com/playlist/0n9fY6g8qywPvR4odLugmI"
#         },
#         "href": "https://api.spotify.com/v1/playlists/0n9fY6g8qywPvR4odLugmI",
#         "type": "playlist",
#         "uri": "spotify:user:perstn:playlist:0n9fY6g8qywPvR4odLugmI"
#     },
#     "progress_ms": 4461,
#     "item": {
#         "album": {
#             "album_type": "album",
#             "artists": [
#                 {
#                     "external_urls": {
#                         "spotify": "https://open.spotify.com/artist/1co4F2pPNH8JjTutZkmgSm"
#                     },
#                     "href": "https://api.spotify.com/v1/artists/1co4F2pPNH8JjTutZkmgSm",
#                     "id": "1co4F2pPNH8JjTutZkmgSm",
#                     "name": "Ramones",
#                     "type": "artist",
#                     "uri": "spotify:artist:1co4F2pPNH8JjTutZkmgSm"
#                 }
#             ],
#             "available_markets": [],
#             "external_urls": {
#                 "spotify": "https://open.spotify.com/album/0Me9wrzxQGN7vZDudzlI4t"
#             },
#             "href": "https://api.spotify.com/v1/albums/0Me9wrzxQGN7vZDudzlI4t",
#             "id": "0Me9wrzxQGN7vZDudzlI4t",
#             "images": [
#                 {
#                     "height": 640,
#                     "url": "https://i.scdn.co/image/578182602020a3cda44ee37d648b7055f700d809",
#                     "width": 640
#                 },
#                 {
#                     "height": 300,
#                     "url": "https://i.scdn.co/image/d229785512afe92994d62991a8adec3ad94bd758",
#                     "width": 300
#                 },
#                 {
#                     "height": 64,
#                     "url": "https://i.scdn.co/image/65a236499cc751694cb7d4c9394f29e1024eea0d",
#                     "width": 64
#                 }
#             ],
#             "name": "Loud, Fast, Ramones: Their Toughest Hits",
#             "release_date": "2002-10-01",
#             "release_date_precision": "day",
#             "total_tracks": 27,
#             "type": "album",
#             "uri": "spotify:album:0Me9wrzxQGN7vZDudzlI4t"
#         },
#         "artists": [
#             {
#                 "external_urls": {
#                     "spotify": "https://open.spotify.com/artist/1co4F2pPNH8JjTutZkmgSm"
#                 },
#                 "href": "https://api.spotify.com/v1/artists/1co4F2pPNH8JjTutZkmgSm",
#                 "id": "1co4F2pPNH8JjTutZkmgSm",
#                 "name": "Ramones",
#                 "type": "artist",
#                 "uri": "spotify:artist:1co4F2pPNH8JjTutZkmgSm"
#             }
#         ],
#         "available_markets": [],
#         "disc_number": 1,
#         "duration_ms": 126653,
#         "explicit": false,
#         "external_ids": {
#             "isrc": "USWB10201792"
#         },
#         "external_urls": {
#             "spotify": "https://open.spotify.com/track/2Zu4uY37o23mLJDQ1hIG5O"
#         },
#         "href": "https://api.spotify.com/v1/tracks/2Zu4uY37o23mLJDQ1hIG5O",
#         "id": "2Zu4uY37o23mLJDQ1hIG5O",
#         "is_local": false,
#         "name": "Rockaway Beach - Remastered Version",
#         "popularity": 0,
#         "preview_url": null,
#         "track_number": 8,
#         "type": "track",
#         "uri": "spotify:track:2Zu4uY37o23mLJDQ1hIG5O"
#     },
#     "currently_playing_type": "track",
#     "is_playing": true
# }
