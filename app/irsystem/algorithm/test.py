import numpy as np

from flask import jsonify

from app.database import database
from app.spotify import spotify

def get_comments(): 
    songs = database.find_reddit_songs()
    reddit_obj = []
    for song in songs: 
        song_id = song["id"]
        reddit_comments = ""
        for comment in song["comments"]:
            reddit_comments += comment["text"]
        reddit_obj.append({"song_id": song_id, "comment": reddit_comments})
    return jsonify(reddit_obj)