import re, os, sys, shutil, json
import yt_dlp
from typing import Optional, Any

# yt-dlp configuration for fetching playlist metadata quickly
config1 = {
    "extract_flat": True,
    "quiet": True,
    "noplaylistunavailablevideos": True
}

# --- Constants and Configurations ---

URL_TYPE = "https://www.youtube.com/playlist?list="


def sanitize_folder_name(name: str) -> str:
    """
    Cleans a string to make it a valid folder name for any operating system.

    Args:
        name: The original string, typically a playlist title.

    Returns:
        A filesystem-safe string to be used as a directory name.
    """
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    name = re.sub(r'[\x00-\x1f\x7f]', "", name)
    name = re.sub(r'\s+', " ", name).strip()
    name = name.strip('. ')
    return name

def sanitize_title(title: str) -> str:
    """
    Cleans a string to make it a valid file name.

    Args:
        title: The original string, typically a video title.

    Returns:
        A filesystem-safe string to be used as a file name.
    """
    title = re.sub(r"[\'\*\?\"<>]", "", title)
    title = title.replace("[", "(").replace("]", ")")
    title = title.replace("{", "(").replace("}", ")")
    title = re.sub(r"[|\\\/]", "-", title)
    title = re.sub(r"^[\'\*\?\"<>]+", "", title)
    title = re.sub(r"[\'\*\?\"<>]+$", "", title)
    return title

def basic_info(playlist_url: str) -> dict[str, Any]:
    """
    Fetches the basic information (list of entries) for a given playlist URL.
    Returns a safe empty structure in case of an error.
    
    Args:
        playlist_url: The URL of the YouTube playlist to fetch.

    Returns:
        The info dictionary from yt-dlp, or a dictionary with an empty 'entries' list on failure.
    """
    try:
        with yt_dlp.YoutubeDL(config1) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            return info if info else {"entries": []}
    except Exception as e:
        print(f"ERROR: Could not fetch playlist info. Reason: {e}")
        return {"entries": []}
    
def get_ffmpeg_path() -> Optional[str]:
    """
    Returns the path to the bundled ffmpeg executable if the script is running
    as a PyInstaller executable, otherwise returns None. This function is cross-platform.
    
    Returns:
        The full path to the ffmpeg executable, or None if not running as a bundle.
    """
    if getattr(sys, 'frozen', False):
        # sys._MEIPASS is a temporary directory created by PyInstaller at runtime.
        base_path = sys._MEIPASS #type: ignore
        
        ffmpeg_executable = os.path.join(base_path, 'dependencies', "ffmpeg")
        
        if os.path.exists(ffmpeg_executable):
            return ffmpeg_executable
    
    return None

def get_format_options(format_choice: str) -> dict:
    """
    Returns a dictionary of yt-dlp options based on the format choice. Handles audio, video, metadata, and thumbnails.
    """
    format_choice = format_choice.lower().strip()

    if format_choice == 'mp3':
        return {
            "format": "bestaudio/best",
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "0"},
                {"key": "EmbedThumbnail"},
            ]
        }

    elif format_choice == 'm4a':
        return {
            "format": "bestaudio/best",
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": "m4a", "preferredquality": "5"},
                {"key": "EmbedThumbnail"},
            ]
        }

    elif format_choice == 'flac':
        return {
            "format": "bestaudio/best",
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": "flac"},
                {"key": "EmbedThumbnail"},
            ]
        }

    elif format_choice == 'opus':
        return {
            "format": "bestaudio/best",
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": "opus"},
                {"key": "EmbedThumbnail"},
            ]
        }

    elif format_choice == 'wav':
        return {
            "format": "bestaudio/best",
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": "wav"},
                {"key": "EmbedThumbnail"},
            ]
        }

    elif format_choice == 'mp4':
        return {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "postprocessors": [
                {"key": "EmbedThumbnail"},
                {"key": "FFmpegMetadata"},
            ]
        }

    elif format_choice == 'mkv':
        return {
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mkv",
            "postprocessors": [
                {"key": "EmbedThumbnail"},
                {"key": "FFmpegMetadata"},
            ]
        }

    elif format_choice == 'webm':
        return {
            "format": "bestvideo[ext=webm]+bestaudio[ext=webm]/best",
            "merge_output_format": "webm",
            "postprocessors": [
                {"key": "EmbedThumbnail"},
                {"key": "FFmpegMetadata"},
            ]
        }
        
    else:
        print(f"Format '{format_choice}' not recognized. Using 'mp3' as default.")
        return get_format_options('mp3')

