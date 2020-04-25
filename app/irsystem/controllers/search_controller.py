from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

from flask_restful import reqparse
from flask import send_from_directory

from app.spotify import spotify
from app.irsystem.algorithm import basic_merge

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
				return jsonify(basic_merge.merge_playlists(args['link']))
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

