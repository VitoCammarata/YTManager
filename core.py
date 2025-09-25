from typing import Optional
import os, json, appdirs, uuid, shutil, sys, subprocess
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

def get_options(format: str, quality: Optional[str]) -> dict:
    """
    Builds yt-dlp configuration for specific format and quality requirements.

    Args:
        format: Output format (mp3, mp4, etc.)
        quality: Video quality in pixels (1080, 720, etc.)

    Returns:
        dict: Complete yt-dlp options dictionary.

    Notes:
        - Audio formats always use best quality
        - Video quality falls back to next best available
        - Handles thumbnail embedding and metadata
    """
    format = format.lower().strip()

    # --- GROUP 1: Audio Formats ---
    if format in ['mp3', 'm4a', 'flac', 'opus', 'wav']:
        audio_quality = "bestaudio/best"

        audio_postprocessors = [
            {"key": "FFmpegMetadata"}
        ]

        if format not in ['opus', 'wav']:
            audio_postprocessors.append({"key": "EmbedThumbnail"})
        
        if format == 'mp3':
            audio_postprocessors.insert(0, {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "0"})
        elif format == 'm4a':
            audio_postprocessors.insert(0, {"key": "FFmpegExtractAudio", "preferredcodec": "m4a", "preferredquality": "5"})
        elif format == 'flac':
            audio_postprocessors.insert(0, {"key": "FFmpegExtractAudio", "preferredcodec": "flac"})
        elif format == 'opus':
            audio_postprocessors.insert(0, {"key": "FFmpegExtractAudio", "preferredcodec": "opus"})
        elif format == 'wav':
            audio_postprocessors.insert(0, {"key": "FFmpegExtractAudio", "preferredcodec": "wav"})
            
        return {
            "format": audio_quality,
            "postprocessors": audio_postprocessors
        }

    # --- GROUP 2: Video Formats ---
    elif format in ['mp4', 'mkv', 'webm']:
        
        if quality is None:
            quality = "1080" 

        if format == 'mp4':
            video_quality = f"bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        elif format == 'webm':
            video_quality = f"bestvideo[height<={quality}][ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best"
        else: # mkv
            video_quality = f"bestvideo[height<={quality}]+bestaudio/best"

        video_postprocessors = [{"key": "FFmpegMetadata"}]

        if format in ['mp4', 'mkv']:
            video_postprocessors.append({"key": "EmbedThumbnail"})
        
        return {
            "format": video_quality,
            "merge_output_format": format if format != 'mp4' else None,
            "postprocessors": video_postprocessors
        }
    
    # --- Fallback ---
    else:
        return get_options("mp3", None)

def make_yt_download_config(path: str, format: str, quality: Optional[str]) -> dict:
    """
    Creates the full yt-dlp configuration dictionary for a download.
    """
    base_config = {
        "outtmpl": os.path.join(path, "%(title)s.%(ext)s"),
        "add_metadata": True,
        "writethumbnail": True,
        "quiet": True,
        "ignoreerrors": True,
        
        "parse_metadata": [
            "artist:%(artist|channel)s",
            "album:%(album|playlist_title)s",
            "date:%(upload_date)s"
        ]
    }
    format_opts = get_options(format, quality)
   
    final_config = {**base_config, **format_opts}

    ffmpeg_location = get_dependencies_path("ffmpeg")
    if ffmpeg_location:
        final_config['ffmpeg_location'] = ffmpeg_location
   
    return final_config

def get_dependencies_path(name: str) -> Optional[str]:
    """Gets the path for a bundled dependency executable.

    If the script is running as a PyInstaller package, this function returns the
    absolute path to the specified dependency (e.g., ffmpeg, ffprobe).
    
    If the script is not running as a package, it provides a specific fallback:
    - For "ffmpeg", it returns `None` (for yt-dlp's 'ffmpeg_location' option).
    - For other names, it returns the name itself (for use with subprocess).

    Args:
        name (str): The name of the dependency to locate (e.g., "ffmpeg").

    Returns:
        Optional[str]: The absolute path to the dependency or a fallback value.
    """
    # When packaged by PyInstaller, sys.frozen is True and _MEIPASS points to a temp folder
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS #type: ignore
        
        executable = os.path.join(
            base_path,
            'dependencies',
            'windows' if os.name == 'nt' else 'linux',
            f'{name}.exe' if os.name == 'nt' else name
        )
        
        if os.path.exists(executable):
            return executable
    
    return None if name == "ffmpeg" else name

def get_playlist_data_path(playlist_id: str) -> str:
    playlist_dir = get_playlist_data_dir(playlist_id)
    return os.path.join(playlist_dir, "state.json")

