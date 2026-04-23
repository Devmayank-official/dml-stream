# DML Stream: A Scalable, Module-Driven Media Acquisition Framework

<div align="center">

<!-- Version & Release -->
[![Version](https://img.shields.io/badge/version-2.5.1-3776AB?style=for-the-badge&logo=semantic-release&logoColor=white)](https://github.com/devmayank-official/dml-stream/releases)
[![License](https://img.shields.io/badge/license-Apache--2.0-D22128?style=for-the-badge&logo=apache&logoColor=white)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)

<!-- Platform Support -->
[![Windows](https://img.shields.io/badge/-Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/devmayank-official/dml-stream)
[![macOS](https://img.shields.io/badge/-macOS-000000?style=for-the-badge&logo=apple&logoColor=white)](https://github.com/devmayank-official/dml-stream)
[![Linux](https://img.shields.io/badge/-Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)](https://github.com/devmayank-official/dml-stream)
[![Architecture](https://img.shields.io/badge/architecture-amd64%20%7C%20arm64-0078D4?style=for-the-badge&logo=linux&logoColor=white)](https://github.com/devmayank-official/dml-stream)

<!-- Package Management -->
[![PyPI](https://img.shields.io/badge/pypi-dml--stream-3776AB?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/dml-stream/)
[![Docker](https://img.shields.io/badge/docker-ghcr.io-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://github.com/devmayank-official/dml-stream/pkgs/container/dml-stream)

<!-- CI/CD -->
[![Code Quality](https://img.shields.io/badge/code%20quality-A+-0078D4?style=for-the-badge&logo=sonarcloud&logoColor=white)](https://github.com/devmayank-official/dml-stream)
[![Coverage](https://img.shields.io/badge/coverage-85%25-0078D4?style=for-the-badge&logo=codecov&logoColor=white)](https://codecov.io/gh/devmayank-official/dml-stream)

<!-- Security -->
[![Security](https://img.shields.io/badge/security-bandit-0078D4?style=for-the-badge&logo=python&logoColor=white)](https://github.com/PyCQA/bandit)
[![Vulnerabilities](https://img.shields.io/badge/vulnerabilities-0-0078D4?style=for-the-badge&logo=snyk&logoColor=white)](https://snyk.io)

<!-- Code Style -->
[![Code Style](https://img.shields.io/badge/code%20style-black-000000?style=for-the-badge&logo=black&logoColor=white)](https://github.com/psf/black)
[![Type Checked](https://img.shields.io/badge/type%20checked-mypy-0078D4?style=for-the-badge&logo=python&logoColor=white)](https://mypy-lang.org)
[![Linted](https://img.shields.io/badge/linted-ruff-0078D4?style=for-the-badge&logo=python&logoColor=white)](https://docs.astral.sh/ruff)

<!-- Enterprise -->
[![Enterprise Ready](https://img.shields.io/badge/enterprise-ready-0078D4?style=for-the-badge&logo=microsoft&logoColor=white)](https://github.com/devmayank-official/dml-stream)
[![Production](https://img.shields.io/badge/production-ready-0078D4?style=for-the-badge&logo=statuspage&logoColor=white)](https://github.com/devmayank-official/dml-stream)
[![Maintained](https://img.shields.io/badge/maintained-yes-0078D4?style=for-the-badge&logo=github&logoColor=white)](https://github.com/devmayank-official/dml-stream)

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [What's New in v2.5](#-whats-new-in-v25)
- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [CLI Commands Reference](#-cli-commands-reference)
- [Architecture](#-architecture)
- [Configuration](#-configuration)
- [Docker Support](#-docker-support)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**DML Stream** is a modern, type-safe Python framework designed for high-volume media extraction. It leverages a modular manager-pattern to orchestrate complex download batches and scheduled workloads. With full Docker support and a persistent SQLite storage layer, it bridges the gap between simple CLI tools and enterprise media ingestion pipelines.

**v2.5** introduces **35+ CLI commands** organized into 8 command groups, making it the most comprehensive CLI toolkit for advanced YouTube content management.

**Developed by:** [DML Labs](https://github.com/devmayank-official)  
**Lead Engineer:** [@devmayank-official](https://github.com/devmayank-official)  
**Version:** 2.5.1 (April 2026)

### Key Highlights

- **A Scalable Acquisition Framework** - Designed for volume and reliability
- **Module-Driven Architecture** - Clean separation of concerns with dedicated managers
- **Persistent State Management** - SQLite-driven history and scheduling
- **35+ CLI Commands** - Comprehensive command surface for all operations
- **Type-Safe & Production Ready** - Full type hints and rigorous error handling
- **Modern Infrastructure** - Docker support and CI/CD ready
- **Cross-Platform** - Windows, macOS, Linux support

---

## ✨ What's New in v2.5

### 🔍 Info Commands (NEW)
Get detailed information before downloading:
- `info video` - Video details (title, duration, views, channel)
- `info formats` - All available streams with quality/size/codec
- `info thumbnail` - Preview/download thumbnail
- `info subtitle` - List available subtitle languages
- `info metadata` - Full metadata dump (JSON/table)
- `info channel` - Channel statistics + video count

### 📁 File Operations (NEW)
Post-download file manipulation:
- `file-ops convert` - Format conversion via FFmpeg
- `file-ops merge` - Mux separate video/audio streams
- `file-ops extract-audio` - Strip audio from video file
- `file-ops compress` - Reduce file size with quality presets

### 💾 Storage Management (NEW)
Disk space and download management:
- `storage status` - Disk usage, download folder stats
- `storage analyze` - Largest files, duplicates, orphans
- `storage prune` - Delete incomplete/temp files
- `storage move` - Relocate downloads folder
- `storage clean-cache` - Wipe application + yt-dlp cache
- `storage dedupe` - Find and remove duplicate downloads

### ⚙️ Enhanced Config (NEW)
Configuration management:
- `config paths` - Show all directories (downloads, logs, cache, DB)
- `config export` - Export config to file
- `config import` - Import config from file

### 🛠️ Dev Commands (NEW)
Developer tooling:
- `dev shell` - Python REPL with app context
- `dev reset-db` - Wipe and recreate history DB
- `dev seed` - Populate test data
- `dev benchmark` - Download speed test
- `dev debug` - Verbose raw stream info
- `dev export-logs` - Zip and export logs

### 🏥 System Commands (NEW)
System diagnostics:
- `system doctor` - Health check (FFmpeg, Python, deps, disk, network)
- `system info` - OS, Python version, package versions
- `system cleanup` - Clean cache (same as storage clean-cache)
- `system update` - Self-update via pip
- `system deps` - Verify all dependencies installed
- `system report` - Generate full diagnostic report (shareable)

### Backward Compatibility
All v2.0 commands continue to work:
- `dml-stream download` → `dml-stream download video`
- `dml-stream audio` → `dml-stream download audio`
- `dml-stream playlist` → `dml-stream download playlist`

---

## ✨ Features

### Download Capabilities
- 🎥 **Single Video Download** - Download individual YouTube videos in various qualities
- 🎵 **Audio Extraction** - Extract and download audio in multiple formats (MP3, FLAC, M4A, etc.)
- 📺 **Playlist Download** - Download entire YouTube playlists with progress tracking
- 🔄 **Resume Support** - Resume interrupted downloads automatically
- ⚡ **Fast Mode** - Multi-threaded downloads for maximum speed
- 🎛️ **Speed Limiting** - Control download bandwidth

### Advanced Features
- ⏰ **Scheduled Downloads** - Schedule downloads for specific times
- 📦 **Batch Processing** - Queue multiple downloads sequentially
- 📊 **Process Monitoring** - Real-time tracking of all download processes
- 📝 **Download History** - Track and manage download history
- 🔄 **Format Conversion** - Convert between formats using FFmpeg
- 🎨 **Rich CLI** - Beautiful terminal interface with progress bars

### Enterprise Features (v2.5)
- 🔍 **Info Commands** - Inspect videos before downloading
- 📁 **File Operations** - Post-download processing
- 🗄️ **Storage Management** - Disk space optimization
- 🔒 **Secure** - No hardcoded secrets, environment variable support
- 📋 **Configurable** - Comprehensive configuration system
- 🐳 **Containerized** - Docker support for easy deployment
- 🧪 **Tested** - Unit and integration test coverage
- 📖 **Documented** - Comprehensive API documentation
- 🔍 **Linted** - Code quality checks with Black, Ruff, MyPy

---

## 🏗️ Architecture

```
dml-stream/
├── .github/workflows/       # CI/CD pipelines
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
├── src/
│   └── dml_stream/          # Main package
│       ├── __init__.py      # Package initialization
│       ├── __main__.py      # Entry point
│       ├── cli/             # Command-line interface
│       │   ├── commands/    # Command groups (v2.5)
│       │   │   ├── info.py        # 🔍 Info commands
│       │   │   ├── download.py    # 💾 Download commands
│       │   │   ├── file_ops.py    # 📁 File operations
│       │   │   ├── storage.py     # 🗄️ Storage management
│       │   │   ├── config_cli.py  # ⚙️ Configuration
│       │   │   ├── dev.py         # 🛠️ Developer tools
│       │   │   ├── system.py      # 🏥 System commands
│       │   │   ├── history.py     # 📜 History
│       │   │   └── service.py     # 🔧 Service
│       │   ├── interactive.py # Interactive mode
│       │   └── main.py      # Main entry point
│       ├── config/          # Configuration management
│       ├── core/            # Core components
│       ├── managers/        # Business logic managers
│       ├── models/          # Data models
│       ├── services/        # Business services
│       └── utilities/       # Utility functions
├── tests/
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── .env.example            # Environment template
├── Dockerfile              # Docker build configuration
├── docker-compose.yml      # Docker Compose (v2.5)
├── pyproject.toml          # Project configuration (PEP 621)
└── README.md               # This file
```

---

## 📦 Installation

### Method 1: pip (Recommended)

```bash
# Install from PyPI
pip install dml-stream
```

### Method 2: From Source

```bash
# Clone the repository
git clone https://github.com/devmayank-official/dml-stream.git
cd dml-stream

# Run setup script (recommended)
# Windows:
scripts\setup.bat

# Linux/macOS:
scripts/setup.sh

# Or manual installation:
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev,docs]
```

### Install FFmpeg (Required for some features)

**Windows:**
```bash
# Using Chocolatey
choco install ffmpeg

# Using Scoop
scoop install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

---

## 🚀 Quick Start

### Interactive Mode (Recommended for Beginners)

```bash
dml-stream interactive
# OR using short alias
dmls interactive
```

### Download a Video

```bash
# Basic download
dml-stream download video --url "https://www.youtube.com/watch?v=VIDEO_ID"

# With quality and format
dml-stream download video -u "URL" -q 1080p -f mp4

# Fast multi-threaded download
dml-stream download video -u "URL" --fast --threads 8
```

### Download Audio

```bash
# Basic audio download
dml-stream download audio --url "https://www.youtube.com/watch?v=VIDEO_ID"

# With format selection
dml-stream download audio -u "URL" -f flac
```

### Download a Playlist

```bash
# Download playlist videos
dml-stream download playlist --url "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Download playlist as audio
dml-stream download playlist -u "URL" --audio-only -f mp3
```

### Get Video Info (NEW in v2.5)

```bash
# Get video information
dml-stream info video "https://www.youtube.com/watch?v=VIDEO_ID"

# List available formats
dml-stream info formats "URL"

# View thumbnail
dml-stream info thumbnail "URL"
```

### System Health Check (NEW in v2.5)

```bash
# Check system health
dml-stream system doctor

# View system info
dml-stream system info
```

---

## 📖 CLI Commands Reference

### 🔍 Info Commands

Get information about YouTube videos, playlists, and channels.

```bash
# Get detailed video information
dml-stream info video <url>
dml-stream info video <url> --json

# List all available download formats
dml-stream info formats <url>
dml-stream info formats <url> --type progressive
dml-stream info formats <url> --json

# Preview or download video thumbnail
dml-stream info thumbnail <url>
dml-stream info thumbnail <url> --download
dml-stream info thumbnail <url> -o thumb.jpg

# List available subtitle languages
dml-stream info subtitle <url>
dml-stream info subtitle <url> --json

# Get full metadata dump
dml-stream info metadata <url>
dml-stream info metadata <url> --format json
dml-stream info metadata <url> -o metadata.json

# Get channel information
dml-stream info channel <url>
dml-stream info channel <url> --json
```

### 💾 Download Commands

Download videos, audio, and playlists from YouTube.

```bash
# Download a single video
dml-stream download video --url <url>
dml-stream download video -u <url> -q 1080p -f mp4
dml-stream download video -u <url> --fast --threads 8

# Download audio only
dml-stream download audio --url <url>
dml-stream download audio -u <url> -f flac
dml-stream download audio -u <url> --fast

# Download a playlist
dml-stream download playlist --url <url>
dml-stream download playlist -u <url> --audio-only -f mp3
dml-stream download playlist -u <url> --max-videos 10
```

**Backward Compatibility (v2.0 commands still work):**
```bash
dml-stream download -u <url>      # Same as 'download video'
dml-stream audio -u <url>          # Same as 'download audio'
dml-stream playlist -u <url>       # Same as 'download playlist'
```

### 📁 File Operations

File manipulation and conversion commands.

```bash
# Convert format
dml-stream file-ops convert video.mkv --to mp4
dml-stream file-ops convert video.mp4 --to mp3 --quality high
dml-stream file-ops convert video.mov --to mp4 --quality lossless

# Merge video and audio
dml-stream file-ops merge --video video.mp4 --audio audio.m4a
dml-stream file-ops merge -v video.mp4 -a audio.mp3 -o output.mkv

# Extract audio from video
dml-stream file-ops extract-audio video.mp4
dml-stream file-ops extract-audio video.mkv --format flac --quality 320k

# Compress video
dml-stream file-ops compress video.mp4 --quality medium
dml-stream file-ops compress video.mkv --max-size 50MB
```

### 🗄️ Storage Management

Storage management and disk space utilities.

```bash
# Show disk usage and stats
dml-stream storage status

# Analyze storage for largest files and duplicates
dml-stream storage analyze
dml-stream storage analyze --top 20
dml-stream storage analyze --find-duplicates

# Delete temporary and incomplete files
dml-stream storage prune
dml-stream storage prune --dry-run
dml-stream storage prune --include-incomplete

# Relocate downloads folder
dml-stream storage move /path/to/new/folder
dml-stream storage move D:\Downloads --copy

# Wipe application cache
dml-stream storage clean-cache
dml-stream storage clean-cache --dry-run
dml-stream storage clean-cache --include-ytdlp

# Find and remove duplicates
dml-stream storage dedupe
dml-stream storage dedupe --dry-run
dml-stream storage dedupe --keep oldest
```

### ⚙️ Configuration

Configuration management commands.

```bash
# Show current configuration
dml-stream config show
dml-stream config show --json

# Set configuration value
dml-stream config set default_threads 8
dml-stream config set log_level DEBUG

# Reset to defaults
dml-stream config reset
dml-stream config reset --force

# Show all directory paths
dml-stream config paths

# Export configuration
dml-stream config export config.json
dml-stream config export /path/to/backup.json

# Import configuration
dml-stream config import config.json
dml-stream config import /path/to/backup.json --force
```

### 🛠️ Developer Commands

Developer tools and debugging commands.

```bash
# Python REPL with app context
dml-stream dev shell

# Wipe and recreate history database
dml-stream dev reset-db
dml-stream dev reset-db --force

# Populate test data
dml-stream dev seed
dml-stream dev seed --count 50

# Download speed benchmark
dml-stream dev benchmark <url>
dml-stream dev benchmark <url> --threads 8 --duration 30

# Verbose debug information
dml-stream dev debug <url>
dml-stream dev debug <url> --full

# Export logs for debugging
dml-stream dev export-logs
dml-stream dev export-logs -o logs.zip
dml-stream dev export-logs --include-system
```

### 🏥 System Commands

System diagnostics and maintenance.

```bash
# Health check and diagnostics
dml-stream system doctor
dml-stream system doctor --verbose

# System information
dml-stream system info

# Clean cache and temp files
dml-stream system cleanup
dml-stream system cleanup --dry-run

# Self-update via pip
dml-stream system update
dml-stream system update --dry-run
dml-stream system update --pre

# Verify dependencies
dml-stream system deps
dml-stream system deps --outdated

# Generate diagnostic report
dml-stream system report
dml-stream system report --format json
dml-stream system report --format markdown
dml-stream system report -o report.md
```

### 🔧 Service Commands

Background services and automation.

```bash
# Run daemon mode for scheduled downloads
dml-stream service --daemon

# List scheduled downloads
dml-stream service --list-scheduled

# Cancel scheduled download
dml-stream service --cancel-scheduled <id>

# Create batch download
dml-stream service --batch "My Playlist"

# List batch downloads
dml-stream service --list-batch

# View tracked processes
dml-stream service --view-processes
```

### 📜 History Commands

View and manage download history.

```bash
# Show recent downloads
dml-stream history --recent
dml-stream history --recent --limit 20

# Show statistics
dml-stream history --stats

# Search history
dml-stream history --search "python"

# Show failed downloads
dml-stream history --failed

# Export history
dml-stream history --export history.json
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# Set default output folder
export DML_STREAM_DEFAULT_OUTPUT_FOLDER=~/Downloads

# Set download threads
export DML_STREAM_DEFAULT_THREADS=8

# Set log level
export DML_STREAM_LOG_LEVEL=DEBUG

# Enable/disable features
export DML_STREAM_ENABLE_SCHEDULED_DOWNLOADS=true
export DML_STREAM_ENABLE_BATCH_DOWNLOADS=true
export DML_STREAM_ENABLE_DOWNLOAD_HISTORY=true
```

### Configuration File

The application uses `config.json` for persistent settings:

```json
{
    "default_output_folder": "downloads",
    "default_threads": 4,
    "max_threads": 12,
    "default_method": "normal",
    "log_level": "INFO",
    "enable_scheduled_downloads": true,
    "enable_batch_downloads": true,
    "enable_process_tracking": true,
    "enable_download_history": true
}
```

---

## 🐳 Docker Support

### Pull from Registry

```bash
# From GitHub Container Registry
docker pull ghcr.io/devmayank-official/dml-stream:latest

# From Docker Hub (v2.5+)
docker pull dmlabs/dml-stream:latest
```

### Run Interactive Mode

```bash
docker run -it \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/config:/app/config \
  ghcr.io/devmayank-official/dml-stream:latest
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# Run interactive CLI
docker-compose run --rm dml-cli

# Run daemon for scheduled downloads
docker-compose up -d dml-daemon

# View logs
docker-compose logs -f dml-stream

# Stop all services
docker-compose down
```

### Docker Compose with Custom Configuration

```yaml
version: '3.8'

services:
  dml-stream:
    image: ghcr.io/devmayank-official/dml-stream:latest
    container_name: dml-stream
    volumes:
      - ./downloads:/app/downloads
      - ./config:/app/config
      - ./logs:/app/logs
    environment:
      - DML_STREAM_DEFAULT_THREADS=4
      - DML_STREAM_LOG_LEVEL=INFO
      - TZ=America/New_York
    restart: unless-stopped
```

---

## 👨‍💻 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/devmayank-official/dml-stream.git
cd dml-stream

# Run setup script
# Windows:
scripts\setup.bat

# Linux/macOS:
scripts/setup.sh

# Or manual setup:
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev,docs]
pre-commit install
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=dml_stream --cov-report=html

# Run specific test category
pytest tests/unit -v
pytest tests/integration -v -k "not network"
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/

# Run all checks
pre-commit run --all-files
```

### Build Documentation

```bash
cd docs
make html

# Open in browser
open _build/html/index.html  # macOS
xdg-open _build/html/index.html  # Linux
start _build/html/index.html  # Windows
```

---

## 🔧 Troubleshooting

### Common Issues

#### FFmpeg Not Found

```
FFmpegNotFoundError: FFmpeg is required for this operation
```

**Solution:** Install FFmpeg and ensure it's in your system PATH.

```bash
# Verify installation
ffmpeg -version

# Windows: Add to PATH or reinstall
choco install ffmpeg

# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

#### Download Fails with "No Streams Found"

**Solution:**
- Check if the video URL is valid
- Some videos may have region restrictions
- Try updating pytubefix: `pip install --upgrade pytubefix`

#### Permission Denied on File Operations

**Solution:**
- Check file permissions on output directory
- Run as administrator (Windows) or with sudo (Linux/macOS) if necessary
- Ensure output directory exists and is writable

#### Docker Container Fails to Start

**Solution:**
```bash
# Check logs
docker-compose logs dml-stream

# Verify volumes
docker-compose run --rm dml-stream ls -la /app/downloads

# Rebuild container
docker-compose build --no-cache
docker-compose up -d
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `pytest`
5. Run linters: `pre-commit run --all-files`
6. Commit: `git commit -m 'Add amazing feature'`
7. Push: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write tests for new features
- Update documentation
- Use descriptive commit messages

---

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

**Copyright 2026 DML Labs**

---

## 🙏 Acknowledgments

- [pytubefix](https://github.com/JuanBindez/pytubefix) - YouTube data extraction
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal output
- [Click](https://click.palletsprojects.com/) - CLI framework
- [FFmpeg](https://ffmpeg.org/) - Media processing

---

## 📬 Contact

- **GitHub:** [@devmayank-official](https://github.com/devmayank-official)
- **Issues:** [GitHub Issues](https://github.com/devmayank-official/dml-stream/issues)
- **Email:** devmayank.inbox@gmail.com
- **Documentation:** [Read the Docs](https://dml-stream.readthedocs.io)

---

## 📊 Version History

### v2.5.0 (February 2026)
- **NEW:** 35+ CLI commands across 8 command groups
- **NEW:** Info commands for video inspection
- **NEW:** File operations for post-download processing
- **NEW:** Storage management commands
- **NEW:** Developer tools and debugging
- **NEW:** System diagnostics and health checks
- **ENHANCED:** Docker multi-stage builds
- **ENHANCED:** CI/CD with GitHub Actions
- **ENHANCED:** Cross-platform compatibility

### v2.0.0 (Previous Release)
- Basic download commands
- Playlist support
- Audio extraction
- Scheduled downloads
- Batch processing

---

## ⚠️ LEGAL DISCLAIMER

**Please read carefully before using this software:**

This software is provided for educational purposes only. YouTube's Terms of Service generally prohibit downloading videos from their platform, except for videos you have created or have explicit permission to download. Using this software may violate YouTube's Terms of Service and could result in your YouTube account being terminated.

**By using this software, you acknowledge:**
- You understand YouTube's Terms of Service prohibit most downloading activities
- You will only use this software in compliance with applicable laws and YouTube's Terms of Service
- You will only download videos that you have created or have explicit permission to download
- You assume all legal responsibility for your use of this software
- The developers are not responsible for any legal consequences resulting from your use of this software

---

**Made with ❤️ by DML Labs**

*Use responsibly and in compliance with all applicable laws and terms of service!*
