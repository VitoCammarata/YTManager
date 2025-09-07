# YTManager

![Licenza MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Ultima Release](https://img.shields.io/github/v/release/VitoCammarata/YTManager)

<!-- Ti consiglio di aggiungere qui uno screenshot o una GIF del programma in azione! -->
<!-- Esempio: <img src="screenshot.gif" width="700"> -->


[English Version](#english) | [Versione Italiana](#italiano)

---

<a name="italiano"></a>
## 🇮🇹 YTManager (Versione Italiana)

### Descrizione

Un'applicazione cross-platform per scaricare e sincronizzare i tuoi video e le tue playlist di YouTube in file locali, in modo semplice e robusto.

YTManager ti permette di mantenere una copia locale dei tuoi contenuti preferiti, offrendo il pieno controllo sul formato e sulla gestione della tua libreria.

### Funzionalità Principali

*   📥 **Gestione Completa delle Playlist:**
    *   **Download:** Scarica un'intera playlist, convertendo ogni video nel formato scelto.
    *   **Update:** Sincronizza una cartella già scaricata con la versione online. Aggiunge nuovi video, rimuove quelli eliminati e riordina i file per rispecchiare l'ordine attuale.

*   🎬 **Download di Video Singoli:**
    *   Non solo playlist! Puoi scaricare rapidamente uno o più video singoli inserendo i loro URL.

*   🎧 **Ampia Scelta di Formati:**
    *   Scegli il formato che preferisci. YTManager supporta sia formati **audio** (come `mp3`, `m4a`, `flac`) che **video** (come `mp4`, `mkv`).

*   🖼️ **Copertine e Metadati Inclusi:**
    *   Per i formati audio, la miniatura del video viene **automaticamente inclusa come copertina del file**, rendendo la tua libreria musicale più bella e organizzata.

*   🛡️ **Sicuro e Robusto:**
    *   Il processo di aggiornamento è protetto da un sistema di **backup automatico**. Se qualcosa va storto, la tua cartella viene ripristinata allo stato originale per non perdere alcun file.

**⚠️ Nota Importante:** Lo script funziona esclusivamente con **playlist e video pubblici o non in elenco**. I contenuti privati non sono supportati perché l'applicazione non implementa un sistema di login, garantendo così la privacy dell'utente senza richiedere l'accesso all'account YouTube.

### Come si Usa

1.  **Scarica l'ultima versione** dalla sezione [**Releases**](https://github.com/VitoCammarata/YTManager/releases) di questo repository.
2.  Scegli il file adatto al tuo sistema operativo.
3.  Metti l'eseguibile nella cartella dove vuoi conservare i tuoi download.
4.  Esegui il programma e segui le istruzioni a schermo:
    *   **Su Windows:** Fai doppio click sul file `YTManager.exe`. Si aprirà automaticamente un terminale per interagire con il programma.
    *   **Su Linux:** Apri un terminale nella cartella in cui hai messo il file ed eseguilo con il comando `./YTManager`.

### Dietro le Quinte

Per garantire un funzionamento sicuro, YTManager crea alcuni file e cartelle di supporto all'interno delle directory delle playlist.

-   **File di Stato (`.json`):** In ogni cartella playlist, viene creato un file di stato nascosto (es. `.NomePlaylist.json`). Questo file è fondamentale per la sincronizzazione. Su Windows, questo file potrebbe essere visibile di default.

-   **Cartella Temporanea (`.tmp`):** Durante il download di una playlist, i file vengono processati in una cartella temporanea che viene eliminata automaticamente a processo concluso.

-   **File Intermedi di Download:** Durante il processo di download, vedrai comparire nella cartella diversi file temporanei (es. flussi video `.mp4`, audio `.m4a`, o la copertina `.webp`). **Questi file sono essenziali per creare il file finale.**

-   **Cartella di Backup (`.bak`):** Durante un "Update", viene creata una copia di sicurezza della playlist. In caso di errori, i tuoi file vengono ripristinati da qui.

**⚠️ Attenzione:** Per garantire il corretto funzionamento del programma e non corrompere i download, **non modificare o eliminare manualmente** nessuno di questi file e cartelle. **Attendi sempre che il programma comunichi il completamento dell'operazione.**

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
    
### Roadmap Futura e Contributi

Questo progetto è in continua evoluzione! Ecco alcune delle funzionalità previste:
-   Interfaccia Grafica (GUI) per un utilizzo ancora più semplice.
-   File di configurazione per salvare le impostazioni preferite.
-   Download e aggiornamenti concorrenti per gestire più operazioni contemporaneamente.
-   ...e altro ancora!

Hai un'idea o hai trovato un bug? Apri una **[Issue](https://github.com/VitoCammarata/YTManager/issues)**! I suggerimenti sono sempre benvenuti.

---

<a name="english"></a>
## 🇬🇧 YTManager (English Version)

### Description

A cross-platform application for simply and robustly downloading and synchronizing your YouTube videos and playlists to local files.

YTManager allows you to keep a local copy of your favorite content, offering full control over the format and management of your library.

### Key Features

*   📥 **Complete Playlist Management:**
    *   **Download:** Download an entire playlist, converting each video to your chosen format.
    *   **Update:** Synchronize a previously downloaded folder with its online version. It adds new videos, removes deleted ones, and reorders files to match the current playlist order.

*   🎬 **Single Video Downloads:**
    *   Not just playlists! You can quickly download one or more individual videos by providing their URLs.

*   🎧 **Wide Choice of Formats:**
    *   Choose the format you prefer. YTManager supports both **audio** formats (like `mp3`, `m4a`, `flac`) and **video** formats (like `mp4`, `mkv`).

*   🖼️ **Cover Art and Metadata Included:**
    *   For audio formats, the video's thumbnail is **automatically embedded as the file's cover art**, making your music library look beautiful and organized.

*   🛡️ **Safe and Robust:**
    *   The update process is protected by an **automatic backup system**. If anything goes wrong, your folder is restored to its original state, so you never lose a file.

**⚠️ Important Note:** The application works exclusively with **public or unlisted playlists and videos**. Private content is not supported because the application does not implement a login system, thus guaranteeing user privacy by not requiring access to your YouTube account.

### How to Use

1.  **Download the latest version** from the [**Releases**](https://github.com/VitoCammarata/YTManager/releases) section of this repository.
2.  Choose the appropriate file for your operating system.
3.  Place the executable in the folder where you want to store your downloads.
4.  Run the program and follow the on-screen instructions:
    *   **On Windows:** Double-click the `YTManager.exe` file. A terminal will automatically open to interact with the program.
    *   **On Linux:** Open a terminal in the folder where you placed the file and run it with the command `./YTManager`.

### Behind the Scenes

To ensure safe operation, YTManager creates several support files and folders within your playlist directories.

-   **State File (`.json`):** In each playlist folder, a hidden state file (e.g., `.PlaylistName.json`) is created. This file is fundamental for synchronization. On Windows, this file might be visible by default.

-   **Temporary Folder (`.tmp`):** During a playlist download, files are processed in a temporary folder which is automatically deleted once the process is complete.

-   **Intermediate Download Files:** During the download process, you will see various temporary files (e.g., video streams `.mp4`, audio `.m4a`, or cover art `.webp`) appear in the folder. **These files are essential for creating the final output file.**

-   **Backup Folder (`.bak`):** During an "Update," a backup copy of the playlist is created. In case of errors, your files are restored from here.

**⚠️ Warning:** To ensure the program works correctly and to avoid corrupting downloads, **do not manually modify or delete** any of these files or folders. **Always wait for the program to confirm the completion of the operation.**

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
    
### Future Roadmap and Contributions

This project is constantly evolving! Here are some of the planned features:
-   Graphical User Interface (GUI) for even easier use.
-   Configuration file to save preferred settings.
-   Concurrent downloads and updates to handle multiple operations at once.
-   ...and more!

Have an idea or found a bug? Open an **[Issue](https://github.com/VitoCammarata/YTManager/issues)**! Suggestions are always welcome.
