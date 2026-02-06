# YTManager

![Licenza MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Ultima Release](https://img.shields.io/github/v/release/VitoCammarata/YTManager)
![Platform](https://img.shields.io/badge/Platform-Linux-orange.svg)

<p align="center">
  <img src="assets/main_menu.png" width="650" alt="Menu Principale">
</p>
<p align="center">
   <img src="assets/playlists_manager.png" width="650" alt="Inserimento URL">
</p>
<p align="center">
   <img src="assets/delete_data_section.png" width="650" alt="Processo di Download">
</p>
 
---

> ⚠️ **IMPORTANT NOTICE: LINUX ONLY** > Starting with version 2.1.0, YTManager is developed and supported **exclusively for Linux**. Windows support has been discontinued to ensure maximum performance and stability.

## YTManager 2.1

### Your Personal YouTube Library, Offline and On Your Terms

YTManager is a simple yet powerful application that lets you download YouTube videos and playlists and save them to your computer. Create your personal music and video library, accessible anywhere, without interruptions.

### Key Features

* 🚀 **Smart Download & Synchronization**
    * **Download:** Download entire playlists with a single command.
    * **Batch Import:** Import multiple playlists at once! Simply create a text file named `url.txt` in the same folder as the executable containing your links (Format: `Playlist Name:URL`).
    * **Update:** Synchronize your local folders with online playlists. YTManager automatically adds new videos, removes unavailable ones, and reorders your files for you.

* 🎬 **Single Videos On the Fly**
    * Need just one video? Paste the URL and quickly download it in your preferred format.

* ✨ **Full Control Over Video Quality**
    * Choose your desired resolution for your videos, from 360p up to 4K. The program will always download the best available quality up to your set limit, optimizing the balance between quality and file size.

* 🎶 **Automatic Metadata & Cover Art**
    * Every file is enriched with essential metadata: Artist, Album (from the playlist title), Date, and Track Number. For supported formats, the video's cover art is also included, ensuring a neatly organized and easy-to-navigate media library.

* 📂 **Wide Format Support**
    * Choose the perfect extension for your needs, for both **audio** (`mp3`, `m4a`, `flac`, `opus`, `wav`) and **video** (`mp4`, `mkv`, `webm`).

* 🛡️ **Peace of Mind and Safety**
    * The most delicate operations, like reordering files, are protected by an **automatic backup system**. In case of issues, your files are safe.

* 🧹 **Clean Data Management**
    * Want to start fresh? A simple menu option lets you **safely delete all application configuration data**, without ever touching your downloaded media files.

### How to Use

1.  **Install Dependencies:** To ensure the best performance and prevent runtime warnings, ensure **Node.js** is installed on your system.
    ```bash
    sudo apt update
    sudo apt install nodejs
    ```

2.  **Download the App:** Get the latest executable from the [**Releases**](https://github.com/VitoCammarata/YTManager/releases) section.

3.  **Grant Permissions (Important):** Before running the file, you must make it executable. Open your terminal in the download folder and run:
    ```bash
    chmod +x YTManager
    ```

4.  **Run:** Launch the program:
    ```bash
    ./YTManager
    ```

### Important Notes

* **Public Content:** The application works with public or unlisted videos and playlists. Private content is not supported.
* **Configuration Data:** To keep your download folders 100% clean, YTManager saves all its working files (playlist states, backups, temp files) in a dedicated system folder (`~/.local/share/YouTubePlaylistManager`). Your downloaded media files are never touched.

### For Developers

If you want to contribute or run the source code directly:

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/VitoCammarata/YTManager.git](https://github.com/VitoCammarata/YTManager.git)
    cd YTManager
    ```
2.  **Set up Environment:**
    Ensure you have Python 3, pip and Node.js installed.
    ```bash
    python -m venv venv
    source venv/bin/activate 
    pip install -r requirements.txt
    ```
3.  **Run:**
    ```bash
    python main.py
    ```

---

### Disclaimer
*This project is for educational purposes only. Please respect YouTube's Terms of Service and copyright laws in your country. The developer assumes no liability for misuse of this software.*
