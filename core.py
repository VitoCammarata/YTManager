import os, sys, shutil, json
import yt_dlp
from typing import Optional, Any
from pathvalidate import sanitize_filename
import appdirs

# --- Constants and Configurations ---

# yt-dlp configuration for fetching playlist metadata quickly
yt_metadata_config = {
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
        # Use the lightweight yt_metadata_config to fetch only metadata (no downloads)
        with yt_dlp.YoutubeDL(yt_metadata_config) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            return info if info else {"entries": []}
    except Exception as e:
        print(f"ERROR: Could not fetch playlist info. Reason: {e}")
        return {"entries": []}
    
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

def get_format_options(format_choice: str) -> dict:
    """
    Build yt-dlp option fragments for a given output format.
    ...
    """
    format_choice = format_choice.lower().strip()

    if format_choice == 'mp3':
        return {
            "format": "bestaudio/best",
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "0"},
                {"key": "EmbedThumbnail"},
                {"key": "FFmpegMetadata"},
            ]
        }

    elif format_choice == 'm4a':
        return {
            "format": "bestaudio/best",
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": "m4a", "preferredquality": "5"},
                {"key": "EmbedThumbnail"},
                {"key": "FFmpegMetadata"}, 
            ]
        }

    elif format_choice == 'flac':
        return {
            "format": "bestaudio/best",
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": "flac"},
                {"key": "EmbedThumbnail"},
                {"key": "FFmpegMetadata"}, 
            ]
        }

    elif format_choice == 'opus':
        return {
            "format": "bestaudio/best",
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": "opus"},
                {"key": "EmbedThumbnail"},
                {"key": "FFmpegMetadata"}, 
            ]
        }

    elif format_choice == 'wav':
        return {
            "format": "bestaudio/best",
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": "wav"},
                {"key": "FFmpegMetadata"},
            ]
        }

    # Video formats are already correct as they included FFmpegMetadata
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
                {"key": "FFmpegMetadata"},
            ]
        }
        
    else:
        print(f"Format '{format_choice}' not recognized. Using 'mp3' as default.")
        return get_format_options('mp3')

def make_config(path: str, format: str = "mp3") -> dict:
    """
    Creates the full yt-dlp configuration dictionary for a download.
    """
    format_opts = get_format_options(format)

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

def download_video(video_url: list[str], format: str = "mp3") -> list[tuple[str, str]]:
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
    directory = "." 
    errors = []

    # Build yt-dlp options using the provided format and the current directory
    ydl_opts = make_config(directory, format=format)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for url in video_url:
            # Default title used in case metadata extraction fails
            video_title = f"Video Sconosciuto ({url})"
            try:
                # Try to obtain metadata first to have a readable error context
                info = ydl.extract_info(url, download=False)
                if info:
                    video_title = info.get('title', video_title)

                # Perform the actual download; any postprocessors run automatically
                ydl.download([url])

            # Collect errors per-video without stopping the whole batch
            except Exception as e:
                errors.append((video_title, str(e)))
    
    return errors

