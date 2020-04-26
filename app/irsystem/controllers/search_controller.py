from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

from flask_restful import reqparse
from flask import send_from_directory

from app.spotify import spotify
from app.irsystem.algorithm import basic_merge

import spotipy
from spotipy import oauth2
import os

SCOPE = "playlist-modify-public"
SPOTIPY_REDIRECT_URI = 'http://localhost:5000/admin'
try:
	if os.environ.get('ENV') == 'prod':
		SPOTIPY_REDIRECT_URI = 'https://playlist-mixer.herokuapp.com/admin'
except:
	print("Not in production")
SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')

sp_oauth = oauth2.SpotifyOAuth( SPOTIPY_CLIENT_ID, \
	SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI,scope=SCOPE,cache_path='.spotipyauthcache' )

parser = reqparse.RequestParser()
parser.add_argument('link', action='append')
parser.add_argument('get_playlist')

project_name = "Ilan's Cool Project Template"
net_id = "Ilan Filonenko: if56"

@irsystem.route('/', methods=['GET', 'POST'])
def search():
	if request.method == 'GET': 
		query = request.args.get('search')
		if not query:
			data = []
			output_message = ''
		else:
			output_message = "Your search: " + query
			data = range(5)
		return send_from_directory('templates', 'index.html')
	else: 
		# argument is an array of playlist links
		args = parser.parse_args()
					
		if args['get_playlist'] == "false": 
			try:
				output = basic_merge.merge_playlists(args['link'])
				ids = list(map(lambda s: s["id"], output))
				created = spotify.create_playlist(ids)
				return jsonify(output)
			except Exception as error:
				print(error)
				return error
		else:
			try:
				playlist_info = spotify.get_playlist(args['link'][0].lstrip('https://open.spotify.com/playlist/'))
				return jsonify(name=playlist_info['name'], image=playlist_info['images'][0]['url'])
			except Exception as error:
				return error
		# test case: curl http://localhost:5000 -d "link=https://open.spotify.com/playlist/5hOxxrUnRYpf6XVScyjF0Y" -d "link=https://open.spotify.com/playlist/48KXkzzA9xkonptFgWx1a9" -X POST -v

@irsystem.route('/favicon.ico')
def favicon(): 
	return send_from_directory('static/img', 'music.ico')

@irsystem.route('/about')
def about():
	return send_from_directory('templates', 'about.html')

@irsystem.route('/admin')
def admin():
	code = sp_oauth.parse_response_code(request.url)
	if code:
		token_info = sp_oauth.get_access_token(code)
		access_token = token_info['access_token']
		sp = spotipy.Spotify(access_token)
		spotify.try_login_cached()
		return render_template("admin.html", good="Authorized", authorize=sp_oauth.get_authorize_url())
	return render_template("admin.html", authorize=sp_oauth.get_authorize_url())