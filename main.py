import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6 import uic
import core
from core import UrlCheckResult

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)

        self.addPlaylistButton.clicked.connect(self.add_playlist)

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
            else:
                self.logOutput.append("Error: Could not fetch info for this playlist. It might be private or deleted.")


if __name__ == '__main__':

    app = QApplication(sys.argv)

    ytManagerApp = MyApp()
    ytManagerApp.show()

    app.exec()
