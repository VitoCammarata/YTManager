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

        self.load_initial_settings()

    def save_directory(self):
        current_path = self.pathLine.text()

        if current_path and os.path.isdir(current_path):
            appSettings = core.load_app_settings()
            appSettings["last_directory"] = current_path
            core.save_app_settings(appSettings)
            self.pathLine.clearFocus()
        else:
            self.logOutput.append("Directory non valida")

    def load_initial_settings(self):
        settings = core.load_app_settings()

        last_dir = settings.get("last_directory", "")

        self.pathLine.setText(last_dir)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")

        if directory:
            self.pathLine.setText(directory)    
            self.save_directory()

    def initialize_playlists_list():
        pass

    def add_playlist_button(self, playlist_title):
        playlist_button = QPushButton(playlist_title)
        playlist_button.setObjectName(playlist_title)

        layout = self.playlistsList.layout()
        count = layout.count()

        layout.insertWidget(count - 1, playlist_button)

    def add_playlist(self):
        user_input = self.urlInsertField.text()
        self.urlInsertField.clear()


        result = core.check_url(user_input)
        
        if result[1] == UrlCheckResult.INVALID_URL:
            self.logOutput.append("This URL is invalid. Please insert a valid URL.")
        elif result[1] == UrlCheckResult.URL_ALREADY_EXISTS:
            self.logOutput.append("This URL already exist in your list.")
        elif result[1] == UrlCheckResult.VALID_AND_NEW:
            playlist_title = core.create_playlist_entry(result[0])
            if playlist_title:
                self.logOutput.append(f"URL correctly saved. Playlist {playlist_title} successfully created.")
                self.add_playlist_button(playlist_title)
            else:
                self.logOutput.append("Error: Could not fetch info for this playlist. It might be private or deleted.")


if __name__ == '__main__':

    app = QApplication(sys.argv)

    ytManagerApp = MyApp()
    ytManagerApp.show()

    app.exec()
