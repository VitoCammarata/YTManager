"""
This script allows downloading and synchronizing YouTube playlists as local MP3 files.

It provides two main functionalities:
1.  Download: Fetches an entire playlist, converts videos to MP3, and adds
    ID3 tags. (Resilient version)
2.  Update: Syncs a local folder with its corresponding YouTube playlist,
    handling new videos, deleted videos, and reordering. (Original version)

A hidden JSON file is used in each playlist folder to maintain state and
track for the correct order of the tracks.
"""
import os, re, sys
import shutil
import json
import yt_dlp
from typing import Optional, Any
from time import sleep
import core

# --- Constants and Configurations ---

URL_TYPE = "https://www.youtube.com/playlist?list="

# yt-dlp configuration for fetching playlist metadata quickly
config1 = {
    "extract_flat": True,
    "quiet": True,
    "noplaylistunavailablevideos": True
}

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

def make_config(tmp_folder: str) -> dict:
    """
    Creates the main yt-dlp configuration for downloading and processing a single video.

    Args:
        tmp_folder: The temporary directory where the raw download will be stored.

    Returns:
        A dictionary containing the complete configuration for yt-dlp.
    """
    config = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(tmp_folder, "%(title)s.%(ext)s"),
        "add_metadata": True,
        "writethumbnail": True,
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "0"},
            {"key": "EmbedThumbnail"},
        ],
        "quiet": True,
        "ignoreerrors": True
    }

    # If running as a bundled app, tell yt-dlp where to find ffmpeg.
    ffmpeg_location = get_ffmpeg_path()
    if ffmpeg_location:
        config['ffmpeg_location'] = ffmpeg_location

    return config

def make_path(folder_name: str) -> str:
    """
    Constructs the path for the hidden JSON state file for a given playlist folder.

    Args:
        folder_name: The name of the playlist's main folder.

    Returns:
        The full path to the JSON file (e.g., "My Playlist/.My Playlist.json").
    """
    return os.path.join(folder_name, f".{os.path.basename(folder_name)}.json")

def urls_aquisition(user_choice: str) -> list[str]:
    """
    Interactively prompts the user to enter one or more YouTube playlist URLs,
    validating and cleaning them.

    Args:
        user_choice: The main menu choice ("1" or "2") to customize prompts.

    Returns:
        A list of cleaned, standardized YouTube playlist URLs.
    """
    def check_url(user_input: str):
        if user_input not in local_playlist_url:
            local_playlist_url.append(user_input)
        else:
            print("\nThis URL has already been added. Press Enter to continue...")
            input()
        os.system("clear")

    local_playlist_url = []
    key_words = ["download", "Download"] if user_choice == "1" else ["update", "Update"]

    while True:
        columns = shutil.get_terminal_size().columns
        print("\n" + "### YOUTUBE PLAYLIST DOWNLOADER AND UPDATER ###".center(columns) + "\n")
        print(f"Insert your playlist URLs: (Insert '{key_words[0]}' to start the {key_words[0]})\n")

        if len(local_playlist_url):
            for j, url in enumerate(local_playlist_url):
                print(f"URL {j+1}: {url}")

        user_input = input(f"Input: ").strip()
        if user_input.lower() == f"{key_words[0]}":
            print(f"\n{key_words[1]}...")
            return local_playlist_url
        # Extracts the playlist ID and rebuilds a clean URL to standardize it.
        elif "https://" in user_input and "list=" in user_input:
            check_url(URL_TYPE + user_input.split("list=")[-1].split("&")[0])
        else:
            print("\nInvalid input. Press Enter to continue...")
            input()
            os.system("clear")

def download_playlist(playlist_url: str, folder_name: str) -> list[tuple[str, str]]:
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
        with yt_dlp.YoutubeDL(make_config(tmp_folder)) as ydl:
            try:
                ydl.download([entry.get('url')])

                downloaded_files = [f for f in os.listdir(tmp_folder) if f.endswith('.mp3')]
                if not downloaded_files: raise FileNotFoundError("MP3 not found in temp folder")

                original_filename = os.path.join(tmp_folder, downloaded_files[0])
                title = entry.get('title', 'Unknown')
                sanitized = core.sanitize_title(title)
                numbered_title = f"{idx+1} - {sanitized}"
                final_filename = os.path.join(folder_name, f"{numbered_title}.mp3")
                os.replace(original_filename, final_filename)

                prev_title = ordered_titles[-1] if ordered_titles else None
                titles_map[title] = [
                    sanitized,
                    core.sanitize_title(prev_title) if prev_title else None,
                    None
                ]
                ordered_titles.append(title)

                # Atomically save the updated state to the JSON file after each success.
                json_filename = make_path(folder_name)
                with open(json_filename, "w", encoding="utf-8") as f:
                    temp_map = titles_map.copy()
                    for i, t in enumerate(ordered_titles[:-1]):
                        next_title = ordered_titles[i+1]
                        temp_map[t][2] = core.sanitize_title(next_title) if next_title else None
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
                sanitized = core.sanitize_title(original_title)
                video_url = entry.get('url')
                ordered_titles.append(original_title)
                if sanitized not in [core.sanitize_title(t) for t in titles_map.keys()]:
                    new_videos[original_title] = video_url
        
        # Rebuild the entire map from scratch to ensure the order is correct.
        for i, title in enumerate(ordered_titles):
            sanitized = core.sanitize_title(title)
            prev_title = core.sanitize_title(ordered_titles[i-1]) if i > 0 else None
            next_title = core.sanitize_title(ordered_titles[i+1]) if i < len(ordered_titles)-1 else None
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
    # --- Phase 1: Download new videos (if any) ---
    if new_videos:
        tmp_folder = os.path.join(folder_name, ".tmp")
        os.makedirs(tmp_folder, exist_ok=True)
        
        ydl_opts = make_config(tmp_folder)

        for title, url in new_videos.items():
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.extract_info(url, download=True)
                    downloaded_files = [f for f in os.listdir(tmp_folder) if f.endswith('.mp3')]
                    if not downloaded_files: raise FileNotFoundError("MP3 not found")

                    original_filename = os.path.join(tmp_folder, downloaded_files[0])
                    sanitized = titles_map[title][0]
                    temp_filename = os.path.join(folder_name, f"{sanitized}.mp3")
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
                current_files = [f for f in os.listdir(folder_name) if f.endswith('.mp3') and sanitized in f]
                if current_files:
                    old_name = os.path.join(folder_name, current_files[0])
                    new_name = os.path.join(folder_name, f"{idx+1} - {sanitized}.mp3")
                    if old_name != new_name:
                        os.replace(old_name, new_name)
            except Exception as e:
                errors.append((f"Error renaming '{original_title}'", str(e)))

    # --- Phase 3: Clean up obsolete files ---
    final_sanitized_titles = {v[0] for v in titles_map.values()}
    for f in os.listdir(folder_name):
        if f.endswith(".mp3"):
            file_sanitized_title = core.sanitize_title(f.split(' - ', 1)[-1].rsplit('.mp3', 1)[0])
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


