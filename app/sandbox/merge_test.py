import sys
sys.path.insert(0, '..')
#sys.path.insert(0, '../..')
# this is necessary to resolve modules

import numpy as np

from database import database

#from irsystem.algorithm import algorithm

#algorithm.merge_playlists(['2dEmomSJHQE2Y5RdHgGzTE', '3sbMiFkUeAkm1GVc4hL37o'])

playlist_1 = database.find_playlist("2dEmomSJHQE2Y5RdHgGzTE") # bunkin
# playlist_1 = database.find_playlist("5hOxxrUnRYpf6XVScyjF0Y") # everybody knows
playlist_2 = database.find_playlist("3sbMiFkUeAkm1GVc4hL37o") # vac's pop playlist
# playlist_2 = database.find_playlist("3gHUDrjoZ8wt2IWR4LlVCd") # car bump playlist

#playlist_1 = database.find_playlist("0tlroh5rNmfNazX2ouLslQ") # Rihanna Babe <- Vac
#playlist_2 = database.find_playlist("1y2pGOreYvC8Tkf1bjQmmA") # bruh


songs = {}

def get_id(track):
    if not track or not track["track"] or not track["track"]["id"]:
        return "None"
    songs[track["track"]["id"]] = {
        "name": track["track"]["name"]
    }
    return track["track"]["id"]

playlist_1_tracks = set(list(map(get_id, playlist_1["tracks"])))
playlist_2_tracks = set(list(map(get_id, playlist_2["tracks"])))
playlist_union = playlist_1_tracks.union(playlist_2_tracks)

print(list(playlist_1_tracks.intersection(playlist_2_tracks)))

playlists = database.find_playlists().batch_size(300)


sim_songs = {}
co_occur_keys = [k for k in playlist_union]
song_to_index = {k: co_occur_keys.index(k) for k in co_occur_keys}
co_occur = np.zeros((len(co_occur_keys), len(co_occur_keys)))

done = 0
for playlist in playlists[9000:10000]:
    # playlist is one of the playlists in database
    # playlist_ids is the list of ids in that playlist
    playlist_ids = set(list(map(get_id, playlist["tracks"])))
    playlists_intersect = playlist_ids.intersection(playlist_union)

    cos_sim = len(playlists_intersect) / (len(playlist_ids) * len(playlist_union) + 0.00001)

    co_occur_vec = [1 if k in playlists_intersect else 0 for k in co_occur_keys]

    for song_id in playlist_ids.intersection(playlist_union):
        if song_id in song_to_index:
            i = song_to_index[song_id]
            co_occur[i] = co_occur[i] + co_occur_vec
    # for song_id in playlist_co_occur:
    #     if song_id not in co_occur:
    #         co_occur[song_id] = 1
    #     else:
    #         co_occur[song_id] += 1
    for track in playlist["tracks"]:
        if not track or not track["track"]:
            continue
        song_id = track["track"]["id"]
        if not song_id:
            continue
        
        if song_id not in playlist_union:
            if song_id not in sim_songs:
                sim_songs[song_id] = cos_sim
            else:
                sim_songs[song_id] += cos_sim

        if song_id not in songs:
            songs[song_id] = {
                "name": track["track"]["name"],
                #"count": 1,
                #"playlists": [playlist["id"]]
            }
        # else:
        #     songs[song_id]["count"] += 1
        #     songs[song_id]["playlists"].append(playlist["id"])
    done += 1
    if done % 100 == 0:
        print(done)

songs_total_co_occur = []
for i in range(0, len(co_occur)):
    total_co_occur = np.sum(co_occur[i]) - co_occur[i][i]
    song_id = co_occur_keys[i]
    song_name = songs[song_id]["name"] if song_id in songs else "None"
    songs_total_co_occur.append((total_co_occur, song_id, song_name))

print(sorted(songs_total_co_occur, reverse=True))

co_occur_top_10 = list(map(lambda total: total[2], sorted(songs_total_co_occur, reverse=True)[0:10]))

# song_count = sorted(songs.keys(), key=lambda k: songs[k]["count"], reverse=True)
sim_songs_sort = sorted(sim_songs.keys(), key=lambda k: sim_songs[k], reverse=True)

top_50 = list(playlist_1_tracks.intersection(playlist_2_tracks)) + sim_songs_sort[0:50]
print(top_50)

print('\n\nOutput "Playlist"')
top_50_named = co_occur_top_10 + list(map(lambda k: (k in songs and songs[k]["name"] or "None"), top_50))
print(top_50_named)

# print(list(map(lambda k: songs[k], song_count[0:20])))