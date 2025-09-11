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
from pathvalidate import sanitize_filename
from time import sleep
import core
from core import yt_metadata_config
from core import PLAYLIST_URL_TYPE, VIDEO_URL_TYPE1, VIDEO_URL_TYPE2

def clear_screen():
    os.system("cls") if os.name == "nt" else os.system("clear")    

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
    clear_screen()    

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
            clear_screen()
            continue
        else:
            clear_screen()
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
        clear_screen()

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
                clear_screen()
                print(f"\n{key_words[1]}...\n")
            return local_playlist_url
        
        # Extracts the playlist ID and rebuilds a clean URL to standardize it.
        # This normalizes many possible YouTube playlist url formats to a single canonical form.
        elif "https://" in user_input and "list=" in user_input:
            check_url(PLAYLIST_URL_TYPE + user_input.split("list=")[-1].split("&")[0])
        else:
            print("\nInvalid input. Press Enter to continue...")
            input()
            clear_screen()

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
        clear_screen()

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
            clear_screen()
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
            clear_screen()
        

if __name__ == "__main__":
    current_state = "main_menu"
    clear_screen()

    while True:
        columns = shutil.get_terminal_size().columns

        # --- MAIN MENU --- 
        if current_state == "main_menu":
            clear_screen()
            print("### --- YOUTUBE MANAGER --- ###".center(columns) + "\n")
            print("1 - Manage Playlists\n2 - Download Videos\n3 - Delete Application Data\n4 - Exit")
            user_choice = input("Select an option: ")

            if user_choice == "1":
                current_state = "playlist_menu"
            elif user_choice == "2":
                current_state = "videos_download"
            elif user_choice == "3":
                current_state = "delete_data"
            elif user_choice == "4":
                current_state = "exit"
            else:
                print("\nInvalid option. Please select 1, 2, or 3. Press 'Enter' to continue...")
                input()
                clear_screen()

        # --- PLAYLIST MANAGEMENT ---
        elif current_state == "playlist_menu":
            while True:
                clear_screen()
                print("### --- YOUTUBE MANAGER --- ###".center(columns) + "\n")
                print("1 - Download\n2 - Update\n3 - Back to main menu\n4 - Exit\n")
                user_choice = input("Select an option: ")

                # --- DOWNLOAD PLAYLIST ---
                if user_choice == "1":
                    clear_screen()
                    playlist_url = playlist_urls_aquisition(user_choice)
                    chosen_format = ask_for_format()
                    errors = []

                    for url in playlist_url:
                        # Fetch playlist metadata (title) quickly using config1
                        with yt_dlp.YoutubeDL(yt_metadata_config) as ydl:
                            info = ydl.extract_info(url, download=False)
                            if info:
                                playlist_title = info.get('title', 'Unknown Playlist')
                                folder_name = sanitize_filename(playlist_title)
                
                        # If the folder already exists, suggest to use Update to avoid duplication
                        if os.path.isdir(folder_name):
                            print(f"\nThe folder '{folder_name}' already exists. Use the Update option to update it.\nPress 'enter' to continue")
                            input()
                            continue

                        # Create destination folder and start downloading playlist entries
                        os.makedirs(folder_name, exist_ok=True)
                        # Delegate the resilient per-entry download to core.download_playlist
                        print("\n")
                        errors.extend(core.download_playlist(url, folder_name, playlist_title, format=chosen_format))

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
                    clear_screen()
                    playlist_url = playlist_urls_aquisition(user_choice)
                    errors = []

                    for url in playlist_url:
                        info = core.fetch_online_playlist_info(url)
                        if not info:
                            errors.append(("Info Error", f"Impossibile ottenere informazioni per l'URL: {url}"))
                            continue

                        playlist_title = info['title']
                        online_videos = info['videos']
                        folder_name = sanitize_filename(playlist_title)

                        # If local folder doesn't exist, cannot update: ask user to download first
                        if not os.path.isdir(folder_name):
                            print(f"\nFolder '{folder_name}' not found. Please use the Download option first.")
                            sleep(1.5)
                            continue
                        
                        try:
                            errors.extend(core.cleanup_deleted_videos(online_videos, playlist_title, folder_name))

                            errors.extend(core.reorder_local_videos(online_videos, playlist_title, folder_name))

                            media_format = core.detect_format(folder_name)
                            if media_format:
                                errors.extend(core.download_new_videos(online_videos, playlist_title, folder_name, media_format))
                            else:
                                media_format = ask_for_format()
                                errors.extend(core.download_new_videos(online_videos, playlist_title, folder_name, chosen_format))


                        except Exception as e:
                            # Record the high-level failure for reporting
                            errors.append(("UPDATE FAILED", f"A critical error occurred: {e}"))

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
                    clear_screen()
                    continue

        # --- VIDEOS MANAGEMENT ---
        elif current_state == "videos_download":
            clear_screen()
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

        elif current_state == "delete_data":
            clear_screen()
            print("\nWARNING: This will permanently delete all saved playlist states,")
            print("backups, and temporary files associated with this application.")
            print("This action CANNOT be undone.")
            print("\nYour downloaded media files (mp3, mp4, etc.) will NOT be affected,")
            print("but the application may not work properly anymore.")   

            confirm = input("\nAre you absolutely sure you want to proceed? (Type 'yes' to confirm, 'no' to exit): ").strip().lower()

            if confirm == 'yes':
                # Call the core function to perform the deletion
                success, message = core.delete_app_data()
                print(f"\n{message}")
            else:
                print("\nOperation cancelled. No data has been deleted.")
            
            print("\nPress 'Enter' to return to the main menu...")
            input()
            current_state = "main_menu"         

        # --- EXIT ---
        elif current_state == "exit":
            break