if __name__ == "__main__":
    os.system("clear")
        
    while True:
        columns = shutil.get_terminal_size().columns
        print("### YOUTUBE PLAYLIST DOWNLOADER AND UPDATER ###".center(columns) + "\n")
        print("1 - Download\n2 - Update\n")

        user_choice = input("Select an option: ")
        if user_choice not in ["1", "2"]:
            print("\nInvalid option. Please select 1 or 2. Press 'Enter' to continue...")
            input()
            os.system("clear")
            continue
        
        os.system("clear")
        
        # --- DOWNLOAD LOGIC ---
        if user_choice == "1":
            playlist_url = urls_aquisition(user_choice)
            errors = []
            for url in playlist_url:
                with yt_dlp.YoutubeDL(config1) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info:
                        folder_name = core.sanitize_folder_name(info['title'])

                if os.path.isdir(folder_name):
                    print(f"\nThe folder '{folder_name}' already exists. Use the Update option to update it.", end="\n")
                    sleep(1.5)
                    continue

                os.makedirs(folder_name, exist_ok=True)
                errors.extend(download_playlist(url, folder_name))

            if errors:
                print("\nSome errors occurred during the download:")
                for error in errors:
                    print(f" - {error}")
            else:
                print("\nDownload completed successfully for all playlists!")
            break

        # --- UPDATE LOGIC ---
        elif user_choice == "2":
            playlist_url = urls_aquisition(user_choice)
            errors = []

            for url in playlist_url:
                with yt_dlp.YoutubeDL(config1) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info:
                        folder_name = core.sanitize_folder_name(info.get("title", "Unknown Playlist"))

                if not os.path.isdir(folder_name):
                    print(f"\nFolder '{folder_name}' not found. Please use the Download option first.")
                    sleep(1.5)
                    continue
                
                backup_path = None 
                try:
                    # Clean up leftovers before backup for a clean state.
                    tmp_folder_path = os.path.join(folder_name, ".tmp")
                    if os.path.isdir(tmp_folder_path):
                        shutil.rmtree(tmp_folder_path)

                    backup_path, backup_error = folder_backup(folder_name)
                    if backup_error:
                        errors.append(("Backup Failed", backup_error))
                        continue
                    
                    # Execute the update process.
                    new_videos, titles_map, get_errors = get_missing_videos(url, folder_name)
                    errors.extend(get_errors)
                    
                    update_errors = update_playlist(new_videos, titles_map, folder_name)
                    errors.extend(update_errors)
                    
                    # If any non-critical errors were reported, trigger a rollback to be safe.
                    if get_errors or update_errors:
                        raise Exception("Update process reported non-critical errors, initiating rollback.")

                except Exception as e:
                    # This is the rollback logic in case of any failure.
                    errors.append(("UPDATE FAILED", f"A critical error occurred: {e}"))
                    
                    if backup_path and os.path.isdir(backup_path):
                        os.system("clear")
                        print("Update failed. Restoring from backup...")
                        sleep(2)
                        try:
                            temp_backup_path = f".{folder_name}.tmp.bak"
                            if os.path.exists(temp_backup_path):
                                shutil.rmtree(temp_backup_path)
                            shutil.move(backup_path, temp_backup_path)

                            shutil.rmtree(folder_name)
                            os.rename(temp_backup_path, folder_name)
                            
                            print("Restore successful.")
                        except Exception as restore_e:
                            errors.append(("CRITICAL RESTORE FAILED", str(restore_e)))
                            print(f"!!! CRITICAL ERROR: Could not restore from backup for '{folder_name}'. Please check the folder manually. !!!")
                    else:
                        print("Update failed, and no backup was available to restore from.")
                
                finally:
                    # Clean up the backup folder if the update was successful.
                    if backup_path and os.path.isdir(backup_path):
                        try:
                            shutil.rmtree(backup_path)
                        except Exception as clean_e:
                            errors.append(("Backup Cleanup Failed", str(clean_e)))

            if errors:
                print("\nSome errors occurred during the update:")
                for error_type, error_msg in errors:
                    print(f" - [{error_type}] {error_msg}")
            else:
                print("\nUpdate completed successfully for all playlists!")
            
            break
