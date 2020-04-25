import sys
sys.path.insert(0, '..')
# this is necessary to resolve modules

import time
from multiprocessing import Process

from spotify import spotify
from database import database

playlists = database.find_playlists()

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

# done = 900
# for playlist in playlists[done:1000]:
#     for track in playlist["tracks"]:
#         if not track or not track["track"]:
#             continue
#         song_id = track["track"]["id"]
#         if not song_id:
#             continue
#         if not database.find_song(song_id):
#             # song = spotify.get_song(song_id)
#             if song_id not in songs:
#                 songs[song_id] = [playlist["id"]]
#             else:
#                 songs[song_id] = songs[song_id] + [playlist["id"]]
#             if(len(songs) == 50):
#                 update_songs()
#         else:
#             update_song_playlist(song_id, playlist["id"])
#     print(done)
#     done += 1
# update_songs()

# We have 30,615 playlists in total
# So far we have 1-2000, 10000-17500, 20000-25000, 27000-30000 done
start = 17500
stop = 20000
failed = []

while start <= stop:
    try:
        playlist = playlists[start]
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
                    update_songs()
            else:
                update_song_playlist(song_id, playlist["id"])
        if (start%10==0): print(start)
    except KeyboardInterrupt:
        break
    except:
        songs.clear()
        failed.append(start)
        print("Failed playlists: " + str(failed))
    start += 1
update_songs()

print("Failed playlists: " + str(failed))
