import sys
sys.path.insert(0, '..')
# this is necessary to resolve modules

import time

from spotify import spotify
from database import database

def scrape(user_id):
    """scrape a users playlists"""
    scraped = database.get_scraped(user_id)
    # check if we've already scraped this user
    if not scraped:
        playlists = spotify.get_user_playlists(user_id.strip())

        # timing variables
        spotify_total = 0
        db_total = 0

        for playlist in playlists:
            spotify_start = time.time() # timing
            # get the playlist
            plst = spotify.get_playlist(playlist["id"], "followers,href,id,images,name,owner(display_name,type,id,uri),public,snapshot_id,type,uri")
            # grab all the tracks (or at least up to 500)
            tracks = spotify.get_playlist_tracks(playlist["id"], \
                "items(added_at,added_by,is_local,track(album(!available_markets),artists,duration_ms,episode,explicit,href,id,is_local,name,popularity,preview_url,track,type,uri)),total,href,next", \
                500)
            plst["tracks"] = tracks
            spotify_end = time.time() # timing
            # add to database
            database.put_playlist(plst)
            db_end = time.time() # timing
            spotify_total += spotify_end - spotify_start # timing
            db_total += db_end - spotify_end # timing

        # print timing for bottleneck analysis
        print(str(spotify_total) + "s waiting for spotify and " + str(db_total) + "s waiting for db")
        # mark that we've scraped this user
        database.put_scraped(user_id)

# output.txt should be account ids (1 per line)
with open("output.txt") as f:
    content = f.readlines()
    for user in content:
        try:
            user_id = user.strip() # strip newline, whitespace etc
            scrape(user_id)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            print(e)