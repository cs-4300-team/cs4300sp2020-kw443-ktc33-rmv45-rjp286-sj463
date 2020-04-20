import sys
sys.path.insert(0, '..')
# this is necessary to resolve modules

from database import database

from psaw import PushshiftAPI

api = PushshiftAPI()

songs = database.find_songs()

subs = ["hiphopheads", "music", "EDM", "Rock", "2010smusic", \
    "2000smusic", "90smusic", "80sMusic", "70sMusic", \
    "listentothis", "Metal", "jazz", "country", "popheads"]

subs_string = ",".join(subs)

import re
def cleanup_body(t):
    no_links = re.sub(r'[\[\(]http.:\/\/.+[\]\)]', '', t, flags=re.MULTILINE)
    just_words = " ".join(re.findall(r'[\w\.!?\']+', no_links))
    return just_words

done = 0

for song in songs[0:100]:
    if not song or not song["name"] or \
        not song["artists"] or not song["artists"][0]:
        continue
    song_name = song["name"]
    song_artist = song["artists"][0]["name"]
    query = song_name + " " + song_artist

    comments = api.search_comments(subreddit=subs_string,\
        q=query, limit=100)

    comments_subs = list(map(lambda c: {"text":cleanup_body(c.body), \
        "subreddit": c.subreddit}, \
        list(comments)))

    database.set_song_comments(song["id"], comments_subs)
    done+=1
    if done % 5 == 0:
        print(done)