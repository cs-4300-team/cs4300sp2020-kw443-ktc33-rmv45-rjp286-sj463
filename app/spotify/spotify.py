import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from datetime import datetime

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

def get_user_playlists(id):
    """Gets a users playlists"""
    playlists_result = spotify.user_playlists(id)
    playlists = playlists_result["items"]

    while playlists_result["next"]:
        playlists_result = spotify.next(playlists_result)
        playlists = playlists + playlists_result["items"]
    return playlists

def get_playlist(id, fields=None):
    """Gets a playlist by id"""
    return spotify.playlist(id, fields)

def get_playlist_tracks(id, fields=None, abort=-1):
    """Gets the tracks from a playlist"""
    tracks_result = spotify.playlist_tracks(id, fields)
    tracks = tracks_result["items"]

    while tracks_result["next"]:
        tracks_result = spotify.next(tracks_result)
        tracks = tracks + tracks_result["items"]
        if abort > -1 and len(tracks) >= abort:
            # abort if there's more than 500 tracks
            break
    return tracks

def get_song(id):
    
    return spotify.track(id)

def get_song_features(id):
    return spotify.audio_features([id])[0]

import os
SCOPE = "playlist-modify-public"
SPOTIPY_REDIRECT_URI = 'http://localhost:5000/admin'
try:
	if os.environ.get('ENV') == 'prod':
		SPOTIPY_REDIRECT_URI = 'https://playlist-mixer.herokuapp.com/admin'
except:
	print("Not in production")
SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')

sp_oauth = SpotifyOAuth( SPOTIPY_CLIENT_ID, \
	SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI,scope=SCOPE,cache_path='.spotipyauthcache' )

authed_spotify = None

def try_login_cached():
    global authed_spotify
    cached = sp_oauth.get_cached_token()
    if cached:
        try:
            access_token = cached["access_token"]
            if sp_oauth.is_token_expired(cached):
                access_token = sp_oauth.refresh_access_token(cached["refresh_token"])
            authed_spotify = spotipy.Spotify(access_token)
            print("Logged in")
        except Exception as e:
            print("error authenticating on spotify")
            print(e)
            authed_spotify = None

try_login_cached()

def create_playlist(song_ids):
    global authed_spotify
    try:
        try_login_cached()
        if authed_spotify:
            me = authed_spotify.me()
            now = datetime.now()
            pl = authed_spotify.user_playlist_create(me["id"], "4300 Playlist", \
                description="Created at " + now.strftime("%m/%d/%Y, %H:%M:%S"))
            authed_spotify.user_playlist_add_tracks(me["id"], pl["id"], song_ids)
            print(pl["external_urls"]["spotify"])
            return pl["external_urls"]["spotify"]
        else:
            print("No authed spotify :/")
    except Exception as e:
        print("Error creating playlist")
        print(e)
    print("No playlist created")
    return None