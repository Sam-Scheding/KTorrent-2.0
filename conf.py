import os, json
from collections import defaultdict


DEFAULT_CONF = 'default.json'
SESSION_CONF = 'session.json'

class Session(object):

	session = defaultdict(list)
	session['DOWNLOADS'] = []
	# defaults = {
	# 	'BASE_DIR': os.getcwd(),
	# 	'APP_NAME': 'KTorrent',
	# 	'RESULTS_COL_NAMES': ['title', 'seeders', 'peers', 'file size', '.torrent size'],
	# 	'DOWNLOADS_COL_NAMES': {'title': 0, 'progress': 1, 'download rate': 2, 'upload rate': 3, 'seeders': 4, 'peers': 5, 'status': 6},
	# 	'DOWNLOADS_DIR': os.path.join(os.getcwd(), 'Downloads'),
	# 	'TAB_NAMES': ['Downloads'],
	# 	'LOCAL_DEBUG': True,
	# 	'TORRENT_CLIENT_UPDATE_INTERVAL': 1,
	# }

	def __init__(self):
		super(Session, self).__init__()
		self.load()
			
	def get(self, key, default=None):
		if key in self.session:
			return self.session[key]
		return default

	def set(self, key, val):
		self.session[key] = val

	def append(self, key, val):
		self.session[key] += [val]

	def save(self):
		print(self.session)	
		with open(SESSION_CONF, 'w') as session_file:
			session_file.write(json.dumps(self.session, indent=4))

	def remove_download(self, torrent):
		downloads = self.session['DOWNLOADS']
		idx = 0
		for download in downloads:
			if download['torrent_file_path'] == torrent.torrent_file_path:
				break
			idx += 1
		self.session['DOWNLOADS'].pop(idx)
		self.save()

	def load(self):

		self.session = {**self.session, **json.loads(open(DEFAULT_CONF).read())}
		prev_session_settings = json.loads(open(SESSION_CONF).read())

		downloads = prev_session_settings['DOWNLOADS']
		for download in downloads:
			self.session['DOWNLOADS'] += [json.loads(download)]

# BASE_DIR = os.getcwd()
# APP_NAME = 'KTorrent'
# RESULTS_COL_NAMES = ['title', 'seeders', 'peers', 'file size', '.torrent size']
# DOWNLOADS_DIR = os.path.join(BASE_DIR, 'Downloads')
# TAB_NAMES = ['Downloads']
# LOCAL_DEBUG = True
# TORRENT_CLIENT_UPDATE_INTERVAL = 1

