from pymongo import MongoClient
from datetime import datetime
import os

client = MongoClient(os.environ.get('MONGO_URL'))

# grab the "playlist" database
db = client.playlist

# grab the "playlists" collection
playlists = db.playlists
scraped_users = db.scrapedusers

def put_playlist(playlist):
    """Add a playlist to the database"""
    playlists.insert_one(playlist)

def put_scraped(user_id):
    """Add a scraped user to the database"""
    scraped_users.insert_one({
        u"user_id": user_id,
        u"time": datetime.now()
    })

def get_scraped(user_id):
    """Get a scraped user from the database"""
    return scraped_users.find_one({
        u"user_id": user_id
    })