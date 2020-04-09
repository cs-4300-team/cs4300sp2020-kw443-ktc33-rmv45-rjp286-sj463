import sys
sys.path.insert(0, '..')

import time

from spotify import spotify
from database import database

playlists = spotify.get_user_playlists("rjpappa")

spotify_total = 0
db_total = 0
for playlist in playlists:
    spotify_start = time.time()
    plst = spotify.get_playlist(playlist["id"], "followers,href,id,images,name,owner(display_name,type,id,uri),public,snapshot_id,type,uri")
    tracks = spotify.get_playlist_tracks(playlist["id"], "items(added_at,added_by,is_local,track(album(!available_markets),artists,duration_ms,episode,explicit,href,id,is_local,name,popularity,preview_url,track,type,uri)),total,href,next")
    plst["tracks"] = tracks
    spotify_end = time.time()
    database.put_playlist(plst)
    db_end = time.time()
    spotify_total += spotify_end - spotify_start
    db_total += db_end - spotify_end

print(str(spotify_total) + "s waiting for spotify and " + str(db_total) + "s waiting for db")