![Licenza MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Ultima Release](https://img.shields.io/github/v/release/TUO_USERNAME/TUO_REPO)

<!-- Ti consiglio di aggiungere qui uno screenshot o una GIF del programma in azione! -->
<!-- Esempio: <img src="screenshot.gif" width="700"> -->

---

[English Version](#english) | [Versione Italiana](#italiano)

---

<a name="italiano"></a>
## 🇮🇹 YTManager (Versione Italiana)

### Descrizione

YTManager ti permette di mantenere una copia locale delle tue playlist preferite di YouTube. Offre due funzionalità principali:
1.  **Download:** Scarica un'intera playlist, convertendo ogni video in un file MP3 di alta qualità. Il processo è resiliente e può essere ripreso in caso di interruzioni.
2.  **Update:** Sincronizza una cartella già scaricata con la versione online della playlist. Aggiunge i nuovi video, rimuove quelli eliminati e riordina i file per rispecchiare l'ordine attuale.

**⚠️ Nota Importante:** Lo script funziona esclusivamente con **playlist pubbliche o non in elenco**. Non è possibile scaricare playlist private.

### Come si Usa

L'utilizzo è identico sia su Windows che su Linux.

1.  **Scarica l'ultima versione** dalla sezione [**Releases**](https://github.com/TUO_USERNAME/TUO_REPO/releases) di questo repository.
2.  Scegli il file adatto al tuo sistema: `YTManager.exe` per Windows o `YTManager` per Linux.
3.  Metti l'eseguibile in una cartella vuota dove vuoi conservare le tue playlist.
4.  Esegui il programma direttamente dal terminale (`./YTManager` su Linux, `YTManager.exe` su Windows) e segui le istruzioni a schermo.

### Dietro le Quinte: Cosa Succede Davvero?

Per garantire un funzionamento sicuro e robusto, YTManager crea alcuni file e cartelle di supporto:

-   **File `.json` di Stato:** In ogni cartella di playlist, viene creato un file JSON nascosto (es. `.NomePlaylist.json`). Questo file è fondamentale: tiene traccia dei video scaricati e del loro ordine corretto, permettendo la sincronizzazione.
-   **Cartella `.tmp`:** Durante il download, i file vengono processati in una cartella temporanea nascosta. Questa viene eliminata automaticamente alla fine del processo.
-   **Cartella di Backup (`.bak`):** Quando si esegue un "Update", l'intera cartella della playlist viene prima copiata in una cartella di backup nascosta. Se qualcosa va storto, i tuoi file originali vengono ripristinati automaticamente, garantendo che non si perda mai nulla.

### Note Aggiuntive e Risoluzione Problemi

-   **Video Non Disponibili:** Lo script ignora automaticamente i video che YouTube segnala come `[Video non disponibile]` o `[Video eliminato]` all'interno di una playlist, evitando così errori.
-   **Account YouTube:** **Non è necessario** avere un account YouTube o essere loggati per scaricare playlist. Lo script funziona in modo anonimo, proprio come un browser in modalità incognito.
-   **Video con Restrizioni di Età:** Se una playlist contiene video con restrizioni di età, il download di *quel video specifico* potrebbe fallire. Questa è una limitazione imposta da YouTube per le richieste anonime.

### Per Sviluppatori (Build dal Codice Sorgente)

Se vuoi contribuire o compilare la tua versione personalizzata:

1.  **Prerequisiti:** Assicurati di avere **Python 3** e **pip** installati.
2.  **Clona il Repository:**
    ```bash
    git clone https://github.com/TUO_USERNAME/TUO_REPO.git
    cd TUO_REPO
    ```
3.  **Crea un Ambiente Virtuale e Installa le Dipendenze:** (Vedi il file [requirements.txt](requirements.txt))
    ```bash
    # Crea l'ambiente
    python -m venv venv
    # Attivalo (es. su Linux)
    source venv/bin/activate
    # Installa le librerie
    pip install -r requirements.txt
    ```
4.  **Esegui lo Script:**
    ```bash
    python YT_Manager.py
    ```

### Roadmap Futura e Contributi

Questo progetto è in continua evoluzione! Ecco alcune delle funzionalità previste:
-   **Interfaccia Grafica (GUI):** Per rendere il programma ancora più user-friendly.
-   **Scelta del Formato:** Possibilità di scaricare video completi o altri formati audio.
-   **File di Configurazione:** Per salvare le playlist e le impostazioni preferite.
-   **Download Paralleli:** Per velocizzare l'aggiornamento di più playlist.

Hai un'idea o hai trovato un bug? Apri una **[Issue](https://github.com/TUO_USERNAME/TUO_REPO/issues)**! I suggerimenti sono sempre benvenuti.

---
<a name="english"></a>
## 🇬🇧 YTManager (English Version)

### Description

YTManager allows you to keep a local copy of your favorite YouTube playlists. It offers two main features:
1.  **Download:** Downloads an entire playlist, converting each video into a high-quality MP3 file. The process is resilient and can be resumed in case of interruptions.
2.  **Update:** Synchronizes an already downloaded folder with the online version of the playlist. It adds new videos, removes deleted ones, and reorders the files to match the current order.

**⚠️ Important Note:** The script works exclusively with **public or unlisted playlists**. It cannot download private playlists.

### How to Use

The usage is identical on both Windows and Linux.

1.  **Download the latest version** from the [**Releases**](https://github.com/TUO_USERNAME/TUO_REPO/releases) section of this repository.
2.  Choose the appropriate file for your system: `YTManager.exe` for Windows or `YTManager` for Linux.
3.  Place the executable in an empty folder where you want to store your playlists.
4.  Run the program from your terminal (`./YTManager` on Linux, `YTManager.exe` on Windows) and follow the on-screen instructions.

### Behind the Scenes: What's Really Happening?

To ensure safe operation, YTManager creates a few support files and folders:

-   **State `.json` File:** In each playlist folder, a hidden JSON file is created (e.g., `.PlaylistName.json`). This file is crucial: it keeps track of downloaded videos and their correct order.
-   **`.tmp` Folder:** During downloads, files are processed in a hidden temporary folder, which is automatically deleted afterward.
-   **Backup Folder (`.bak`):** When running an "Update", the entire playlist folder is first copied to a hidden backup folder. If anything goes wrong, your original files are automatically restored.

### Additional Notes & Troubleshooting

-   **Unavailable Videos:** The script automatically ignores videos that YouTube marks as `[Video unavailable]` or `[Private video]` within a playlist, thus preventing errors.
-   **YouTube Account:** You **do not need** a YouTube account to download playlists. The script works anonymously, just like a browser in incognito mode.
-   **Age-Restricted Videos:** If a playlist contains age-restricted videos, the download for *that specific video* may fail due to YouTube's policies for anonymous requests.

### For Developers (Building from Source)

If you want to contribute or build your own version:

1.  **Prerequisites:** Ensure you have **Python 3** and **pip** installed.
2.  **Clone the Repository:**
    ```bash
    git clone https://github.com/TUO_USERNAME/TUO_REPO.git
    cd TUO_REPO
    ```
3.  **Create a Virtual Environment and Install Dependencies:** (See the [requirements.txt](requirements.txt) file)
    ```bash
    # Create the environment
    python -m venv venv
    # Activate it (e.g., on Linux)
    source venv/bin/activate
    # Install libraries
    pip install -r requirements.txt
    ```
4.  **Run the Script:**
    ```bash
    python YT_Manager.py
    ```

### Future Roadmap & Contributions

This project is constantly evolving! Here are some planned features:
-   **Graphical User Interface (GUI):** To make the program even more user-friendly.
-   **Format Selection:** Ability to download full videos or other audio formats.
-   **Configuration File:** To save preferred playlists and settings.
-   **Parallel Downloads:** To speed up the update process for multiple playlists.

Have an idea or found a bug? Please open an **[Issue](https://github.com/TUO_USERNAME/TUO_REPO/issues)**! Suggestions are always welcome.
