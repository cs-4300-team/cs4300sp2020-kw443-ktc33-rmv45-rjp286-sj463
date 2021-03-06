import numpy as np
import math

from app.database import database
from app.spotify import spotify
from collections import defaultdict

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

def merge_playlists(playlists_in, target_len = 50):
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
    return find_merge(track_ids, playlist_union, playlist_intersect, track_ids, target_len)

def find_merge(track_ids_list, playlist_union, playlist_intersect, track_ids, target_len = 50):
    svd_sim = defaultdict(float)
    songs_with_similar = 0

    songs_union = database.find_songs(list(playlist_union))
    song_df = defaultdict(int)

    playlists_1 = []
    pl_set = None
    for song in songs_union:
        count = 0
        for pl in track_ids:
            if song["id"] in pl:
                count+=1
            if count > 1:
                break
        if count == 0:
            continue
        playlists_1.append(song["playlists"])
        if "similar" in song:
            songs_with_similar+=1
            for sim in song["similar"]:
                svd_sim[sim["id"]] += sim["score"]
    # playlists_1 = list(map(lambda x: x["playlists"], songs_union))
    # bless up https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-list-of-lists
    #flatten_playlists = lambda l: [item for sublist in l for item in sublist]
    playlist_song_count = dict()
    for playlists in playlists_1:
        for playlist in playlists:
            if playlist not in playlist_song_count:
                playlist_song_count[playlist] = 1
            else:
                playlist_song_count[playlist] += 1

    playlist_ids = sorted(playlist_song_count.keys(), key=lambda x: playlist_song_count[x], reverse=True)
    TARGET = 1000
    step = math.ceil(len(playlist_ids) / TARGET)
    if(step == 0):
        step = 1
    idxs = list(range(0, len(playlist_ids), step))
    playlist_ids = [playlist_ids[i] for i in idxs]


    #playlist_ids = list(set(flatten_playlists(playlists_1)))

    playlists = database.find_playlists_ids(playlist_ids).batch_size(300)


    # similar songs
    sim_songs = {}
    co_occur_keys = [k for k in playlist_union]
    song_to_index = {k: co_occur_keys.index(k) for k in co_occur_keys}
    co_occur = np.zeros((len(co_occur_keys), len(co_occur_keys)))

    doc_count = playlists.count()

    done = 0
    for playlist in playlists:
        # playlist is one of the playlists in database
        # playlist_ids is the list of ids in that playlist
        playlist_ids = set(list(map(get_id, playlist["tracks"])))
        playlists_intersect = playlist_ids.intersection(playlist_union)
        cos_sim = 999
        cos_sim_len = 0
        # tracks is the songs of one of input playlists
        for tracks in track_ids_list:
            # playlists_intersect is the intersection of songs in this playlist
            # and songs in one of the input playlists
            playlists_intersect_tracks = playlist_ids.intersection(tracks)

            # find the cosine similarity of this playlist and the input playlist
            _cos_sim = len(playlists_intersect_tracks) / \
                (np.sqrt(len(playlist_ids)) * np.sqrt(len(tracks)) + 0.00001)
            if _cos_sim < cos_sim:
                cos_sim = _cos_sim
                cos_sim_len = len(tracks)
        if(cos_sim == 0):
            continue

        # co occurance vector: 0 if song not in playlists_intersect and 1 if it is
        co_occur_vec = \
            [1 if 0 not in [1 if k in t else 0 for t in track_ids] else 0 for k in co_occur_keys]

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
            song_df[song_id] += 1


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

    CO_OCCUR_WEIGHT = 0.2
    COS_SIM_WEIGHT = 0.4
    SVD_WEIGHT = 0.4

    idf = dict()
    for song in song_df:
        idf[song] = np.log(doc_count/(1 + song_df[song])) + 1

    songs_total_co_occur = []
    for i in range(0, len(co_occur)):
        # find the number of co-occurances with other input songs
        total_co_occur = np.sum(co_occur[i]) - co_occur[i][i]
        song_id = co_occur_keys[i]
        song= songs[song_id] if song_id in songs else "None"
        songs_total_co_occur.append((total_co_occur, song_id, song))

    svd_top = sorted(list(map(lambda k: (svd_sim[k], k), svd_sim.keys())), reverse=True)

    co_occur_top_10 = list(map(lambda total: total[2], sorted(songs_total_co_occur, reverse=True)[0:10]))

    # song_count = sorted(songs.keys(), key=lambda k: songs[k]["count"], reverse=True)
    sim_songs_sort = sorted(sim_songs.keys(), key=lambda k: sim_songs[k]*idf[k], reverse=True)

    top_50 = list(playlist_intersect) + sim_songs_sort[0:50]

    # not really a top 50
    top_50_named = co_occur_top_10 + list(map(lambda k: (k in songs and songs[k] or "None"), top_50))

    reasons = {
        "intersect": "Intersection: Song is in the intersection of input playlists",
        "co_occur": "Co-Occurance: Song co-occurs strongly (in other playlists) with songs in the input playlists",
        "cos_sim": "Cosine Similarity: Song occurs frequently in similar playlists to the input playlists",
        "svd_sim": "Social: Song is discussed similarly to songs in the input playlist"
    }

    output = set()
    song_id_reason = {}
    # first grab intersection
    for song_id in playlist_intersect:
        if song_id in songs:
            output.add(song_id)
            song_id_reason[song_id] = "intersect"
    # now grab co occur
    co_occur_left = math.ceil((target_len) * CO_OCCUR_WEIGHT)
    for total, song_id, song in songs_total_co_occur:
        if co_occur_left <= 0:
            break
        if song_id not in output and song_id in songs:
            output.add(song_id)
            song_id_reason[song_id] = "co_occur"
            co_occur_left -= 1
    # next grab cosine similarity
    cos_sim_left = math.ceil((target_len) * COS_SIM_WEIGHT)
    for song_id in sim_songs_sort:
        if cos_sim_left <= 0:
            break
        if song_id not in output and song_id in songs:
            output.add(song_id)
            song_id_reason[song_id] = "cos_sim"
            cos_sim_left -= 1
    # finally grab cosine similarity
    svd_left = math.ceil((target_len) * SVD_WEIGHT)
    for score, song_id in svd_top:
        if svd_left <= 0:
            break
        if song_id not in output and song_id in songs:
            output.add(song_id)
            song_id_reason[song_id] = "svd_sim"
            svd_left -= 1

    for song_id in song_id_reason:
        songs[song_id]["reason"] = reasons[song_id_reason[song_id]]

    return list(map(lambda k: (k in songs and songs[k] or "None"), list(output)))

# playlist1 = "https://open.spotify.com/playlist/37i9dQZF1DWTwnEm1IYyoj"
# playlist2 = "https://open.spotify.com/playlist/37i9dQZF1DX9s3cYAeKW5d"

# print(merge_playlists([playlist1, playlist2]))