def make_config(tmp_folder: str, format: str = "mp3") -> dict:

    format_opts = get_format_options(format)

    base_config = {
        "outtmpl": os.path.join(tmp_folder, "%(title)s.%(ext)s"),
        "add_metadata": True,
        "writethumbnail": True,
        "quiet": True,
        "ignoreerrors": True
    }
   
    final_config = {**base_config, **format_opts}

    ffmpeg_location = get_ffmpeg_path()
    if ffmpeg_location:
        final_config['ffmpeg_location'] = ffmpeg_location
   
    return final_config

def make_path(folder_name: str) -> str:
    """
    Constructs the path for the hidden JSON state file for a given playlist folder.

    Args:
        folder_name: The name of the playlist's main folder.

    Returns:
        The full path to the JSON file (e.g., "My Playlist/.My Playlist.json").
    """
    return os.path.join(folder_name, f".{os.path.basename(folder_name)}.json")

def download_playlist(playlist_url: str, folder_name: str, format: str = "mp3") -> list[tuple[str, str]]:
    """
    Downloads a new playlist using a resilient, one-by-one process.
    It saves the state to a JSON file after each successful download, allowing
    the process to be resumed via the 'Update' function if it crashes.

    Args:
        playlist_url: The URL of the YouTube playlist to download.
        folder_name: The destination folder for the MP3 files.

    Returns:
        A list of errors that occurred during the process, as tuples of (title, error_message).
    """
    tmp_folder = os.path.join(folder_name, ".tmp")
    os.makedirs(tmp_folder, exist_ok=True)

    titles_map = {}
    ordered_titles = []
    errors = []

    info = basic_info(playlist_url)

    for idx, entry in enumerate(info.get('entries', [])): 
        with yt_dlp.YoutubeDL(make_config(tmp_folder, format=format)) as ydl:
            try:
                ydl.download([entry.get('url')])

                downloaded_files = [f for f in os.listdir(tmp_folder) if f.endswith(format)]
                if not downloaded_files: raise FileNotFoundError(f"{format.upper()} not found in temp folder")

                original_filename = os.path.join(tmp_folder, downloaded_files[0])
                title = entry.get('title', 'Unknown')
                sanitized = sanitize_title(title)
                numbered_title = f"{idx+1} - {sanitized}"
                final_filename = os.path.join(folder_name, f"{numbered_title}.{format}")
                os.replace(original_filename, final_filename)

                prev_title = ordered_titles[-1] if ordered_titles else None
                titles_map[title] = [
                    sanitized,
                    sanitize_title(prev_title) if prev_title else None,
                    None
                ]
                ordered_titles.append(title)

                # Atomically save the updated state to the JSON file after each success.
                json_filename = make_path(folder_name)
                with open(json_filename, "w", encoding="utf-8") as f:
                    temp_map = titles_map.copy()
                    for i, t in enumerate(ordered_titles[:-1]):
                        next_title = ordered_titles[i+1]
                        temp_map[t][2] = sanitize_title(next_title) if next_title else None
                    json.dump(temp_map, f, ensure_ascii=False, indent=4)
                    

            except Exception as e:
                errors.append((entry.get('title', 'Unknown'), str(e)))
                continue

    try:
        shutil.rmtree(tmp_folder)
    except Exception as e:
        errors.append((".tmp cleanup failed", str(e)))

    return errors

def get_missing_videos(playlist_url: str, folder_name: str) -> tuple[dict, dict, list[str]]:
    """
    Compares the local state (from JSON) with the online playlist to plan an update.
    It identifies new videos to download and rebuilds the title map to reflect the
    current official order of the playlist.

    Args:
        playlist_url: The URL of the YouTube playlist.
        folder_name: The local folder containing the playlist.

    Returns:
        A tuple containing:
        - new_videos: A dictionary of new videos to download {title: url}.
        - new_titles_map: The complete, correctly ordered map of the playlist.
        - errors: A list of errors encountered.
    """
    errors = []
    new_videos = {}
    new_titles_map = {}

    try:
        json_filename = make_path(folder_name)
        try:
            if os.path.exists(json_filename):
                with open(json_filename, "r", encoding="utf-8") as f:
                    titles_map = json.load(f)
            else: titles_map = {}
        except Exception as e:
            titles_map = {}
            errors.append(("JSON Error", f"Error loading state file: {e}"))

        with yt_dlp.YoutubeDL(config1) as ydl: info = ydl.extract_info(playlist_url, download=False)

        # Identify videos that are in the online playlist but not in our local state.
        ordered_titles = []
        if info and info.get('entries'):
            for entry in info.get('entries', []):
                original_title = entry.get('title', 'Unknown')
                sanitized = sanitize_title(original_title)
                video_url = entry.get('url')
                ordered_titles.append(original_title)
                if sanitized not in [sanitize_title(t) for t in titles_map.keys()]:
                    new_videos[original_title] = video_url
        
        # Rebuild the entire map from scratch to ensure the order is correct.
        for i, title in enumerate(ordered_titles):
            sanitized = sanitize_title(title)
            prev_title = sanitize_title(ordered_titles[i-1]) if i > 0 else None
            next_title = sanitize_title(ordered_titles[i+1]) if i < len(ordered_titles)-1 else None
            new_titles_map[title] = [sanitized, prev_title, next_title]

        # Overwrite the old JSON with the new, perfectly ordered map.
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(new_titles_map, f, ensure_ascii=False, indent=4)

    except Exception as e:
        errors.append(("Sync Planning", f"General error in get_missing_videos: {e}"))

    return new_videos, new_titles_map, errors

