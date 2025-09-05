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
import os
import shutil
import yt_dlp
from time import sleep
import core
from core import config1
from core import PLAYLIST_URL_TYPE, VIDEO_URL_TYPE1, VIDEO_URL_TYPE2

def ask_for_format() -> str:
    """
    Prompt the user to choose a download format.

    Returns:
        The chosen format as a lowercase string (e.g. "mp3", "m4a", "mp4").

    Behavior:
        Clears the terminal, shows available formats, validates input and
        repeats until a supported format is entered.
    """
    formats_list = ["mp3", "m4a", "flac", "opus", "wav", "mp4", "mkv", "webm"]
    os.system("clear")    

    while True:
        print("\nChose a format for the download:")
        print("- mp3  (Audio, max compatibility)")
        print("- m4a  (Audio, modern & efficient)")
        print("- flac (Audio, lossless - large files)")
        print("- opus (Audio, ideal for speech - small files)")
        print("- wav  (Audio, uncompressed - for editing)")
        print("- mp4  (Video + Audio, max compatibility)")
        print("- mkv  (Video + Audio, flexible format)")
        print("- webm (Video + Audio, modern web format)")
        
        chosen_format = input("\nFormat: ").strip().lower()
        if chosen_format not in formats_list:
            print("\nInvalid format. Press 'Enter' continue...")
            input()
            os.system("clear")
            continue
        else:
            os.system("clear")
            print("Download...")
            return chosen_format
    

def playlist_urls_aquisition(user_choice: str) -> list[str]:
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
        print("\n" + "### --- YOUTUBE MANAGER --- ###".center(columns) + "\n")
        print(f"Insert your playlist URLs: (Insert '{key_words[0]}' to start the {key_words[0]})\n")

        if len(local_playlist_url):
            for j, url in enumerate(local_playlist_url):
                print(f"URL {j+1}: {url}")

        user_input = input(f"Input: ").strip()
        if user_input.lower() == f"{key_words[0]}":
            if user_input == "update":
                os.system("clear")
                print(f"\n{key_words[1]}...")
            return local_playlist_url
        
        # Extracts the playlist ID and rebuilds a clean URL to standardize it.
        # This normalizes many possible YouTube playlist url formats to a single canonical form.
        elif "https://" in user_input and "list=" in user_input:
            check_url(PLAYLIST_URL_TYPE + user_input.split("list=")[-1].split("&")[0])
        else:
            print("\nInvalid input. Press Enter to continue...")
            input()
            os.system("clear")

def video_urls_aquisition() -> list[str]:
    """
    Interactively prompts the user to enter one or more YouTube video URLs,
    validating and normalizing them.

    Returns:
        A list of cleaned, standardized YouTube video URLs.

    Notes:
        This function accepts both standard "watch?v=" URLs and short youtu.be
        links. It collects multiple URLs until the user types 'download'.
        It relies on the outer-scope `user_choice` variable to avoid including
        playlist URLs when collecting single-video downloads.
    """
    def check_url(user_input: str):
        if user_input not in local_videos_url:
            local_videos_url.append(user_input)
        else:
            print("\nThis URL has already been added. Press Enter to continue...")
            input()
        os.system("clear")

    local_videos_url = []

    while True:
        columns = shutil.get_terminal_size().columns
        print("\n" + "### --- YOUTUBE MANAGER --- ###".center(columns) + "\n")
        print("Insert your videos URLs: (Insert 'download' to start the download)\n")

        if len(local_videos_url):
            for j, url in enumerate(local_videos_url):
                print(f"URL {j+1}: {url}")

        user_input = input(f"Input: ").strip()
        if user_input.lower() == "download":
            os.system("clear")
            print("\nDownload...")
            return local_videos_url
    
        # Extracts the video ID and rebuilds a clean URL to standardize it.
        # Note: the check avoids interpreting playlist links as single-video downloads.
        elif "https://" in user_input and "watch?v=" in user_input and "list=" not in user_choice:
            check_url(VIDEO_URL_TYPE1 + user_input.split("watch?v=")[-1].split("&")[0])
        elif user_input.startswith(VIDEO_URL_TYPE2):
            # Shortened youtu.be link -> convert to canonical watch?v= link
            check_url(VIDEO_URL_TYPE1 + user_input.split(".be/")[-1]) 
        else:
            print("\nInvalid input. Press Enter to continue...")
            input()
            os.system("clear")
        

