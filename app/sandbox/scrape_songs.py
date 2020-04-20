import sys
sys.path.insert(0, '..')
# this is necessary to resolve modules

import time
from multiprocessing import Process

from spotify import spotify
from database import database

playlists = database.find_playlists()

done = 0

songs = {}

def update_songs():
    keys = songs.keys()
    mult_songs = spotify.get_mult_songs(keys)
    mult_audio_features = spotify.get_mult_song_features(keys)
    to_insert = []
    for song_id in keys:
        _song = list(filter(lambda x: x and x["id"]==song_id, mult_songs))
        song = len(_song) > 0 and _song[0]
        if not song:
            continue
        _feature = list(filter(lambda x: x and x["id"]==song_id, mult_audio_features))
        feature = len(_feature) > 0 and _feature[0]
        if not feature:
            continue
        song["playlists"] = songs[song_id]
        song["features"] = feature
        # database.put_song(song)
        to_insert.append(song)
    database.put_songs(to_insert)
    songs.clear()

def update_song_playlist(song_id, playlist_id):
    database.add_song_playlist(song_id, playlist["id"])

for playlist in playlists[48:100]:
    for track in playlist["tracks"]:
        if not track or not track["track"]:
            continue
        song_id = track["track"]["id"]
        if not song_id:
            continue
        if not database.find_song(song_id):
            # song = spotify.get_song(song_id)
            if song_id not in songs:
                songs[song_id] = [playlist["id"]]
            else:
                songs[song_id] = songs[song_id] + [playlist["id"]]
            if(len(songs) == 50):
                start = time.time()
                update_songs()
                end = time.time()
                print(str(end -start) + "s spend adding songs")
        else:
            update_song_playlist(song_id, playlist["id"])
    done += 1
    if done % 10 == 0:
        print(done)
    else:
        print(done)
update_songs()