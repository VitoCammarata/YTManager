# YTManager v0.1.0

![Licenza MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Ultima Release](https://img.shields.io/github/v/release/VitoCammarata/YTManager)

<!-- Ti consiglio di aggiungere qui uno screenshot o una GIF del programma in azione! -->
<!-- Esempio: <img src="screenshot.gif" width="700"> -->

---

[English Version](#english) | [Versione Italiana](#italiano)

---

<a name="italiano"></a>
## 🇮🇹 YTManager (Versione Italiana)

### Descrizione

Un'applicazione cross-platform per scaricare e sincronizzare le tue playlist di YouTube in file MP3 locali in modo semplice e robusto.

YTManager ti permette di mantenere una copia locale delle tue playlist preferite. Offre due funzionalità principali:
1.  **Download:** Scarica un'intera playlist, convertendo ogni video in un file MP3 di alta qualità. Il processo è resiliente e può essere ripreso in caso di interruzioni.
2.  **Update:** Sincronizza una cartella già scaricata con la versione online della playlist. Aggiunge i nuovi video, rimuove quelli eliminati e riordina i file per rispecchiare l'ordine attuale.

**⚠️ Nota Importante:** Lo script funziona esclusivamente con **playlist pubbliche o non in elenco**. Le playlist private non sono supportate perché l'applicazione non implementa un sistema di login, garantendo così la privacy dell'utente senza richiedere l'accesso all'account YouTube.

### Come si Usa

1.  **Scarica l'ultima versione** dalla sezione [**Releases**](https://github.com/VitoCammarata/YTManager/releases) di questo repository.
2.  Scegli il file adatto al tuo sistema operativo.
3.  Metti l'eseguibile nella cartella dove vuoi conservare le tue playlist.
4.  Esegui il programma e segui le istruzioni a schermo:
    *   **Su Windows:** Fai doppio click sul file `YTManager.exe`. Si aprirà automaticamente un terminale per interagire con il programma.
    *   **Su Linux:** Apri un terminale nella cartella in cui hai messo il file ed eseguilo con il comando `./YTManager`.

### Dietro le Quinte: File di Supporto

Per garantire un funzionamento sicuro, YTManager crea alcuni file e cartelle di supporto.

-   **File di Stato (`.json`):** In ogni cartella viene creato un file di stato nascosto (es. `.NomePlaylist.json` su Linux, o `NomePlaylist.json` su Windows, reso nascosto dal sistema). Questo file è fondamentale per la sincronizzazione.
-   **Cartella Temporanea:** Durante il download, i file vengono processati in una cartella temporanea (`.tmp` su Linux, `tmp` su Windows), anch'essa nascosta. Viene eliminata automaticamente a processo concluso.
-   **Cartella di Backup:** Durante un "Update", viene creata una copia di sicurezza della playlist (`.bak` su Linux, `bak` su Windows). In caso di errori, i tuoi file vengono ripristinati da qui.

**⚠️ Attenzione:** Per garantire il corretto funzionamento del programma, **non modificare o eliminare manualmente** questi file e cartelle.

### Per Sviluppatori

Se vuoi contribuire o eseguire il codice sorgente:

1.  **Prerequisiti:** Assicurati di avere **Python 3** e **pip** installati.
2.  **Clona il Repository:**
    ```bash
    git clone https://github.com/VitoCammarata/YTManager.git
    cd YTManager
    ```
3.  **Installa le Dipendenze:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Esegui lo Script:**
    ```bash
    python YT_Manager_Windos.py
    ```
    for Windows 

### Roadmap Futura e Contributi

Questo progetto è in continua evoluzione! Ecco alcune delle funzionalità previste:
-   Interfaccia Grafica (GUI) per un utilizzo ancora più semplice.
-   Scelta del formato di download (video MP4, altri formati audio).
-   File di configurazione per salvare playlist e impostazioni.
-   Download paralleli per aggiornare più playlist contemporaneamente.
-   ...e altro ancora!

Hai un'idea o hai trovato un bug? Apri una **[Issue](https://github.com/VitoCammarata/YTManager/issues)**! I suggerimenti sono sempre benvenuti.

---
<a name="english"></a>
## 🇬🇧 YTManager (English Version)

### Description

A cross-platform application to easily and robustly download and synchronize your YouTube playlists into local MP3 files.

YTManager allows you to keep a local copy of your favorite playlists. It offers two main features:
1.  **Download:** Downloads an entire playlist, converting each video into a high-quality MP3 file. The process is resilient and can be resumed if interrupted.
2.  **Update:** Synchronizes an already downloaded folder with its online counterpart. It adds new videos, removes deleted ones, and reorders files to match the current playlist order.

**⚠️ Important Note:** The script works exclusively with **public or unlisted playlists**. Private playlists are not supported because the application does not implement a login feature, thus ensuring user privacy by not requiring access to their YouTube account.

### How to Use

1.  **Download the latest version** from the [**Releases**](https://github.com/VitoCammarata/YTManager/releases) section of this repository.
2.  Choose the file appropriate for your operating system.
3.  Place the executable in the folder where you want to store your playlists.
4.  Run the program and follow the on-screen instructions:
    *   **On Windows:** Double-click the `YTManager.exe` file. A terminal window will open automatically for you to interact with the program.
    *   **On Linux:** Open a terminal in the folder where you placed the file and run it with the command `./YTManager`.

### Behind the Scenes: Support Files

To ensure safe operation, YTManager creates a few support files and folders.

-   **State File (`.json`):** A hidden state file is created in each folder (e.g., `.PlaylistName.json` on Linux, or `PlaylistName.json` on Windows, made hidden by the system). This file is crucial for synchronization.
-   **Temporary Folder:** During downloads, files are processed in a temporary folder (`.tmp` on Linux, `tmp` on Windows), which is also hidden. It is automatically deleted when the process is complete.
-   **Backup Folder:** During an "Update", a backup copy of the playlist is created (`.bak` on Linux, `bak` on Windows). In case of an error, your files are restored from it.

**⚠️ Warning:** To ensure the program works correctly, **do not manually modify or delete** these files and folders.

### For Developers

If you want to contribute or run the source code:

1.  **Prerequisites:** Ensure you have **Python 3** and **pip** installed.
2.  **Clone the Repository:**
    ```bash
    git clone https://github.com/VitoCammarata/YTManager.git
    cd YTManager
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the Script:**
    ```bash
    python YT_Manager.py
    ```

### Future Roadmap & Contributions

This project is constantly evolving! Here are some of the planned features:
-   A Graphical User Interface (GUI) for an even more user-friendly experience.
-   Format selection (MP4 videos, other audio formats).
-   A configuration file to save playlists and preferred settings.
-   Parallel downloads to speed up updating multiple playlists.
-   ...and much more!

Have an idea or found a bug? Please open an **[Issue](https://github.com/VitoCammarata/YTManager/issues)**! Suggestions are always welcome.
