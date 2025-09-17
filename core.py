from typing import Optional
import os, json, appdirs
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

def get_playlists_list() -> dict:
    app_data_dir = get_app_data_dir()
    json_playlist_path = os.path.join(app_data_dir, "playlistsList.json")

    try:
        with open(json_playlist_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            else:
                return {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def get_playlist_title(url: str) -> str:
    try:
        with yt_dlp.YoutubeDL(yt_config) as ydl:
            info = ydl.extract_info(url, download=False)
            if info:
                playlist_title = info.get('title', 'Unknown Playlist')
        return sanitize_filename(playlist_title)
    except Exception:
        return None
    return None

def get_playlist_data_dir(playlist_title: str) -> str:
    playlist_dir = os.path.join(get_app_data_dir(), playlist_title)
    os.makedirs(playlist_dir, exist_ok=True)
    return playlist_dir

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

def check_url(user_input: str) -> tuple[Optional[str], UrlCheckResult]:
    url = validate_url(user_input)

    if url is None:
        return (None, UrlCheckResult.INVALID_URL)

    playlists_list = get_playlists_list()

    if url in playlists_list.values():
        return (None, UrlCheckResult.URL_ALREADY_EXISTS)
    else:
        return (url, UrlCheckResult.VALID_AND_NEW)

def create_playlist_entry(url: str) -> Optional[str]:
    playlist_title = get_playlist_title(url)
    if playlist_title is None:
        return None

    app_data_dir = get_app_data_dir()
    json_playlist_path = os.path.join(app_data_dir, "playlistsList.json")

    try:
        with open(json_playlist_path, "r", encoding="utf-8") as f:
            playlists_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        playlists_data = {}

    playlists_data[playlist_title] = url

    with open(json_playlist_path, "w", encoding="utf-8") as f:
        json.dump(playlists_data, f, ensure_ascii=False, indent=4)

    get_playlist_data_dir(playlist_title)
    
    return playlist_title