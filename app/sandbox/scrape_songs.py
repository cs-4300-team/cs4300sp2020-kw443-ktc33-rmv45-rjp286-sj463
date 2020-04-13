import sys
sys.path.insert(0, '..')
# this is necessary to resolve modules

import time

from spotify import spotify
from database import database

playlists = database.find_playlists()

done = 0
for playlist in playlists[5:100]:
    for track in playlist["tracks"]:
        if not track or not track["track"]:
            continue
        song_id = track["track"]["id"]
        if not song_id:
            continue
        if not database.find_song(song_id):
            song = spotify.get_song(song_id)
            song["playlists"] = [playlist["id"]]
            song["features"] = spotify.get_song_features(song_id)
            database.put_song(song)
        else:
            database.add_song_playlist(song_id, playlist["id"])
    done += 1
    if done % 100 == 0:
        print(done)