if __name__ == "__main__":
    current_state = "main_menu"
    os.system("clear")

    while True:
        columns = shutil.get_terminal_size().columns

        # --- MAIN MENU --- 
        if current_state == "main_menu":
            os.system("clear")
            print("### --- YOUTUBE MANAGER --- ###".center(columns) + "\n")
            print("1 - Manage Playlists\n2 - Download Videos\n3 - Exit\n")
            user_choice = input("Select an option: ")

            if user_choice == "1":
                current_state = "playlist_menu"
            elif user_choice == "2":
                current_state = "videos_download"
            elif user_choice == "3":
                current_state = "exit"
            else:
                print("\nInvalid option. Please select 1, 2, or 3. Press 'Enter' to continue...")
                input()
                os.system("clear")

        # --- PLAYLIST MANAGEMENT ---
        elif current_state == "playlist_menu":
            while True:
                os.system("clear")
                print("### --- YOUTUBE MANAGER --- ###".center(columns) + "\n")
                print("1 - Download\n2 - Update\n3 - Back to main menu\n4 - Exit\n")
                user_choice = input("Select an option: ")

                # --- DOWNLOAD PLAYLIST ---
                if user_choice == "1":
                    os.system("clear")
                    playlist_url = playlist_urls_aquisition(user_choice)
                    chosen_format = ask_for_format()
                    errors = []

                    for url in playlist_url:
                        # Fetch playlist metadata (title) quickly using config1
                        with yt_dlp.YoutubeDL(config1) as ydl:
                            info = ydl.extract_info(url, download=False)
                            if info:
                                folder_name = core.sanitize_folder_name(info['title'])

                        # If the folder already exists, suggest to use Update to avoid duplication
                        if os.path.isdir(folder_name):
                            print(f"\nThe folder '{folder_name}' already exists. Use the Update option to update it.", end="\n")
                            sleep(1.5)
                            continue

                        # Create destination folder and start downloading playlist entries
                        os.makedirs(folder_name, exist_ok=True)
                        # Delegate the resilient per-entry download to core.download_playlist
                        errors.extend(core.download_playlist(url, folder_name, format=chosen_format))

                    # Report download errors (if any)
                    if errors:
                        print("\nSome errors occurred during the download:")
                        for error in errors:
                            print(f" - {error}")
                    else:
                        print("\nDownload completed successfully for all playlists!")
                        sleep(1)

                    current_state = "main_menu"
                    break

                # --- UPDATE PLAYLIST ---
                elif user_choice == "2":
                    os.system("clear")
                    playlist_url = playlist_urls_aquisition(user_choice)
                    errors = []

                    for url in playlist_url:
                        # Get playlist metadata to derive local folder name
                        with yt_dlp.YoutubeDL(config1) as ydl:
                            info = ydl.extract_info(url, download=False)
                            if info:
                                folder_name = core.sanitize_folder_name(info.get("title", "Unknown Playlist"))

                        # If local folder doesn't exist, cannot update: ask user to download first
                        if not os.path.isdir(folder_name):
                            print(f"\nFolder '{folder_name}' not found. Please use the Download option first.")
                            sleep(1.5)
                            continue
                        
                        backup_path = None 
                        try:
                            # Clean up any residual temp folder to ensure a clean state before backup
                            tmp_folder_path = os.path.join(folder_name, ".tmp")
                            if os.path.isdir(tmp_folder_path):
                                shutil.rmtree(tmp_folder_path)

                            # Create a backup copy of the folder so we can rollback on failure
                            backup_path, backup_error = core.folder_backup(folder_name)
                            if backup_error:
                                # If backup failed, skip updating this playlist and record the error
                                errors.append(("Backup Failed", backup_error))
                                continue
                            
                            # Determine missing videos and build the final titles map
                            new_videos, titles_map, get_errors = core.get_missing_videos(url, folder_name)
                            errors.extend(get_errors)
                            
                            # Apply the update plan (downloads, renames, cleanup)
                            update_errors = core.update_playlist(new_videos, titles_map, folder_name)
                            errors.extend(update_errors)
                            
                            # If any non-critical errors were returned, treat as failure and rollback
                            if get_errors or update_errors:
                                raise Exception("Update process reported non-critical errors, initiating rollback.")

                        except Exception as e:
                            # Record the high-level failure for reporting
                            errors.append(("UPDATE FAILED", f"A critical error occurred: {e}"))
                            
                            # Try to restore from the previously created backup if available
                            if backup_path and os.path.isdir(backup_path):
                                os.system("clear")
                                print("Update failed. Restoring from backup...")
                                sleep(2)
                                try:
                                    # Move backup into a temporary name then replace the broken folder atomically
                                    temp_backup_path = f".{folder_name}.tmp.bak"
                                    if os.path.exists(temp_backup_path):
                                        shutil.rmtree(temp_backup_path)
                                    shutil.move(backup_path, temp_backup_path)

                                    shutil.rmtree(folder_name)
                                    os.rename(temp_backup_path, folder_name)
                                    
                                    print("Restore successful.")
                                except Exception as restore_e:
                                    # If restore fails, append a critical error for manual intervention
                                    errors.append(("CRITICAL RESTORE FAILED", str(restore_e)))
                                    print(f"!!! CRITICAL ERROR: Could not restore from backup for '{folder_name}'. Please check the folder manually. !!!")
                            else:
                                # No backup available to restore from
                                print("Update failed, and no backup was available to restore from.")
                        
                        finally:
                            # If backup folder still exists (update succeeded or partially succeeded),
                            # attempt to remove it to avoid clutter; record errors if cleanup fails.
                            if backup_path and os.path.isdir(backup_path):
                                try:
                                    shutil.rmtree(backup_path)
                                except Exception as clean_e:
                                    errors.append(("Backup Cleanup Failed", str(clean_e)))

                    # Report update errors (if any)
                    if errors:
                        print("\nSome errors occurred during the update:")
                        for error_type, error_msg in errors:
                            print(f" - [{error_type}] {error_msg}")
                    else:
                        print("\nUpdate completed successfully for all playlists!")
                        sleep(1)

                    current_state = "main_menu"
                    break

                elif user_choice == "3":
                    current_state = "main_menu"
                    break

                elif user_choice == "4":
                    current_state = "exit"
                    break

                else:
                    print("\nInvalid option. Please select 1 or 2. Press 'Enter' to continue...")
                    input()
                    os.system("clear")
                    continue

        # --- VIDEOS MANAGEMENT ---
        elif current_state == "videos_download":
            os.system("clear")
            video_url = video_urls_aquisition()
            chosen_format = ask_for_format()
            errors = []

            # Delegate single-video downloads to core.download_video
            errors.extend(core.download_video(video_url, format=chosen_format))

            if errors:
                print("\nSome errors occurred during the download:")
                for error in errors:
                    print(f" - {error}")
            else:
                print("\nDownload completed successfully for all videos!")
                sleep(1)

            current_state = "main_menu"

        # --- EXIT ---
        elif current_state == "exit":
            break
