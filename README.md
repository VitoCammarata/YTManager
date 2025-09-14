# YTManager

![Licenza MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Ultima Release](https://img.shields.io/github/v/release/VitoCammarata/YTManager)

<!-- Ti consiglio di aggiungere qui uno screenshot o una GIF del programma in azione! -->
<!-- Esempio: <img src="screenshot.gif" width="700"> -->


[English Version](#english) | [Versione Italiana](#italiano)

---

<a name="italiano"></a>
## 🇮🇹 YTManager 2.0

### La Tua Libreria YouTube Personale, Offline e Sotto Controllo

YTManager è un'applicazione semplice e potente che ti permette di scaricare video e playlist da YouTube e salvarli sul tuo computer. Crea la tua libreria musicale e video personale, accessibile ovunque e senza interruzioni.

### Funzionalità Principali

*   🚀 **Download e Sincronizzazione Intelligente**
    *   **Download:** Scarica intere playlist con un solo comando.
    *   **Update:** Sincronizza le tue cartelle locali con le playlist online. YTManager aggiunge automaticamente i nuovi video, rimuove quelli non più disponibili e riordina i file per te.

*   🎬 **Video Singoli al Volo**
    *   Hai bisogno di un solo video? Incolla l'URL e scaricalo rapidamente nel formato che preferisci.

*   ✨ **Pieno Controllo sulla Qualità Video**
    *   Scegli la risoluzione desiderata per i tuoi video, da 360p fino al 4K. Il programma scaricherà sempre la migliore qualità disponibile fino al limite da te impostato, ottimizzando così l'equilibrio tra qualità e dimensione dei file.

*   🎶 **Metadati e Copertine Automatici**
    *   Ogni file viene arricchito con i metadati essenziali: Artista, Album (dal titolo della playlist), Data e Numero Traccia. Per i formati che lo supportano, viene inclusa anche la copertina del video, garantendo una libreria multimediale sempre ordinata e facile da navigare.

*   📂 **Ampio Supporto di Formati**
    *   Scegli il formato perfetto per le tue esigenze, sia **audio** (`mp3`, `m4a`, `flac`, `opus`, `wav`) che **video** (`mp4`, `mkv`, `webm`).

*   🛡️ **Tranquillità e Sicurezza**
    *   Le operazioni più delicate, come il riordinamento dei file, sono protette da un sistema di **backup automatico**. In caso di problemi, i tuoi file sono al sicuro.

*   🧹 **Controllo Pulito dei Dati**
    *   Vuoi ricominciare da capo? Una semplice opzione nel menu ti permette di **cancellare tutti i dati di configurazione** dell'applicazione, senza mai toccare i tuoi file multimediali scaricati.

### Come si Usa

1.  **Scarica l'ultima versione** dalla sezione [**Releases**](https://github.com/VitoCammarata/YTManager/releases).
2.  Metti l'eseguibile nella cartella dove vuoi che vengano salvati i tuoi download.
3.  Esegui il programma e segui le semplici istruzioni a schermo.
    *   **Windows:** Fai doppio click su `YTManager.exe`.
    *   **Linux:** Apri un terminale ed esegui con `./YTManager`.

### Note Importanti

*   **Playlist Pubbliche:** L'applicazione funziona con video e playlist pubblici o non in elenco. I contenuti privati non sono supportati.
*   **Dati di Configurazione:** Per mantenere le tue cartelle di download pulite al 100%, YTManager ora salva tutti i suoi file di lavoro (stati delle playlist, backup, file temporanei) in una cartella di sistema dedicata (`AppData` su Windows, `~/.local/share` su Linux). I tuoi file scaricati non vengono mai toccati.

### Per Sviluppatori

Se vuoi contribuire o eseguire il codice sorgente:

1.  **Prerequisiti:** Assicurati di avere **Python 3** e **pip** installati.
2.  **Clona il Repository:**
    ```bash
    git clone https://github.com/VitoCammarata/YTManager.git
    cd YTManager
    ```
3.  **Crea un Ambiente Virtuale e Installa le Dipendenze:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Su Linux: source venv/bin/activate
    pip install -r requirements.txt
    ```

### Roadmap Futura

Il progetto è vivo e in crescita! Le prossime idee includono:
-   Un'interfaccia grafica (GUI) per un'esperienza ancora più intuitiva.
-   Un file di configurazione per salvare le impostazioni preferite (formato, qualità, ecc.).
-   Una versione per Android e IOS.
-   ...e molto altro!

Hai un'idea o hai trovato un bug? Apri una **[Issue](https://github.com/VitoCammarata/YTManager/issues)**! I suggerimenti sono sempre i benvenuti.

---

<a name="english"></a>
## 🇬🇧 YTManager 2.0

### Your Personal YouTube Library, Offline and On Your Terms

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
    *   **Windows:** Double-click `YTManager.exe`.
    *   **Linux:** Open a terminal and run it with `./YTManager`.

### Important Notes

*   **Public Content:** The application works with public or unlisted videos and playlists. Private content is not supported.
*   **Configuration Data:** To keep your download folders 100% clean, YTManager now saves all its working files (playlist states, backups, temp files) in a dedicated system folder (`AppData` on Windows, `~/.local/share` on Linux). Your downloaded media files are never touched.

### For Developers

If you want to contribute or run the source code:

1.  **Prerequisites:** Make sure you have **Python 3** and **pip** installed.
2.  **Clone the Repository:**
    ```bash
    git clone https://github.com/VitoCammarata/YTManager.git
    cd YTManager
    ```
3.  **Create a Virtual Environment and Install Dependencies:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # On Linux: source venv/bin/activate
    pip install -r requirements.txt
    ```

### Future Roadmap

This project is alive and growing! Future ideas include:
-   A Graphical User Interface (GUI) for an even more intuitive experience.
-   A configuration file to save preferred settings (format, quality, etc.).
-   Android and IOS app.
-   ...and much more!

Have an idea or found a bug? Open an **[Issue](https://github.com/VitoCammarata/YTManager/issues)**! Suggestions are always welcome.
Have an idea or found a bug? Open an **[Issue](https://github.com/VitoCammarata/YTManager/issues)**! Suggestions are always welcome.
