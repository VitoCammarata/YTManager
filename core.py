from typing import Optional
import os, json, appdirs, uuid
from enum import Enum, auto
import yt_dlp
from pathvalidate import sanitize_filename

PLAYLIST_URL_TYPE = "https://www.youtube.com/playlist?list="
APP_NAME = "YouTubePlaylistManager"

class UrlCheckResult(Enum):
    VALID_AND_NEW = auto() 
    URL_ALREADY_EXISTS = auto() 
    INVALID_URL = auto()

yt_config = {
    "extract_flat": True,
    "quiet": True,
    "noplaylistunavailablevideos": True
} 

def get_app_data_dir() -> str:
    data_dir = appdirs.user_data_dir(appname=APP_NAME)
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def get_playlists_list() -> list:
    app_data_dir = get_app_data_dir()
    json_playlist_path = os.path.join(app_data_dir, "playlistsList.json")

    try:
        with open(json_playlist_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_playlists_list(data: list) -> None:
    app_data_dir = get_app_data_dir()
    json_playlist_path = os.path.join(app_data_dir, "playlistsList.json")

    with open(json_playlist_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_playlist_title(url: str) -> Optional[str]:
    try:
        with yt_dlp.YoutubeDL(yt_config) as ydl:
            info = ydl.extract_info(url, download=False, process=False)
            if info:
                title = info.get('title', 'Unknown Playlist')
                return sanitize_filename(title)
    except Exception:
        return None
    return None

def create_playlist_data_dir(playlist_id: str) -> str:
    playlist_dir = os.path.join(get_app_data_dir(), playlist_id)
    os.makedirs(playlist_dir, exist_ok=True)
    return playlist_dir


def load_app_settings() -> dict:
    app_data_dir = get_app_data_dir()
    file_settings_path = os.path.join(app_data_dir, "appSettings.json")

    try:
        with open(file_settings_path, "r", encoding="utf-8") as f:
            appSettings = json.load(f)
            if isinstance(appSettings, dict):
                return appSettings
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    return {}

def save_app_settings(app_data: dict):
    app_data_dir = get_app_data_dir()
    file_settings_path = os.path.join(app_data_dir, "appSettings.json")

    with open(file_settings_path, "w", encoding="utf-8") as f:
        json.dump(app_data, f, ensure_ascii=False, indent=4) 


def validate_url(user_input: str) -> Optional[str]:
    url = user_input.strip()

    if "https://" in url and "list=" in url:
        try:
            playlist_id = url.split("list=")[1].split("&")[0]
            if playlist_id:
                return PLAYLIST_URL_TYPE + playlist_id

        except IndexError:
            return None
    return None

def check_url(user_input: str, directory: str) -> tuple[Optional[str], UrlCheckResult]:
    url = validate_url(user_input)

    if url is None:
        return (None, UrlCheckResult.INVALID_URL)

    playlists_list = get_playlists_list()

    for playlist in playlists_list:
        if playlist.get("url") == url and playlist.get("directory") == directory:
            return (None, UrlCheckResult.URL_ALREADY_EXISTS)

    return (url, UrlCheckResult.VALID_AND_NEW)

def create_playlist_entry(url: str, directory: str) -> Optional[tuple[str, str]]:
    playlist_title = get_playlist_title(url)
    if playlist_title is None:
        return None

    playlist_id = str(uuid.uuid4())

    playlists_list = get_playlists_list()

    new_playlist_data = {
        "id": playlist_id,
        "title": playlist_title,
        "directory": directory,
        "url": url,
        "format": "",
        "quality": ""
    }
    playlists_list.append(new_playlist_data)
    save_playlists_list(playlists_list)
    create_playlist_data_dir(playlist_id)

    playlist_download_dir = os.path.join(directory, playlist_title)
    os.makedirs(playlist_download_dir, exist_ok=True)

    return (playlist_id, playlist_title)

def playlist_state(playlist_id:str) -> bool:
    playlist_data_dir = create_playlist_data_dir(playlist_id)

    playlist_settings_filepath = os.path.join(playlist_data_dir, f"{playlist_id}.json")

    return os.path.isfile(playlist_settings_filepath)
