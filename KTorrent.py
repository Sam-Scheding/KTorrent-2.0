#! /usr/bin/env python3
from threading import Thread
import sys, functools, os, shutil, time, json, pickle
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore 

#Local imports
from conf import Session
import network

session = Session()

class MainWindow(QtWidgets.QMainWindow):

    
    def __init__(self):
        
        QtWidgets.QMainWindow.__init__(self)
 
        self.setMinimumSize(QtCore.QSize(1000, 480))    
        self.setWindowTitle(session.get('APP_NAME'))

        self.populate_menu_bar(self, self.menuBar())

        self.downloads_table = DownloadsTable(self)
        downloads_layout = QtWidgets.QVBoxLayout()
        self.downloads_table.setLayout(downloads_layout)
        self.setCentralWidget(self.downloads_table)
        self.show()

        self.downloads_table.load_session()


    def populate_menu_bar(self, window, menu_bar):

        file_menu = menu_bar.addMenu('File')
        
        import_action = QtWidgets.QAction('Import', window) 
        import_action.setShortcut('Ctrl+O')
        import_action.triggered.connect(self.open_torrent_files_dialog)
        file_menu.addAction(import_action)
        
        exit_action = QtWidgets.QAction('Quit', window) 
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(QtWidgets.qApp.quit)
        file_menu.addAction(exit_action)


 
    def open_torrent_files_dialog(self):

        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        files_list, success = QtWidgets.QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","All Files (*);;Torrent Files (*.torrent)", options=options)

        if not success: return None

        for import_path in files_list:

            path, file_name = os.path.split(import_path)
            torrent_name, file_extension = os.path.splitext(file_name)

            if file_extension.lower() != '.torrent':
                print("Couldn't import", import_path)
                continue

            dest_path = os.path.join(session.get('DOWNLOADS_DIR'), file_name)
            counter = 0
            duplicate = False
            while os.path.isfile(dest_path):
                duplicate = True
                counter += 1
                new_copy = "{} ({}){}".format(torrent_name, counter, file_extension.lower())
                dest_path = os.path.join(session.get('DOWNLOADS_DIR'), new_copy)

            if duplicate:
                torrent_name = "{} ({})".format(torrent_name, counter)
 
            try:
                shutil.copyfile(import_path, dest_path)
            except FileNotFoundError as e:
                print("Couldn't import {} to {}. Check that the {} directory exists.".format(import_path, dest_path, settings['DOWNLOADS_DIR']))

            kwargs = {
                'torrent_name': torrent_name, 
                'torrent_file_path': dest_path, 
                'torrent_file_size': os.path.getsize(dest_path),
                'torrent_download_dir': torrent_name,
            }
            torrent = network.TorrentObject(**kwargs)
            self.downloads_table.download(torrent)
            session.append('DOWNLOADS', repr(torrent))
            session.save()



class DownloadsTable(QtWidgets.QTableWidget):

    cols = len(session.get('DOWNLOADS_COL_NAMES'))
    current_downloads = []
    row_height = 20
    min_height = 50
    torrent_updated = QtCore.pyqtSignal(network.TorrentObject, int)

    def __init__(self, parent):
        super(DownloadsTable, self).__init__(parent)
        self.setColumnCount(self.cols)
        self.setHorizontalHeaderLabels(session.get('DOWNLOADS_COL_NAMES'));
        self.setSortingEnabled(True)
        self.verticalHeader().setDefaultSectionSize(self.row_height); #  Make the rows a bit thinner
        self.verticalHeader().hide()
        self.horizontalHeader().setSectionsMovable(True)
        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # Make table cells uneditable
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows) # Select entire row, rather than just a cell
        self.setMinimumHeight(self.min_height)
        self.doubleClicked.connect(self.on_click)
        self.torrent_updated.connect(self.update_download)

    def load_session(self):

        # Add previous and incomplete downloads to the downloads table
        for download in session.get('DOWNLOADS'):
            kwargs = download
            torrent_object = network.TorrentObject(**kwargs)

            self.download(torrent_object)

    def download(self, torrent_object):

        row = self.rowCount()
        self.insertRow(row)
        self.current_downloads += [torrent_object]
        self.setItem(row, 0, QtWidgets.QTableWidgetItem(torrent_object.torrent_name))
        download_thread = Thread(target=self.download_torrent_thread, args=(torrent_object, row,))
        download_thread.daemon = True
        download_thread.start()

    def download_torrent_thread(self, torrent, row):

        torrent_client = network.BitTorrentClient(session)
        torrent_client.download(torrent)

        while not torrent_client.s.is_seeding:
            status = torrent_client.update_status(torrent)
            torrent.status = status
            self.torrent_updated.emit(torrent, row)
            time.sleep(session.get('TORRENT_CLIENT_UPDATE_INTERVAL'))

    def update_download(self, torrent, row):

        cols = session.get('DOWNLOADS_COL_NAMES')
        s = torrent.status
        self.setItem(row, cols.index('title'), QtWidgets.QTableWidgetItem(torrent.torrent_name))
        self.setItem(row, cols.index('seeders'), QtWidgets.QTableWidgetItem(s.num_peers))
        self.setItem(row, cols.index('peers'), QtWidgets.QTableWidgetItem(s.num_peers))
        self.setItem(row, cols.index('progress'), QtWidgets.QTableWidgetItem("{}%".format(round(s.progress * 100, 2))))
        self.setItem(row, cols.index('download rate'), QtWidgets.QTableWidgetItem("{} kb/s".format(round(s.download_rate / 1000, 2))))
        self.setItem(row, cols.index('upload rate'), QtWidgets.QTableWidgetItem("{} kB/s".format(round(s.upload_rate / 1000, 2))))
        self.setItem(row, cols.index('status'), QtWidgets.QTableWidgetItem(str(s.state)))

    def sort(self, Ncol, order):

        self.layoutAboutToBeChanged.emit()
        self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))        
        if order == Qt.DescendingOrder:
            self.arraydata.reverse()
        self.layoutChanged.emit()

    def on_click(self):

        for item in self.selectedItems():
            print("HERE: " + item.text())



if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()

    sys.exit(app.exec_())

