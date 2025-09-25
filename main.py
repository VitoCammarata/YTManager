import sys, os, subprocess, webbrowser
from typing import Optional
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QLineEdit, QDialog
from PyQt6.QtGui import QIcon
from PyQt6 import uic
import core
import resources_rc
from core import UrlCheckResult

class DownloadOptions(QDialog):
    AUDIO_FORMATS = ['mp3', 'm4a', 'flac', 'opus', 'wav']
    VIDEO_FORMATS = ['mp4', 'mkv', 'webm']

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("download_options_dialog.ui", self)

        self.formatsList.currentTextChanged.connect(self.update_quality_state)

        self.update_quality_state(self.formatsList.currentText())

    def update_quality_state(self, format):

        if format.lower() in self.AUDIO_FORMATS:
            self.qualityList.setEnabled(False)
            self.qualityList.clear()
            self.qualityList.addItem("BEST")

        elif format.lower() in self.VIDEO_FORMATS:
            self.qualityList.setEnabled(True)
            
            if self.qualityList.count() == 1 and self.qualityList.itemText(0) == "BEST":
                self.qualityList.clear()
                self.qualityList.addItems([
                    "4k (2160p)",
                    "2K (1440p)",
                    "Full HD (1080p)",
                    "HD (720p)",
                    "Standard (480p)",
                    "Low (360p)"
                ])

    def get_selected_options(self) -> tuple[str, Optional[str]]:
        format = self.formatsList.currentText()
        quality = None
        
        if self.qualityList.isEnabled():
            quality_text = self.qualityList.currentText()
            quality = quality_text[quality_text.find("(")+1:quality_text.find("p")]

        return (format.lower(), quality)

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)

        #Istance variable for saving playlist_id
        self.playlist_id = None

        self.viewPath.clicked.connect(self.select_directory)
        self.pathLine.returnPressed.connect(self.save_directory)
        self.addPlaylistButton.clicked.connect(self.add_playlist)
        self.backButton.clicked.connect(self.show_add_playlists_page)
        self.openDirectory.clicked.connect(self.show_playlist_directory)
        self.go_to_YT.clicked.connect(self.youtube_redirect)
        self.downloadUpdateButton.clicked.connect(self.handle_download_or_update)

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
        self.playlist_id = playlist_id

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
            if key == "directory":
                value = os.path.join(value, playlist_data["title"].strip())
            if key != "id":
                try:
                    data_value = getattr(self, f"{key}Name")
                    data_value.setText((value if key != "quality" else (value if value == "BEST" else f"{value}p")) if value else "N/A")
                    data_value.setCursorPosition(0)
                except AttributeError:
                    pass

        playlist_id = playlist_data.get("id")

        if playlist_id:
            local_count, remote_count = core.check_playlist_state(playlist_id)

            if remote_count is None:
                state_string = f"Local: {local_count} (Could not verify online)"
            
            elif local_count == 0 and remote_count > 0:
                state_string = f"Not downloaded ({local_count}/{remote_count} videos)"
                
            elif local_count == remote_count and local_count > 0:
                state_string = f"Synced ({local_count}/{remote_count} videos)"
                
            elif local_count < remote_count:
                state_string = f"Update needed ({local_count}/{remote_count} videos)"

            elif local_count > remote_count:
                state_string = f"Needs verification ({local_count}/{remote_count} videos)"

            else:
                state_string = "N/A (Playlist empty?)"

            self.stateName.setText(state_string)
            self.stateName.setCursorPosition(0)

            playlist_downloaded = core.get_playlist_state(playlist_id)
            if playlist_downloaded:
                self.downloadUpdateButton.setText("UPDATE")
                self.downloadUpdateButton.setIcon(QIcon.fromTheme("view-refresh"))
            else:
                self.downloadUpdateButton.setText("DOWNLOAD")
                self.downloadUpdateButton.setIcon(QIcon(":/assets/gui_icons/down-to-line.svg"))
        else:
            self.stateName.setText("N/A")
            self.stateName.setCursorPosition(0)

    def show_playlist_directory(self):
        playlist_directory = self.directoryName.text()
        
        if playlist_directory and os.path.isdir(playlist_directory):
            try:
                if sys.platform == "win32":
                    os.startfile(playlist_directory)
                else:
                    subprocess.Popen(["xdg-open", playlist_directory])
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

    def handle_download_or_update(self):
        button_text = self.downloadUpdateButton.text()
        if button_text == "DOWNLOAD":
            self.download_playlist()
        elif button_text == "UPDATE":
            self.update_playlist()

    def download_playlist(self):
        downloadOptionsDialog = DownloadOptions(self)

        if downloadOptionsDialog.exec() == QDialog.DialogCode.Accepted:
            format, quality = downloadOptionsDialog.get_selected_options()

            self.playlistsLogsOutput.setText(f"Starting download for '{self.titleName.text()}'...")
            QApplication.processEvents()

            errors = core.download_playlist(
                self.urlName.text(), 
                self.directoryName.text(), 
                self.playlist_id, 
                format,
                quality
            )

            if errors:
                self.playlistsLogsOutput.append("\n<font color='orange'>Download completed with some errors:</font>")
                for video_title, error_message in errors:
                    self.playlistsLogsOutput.append(f"- <b>{video_title}</b>: {error_message}")
            else:
                self.playlistsLogsOutput.append("\n<font color='green'>Download completed successfully!</font>")

            playlists_list = core.get_playlists_list()
            updated_playlist_data = next((p for p in playlists_list if p.get("id") == self.playlist_id), None)
            if updated_playlist_data:
                self.show_playlist_data(updated_playlist_data)

        else:
            self.playlistsLogsOutput.append("Download cancelled.")
            return

    def update_playlist(self):
        pass


if __name__ == '__main__':

    app = QApplication(sys.argv)

    ytManagerApp = MyApp()
    ytManagerApp.show()

    app.exec()
