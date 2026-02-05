# YTManager - GUI Edition

![Work in Progress](https://img.shields.io/badge/Status-Work_in_Progress-orange)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

> ⚠️ **Warning: Under Active Development**
>
> This branch (`gui_version`) contains the source code for the upcoming **Graphical User Interface** of YTManager.
> The code here may be unstable, incomplete, or buggy. It is intended for testing and development purposes only.

---

<<<<<<< HEAD
### 🚧 What is happening here?

We are working on transitioning YTManager from a Command Line Interface (CLI) to a full modern **GUI**.
The goal is to make the application accessible to everyone, eliminating the need to use the terminal while keeping the same powerful features of the original version.

### Current Status

* [x] Project Structure Setup
* [ ] Main Menu UI Design
* [ ] Playlist Manager Integration
* [ ] Settings & Configuration UI
* [ ] Real-time Download Progress Bars

### 🔙 Looking for the stable version?

If you just want to download videos and playlists right now, please use the **Stable CLI Version**.

👉 **[Go to the CLI Version (Stable)](https://github.com/VitoCammarata/YTManager/tree/cli_version)**

---

### 🛠️ For Developers & Testers
=======
## YTManager 2.0
>>>>>>> a057d67272cd81a0f8d40efa0fd9cbdf91bbe9da

If you want to test the current state of the GUI or contribute to the development:

<<<<<<< HEAD
1.  **Clone this specific branch:**
=======
YTManager is a simple yet powerful application that lets you download YouTube videos and playlists and save them to your computer. Create your personal music and video library, accessible anywhere, without interruptions.

### Key Features

*   🚀 **Smart Download & Synchronization**
    *   **Download:** Download entire playlists with a single command.
    *   **Update:** Synchronize your local folders with online playlists. YTManager automatically adds new videos, removes unavailable ones, and reorders your files for you.

*   🎬 **Single Videos On the Fly**
    *   Need just one video? Paste the URL and quickly download it in your preferred format.

*   ✨ **Full Control Over Video Quality**
    *   Choose your desired resolution for your videos, from 360p up to 4K. The program will always download the best available quality up to your set limit, optimizing the balance between quality and file size.

*   🎶 **Automatic Metadata & Cover Art**
    *   Every file is enriched with essential metadata: Artist, Album (from the playlist title), Date, and Track Number. For supported formats, the video's cover art is also included, ensuring a neatly organized and easy-to-navigate media library.

*   📂 **Wide Format Support**
    *   Choose the perfect extension for your needs, for both **audio** (`mp3`, `m4a`, `flac`, `opus`, `wav`) and **video** (`mp4`, `mkv`, `webm`).

*   🛡️ **Peace of Mind and Safety**
    *   The most delicate operations, like reordering files, are protected by an **automatic backup system**. In case of issues, your files are safe.

*   🧹 **Clean Data Management**
    *   Want to start fresh? A simple menu option lets you **safely delete all application configuration data**, without ever touching your downloaded media files.

### How to Use

1.  **Download the latest version** from the [**Releases**](https://github.com/VitoCammarata/YTManager/releases) section of this repository.
2.  Place the executable file in the folder where you want your downloads to be saved.
3.  Run the program and follow the simple on-screen instructions.
    *   Open a terminal and run it with `./YTManager`.

### Important Notes

*   **Public Content:** The application works with public or unlisted videos and playlists. Private content is not supported.
*   **Configuration Data:** To keep your download folders 100% clean, YTManager now saves all its working files (playlist states, backups, temp files) in a dedicated system folder (`~/.local/share`). Your downloaded media files are never touched.

### For Developers

If you want to contribute or run the source code:

1.  **Prerequisites:** Make sure you have **Python 3** and **pip** installed.
2.  **Clone the Repository:**
>>>>>>> a057d67272cd81a0f8d40efa0fd9cbdf91bbe9da
    ```bash
    git clone -b gui_version [https://github.com/VitoCammarata/YTManager.git](https://github.com/VitoCammarata/YTManager.git)
    cd YTManager
    ```

2.  **Set up the environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: .\venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Run the GUI:**
    ```bash
    python main.py
    ```

---
*Stay tuned! The graphical revolution is coming soon.* 🚀