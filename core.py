import re, os, sys, shutil, json
import yt_dlp
from typing import Optional, Any

# --- Constants and Configurations ---

# yt-dlp configuration for fetching playlist metadata quickly
config1 = {
    "extract_flat": True,
    "quiet": True,
    "noplaylistunavailablevideos": True
}
PLAYLIST_URL_TYPE = "https://www.youtube.com/playlist?list="

VIDEO_URL_TYPE1 = "https://www.youtube.com/watch?v="
VIDEO_URL_TYPE2 = "https://youtu.be/"

def sanitize_folder_name(name: str) -> str:
    """
    Make a string safe to use as a folder name across filesystems.

    Args:
        name: Original string (typically a playlist title).

    Returns:
        A sanitized string suitable for use as a directory name.
    """
    name = re.sub(r'[\\/*?:"<>|]', "_", name)       # Replace common illegal filename characters with underscore
    name = re.sub(r'[\x00-\x1f\x7f]', "", name)     # Remove control characters
    name = re.sub(r'\s+', " ", name).strip()        # Normalize whitespace and trim edges
    name = name.strip('. ')                         # Avoid trailing dots or spaces which are problematic on some systems    
    return name

def sanitize_title(title: str) -> str:
    """
    Make a string safe to use as a filename.

    Args:
        title: Original string (typically a video title).

    Returns:
        A sanitized string suitable for use as a file name.
    """
    title = re.sub(r"[\'\*\?\"<>]", "", title)              # Remove problematic characters and normalize bracket
    title = title.replace("[", "(").replace("]", ")")
    title = title.replace("{", "(").replace("}", ")")
    title = re.sub(r"[|\\\/]", "-", title)                  # Replace path separators and pipes with a dash
    title = re.sub(r"^[\'\*\?\"<>]+", "", title)            # Trim leading/trailing punctuation introduced by some titles
    title = re.sub(r"[\'\*\?\"<>]+$", "", title)
    return title

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
        # Use the lightweight config1 to fetch only metadata (no downloads)
        with yt_dlp.YoutubeDL(config1) as ydl:
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
        
        ffmpeg_executable = os.path.join(base_path, 'dependencies', "ffmpeg.exe" if os.name == "nt" else "ffmpeg")
        
        if os.path.exists(ffmpeg_executable):
            return ffmpeg_executable
    
    return None

def get_format_options(format_choice: str) -> dict:
    """
    Build yt-dlp option fragments for a given output format.

    Args:
        format_choice: Desired output format (mp3, m4a, flac, opus, wav, mp4, mkv, webm).

    Returns:
        A dict with yt-dlp configuration options for the selected format.
    """
    format_choice = format_choice.lower().strip()

    # Audio extraction options: choose codec and thumbnail embedding where appropriate
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
            ]
        }

    # Video formats: prefer container/codec combinations for predictable output
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
        # Unknown format: fallback to mp3 options and inform the user
        print(f"Format '{format_choice}' not recognized. Using 'mp3' as default.")
        return get_format_options('mp3')

def make_config(path: str, format: str = "mp3") -> dict:

    format_opts = get_format_options(format)

    base_config = {
        # Use title-based template; extension will be chosen by yt-dlp/ffmpeg
        "outtmpl": os.path.join(path, "%(title)s.%(ext)s"),
        "add_metadata": True,
        "writethumbnail": True,
        "quiet": True,
        "ignoreerrors": True
    }
   
    final_config = {**base_config, **format_opts}

    # If the bundle contains a private ffmpeg, point yt-dlp to it
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

