import os, sys, shutil, json
import appdirs, subprocess
import yt_dlp
from typing import Optional, Any
from pathvalidate import sanitize_filename

# --- Constants and Configurations ---

# yt-dlp configuration for fetching playlist metadata quickly
yt_config = {
    "extract_flat": True,
    "quiet": True,
    "noplaylistunavailablevideos": True
}
PLAYLIST_URL_TYPE = "https://www.youtube.com/playlist?list="
VIDEO_URL_TYPE1 = "https://www.youtube.com/watch?v="
VIDEO_URL_TYPE2 = "https://youtu.be/"
APP_NAME = "YouTubePlaylistManager"

def get_app_data_dir() -> str:
    data_dir = appdirs.user_data_dir(appname=APP_NAME)
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def get_playlist_data_dir(playlist_title: str) -> str:
    sanitize_title = sanitize_filename(playlist_title)
    playlist_dir = os.path.join(get_app_data_dir(), sanitize_title)
    os.makedirs(playlist_dir, exist_ok=True)
    return playlist_dir

def get_playlist_state_path(playlist_title: str) -> str:
    playlist_dir = get_playlist_data_dir(playlist_title)
    return os.path.join(playlist_dir, "state.json")

def get_temp_dir(playlist_title: str) -> str:
    playlist_dir = get_playlist_data_dir(playlist_title)
    temp_dir = os.path.join(playlist_dir, "temp")
    if os.path.isdir(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

def get_actual_file_quality(file_path: str) -> str:
    """
    Uses ffprobe to inspect a media file and get its actual quality.

    Args:
        file_path: The full path to the media file.

    Returns:
        A formatted quality string (e.g., "(1080p)", "(128kbps)") or an empty string.
    """
    try:
        # Questo comando chiede a ffprobe di mostrare le info sui flussi (streams) in formato JSON
        command = [
            'ffprobe',
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
        # Se ffprobe non viene trovato, o il file non ha info valide, o c'è un errore,
        # restituiamo una stringa vuota per non rompere il programma.
        # print(f"Could not get quality for {file_path}: {e}") # (opzionale, per debug)
        return ""
    
    return ""

def basic_info(playlist_url: str) -> dict[str, Any]:
    """
    Retrieve basic playlist information (entries list) via yt-dlp.

    Args:
        playlist_url: YouTube playlist URL.

    Returns:
        The info dictionary returned by yt-dlp, or a safe structure with
        an empty 'entries' list if fetching fails.
    """
    try:
        # Use the lightweight yt_config to fetch only metadata (no downloads)
        with yt_dlp.YoutubeDL(yt_config) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            return info if info else {"entries": []}
    except Exception as e:
        raise Exception(f"Could not fetch basic playlist info. Reason: {e}")
    
def get_ffmpeg_path() -> Optional[str]:
    """
    If running as a PyInstaller bundle, return the path to the bundled ffmpeg.

    Returns:
        Full path to the ffmpeg executable when bundled, otherwise None.
    """
    # When packaged by PyInstaller, sys.frozen is True and _MEIPASS points to a temp folder
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS #type: ignore
        
        ffmpeg_executable = os.path.join(
            base_path,
            'dependencies',
            'windows' if os.name == 'nt' else 'linux',
            'ffmpeg.exe' if os.name == 'nt' else 'ffmpeg'
        )
        
        if os.path.exists(ffmpeg_executable):
            return ffmpeg_executable
    
    return None

def get_options(format: str, quality: Optional[str]) -> dict:
    """
    Builds yt-dlp option fragments for a given format and quality.
    Audio is always best quality; video quality is user-defined.
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
        

def make_config(path: str, format: str, quality: Optional[str]) -> dict:
    """
    Creates the full yt-dlp configuration dictionary for a download.
    """
    format_opts = get_options(format, quality)

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
   
    final_config = {**base_config, **format_opts}

    ffmpeg_location = get_ffmpeg_path()
    if ffmpeg_location:
        final_config['ffmpeg_location'] = ffmpeg_location
   
    return final_config

def make_path(folder_name: str) -> str:
    """
    Build the path to the hidden JSON state file inside a playlist folder.

    Args:
        folder_name: Folder name of the playlist.

    Returns:
        Path to the JSON state file (e.g., "My Playlist/.My Playlist.json").
    """
    return os.path.join(folder_name, f".{os.path.basename(folder_name)}.json")

def download_video(video_url: list[str], format: str, quality: Optional[str]) -> list[tuple[str, str]]:
    """
    Download one or more single videos into the current directory.

    This function does not use numbering or the JSON state file; it simply
    downloads the specified URLs into the working directory.

    Args:
        video_url: List of YouTube video URLs to download.
        format: Desired output format (e.g., "mp3", "mp4").

    Returns:
        A list of errors as tuples (video_title, error_message).
    """
    # Temporary folder for yt-dlp downloads to avoid partial files in target
    temp_folder = get_temp_dir("video download")
    errors = []

    with yt_dlp.YoutubeDL(make_config(temp_folder, format, quality)) as ydl:
        for url in video_url:
            try:
                # Try to obtain metadata first to have a readable error context
                info = ydl.extract_info(url, download=False)
                if info:
                    video_title = info.get('title', 'Unknown Title')

                sanitized_title = sanitize_filename(video_title)

                # Perform the actual download; any postprocessors run automatically
                ydl.download([url])

                downloaded_video = os.listdir(temp_folder)
                if not downloaded_video:
                    # If no file found, treat as a recoverable error for this entry
                    raise FileNotFoundError(f"{format.upper()} not found in temp folder")
                
                video_path = os.path.join(temp_folder, downloaded_video[0])

                quality_str = ""
                if format in ['mp4', 'mkv', 'webm']:
                    quality_str = get_actual_file_quality(video_path)

                final_filename = f"{sanitized_title}{quality_str}.{format}"
                final_path = os.path.join(".", final_filename)

                os.rename(video_path, final_path)

            # Collect errors per-video without stopping the whole batch
            except Exception as e:
                errors.append((video_title, str(e)))
    
    return errors

def download_playlists(playlist_url: str, folder_name: str, playlist_title: str, format: str, quality: Optional[str]) -> list[tuple[str, str]]:
    """
    Download a playlist entry-by-entry in a resilient manner.

    The function downloads each item to a temporary folder, moves the file into
    the destination with a numbered name, and updates the JSON state file after
    each successful download so the process can be resumed if interrupted.

    Args:
        playlist_url: URL of the YouTube playlist.
        folder_name: Destination folder for the downloaded files.
        format: Desired output format.

    Returns:
        A list of errors as tuples (title, error_message).
    """
    # Temporary folder for yt-dlp downloads to avoid partial files in target
    temp_folder = get_temp_dir(playlist_title)

    titles_map = {
        "quality": quality,
        "files": {}
    }
    errors = []

    # Get playlist entries (lightweight)
    info = basic_info(playlist_url)

    # Iterate entries in playlist order and download one by one
    for idx, entry in enumerate(info.get('entries', [])): 
        with yt_dlp.YoutubeDL(make_config(temp_folder, format, quality)) as ydl:
            try:
                # Download the single entry into the temporary folder
                ydl.download([entry.get('url')])

                # yt-dlp output filename may vary depending on metadata; find the downloaded file
                downloaded_files = [f for f in os.listdir(temp_folder) if f.endswith(format)]
                if not downloaded_files:
                    # If no file found, treat as a recoverable error for this entry
                    raise FileNotFoundError(f"{format.upper()} not found in temp folder")

                original_filename_path = os.path.join(temp_folder, downloaded_files[0])
                video_id = entry.get('id')
                title = entry.get('title', 'Unknown')

                quality_str = ""
                if format in ['mp4', 'mkv', 'webm']:
                    quality_str = get_actual_file_quality(original_filename_path)

                # Sanitize title for filesystem, and add numeric prefix to preserve order
                sanitized_title = sanitize_filename(title)
                final_title = os.path.join(folder_name, f"{idx+1} - {sanitized_title}{quality_str}.{format}")

                # Move the file atomically into the destination folder
                os.replace(original_filename_path, final_title)

                # Build/update the titles map
                video_details = {
                    "title": title,
                    "sanitized_title": sanitized_title,
                    "playlist_index": idx+1
                }

                titles_map["files"][video_id] = video_details

                # Save an updated JSON state after each successful entry so downloads are resumable
                json_filename = get_playlist_state_path(playlist_title)
                with open(json_filename, "w", encoding="utf-8") as f:
                    json.dump(titles_map, f, ensure_ascii=False, indent=4)

                print(f"- {sanitized_title} downloaded.")
                 
            except Exception as e:
                # Record the failure for this entry, but continue with the rest
                errors.append((entry.get('title', 'Unknown'), str(e)))
                continue

    # Attempt to remove temporary folder and report errors if unable
    try:
        shutil.rmtree(temp_folder)
    except Exception as e:
        errors.append(("temp cleanup failed", str(e)))

    return errors

def fetch_online_playlist_info(playlist_url: str) -> Optional[dict]:
    """
    Fetches essential playlist data from YouTube in a single call.

    Args:
        playlist_url: The URL of the YouTube playlist.

    Returns:
        A dictionary containing the playlist title and a list of its video entries
        (id, title, index), or None if fetching fails.
    """
    try:
        # Use the lightweight yt_config to fetch only metadata
        with yt_dlp.YoutubeDL(yt_config) as ydl:
            info = ydl.extract_info(playlist_url, download=False)

            # Check if yt-dlp returned valid information
            if not info or 'entries' not in info:
                return None

        # Prepare the data structure to be returned
        playlist_title = info.get('title', 'Unknown Playlist')
        online_videos = []

        # Loop through all entries and extract only the necessary data
        for idx, entry in enumerate(info.get('entries', [])):
            if not entry:
                # Skip corrupted or unavailable entries
                continue
            
            video_info = {
                'id': entry.get('id'),
                'title': entry.get('title', 'Unknown Title'),
                'index': idx + 1  # Playlist index is 1-based
            }
            online_videos.append(video_info)

        return {
            'title': playlist_title,
            'videos': online_videos
        }

    except:
        # Catch any exception from yt-dlp (e.g., network error, invalid URL)
        return None
    
def detect_format(folder_name: str) -> Optional[str]:
    """
    Scans a folder to detect the media file format (extension) of the first found file.

    Args:
        folder_name: The path to the folder to scan.

    Returns:
        The file extension (e.g., "mp3", "m4a") as a string, or None if no
        media files are found.
    """
    # A list of common media extensions to look for.
    # This avoids picking up other files like .txt, .json, .jpg etc.
    supported_formats = {"mp3", "m4a", "flac", "opus", "wav", "mp4", "mkv", "webm"}

    try:
        for filename in os.listdir(folder_name):
            # Check if it's a file and not a directory
            if os.path.isfile(os.path.join(folder_name, filename)):
                # Extract the extension, remove the dot, and convert to lowercase
                extension = os.path.splitext(filename)[1].replace('.', '').lower()
                
                # If the extension is one of our supported media formats, we found it.
                if extension in supported_formats:
                    return extension
    except FileNotFoundError:
        # The folder might not exist, which is a possible scenario
        return None
    
    # If the loop finishes without finding any suitable file
    return None

def cleanup_deleted_videos(online_videos: list, playlist_title: str, folder_name: str) -> list[tuple[str, str]]:
    """
    Compares local state with online and removes obsolete files.

    Args:
        online_videos: The list of video dictionaries from fetch_online_playlist_info.
        playlist_title: The title of the playlist.
        folder_name: The path to the local media folder.
        
    Returns:
        A list of non-critical errors encountered during the cleanup process.
    """
    errors = []
    state_path = get_playlist_state_path(playlist_title)

    try:
        with open(state_path, "r", encoding="utf-8") as f:
            local_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # No state file, nothing to clean up.
        return errors

    online_ids = {video['id'] for video in online_videos}
    local_ids = list(local_data.get("files", {}).keys())
    videos_to_delete_ids = [vid_id for vid_id in local_ids if vid_id not in online_ids]

    if not videos_to_delete_ids:
        return errors

    file_format = detect_format(folder_name)
    if not file_format:
        errors.append(("Cleanup Warning", "Could not detect media format. Skipping cleanup."))
        return errors

    for video_id in videos_to_delete_ids:
        video_info = local_data["files"].get(video_id)
        if not video_info:
            continue

        index = video_info.get("playlist_index")
        sanitized_title = video_info.get("sanitized_title")
        filename_to_delete = f"{index} - {sanitized_title}.{file_format}"
        file_path_to_delete = os.path.join(folder_name, filename_to_delete)

        try:
            if os.path.exists(file_path_to_delete):
                os.remove(file_path_to_delete)

            del local_data["files"][video_id]

            with open(state_path, "w", encoding="utf-8") as f:
                json.dump(local_data, f, ensure_ascii=False, indent=4)

        except OSError as e:
            # We add the error to our list and continue with the next file.
            errors.append(("Deletion Error", f"Could not delete file {filename_to_delete}: {e}"))
            continue
            
    return errors

def reorder_local_videos(online_videos: list, playlist_title: str, folder_name: str) -> list[tuple[str, str]]:
    """
    Reorders local files to match the current online playlist order.

    This function compares the index of local videos (from state.json) with the
    online order. It renames files accordingly and handles a backup-restore
    process to ensure safety during file operations.

    Args:
        online_videos: The list of video dictionaries from fetch_online_playlist_info.
        playlist_title: The title of the playlist.
        folder_name: The path to the local media folder.

    Returns:
        A list of non-critical errors encountered during the reordering process.
    """
    errors = []
    state_path = get_playlist_state_path(playlist_title)

    # --- Step 1: Backup and State Loading ---
    backup_path = None
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            local_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # No state file, nothing to reorder.
        return errors

    # Create a mapping of online IDs to their new index for quick lookup
    youtube_video_map = {video['id']: video['index'] for video in online_videos}
    
    # Identify files that need renaming
    files_to_rename = []
    for video_id, video_info in local_data.get("files", {}).items():
        if video_id in youtube_video_map:
            current_index = video_info.get("playlist_index")
            new_index = youtube_video_map[video_id]
            if current_index != new_index:
                files_to_rename.append({
                    'id': video_id,
                    'old_index': current_index,
                    'new_index': new_index,
                    'sanitized_title': video_info.get("sanitized_title")
                })
    
    if not files_to_rename:
        # Everything is already in order.
        return errors

    # --- Step 2: Critical Phase - Backup and Rename ---
    try:
        # Create backup ONLY if there are files to rename
        backup_path, backup_error = folder_backup(folder_name, playlist_title)
        if backup_error:
            errors.append(("Backup Error", backup_error))
            return errors

        file_format = detect_format(folder_name)
        if not file_format:
            errors.append(("Reorder Warning", "Could not detect media format. Skipping reorder."))
            return errors

        for file in files_to_rename:
            old_filename = f"{file['old_index']} - {file['sanitized_title']}.{file_format}"
            new_filename = f"{file['new_index']} - {file['sanitized_title']}.{file_format}"
            old_filepath = os.path.join(folder_name, old_filename)
            new_filepath = os.path.join(folder_name, new_filename)
            
            if os.path.exists(old_filepath):
                os.rename(old_filepath, new_filepath)
                # Update the index in our local data
                local_data["files"][file['id']]['playlist_index'] = file['new_index']
                # Atomically save the state file
                with open(state_path, "w", encoding="utf-8") as f:
                    json.dump(local_data, f, ensure_ascii=False, indent=4)
            else:
                errors.append(("File Not Found", f"Could not find file to rename: {old_filename}"))

    except Exception as e:
        # --- Step 3: Rollback on Critical Failure ---
        errors.append(("CRITICAL REORDER FAILED", f"An error occurred: {e}. Attempting to restore from backup."))
        if backup_path and os.path.isdir(backup_path):
            try:
                # Simple restore: remove the broken folder and replace it with the backup
                shutil.rmtree(folder_name)
                shutil.copytree(backup_path, folder_name)
                errors.append(("Restore Success", "Successfully restored folder from backup."))
            except Exception as restore_e:
                errors.append(("CRITICAL RESTORE FAILED", f"Could not restore from backup: {restore_e}"))
        raise  # Re-raise the exception to stop the update process in main

    finally:
        # --- Step 4: Cleanup ---
        # Always remove the backup folder when done
        if backup_path and os.path.isdir(backup_path):
            try:
                shutil.rmtree(backup_path)
            except Exception as clean_e:
                errors.append(("Backup Cleanup Failed", str(clean_e)))

    return errors

def download_new_videos(online_videos: list, playlist_title: str, folder_name: str, format: str) -> list[tuple[str, str]]:
    """
    Downloads new videos that are in the online playlist but not locally.

    This function identifies missing videos by comparing the online playlist
    with the local state file. It downloads each new video and adds its entry

    to the state file upon success.

    Args:
        online_videos: The list of video dictionaries from fetch_online_playlist_info.
        playlist_title: The title of the playlist.
        folder_name: The path to the local media folder.
        file_format: The desired output format (e.g., "mp3").

    Returns:
        A list of non-critical errors encountered during the download process.
    """
    errors = []
    state_path = get_playlist_state_path(playlist_title)

    # Step 1: Load local state
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            local_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If the state file doesn't exist, we start with an empty dictionary.
        local_data = {}

    # Step 2: Identify missing videos
    local_ids = set(local_data.get("files", {}).keys())
    new_videos = [video for video in online_videos if video['id'] not in local_ids]

    if not new_videos:
        return errors

    # Step 3: Set up for download
    quality = local_data.get("quality", None)

    temp_folder = get_temp_dir(playlist_title)
    ydl_opts = make_config(temp_folder, format, quality)
    
    # Step 4: Perform atomic download operations
    for video in new_videos:
        video_url = VIDEO_URL_TYPE1 + video['id']
        video_title = video['title']
        
        try:
            # a. Download the video to the temp folder
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            # Find the downloaded file in the temp folder
            downloaded_files = [f for f in os.listdir(temp_folder) if f.endswith(format)]
            if not downloaded_files:
                raise FileNotFoundError(f"Downloaded file with format .{format} not found in temp folder.")

            original_filename_path = os.path.join(temp_folder, downloaded_files[0])
            
            # b. Move the file to the final destination
            sanitized_title = sanitize_filename(video_title)
            final_filename = f"{video['index']} - {sanitized_title}.{format}"
            final_file_path = os.path.join(folder_name, final_filename)
            
            shutil.move(original_filename_path, final_file_path)

            # c. Add the new video to our local data
            local_data["files"][video['id']] = {
                "title": video_title,
                "sanitized_title": sanitized_title,
                "playlist_index": video['index']
            }

            # d. Save the updated state file
            with open(state_path, "w", encoding="utf-8") as f:
                json.dump(local_data, f, ensure_ascii=False, indent=4)

            print(f"- {sanitized_title} downloaded")

        except Exception as e:
            errors.append(("Download Error", f"Failed to download '{video_title}': {e}"))
            # Clean up the temp folder to avoid issues with the next video
            for f in os.listdir(temp_folder):
                os.remove(os.path.join(temp_folder, f))
            continue

    # Step 5: Final cleanup
    try:
        shutil.rmtree(temp_folder)
    except Exception as e:
        errors.append(("Temp Cleanup Failed", str(e)))

    return errors

def folder_backup(folder_name: str, playlist_title: str) -> tuple[Optional[str], Optional[str]]:
    playlist_data_dir = get_playlist_data_dir(playlist_title)
    
    backup_path = os.path.join(playlist_data_dir, "backup")

    if os.path.isdir(backup_path):
        try:
            shutil.rmtree(backup_path)
        except Exception as e:
            return None, f"Could not remove old backup folder: {e}"
        
    try:
        shutil.copytree(folder_name, backup_path)
        return backup_path, None
    except Exception as e:
        return None, f"Failed to create backup for '{folder_name}': {e}"
    
def delete_app_data() -> tuple[bool, str]:
    """
    Finds and deletes the entire application data directory.

    This is a destructive operation and should be used with caution.

    Returns:
        A tuple containing a success boolean and a message string.
    """
    try:
        data_dir = get_app_data_dir()
        
        # Check if the directory actually exists
        if not os.path.isdir(data_dir):
            return (True, "Application data directory does not exist. Nothing to delete.")
        
        # Delete the entire directory tree
        shutil.rmtree(data_dir)
        
        return (True, f"Successfully deleted application data from: {data_dir}")

    except Exception as e:
        # Catch potential permission errors or other OS-level issues
        return (False, f"An error occurred while deleting application data: {e}")
    