def download_playlist(playlist_url: str, folder_name: str, playlist_title: str, format: str = "mp3") -> list[tuple[str, str]]:
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
    tmp_folder = get_temp_dir(playlist_title)

    titles_map = {}
    errors = []

    # Get playlist entries (lightweight)
    info = basic_info(playlist_url)

    # Iterate entries in playlist order and download one by one
    for idx, entry in enumerate(info.get('entries', [])): 
        with yt_dlp.YoutubeDL(make_config(tmp_folder, format=format)) as ydl:
            try:
                # Download the single entry into the temporary folder
                ydl.download([entry.get('url')])

                # yt-dlp output filename may vary depending on metadata; find the downloaded file
                downloaded_files = [f for f in os.listdir(tmp_folder) if f.endswith(format)]
                if not downloaded_files:
                    # If no file found, treat as a recoverable error for this entry
                    raise FileNotFoundError(f"{format.upper()} not found in temp folder")

                original_filename = os.path.join(tmp_folder, downloaded_files[0])
                video_id = entry.get('id')
                title = entry.get('title', 'Unknown')

                # Sanitize title for filesystem, and add numeric prefix to preserve order
                sanitized_title = sanitize_filename(title)
                final_title = os.path.join(folder_name, f"{idx+1} - {sanitized_title}.{format}")

                # Move the file atomically into the destination folder
                os.replace(original_filename, final_title)

                # Build/update the titles map
                titles_map[video_id] = {
                    "title": title,
                    "sanitized_title": sanitized_title,
                    "playlist_index": idx+1
                }

                # Save an updated JSON state after each successful entry so downloads are resumable
                json_filename = get_playlist_state_path(playlist_title)
                with open(json_filename, "w", encoding="utf-8") as f:
                    json.dump(titles_map, f, ensure_ascii=False, indent=4)
                 
            except Exception as e:
                # Record the failure for this entry, but continue with the rest
                errors.append((entry.get('title', 'Unknown'), str(e)))
                continue

    # Attempt to remove temporary folder and report errors if unable
    try:
        shutil.rmtree(tmp_folder)
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
        # Use the lightweight config1 to fetch only metadata
        with yt_dlp.YoutubeDL(yt_metadata_config) as ydl:
            info = ydl.extract_info(playlist_url, download=False)

            # Check if yt-dlp returned valid information
            if not info or 'entries' not in info:
                print(f"ERROR: Could not retrieve valid playlist info for {playlist_url}")
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

    except Exception as e:
        # Catch any exception from yt-dlp (e.g., network error, invalid URL)
        print(f"ERROR: An exception occurred while fetching playlist info: {e}")
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
    local_ids = list(local_data.keys())
    videos_to_delete_ids = [vid_id for vid_id in local_ids if vid_id not in online_ids]

    if not videos_to_delete_ids:
        return errors

    media_format = detect_format(folder_name)
    if not media_format:
        errors.append(("Cleanup Warning", "Could not detect media format. Skipping cleanup."))
        return errors

    for video_id in videos_to_delete_ids:
        video_info = local_data.get(video_id)
        if not video_info:
            continue

        index = video_info.get("playlist_index")
        sanitized_title = video_info.get("sanitized_title")
        filename_to_delete = f"{index} - {sanitized_title}.{media_format}"
        file_path = os.path.join(folder_name, filename_to_delete)

        try:
            if os.path.exists(file_path):
                os.remove(file_path)

            del local_data[video_id]

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
    online_order_map = {video['id']: video['index'] for video in online_videos}
    
    # Identify files that need renaming
    files_to_rename = []
    for video_id, video_info in local_data.items():
        if video_id in online_order_map:
            current_index = video_info.get("playlist_index")
            new_index = online_order_map[video_id]
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

        media_format = detect_format(folder_name)
        if not media_format:
            errors.append(("Reorder Warning", "Could not detect media format. Skipping reorder."))
            return errors

        for task in files_to_rename:
            old_filename = f"{task['old_index']} - {task['sanitized_title']}.{media_format}"
            new_filename = f"{task['new_index']} - {task['sanitized_title']}.{media_format}"
            old_filepath = os.path.join(folder_name, old_filename)
            new_filepath = os.path.join(folder_name, new_filename)
            
            if os.path.exists(old_filepath):
                os.rename(old_filepath, new_filepath)
                # Update the index in our local data
                local_data[task['id']]['playlist_index'] = task['new_index']
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

def download_new_videos(online_videos: list, playlist_title: str, folder_name: str, media_format: str) -> list[tuple[str, str]]:
    """
    Downloads new videos that are in the online playlist but not locally.

    This function identifies missing videos by comparing the online playlist
    with the local state file. It downloads each new video and adds its entry

    to the state file upon success.

    Args:
        online_videos: The list of video dictionaries from fetch_online_playlist_info.
        playlist_title: The title of the playlist.
        folder_name: The path to the local media folder.
        media_format: The desired output format (e.g., "mp3").

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
    local_ids = set(local_data.keys())
    new_videos = [video for video in online_videos if video['id'] not in local_ids]

    if not new_videos:
        return errors

    # Step 3: Set up for download
    tmp_folder = get_temp_dir(playlist_title)
    ydl_opts = make_config(tmp_folder, format=media_format)
    
    # Step 4: Perform atomic download operations
    for video in new_videos:
        video_url = VIDEO_URL_TYPE1 + video['id']
        video_title = video['title']
        
        try:
            # a. Download the video to the temp folder
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            # Find the downloaded file in the temp folder
            downloaded_files = [f for f in os.listdir(tmp_folder) if f.endswith(media_format)]
            if not downloaded_files:
                raise FileNotFoundError(f"Downloaded file with format .{media_format} not found in temp folder.")

            original_filepath = os.path.join(tmp_folder, downloaded_files[0])
            
            # b. Move the file to the final destination
            sanitized_title = sanitize_filename(video_title)
            final_filename = f"{video['index']} - {sanitized_title}.{media_format}"
            final_filepath = os.path.join(folder_name, final_filename)
            
            shutil.move(original_filepath, final_filepath)

            # c. Add the new video to our local data
            local_data[video['id']] = {
                "title": video_title,
                "sanitized_title": sanitized_title,
                "playlist_index": video['index']
            }

            # d. Save the updated state file
            with open(state_path, "w", encoding="utf-8") as f:
                json.dump(local_data, f, ensure_ascii=False, indent=4)

        except Exception as e:
            errors.append(("Download Error", f"Failed to download '{video_title}': {e}"))
            # Clean up the temp folder to avoid issues with the next video
            for f in os.listdir(tmp_folder):
                os.remove(os.path.join(tmp_folder, f))
            continue

    # Step 5: Final cleanup
    try:
        shutil.rmtree(tmp_folder)
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
    