def download_playlist(playlist_url: str, folder_name: str, format: str = "mp3") -> list[tuple[str, str]]:
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
    tmp_folder = os.path.join(folder_name, ".tmp")
    os.makedirs(tmp_folder, exist_ok=True)
    if os.name == "nt":
        os.system(f'attrib +h "{tmp_folder}"')

    titles_map = {}
    ordered_titles = []
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
                title = entry.get('title', 'Unknown')

                # Sanitize title for filesystem, and add numeric prefix to preserve order
                sanitized = sanitize_title(title)
                numbered_title = f"{idx+1} - {sanitized}"
                final_filename = os.path.join(folder_name, f"{numbered_title}.{format}")

                # Move the file atomically into the destination folder
                os.replace(original_filename, final_filename)

                # Build/update the titles map (prev, next will be calculated when saving)
                prev_title = ordered_titles[-1] if ordered_titles else None
                titles_map[title] = [
                    sanitized,
                    sanitize_title(prev_title) if prev_title else None,
                    None
                ]
                ordered_titles.append(title)

                # Save an updated JSON state after each successful entry so downloads are resumable
                json_filename = make_path(folder_name)
                with open(json_filename, "w", encoding="utf-8") as f:
                    # Populate 'next' links for the serialized map before writing
                    temp_map = titles_map.copy()
                    for i, t in enumerate(ordered_titles[:-1]):
                        next_title = ordered_titles[i+1]
                        temp_map[t][2] = sanitize_title(next_title) if next_title else None
                    json.dump(temp_map, f, ensure_ascii=False, indent=4)
                 
            except Exception as e:
                # Record the failure for this entry, but continue with the rest
                errors.append((entry.get('title', 'Unknown'), str(e)))
                continue

    if os.name == "nt":
        os.system(f'attrib +h "{json_filename}"')

    # Attempt to remove temporary folder and report errors if unable
    try:
        shutil.rmtree(tmp_folder)
    except Exception as e:
        errors.append((".tmp cleanup failed", str(e)))

    return errors

def get_missing_videos(playlist_url: str, folder_name: str) -> tuple[dict, dict, list[str]]:
    """
    Compare local state with the online playlist and prepare an update plan.

    The function identifies new videos to download, rebuilds a fully ordered
    titles map, and writes the updated map to the JSON state file.

    Args:
        playlist_url: YouTube playlist URL.
        folder_name: Local playlist folder path.

    Returns:
        A tuple (new_videos, new_titles_map, errors) where:
            - new_videos: dict {original_title: url} for items missing locally
            - new_titles_map: complete ordered map {title: [sanitized, prev, next]}
            - errors: list of error tuples
    """
    errors = []
    new_videos = {}
    new_titles_map = {}

    try:
        json_filename = make_path(folder_name)
        if os.name == "nt":
            os.system(f'attrib -h "{json_filename}"')
        try:
            if os.path.exists(json_filename):
                # Load existing JSON state to know which videos are already present
                with open(json_filename, "r", encoding="utf-8") as f:
                    titles_map = json.load(f)
            else:
                # No existing state: start from empty map
                titles_map = {}
        except Exception as e:
            # If JSON is corrupt/unreadable, continue with empty map but log the error
            titles_map = {}
            errors.append(("JSON Error", f"Error loading state file: {e}"))

        # Use config1 (lightweight) to fetch the playlist listing
        with yt_dlp.YoutubeDL(config1) as ydl:
            info = ydl.extract_info(playlist_url, download=False)

        # Identify videos that are in the online playlist but not in our local state.
        ordered_titles = []
        if info and info.get('entries'):
            for entry in info.get('entries', []):
                original_title = entry.get('title', 'Unknown')
                sanitized = sanitize_title(original_title)
                video_url = entry.get('url')
                ordered_titles.append(original_title)
                # Compare sanitized names to detect missing items regardless of numbering
                if sanitized not in [sanitize_title(t) for t in titles_map.keys()]:
                    new_videos[original_title] = video_url
        
        # Rebuild the entire map from scratch to ensure the order is correct.
        for i, title in enumerate(ordered_titles):
            sanitized = sanitize_title(title)
            prev_title = sanitize_title(ordered_titles[i-1]) if i > 0 else None
            next_title = sanitize_title(ordered_titles[i+1]) if i < len(ordered_titles)-1 else None
            new_titles_map[title] = [sanitized, prev_title, next_title]

        # Overwrite the old JSON with the new, perfectly ordered map for future updates
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(new_titles_map, f, ensure_ascii=False, indent=4)

        if os.name == "nt":
            os.system(f'attrib +h "{json_filename}"')

    except Exception as e:
        errors.append(("Sync Planning", f"General error in get_missing_videos: {e}"))

    return new_videos, new_titles_map, errors

