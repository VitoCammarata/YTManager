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

key_words = [("download", "Download"), ("update", "Update")]

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
    clear_screen()  

    formats_list = {
        "1": "mp3",
        "2": "m4a",
        "3": "flac",
        "4": "opus",
        "5": "wav",
        "6": "mp4",
        "7": "mkv",
        "8": "webm"
    }
  

    while True:
        print("\nChose a format for the download:")
        print("1: mp3  (Audio, max compatibility)")
        print("2: m4a  (Audio, modern & efficient)")
        print("3: flac (Audio, lossless - large files)")
        print("4: opus (Audio, ideal for speech - small files)")
        print("5: wav  (Audio, uncompressed - for editing)")
        print("6: mp4  (Video + Audio, max compatibility)")
        print("7: mkv  (Video + Audio, flexible format)")
        print("8: webm (Video + Audio, modern web format)")
        
        chosen_format = input("\nFormat: ").strip()

        if chosen_format in formats_list:
            clear_screen()
            return formats_list[chosen_format]
        else:
            print(f"\nInvalid choice. Please select a number from 1 to {len(formats_list)}. Press 'Enter' to continue...")
            input()
            clear_screen()
        
def ask_for_video_quality() -> str:
    """
    Prompts the user to choose a specific video resolution.

    Returns:
        The chosen resolution as a string (e.g., "1080", "720").
    """
    clear_screen()

    quality_options = {
        "1": "2160", 
        "2": "1440",  
        "3": "1080",  
        "4": "720",   
        "5": "480",   
        "6": "360"   
    }
    
    while True:
        print("\nChoose a maximum video resolution for the download:")
        print("Note: If a video is not available in the chosen quality,")
        print("the next best available quality will be downloaded.")
        print("1: 4K (2160p)")
        print("2: 2K (1440p)")
        print("3: Full HD (1080p)")
        print("4: HD (720p)")
        print("5: Standard (480p)")
        print("6: Low (360p)")
        
        choice = input("\nResolution: ").strip()
        
        if choice in quality_options:
            clear_screen()
            return quality_options[choice]
        else:
            print(f"\nInvalid choice. Please select a number from 1 to {len(quality_options)}. Press 'Enter' to continue...")
            input()
            clear_screen()
        
    

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

    key_word = key_words[0 if user_choice == "1" else 1][0]

    while True:
        columns = shutil.get_terminal_size().columns
        print("\n" + "### --- YOUTUBE MANAGER --- ###".center(columns) + "\n")
        print(f"Insert your playlist URLs: (Insert '{key_word}' to start the {key_word})\n")

        if len(local_playlist_url):
            for j, url in enumerate(local_playlist_url):
                print(f"URL {j+1}: {url}")

        user_input = input(f"Input: ").strip()
        if user_input.lower() == key_words[0][0] and user_choice == "1" or user_input.lower() == key_words[1][0] and user_choice == "2":
            clear_screen()
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

                    chosen_quality = None
                    if chosen_format not in ['mp3', 'm4a', 'flac', 'opus', 'wav']:
                        chosen_quality = ask_for_video_quality()

                    print(f"{key_words[0][1]}...\n")

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
                        errors.extend(core.download_playlist(url, folder_name, playlist_title, chosen_format, chosen_quality))

                    # Report download errors (if any)
                    if errors:
                        print("\nSome errors occurred during the download:")
                        for error in errors:
                            print(f" - {error}")
                    else:
                        print("\nDownload completed successfully for all playlists!")
                        sleep(2)

                    current_state = "main_menu"
                    break

                # --- UPDATE PLAYLIST ---
                elif user_choice == "2":
                    clear_screen()
                    playlist_url = playlist_urls_aquisition(user_choice)
                    errors = []

                    print(f"{key_words[1][1]}...\n")

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
                            print(f"\nFolder '{folder_name}' not found. Please use the Download option first.\nPress 'Enter' to continue...")
                            input()
                            continue
                        
                        try:
                            errors.extend(core.cleanup_deleted_videos(online_videos, playlist_title, folder_name))

                            errors.extend(core.reorder_local_videos(online_videos, playlist_title, folder_name))

                            media_format = core.detect_format(folder_name)
                            if media_format:
                                errors.extend(core.download_new_videos(online_videos, playlist_title, folder_name, media_format))
                            else:
                                media_format = ask_for_format()
                                errors.extend(core.download_new_videos(online_videos, playlist_title, folder_name, media_format))


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
                        sleep(2)

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

            chosen_quality = None
            if chosen_format not in ['mp3', 'm4a', 'flac', 'opus', 'wav']:
                chosen_quality = ask_for_video_quality()

            print(f"{key_words[0][1]}...\n")

            errors = []

            # Delegate single-video downloads to core.download_video
            errors.extend(core.download_video(video_url, chosen_format, chosen_quality))

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