def update_playlist(new_videos: dict[str, str], titles_map: dict[str, list[Optional[str]]], folder_name: str) -> list[str]:
    """
    Executes the update plan from get_missing_videos. It downloads new files,
    renames all files to match the new order, and deletes obsolete files.

    Args:
        new_videos: Dictionary of new videos to download.
        titles_map: The final, correct map of the playlist.
        folder_name: The target folder to update.

    Returns:
        A list of errors that occurred during the update.
    """
    errors = []

    # --- Get back file's format ---
    for f in os.listdir(folder_name):
        if os.path.isfile(os.path.join(folder_name, f)):
            format = os.path.splitext(f)[1].replace('.', '')

            if format.endswith("json"):
                continue
            else:
                break

    print(format)

    if not format:
        errors.append(f"Nessun file multimediale trovato nella cartella '{folder_name}'. Impossibile eseguire l'update. ")
        return errors


    # --- Phase 1: Download new videos (if any) ---
    if new_videos:
        tmp_folder = os.path.join(folder_name, ".tmp")
        os.makedirs(tmp_folder, exist_ok=True)
        
        ydl_opts = make_config(tmp_folder)

        for title, url in new_videos.items():
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.extract_info(url, download=True)
                    downloaded_files = [f for f in os.listdir(tmp_folder) if f.endswith(format)]
                    if not downloaded_files: raise FileNotFoundError(f"{format.upper()} not found")

                    original_filename = os.path.join(tmp_folder, downloaded_files[0])
                    sanitized = titles_map[title][0]
                    temp_filename = os.path.join(folder_name, f"{sanitized}.{format}")
                    os.replace(original_filename, temp_filename)
            except Exception as e:
                errors.append((f"Error with '{title}'", str(e)))
        try:
            shutil.rmtree(tmp_folder)
        except Exception as e:
            errors.append(("Cleanup Error", f"Error deleting tmp_folder: {e}"))
    
    # --- Phase 2: Re-number all files to match the final order ---
    ordered_titles = list(titles_map.keys())
    for idx, original_title in enumerate(ordered_titles):
        sanitized = titles_map[original_title][0]
        if sanitized:
            try:
                current_files = [f for f in os.listdir(folder_name) if f.endswith(f'.{format}') and sanitized in f]
                if current_files:
                    old_name = os.path.join(folder_name, current_files[0])
                    new_name = os.path.join(folder_name, f"{idx+1} - {sanitized}.{format}")
                    if old_name != new_name:
                        os.replace(old_name, new_name)
            except Exception as e:
                errors.append((f"Error renaming '{original_title}'", str(e)))

    # --- Phase 3: Clean up obsolete files ---
    final_sanitized_titles = {v[0] for v in titles_map.values()}
    for f in os.listdir(folder_name):
        if f.endswith(f".{format}"):
            file_sanitized_title = sanitize_title(f.split(' - ', 1)[-1].rsplit(f'.{format}', 1)[0])
            if file_sanitized_title not in final_sanitized_titles:
                try:
                    os.remove(os.path.join(folder_name, f))
                except Exception as e:
                    errors.append((f"Error deleting '{f}'", str(e)))
    return errors

def folder_backup(folder_name: str) -> tuple[Optional[str], Optional[str]]:
    """
    Creates a backup of a folder by copying its contents to a subdirectory
    (e.g., "My Playlist" is backed up to "My Playlist/.bak").

    Args:
        folder_name: The path to the folder to be backed up.

    Returns:
        A tuple containing the backup folder path and an error message (or None).
    """
    # Note: A sibling backup folder is safer and makes restore logic simpler.
    backup_folder = os.path.join(folder_name, ".bak")
    
    if os.path.isdir(backup_folder):
        try:
            shutil.rmtree(backup_folder)
        except Exception as e:
            return None, f"Could not remove old backup folder: {e}"

    try:
        shutil.copytree(folder_name, backup_folder, ignore=shutil.ignore_patterns(".bak"))

        return backup_folder, None
    except Exception as e:
        return None, f"Failed to create backup for '{folder_name}': {e}"
    