def create_download_temp_dir(playlist_id):
    playlist_data_dir = get_playlist_data_dir(playlist_id)
    temp_dir = os.path.join(playlist_data_dir, "temp")
    if os.path.isdir(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

def get_playlist_basic_info(url):
    try:
        with yt_dlp.YoutubeDL(yt_config) as ydl:
            info = ydl.extract_info(url, download=False)
            return info if info else {"entries": []}
    except Exception as e:
        raise Exception(f"Could not fetch basic playlist info. Reason: {e}")  

def get_video_quality(file_path: str) -> str:
    try:
        # Questo comando chiede a ffprobe di mostrare le info sui flussi (streams) in formato JSON
        command = [
            get_dependencies_path("ffprobe"),
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_streams',
            file_path
        ]
        
        # Esegui il comando e cattura l'output
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        # Carica l'output JSON in un dizionario Python
        media_info = json.loads(result.stdout)
        
        # Il primo flusso ('streams'[0]) è di solito quello che ci interessa
        stream_info = media_info['streams'][0]
        
        if stream_info['codec_type'] == 'video':
            # Per i video, prendiamo l'altezza (height)
            height = stream_info.get('height')
            return f"({height}p)" if height else ""
        
        elif stream_info['codec_type'] == 'audio':
            # Per l'audio, prendiamo il bitrate in bits/sec e lo convertiamo in kbps
            bit_rate = stream_info.get('bit_rate')
            if bit_rate:
                kbps = round(int(bit_rate) / 1000)
                return f"({kbps}kbps)"
            return ""

    except (FileNotFoundError, subprocess.CalledProcessError, IndexError, KeyError) as e:
        return ""
    
    return ""

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

def get_playlist_data_dir(playlist_id: str) -> str:
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
    get_playlist_data_dir(playlist_id)

    playlist_download_dir = os.path.join(directory, playlist_title)
    os.makedirs(playlist_download_dir, exist_ok=True)

    return (playlist_id, playlist_title)

def get_playlist_state(playlist_id:str) -> bool:
    state_file_path = get_playlist_data_path(playlist_id)

    return os.path.isfile(state_file_path)

def check_playlist_state(playlist_id: str) -> tuple[int, int | None]:
    folder_videos_count = 0
    state_file_path = get_playlist_data_path(playlist_id)
    if os.path.exists(state_file_path):
        try:
            with open(state_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                folder_videos_count = len(data.get("files", {}))
        except (json.JSONDecodeError, KeyError):
            pass

    playlists_list = get_playlists_list()
    playlist_data = next((p for p in playlists_list if p.get("id") == playlist_id), None)
    
    if not playlist_data:
        return folder_videos_count, 0

    try:
        playlist_info = get_playlist_basic_info(playlist_data["url"])
        remote_videos_count = len(playlist_info.get("entries", []))
        return folder_videos_count, remote_videos_count
    except Exception:
        return folder_videos_count, None

def download_playlist(url: str, folder_name: str, playlist_id: str, format: str, quality: Optional[str]):
    temp_download_folder = create_download_temp_dir(playlist_id)

    playlist_config_map = {
        "quality": quality,
        "files": {}
    }
    errors = []

    playlist_basic_info = get_playlist_basic_info(url)

    for idx, entry in enumerate(playlist_basic_info.get('entries', [])): 
            with yt_dlp.YoutubeDL(make_yt_download_config(temp_download_folder, format, quality)) as ydl:
                try:
                    ydl.download([entry.get('url')])

                    downloaded_files = [f for f in os.listdir(temp_download_folder) if f.endswith(format)]
                    if not downloaded_files:
                        raise FileNotFoundError(f"{format.upper()} not found in temp folder")

                    temp_filename_path = os.path.join(temp_download_folder, downloaded_files[0])
                    video_id = entry.get('id')
                    video_title = entry.get('title', 'Unknown')

                    video_quality = ""
                    if format in ['mp4', 'mkv', 'webm']:
                        video_quality = get_video_quality(temp_filename_path)

                    sanitized_title = sanitize_filename(video_title)
                    filename_path = os.path.join(folder_name, f"{idx+1} - {sanitized_title}{video_quality}.{format}")

                    os.replace(temp_filename_path, filename_path)

                    video_details = {
                        "title": video_title,
                        "sanitized_title": sanitized_title,
                        "playlist_index": idx+1
                    }

                    playlist_config_map["files"][video_id] = video_details

                    file_data_path = get_playlist_data_path(playlist_id)
                    with open(file_data_path, "w", encoding="utf-8") as f:
                        json.dump(playlist_config_map, f, ensure_ascii=False, indent=4)

                except Exception as e:
                    errors.append((entry.get('title', 'Unknown'), str(e)))
                    continue

    playlists_list = get_playlists_list()
    for playlist_data in playlists_list:
        if playlist_data.get("id") == playlist_id:
            playlist_data["format"] = format.upper()
            playlist_data["quality"] = quality if quality else "BEST"
            break  
    save_playlists_list(playlists_list)

    try:
        shutil.rmtree(temp_download_folder)
    except Exception as e:
        errors.append(("temp cleanup failed", str(e)))


    return errors
