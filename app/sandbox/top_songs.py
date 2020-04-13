import sys
sys.path.insert(0, '..')
# this is necessary to resolve modules

from database import database

songs = {}

playlists = database.find_playlists()

done = 0
for playlist in playlists:
    for track in playlist["tracks"]:
        if not track or not track["track"]:
            continue
        song_id = track["track"]["id"]
        if not song_id:
            continue
        if song_id not in songs:
            songs[song_id] = {
                "name": track["track"]["name"],
                "count": 1,
                "artist": track["track"]["artists"][0]["name"]
            }
        else:
            songs[song_id]["count"] += 1
    done += 1
    if done % 100 == 0:
        print(done)

song_count = sorted(songs.keys(), key=lambda k: songs[k]["count"], reverse=True)
# print(song_count[0:300])
print(len(song_count))

#import json
#dump = json.dumps(list(map(lambda k: songs[k], song_count[0:1000])))
#file = open('top_songs.json', 'w')
#file.write(dump)
#file.close()