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
import json
import yt_dlp
from typing import Optional
from time import sleep
import core
from core import config1, URL_TYPE
    

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
                errors.extend(core.download_playlist(url, folder_name))

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

                    backup_path, backup_error = core.folder_backup(folder_name)
                    if backup_error:
                        errors.append(("Backup Failed", backup_error))
                        continue
                    
                    # Execute the update process.
                    new_videos, titles_map, get_errors = core.get_missing_videos(url, folder_name)
                    errors.extend(get_errors)
                    
                    update_errors = core.update_playlist(new_videos, titles_map, folder_name)
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
