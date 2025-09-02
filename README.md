# YTDL - Advanced YouTube Downloader

A powerful shell script for downloading YouTube videos and playlists with embedded subtitles, custom fonts and high-quality output formatting.

## 🚀 Features

- **Multi-Quality Downloads**: Support for 144p to 4K (2160p) video quality
- **Playlist Support**: Download entire playlists with automatic indexing
- **Embedded Subtitles**: Auto-download and embed English subtitles with custom styling
- **Custom Font Integration**: Uses Montara Gothic font for enhanced subtitle appearance  
- **Thumbnail Integration**: Embeds video thumbnails as cover art
- **Metadata Preservation**: Maintains video metadata and adds custom tags
- **Progress Tracking**: Real-time download progress with completion time statistics
- **Clean Output**: Automatically removes temporary files and organizes downloads

## 📋 Prerequisites

Before using this script ensure you have the following dependencies installed:

```bash
# Core dependencies
sudo apt install ffmpeg wget python3 python3-pip

# Install yt-dlp
pip3 install yt-dlp

# Install subtitle fixer (run once)
python3 -m pip install -U https://github.com/bindestriche/srt_fix/archive/refs/heads/master.zip
```

## 🛠️ Installation

1. Clone this repository:
```bash
git clone https://github.com/BetterCallShiv/YTDL.git
cd YTDL
```

2. Make the script executable:
```bash
chmod +x YTDL.sh
```

3. Run the script:
```bash
./YTDL.sh
```

## 📖 Usage

1. **Run the script**: Execute `./YTDL.sh`
2. **Paste YouTube URL**: Enter any YouTube video or playlist URL
3. **Select Quality**: Choose from available quality options (144p - 4K)
4. **Wait for completion**: The script handles everything automatically

### Supported URL Types
- Individual YouTube videos
- YouTube playlists
- YouTube channels (as playlists)

## 🎯 Output Features

- **Format**: High-quality MKV files with embedded content
- **Subtitles**: Styled ASS subtitles with custom font
- **Thumbnails**: Embedded as cover art
- **Metadata**: Complete video information preserved
- **Organization**: Clean file structure with descriptive names

## 📝 TODO

- [ ] **Parallel Download Support**: Implement concurrent downloads for playlist videos to significantly reduce total download time
- [ ] **Resume Capability**: Add support for resuming interrupted downloads
- [ ] **Download Queue Management**: Allow users to queue multiple URLs and process them sequentially
- [ ] **ETA Calculation**: Display estimated time remaining for current download and total queue
- [ ] **Custom Output Directory**: Allow users to specify custom download locations
- [ ] **Multiple Subtitle Languages**: Support for downloading and embedding multiple subtitle languages
- [ ] **Batch Processing**: Support for processing multiple URLs from a text file
- [ ] **Download History**: Keep track of previously downloaded videos to avoid duplicates
- [ ] **Error Handling**: Improve error messages and recovery mechanisms
- [ ] **Dependency Checking**: Add automatic dependency verification at startup
- [ ] **Update Mechanism**: Auto-update functionality for yt-dlp and script

## 👨‍💻 Author

**Shivam Raj** ([@BetterCallShiv](https://github.com/BetterCallShiv))
- Email: [bettercallshiv@gmail.com](mailto:bettercallshiv@gmail.com)
- GitHub: [github.com/BetterCallShiv](https://github.com/BetterCallShiv)
