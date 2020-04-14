import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

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