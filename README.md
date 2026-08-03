# YTDL - Advanced YouTube Downloader

A powerful, interactive Python-based command-line application for downloading YouTube videos and playlists. It features a beautiful terminal UI, automatic subtitle styling, custom font embedding, metadata injection and parallel processing.

## 🚀 Features

- **Beautiful Interactive UI**: Built with `Rich`, featuring live progress bars, real-time download/encoding stats and clean menus.
- **Multi-Quality Downloads**: Seamlessly pick formats ranging from 144p all the way up to 4K (2160p).
- **Advanced Playlist Support**: Automatically detects playlists, creates dedicated subdirectories for them and downloads the videos in parallel.
- **Subtitle Processing**: Automatically probes YouTube for available subtitle tracks, downloads them, converts them to .ass and embeds them into the final MKV container with custom styling.
- **Custom Fonts**: Embeds custom fonts directly into the MKV so your subtitles look gorgeous on any media player.
- **Thumbnail & Metadata Injection**: Automatically embeds the highest quality video thumbnail as cover art and preserves crucial video metadata.
- **Parallel Downloading**: Queue multiple URLs or process massive playlists using multi-threading (up to 5 concurrent workers) to saturate your bandwidth.
- **Resilient Error Recovery**: Smart retry logic automatically catches YouTube `403 Forbidden` disconnects and auto-restarts the download exactly where it left off.
- **Batch Processing**: Feed it a `.txt` file full of URLs and walk away while it processes the entire batch.
- **Dependency Management**: Built-in dependency checker (ffmpeg, yt-dlp, etc.) and a one-click `yt-dlp` updater right from the menu.

## 📋 Prerequisites

Before using this script, ensure you have the following dependencies installed on your system (Linux / WSL / Windows):

```bash
# 1. Install FFmpeg (Required for audio/video muxing)
# Debian/Ubuntu:
sudo apt update && sudo apt install ffmpeg

# 2. Install Python 3 and pip
sudo apt install python3 python3-pip

# 3. Install required Python packages
pip install yt-dlp rich requests srt_fix
```

## 🛠️ Installation & Usage

1. Clone this repository:
```bash
git clone https://github.com/BetterCallShiv/YTDL.git
cd YTDL
```

2. Run the interactive script:
```bash
python YTDL.py
```

### Modes of Operation
You can launch the script in interactive mode or pass arguments directly:
- **Interactive Mode**: `python YTDL.py` (Brings up the visual main menu)
- **Fast Single Video**: `python YTDL.py "https://youtube.com/watch?v=..." -q 1080`
- **Fast Playlist**: `python YTDL.py "https://youtube.com/playlist?..." -q 720`
- **Batch File**: `python YTDL.py --batch urls.txt -q best`
- **Update Tool**: `python YTDL.py --update`

## ⚙️ Configuration & Customization
- **Fonts**: Place your custom fonts inside a `fonts.zip` archive or directly define a `.ttf` file path in the `Settings` menu.
- **Output Directory**: Change your default save location inside the interactive `Settings` menu.
- **Numbering**: Toggle automatic prefix numbering (e.g., `001 - Video Title.mkv`) for playlists to keep them perfectly ordered.

## 📝 Changelog / Completed TODOs

- [x] **Parallel Download Support**: Implemented concurrent downloads for playlist videos using ThreadPoolExecutor.
- [x] **Resume Capability**: yt-dlp handles chunk resuming natively, backed by our smart exception-catching retry loops.
- [x] **Download Queue Management**: Interactive queue builder added.
- [x] **Subtitle Merging**: Sequential ffmpeg pass implemented to securely embed multiple languages.
- [x] **ETA Calculation**: Live speeds, file sizes, and ETA tracked for both download and ffmpeg muxing phases.
- [x] **Custom Output Directory**: Configurable via the settings menu.
- [x] **Multiple Subtitle Languages**: Real-time probing allows multi-select (e.g., `1,3,4`).
- [x] **Batch Processing**: Fully supported via file ingestion.
- [x] **Error Handling**: Implemented aggressive retry loops for 429/403 HTTP drops and bypassed minor yt-dlp post-processing errors.
- [x] **Dependency Checking**: Automated pre-flight checks added.
- [x] **Update Mechanism**: Auto-update yt-dlp option integrated into the main menu.

## 👨‍💻 Author

**Shivam Raj** ([@BetterCallShiv](https://github.com/BetterCallShiv))
- Email: [bettercallshiv@gmail.com](mailto:bettercallshiv@gmail.com)
- GitHub: [github.com/BetterCallShiv](https://github.com/BetterCallShiv)