def update_playlist(new_videos: dict[str, str], titles_map: dict[str, list[Optional[str]]], folder_name: str) -> list[str]:
    """
    Apply the update plan: download missing files, rename files to match the
    new order, and remove obsolete files.

    Args:
        new_videos: Mapping of new titles to their URLs.
        titles_map: Final ordered map {title: [sanitized, prev, next]}.
        folder_name: Target folder to update.

    Returns:
        A list of errors encountered during the update.
    """
    errors = []

    # --- Determine media file format by inspecting a file in the folder ---
    for f in os.listdir(folder_name):
        if os.path.isfile(os.path.join(folder_name, f)):
            format = os.path.splitext(f)[1].replace('.', '')

            # Skip JSON files or other metadata files
            if format.endswith("json"):
                continue
            else:
                # Found a candidate media file; break and use its extension as format
                break

    # If no media file format was detected, abort with an error
    if not format:
        errors.append(f"No media files found in folder '{folder_name}'. Unable to perform update.")
        return errors


    # --- Phase 1: Download new videos (if any) into a temp folder and move them in place ---
    if new_videos:
        tmp_folder = os.path.join(folder_name, ".tmp")
        os.makedirs(tmp_folder, exist_ok=True)
        if os.name == "nt":
            os.system(f'attrib +h "{tmp_folder}"')
        
        ydl_opts = make_config(tmp_folder, format)

        for title, url in new_videos.items():
            try:
                # Download each missing video into the tmp folder
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.extract_info(url, download=True)
                    downloaded_files = [f for f in os.listdir(tmp_folder) if f.endswith(format)]
                    if not downloaded_files:
                        # If expected file not found, record an error for this title
                        raise FileNotFoundError(f"{format.upper()} not found")

                    original_filename = os.path.join(tmp_folder, downloaded_files[0])
                    sanitized = titles_map[title][0]
                    temp_filename = os.path.join(folder_name, f"{sanitized}.{format}")

                    # Move downloaded file into the playlist folder (un-numbered yet)
                    os.replace(original_filename, temp_filename)
            except Exception as e:
                # Collect per-title download errors but proceed with other tasks
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
                # Find any existing file that matches the sanitized title (numbered or not)
                current_files = [f for f in os.listdir(folder_name) if f.endswith(f'.{format}') and sanitized in f]
                if current_files:
                    old_name = os.path.join(folder_name, current_files[0])
                    new_name = os.path.join(folder_name, f"{idx+1} - {sanitized}.{format}")
                    # Rename only when the target name differs to avoid unnecessary operations
                    if old_name != new_name:
                        os.replace(old_name, new_name)
            except Exception as e:
                errors.append((f"Error renaming '{original_title}'", str(e)))

    # --- Phase 3: Clean up obsolete files not present in the final map ---
    final_sanitized_titles = {v[0] for v in titles_map.values()}
    for f in os.listdir(folder_name):
        if f.endswith(f".{format}"):
            # Extract sanitized title portion after any numeric prefix "N - "
            file_sanitized_title = sanitize_title(f.split(' - ', 1)[-1].rsplit(f'.{format}', 1)[0])
            if file_sanitized_title not in final_sanitized_titles:
                try:
                    os.remove(os.path.join(folder_name, f))
                except Exception as e:
                    errors.append((f"Error deleting '{f}'", str(e)))
    return errors

def folder_backup(folder_name: str) -> tuple[Optional[str], Optional[str]]:
    """
    Create a backup copy of the specified folder as a subfolder named '.bak'.

    The backup is used to restore the folder in case an update operation fails.

    Args:
        folder_name: Path of the folder to back up.

    Returns:
        (backup_folder_path, error_message). On success error_message is None.
    """
    # Note: A sibling backup folder is safer and makes restore logic simpler.
    backup_folder = os.path.join(folder_name, ".bak")
    
    # Remove any existing backup to ensure we create a fresh snapshot
    if os.path.isdir(backup_folder):
        try:
            shutil.rmtree(backup_folder)
        except Exception as e:
            return None, f"Could not remove old backup folder: {e}"

    try:
        # Copy the folder tree to the backup location (excluding .bak itself)
        shutil.copytree(folder_name, backup_folder, ignore=shutil.ignore_patterns(".bak"))
        if os.name == "nt":
            os.system(f'attrib +h "{backup_folder}"')
        return backup_folder, None
    except Exception as e:
        return None, f"Failed to create backup for '{folder_name}': {e}"
    