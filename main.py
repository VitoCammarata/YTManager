import sys, os
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog
from PyQt6 import uic
import core
from core import UrlCheckResult

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)

        self.viewPath.clicked.connect(self.select_directory)
        self.pathLine.returnPressed.connect(self.save_directory)
        self.addPlaylistButton.clicked.connect(self.add_playlist)
        self.backButton.clicked.connect(self.show_add_playlists_page)

        self.show_playlists_list()
        self.load_initial_settings()

    def save_directory(self):
        current_path = self.pathLine.text()

        if (current_path and os.path.isdir(current_path)) or current_path == "":
            appSettings = core.load_app_settings()
            appSettings["last_directory"] = current_path
            core.save_app_settings(appSettings)
            self.pathLine.clearFocus()
        else:
            self.logsOutput.append("Not a valid directory")

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")

        if directory:
            self.pathLine.setText(directory)    
            self.save_directory()

    def load_initial_settings(self):
        settings = core.load_app_settings()

        last_dir = settings.get("last_directory", "")

        self.pathLine.setText(last_dir)

    def show_playlists_list(self):
        playlists_list = core.get_playlists_list()

        for data in playlists_list:
            playlist_title = data.get("title")
            playlist_id = data.get("id")
            if playlist_title and playlist_id:
                self.add_playlist_button(playlist_title, playlist_id)

    def show_add_playlists_page(self):
        self.rightSide.setCurrentWidget(self.addURLs)

    def show_playlist_menu(self):
        playlist_button = self.sender()
        if not playlist_button:
            return

        playlist_id = playlist_button.property("playlist_id")
        if not playlist_id:
            return

        playlists_list = core.get_playlists_list()
        target_playlist_data = None
        for p_data in playlists_list:
            if p_data.get("id") == playlist_id:
                target_playlist_data = p_data
                break
        
        if not target_playlist_data:
            self.playlistsLogsOutput.append(f"Error: Could not find data for this playlist")
            return

        self.rightSide.setCurrentWidget(self.managePlaylist)


    def add_playlist_button(self, playlist_title: str, playlist_id: str):
        playlist_button = QPushButton(playlist_title)
        playlist_button.setObjectName(playlist_title)
        playlist_button.setProperty("playlist_id", playlist_id)
        playlist_button.clicked.connect(self.show_playlist_menu)

        layout = self.playlistsList.layout()
        count = layout.count()

        layout.insertWidget(count - 1, playlist_button)

    def add_playlist(self):
        user_input = self.urlInsertField.text()
        directory = self.pathLine.text()

        self.urlInsertField.clear()

        if not directory or not os.path.isdir(directory):
            self.urlLogsOutput.append("Error: Please select a valid download directory.")
            return

        url, status = core.check_url(user_input, directory)
        
        if status == UrlCheckResult.INVALID_URL:
            self.urlLogsOutput.append("This URL is invalid. Please insert a valid URL.")
        elif status == UrlCheckResult.URL_ALREADY_EXISTS:
            self.urlLogsOutput.append("This playlist already exists in the current directory. Please choose a new directory.")
        elif status == UrlCheckResult.VALID_AND_NEW:
            self.urlLogsOutput.append(f"URL is valid, fetching title from YouTube...")

            result_tuple = core.create_playlist_entry(url, directory)
            
            if result_tuple:
                playlist_id, playlist_title = result_tuple
                self.urlLogsOutput.append(f"Playlist '{playlist_title}' added successfully.")
                self.add_playlist_button(playlist_title, playlist_id)
            else:
                self.urlLogsOutput.append("Error: Could not fetch info. The playlist might be private or deleted.")


if __name__ == '__main__':

    app = QApplication(sys.argv)

    ytManagerApp = MyApp()
    ytManagerApp.show()

    app.exec()
