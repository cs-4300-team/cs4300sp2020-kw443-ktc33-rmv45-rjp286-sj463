import numpy as np

from app.database import database
from app.spotify import spotify

songs = {}

def get_id(track):
    if not track or not track["track"] or not track["track"]["id"]:
        return "None"
    song_id = track["track"]["id"]
    songs[track["track"]["id"]] = {
        "name": track["track"]["name"],
        "artists": list(map(lambda a: a["name"], track["track"]["artists"])),
        "images": track["track"]["album"]["images"],
        "id": song_id
    }
    return song_id

def merge_playlists(playlists_in):
    songs.clear()
    # turn input playlists into a list of their tracks
    playlist_ids = list(map(lambda pl: pl.lstrip('https://open.spotify.com/playlist/'), playlists_in))
    playlists = list(map(lambda pl_id: spotify.get_playlist_tracks(pl_id), playlist_ids))

    track_ids = list(map(lambda pl: set(list(map(get_id, pl))), playlists))
    playlist_union = set()
    for tracks in track_ids:
        # create playlist union (union of tracks in input playlists)
        playlist_union = playlist_union.union(tracks)
    playlist_intersect = track_ids[0]
    if len(tracks) > 1:
        for tracks in track_ids:
            # create playlist intersect
            playlist_intersect = playlist_intersect.intersection(tracks)
            if len(playlist_intersect) == 0:
                break
    return find_merge(playlist_union, playlist_intersect)

def find_merge(playlist_union, playlist_intersect):

    playlists = database.find_playlists().batch_size(300)


    # similar songs
    sim_songs = {}
    co_occur_keys = [k for k in playlist_union]
    song_to_index = {k: co_occur_keys.index(k) for k in co_occur_keys}
    co_occur = np.zeros((len(co_occur_keys), len(co_occur_keys)))

    done = 0
    for playlist in playlists[0:500]:
        # playlist is one of the playlists in database
        # playlist_ids is the list of ids in that playlist
        playlist_ids = set(list(map(get_id, playlist["tracks"])))
        # playlists_intersect is the intersection of songs in this playlist
        # and songs in the input playlist
        playlists_intersect = playlist_ids.intersection(playlist_union)

        # find the cosine similarity of this playlist and the input playlists(' union)
        cos_sim = len(playlists_intersect) / (len(playlist_ids) * len(playlist_union) + 0.00001)

        # co occurance vector: 0 if song not in playlists_intersect and 1 if it is
        co_occur_vec = [1 if k in playlists_intersect else 0 for k in co_occur_keys]

        # weight input songs by co_occur_vec
        # this logic is that songs that co-occur with other input
        # songs will have a larger sum(co_occur[song])
        for song_id in playlist_ids.intersection(playlist_union):
            if song_id in song_to_index:
                i = song_to_index[song_id]
                co_occur[i] = co_occur[i] + co_occur_vec
        
        for track in playlist["tracks"]:
            if not track or not track["track"]:
                continue
            song_id = track["track"]["id"]
            if not song_id:
                continue
            
            # if this song isn't in the union of the playlist inputs,
            # update it in the "similar songs" dict by the cosine similarity
            # todo: account for tf-idf or something
            if song_id not in playlist_union:
                if song_id not in sim_songs:
                    sim_songs[song_id] = cos_sim
                else:
                    sim_songs[song_id] += cos_sim

            if song_id not in songs:
                songs[song_id] = {
                    "name": track["track"]["name"],
                    "artists": list(map(lambda a: a["name"], track["track"]["artists"])),
                    "images": track["track"]["album"]["images"],
                    "id": song_id
                }
        done += 1
        if done % 50 == 0:
            print(done)

    songs_total_co_occur = []
    for i in range(0, len(co_occur)):
        # find the number of co-occurances with other input songs
        total_co_occur = np.sum(co_occur[i]) - co_occur[i][i]
        song_id = co_occur_keys[i]
        song= songs[song_id] if song_id in songs else "None"
        songs_total_co_occur.append((total_co_occur, song_id, song))

    co_occur_top_10 = list(map(lambda total: total[2], sorted(songs_total_co_occur, reverse=True)[0:10]))

    # song_count = sorted(songs.keys(), key=lambda k: songs[k]["count"], reverse=True)
    sim_songs_sort = sorted(sim_songs.keys(), key=lambda k: sim_songs[k], reverse=True)

    top_50 = list(playlist_intersect) + sim_songs_sort[0:50]

    # not really a top 50
    top_50_named = co_occur_top_10 + list(map(lambda k: (k in songs and songs[k] or "None"), top_50))
    return top_50_named