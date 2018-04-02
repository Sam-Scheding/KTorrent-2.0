import os
import conf
import pickle, json
import libtorrent as lt
import time, sys


class BitTorrentClient():


    def __init__(self, session, **kwargs):

        super(BitTorrentClient,).__init__()
        self.ses = lt.session()
        self.ses.listen_on(6881, 6891)
        self.session = session

    def download(self, torrent):

        if not self.isValidTorrent(torrent):
            self.session.remove_download(torrent)
            return

        torrent_contents = open(torrent.torrent_file_path, 'rb').read()        
        e = lt.bdecode(torrent_contents)
        info = lt.torrent_info(e)

        params = { 
            'save_path': self.session.get('DOWNLOADS_DIR'),
            'storage_mode': lt.storage_mode_t.storage_mode_sparse,
            'ti': info 
        }
        self.h = self.ses.add_torrent(params)
        self.s = self.h.status()


    def pause(self, torrent):

        self.h.status().pause()

    # TODO: Implement the checks from the test torrents here                 
    def isValidTorrent(self, torrent):

        if not os.path.isfile(torrent.torrent_file_path):
            print(torrent.torrent_file_path, 'does not exist.')
            return False

        stats = os.stat(torrent.torrent_file_path)
        if stats.st_size == 0:
            print("file_size was 0")
            return False
        return True

    def update_status(self, torrent):

        torrent.status = self.h.status
        s = self.h.status()
        # print(s)
        # print("Progress: {}%\nDownload Rate: {}kb/s\nUpload Rate: {}Kb/s\nPeers: {}\nState: {}\n\n".format(
        #     s.progress * 100, 
        #     s.download_rate / 1000, 
        #     s.upload_rate / 1000, 
        #     s.num_peers, 
        #     s.state
        # ))
        return s

class TorrentObject():

    def __init__(self, torrent_name=None, torrent_file_path=None, torrent_download_dir=None, torrent_file_size=0, file_size=0, status=None, current_seeders=None, current_peers=None):

        super(TorrentObject,).__init__()
        self.torrent_name = torrent_name
        self.torrent_file_path = torrent_file_path
        self.torrent_download_dir = torrent_download_dir
        self.file_size = file_size
        self.torrent_file_size = torrent_file_size
        self.status = status  # status object from libtorrent library

    def __repr__(self):
        return json.dumps(self.__dict__)
