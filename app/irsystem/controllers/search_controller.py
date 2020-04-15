from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

from flask_restful import reqparse
from flask import send_from_directory

from app.spotify import spotify

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
			track_list = []
			songs = []
			try: 
				for i in range(len(args['link'])):
					playlist_id = args['link'][i].lstrip('https://open.spotify.com/playlist/')
					track_list.append(spotify.get_playlist_tracks(playlist_id))

				songs = []
				for tracks in track_list:
					for song in tracks:
						all_artists = ""
						for artist in song['track']['artists']: 
							if all_artists == "": 
								all_artists = artist['name']
							else: 
								all_artists += artist['name']
						songs.append(dict(name=song['track']['name'], artists=all_artists, image=song['track']['album']['images'][0]['url']))
				# POST can't return a list 
				return jsonify(songs)
			except Exception as error: 
				return error
		else:
			try:
				playlist_info = spotify.get_playlist(args['link'][0].lstrip('https://open.spotify.com/playlist/'))
				return jsonify(name=playlist_info['name'], image=playlist_info['images'][0]['url'])
			except Exception as error:
				return error
		# test case: curl http://localhost:5000 -d "link=https://open.spotify.com/playlist/5hOxxrUnRYpf6XVScyjF0Y" -d "link=https://open.spotify.com/playlist/48KXkzzA9xkonptFgWx1a9" -X POST -v



