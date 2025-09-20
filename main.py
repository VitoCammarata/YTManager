import sys, os, subprocess, webbrowser
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QLineEdit
from PyQt6.QtGui import QIcon
from PyQt6 import uic
import core
import resources_rc
from core import UrlCheckResult

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)

        self.viewPath.clicked.connect(self.select_directory)
        self.pathLine.returnPressed.connect(self.save_directory)
        self.addPlaylistButton.clicked.connect(self.add_playlist)
        self.backButton.clicked.connect(self.show_add_playlists_page)
        self.openDirectory.clicked.connect(self.show_playlist_directory)
        self.go_to_YT.clicked.connect(self.youtube_redirect)

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

        for playlist_data in playlists_list:
            playlist_title = playlist_data.get("title")
            playlist_id = playlist_data.get("id")
            if playlist_title and playlist_id:
                self.add_playlist_buttons(playlist_title, playlist_id)

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
        for playlist_data in playlists_list:
            if playlist_data.get("id") == playlist_id:
                target_playlist_data = playlist_data
                break
                
        if target_playlist_data:
            self.show_playlist_data(target_playlist_data)
            self.rightSide.setCurrentWidget(self.managePlaylist)
        else:
            self.playlistsLogsOutput.append(f"Error: Could not find data for this playlist")
            return

    def show_playlist_data(self, playlist_data: dict):

        for key, value in playlist_data.items():
            if key != "id":
                button_name = getattr(self, f"{key}Name")
                button_name.setText(value if value else "N/A")
                button_name.setCursorPosition(0)

        state = ""
        self.stateName.setText(state if state else "N/A")
        self.stateName.setCursorPosition(0)

        playlist_id = playlist_data.get("id")
        if playlist_id:
            playlist_downloaded = core.playlist_state(playlist_id)

            if playlist_downloaded:
                self.downloadUpdateButton.setText("UPDATE")
                self.downloadUpdateButton.setIcon(QIcon.fromTheme("view-refresh"))
            else:
                self.downloadUpdateButton.setText("DOWNLOAD")
                self.downloadUpdateButton.setIcon(QIcon(":/assets/gui_icons/down-to-line.svg"))



    def show_playlist_directory(self, directory: str):
        playlist_directory = os.path.join(self.directoryName.text(), self.titleName.text())
        
        if playlist_directory and os.path.isdir(playlist_directory):
            try:
                if sys.platform == "win32":
                    os.startfile(playlist_directory)
                else:
                    subprocess.Popen(["open", playlist_directory])
            except Exception as e:
                self.playlistsLogsOutput.append(f"Error opening directory: {e}")
        else:
            self.playlistsLogsOutput.append("Error: Directory not found.")

    def youtube_redirect(self, url: str):
        url = self.urlName.text()

        if url:
            webbrowser.open(url)
        else:
            self.playlistsLogsOutput.append("Error: URL for this playlist is missing.")


    def add_playlist_buttons(self, playlist_title: str, playlist_id: str):
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
                self.add_playlist_buttons(playlist_title, playlist_id)
            else:
                self.urlLogsOutput.append("Error: Could not fetch info. The playlist might be private or deleted.")


if __name__ == '__main__':

    app = QApplication(sys.argv)

    ytManagerApp = MyApp()
    ytManagerApp.show()

    app.exec()
