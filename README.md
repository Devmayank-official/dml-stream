# DML Stream - Enterprise Edition

<div align="center">

[![Release](https://img.shields.io/github/v/release/devmayank-official/dml-stream?style=for-the-badge&logo=github&color=blue)](https://github.com/devmayank-official/dml-stream/releases)
[![PyPI version](https://img.shields.io/pypi/v/dml-stream.svg?style=for-the-badge&logo=pypi&color=blue)](https://pypi.org/project/dml-stream/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/dml-stream?style=for-the-badge&logo=pypi&color=green)](https://pypi.org/project/dml-stream/)
[![Python Versions](https://img.shields.io/pypi/pyversions/dml-stream?style=for-the-badge&logo=python&color=green)](https://pypi.org/project/dml-stream/)
[![License](https://img.shields.io/github/license/devmayank-official/dml-stream?style=for-the-badge&logo=apache&color=blue)](https://github.com/devmayank-official/dml-stream/blob/main/LICENSE)

[![CI/CD](https://img.shields.io/github/actions/workflow/status/devmayank-official/dml-stream/ci-cd.yml?style=for-the-badge&logo=github-actions)](https://github.com/devmayank-official/dml-stream/actions)
[![Tests](https://img.shields.io/github/actions/workflow/status/devmayank-official/dml-stream/ci-cd.yml?style=for-the-badge&logo=pytest&label=Tests)](https://github.com/devmayank-official/dml-stream/actions)
[![Coverage](https://img.shields.io/codecov/c/github/devmayank-official/dml-stream?style=for-the-badge&logo=codecov)](https://codecov.io/gh/devmayank-official/dml-stream)
[![Docker Pulls](https://img.shields.io/docker/pulls/devmayank/dml-stream?style=for-the-badge&logo=docker)](https://ghcr.io/devmayank-official/dml-stream)
[![Docker Image Size](https://img.shields.io/docker/image-size/devmayank/dml-stream/latest?style=for-the-badge&logo=docker)](https://ghcr.io/devmayank-official/dml-stream)

[![Platforms](https://img.shields.io/badge/Platforms-Windows%20%7C%20macOS%20%7C%20Linux-blue?style=for-the-badge&logo=windows)](https://github.com/devmayank-official/dml-stream)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge&logo=python)](https://github.com/psf/black)
[![Security](https://img.shields.io/badge/security-bandit-green.svg?style=for-the-badge&logo=python)](https://github.com/PyCQA/bandit)

</div>

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

## 📖 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Configuration](#configuration)
- [Docker Support](#docker-support)
- [Development](#development)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**DML Stream** is an enterprise-level, production-ready Python application for downloading YouTube videos, audio, and playlists. Built with a modular architecture following best practices for scalability, maintainability, and security.

**Developed by:** [DML Labs](https://github.com/devmayank-official)  
**Lead Engineer:** [@devmayank-official](https://github.com/devmayank-official)

### Key Highlights

- **Modular Architecture**: Clean separation of concerns with dedicated modules
- **Type-Safe**: Full type hints throughout the codebase
- **Production Ready**: Comprehensive error handling, logging, and testing
- **Scalable**: Multi-threaded downloads, batch processing, and scheduled downloads
- **Modern Python**: Built with Python 3.9+ using latest features
- **Docker Support**: Multi-stage Dockerfile for production deployments
- **CI/CD Ready**: GitHub Actions workflows for automated testing and deployment

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

### Enterprise Features
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

# Install in development mode
pip install -e .
```

### Install FFmpeg

**Windows:**
```bash
choco install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update && sudo apt install ffmpeg
```

---

## 🚀 Quick Start

### Interactive Mode

```bash
dml-stream interactive
```

### Download a Video

```bash
dml-stream download --url "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Download Audio

```bash
dml-stream audio --url "https://www.youtube.com/watch?v=VIDEO_ID" --format mp3
```

### Download a Playlist

```bash
dml-stream playlist --url "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

---

## 📖 Usage

### CLI Commands

#### Download Video

```bash
# Basic download
dml-stream download --url "URL"

# With quality and format
dml-stream download -u "URL" -q 1080p -f mp4

# Fast multi-threaded download
dml-stream download -u "URL" --fast --threads 8
```

#### Download Audio

```bash
# Basic audio download
dml-stream audio --url "URL"

# With format selection
dml-stream audio -u "URL" -f flac
```

#### Download Playlist

```bash
# Download playlist videos
dml-stream playlist --url "URL"

# Download playlist as audio
dml-stream playlist -u "URL" --audio-only -f mp3
```

#### Service Commands

```bash
# Run daemon mode for scheduled downloads
dml-stream service --daemon

# List scheduled downloads
dml-stream service --list-scheduled

# View all processes
dml-stream service --view-processes
```

#### History & Config

```bash
# View recent downloads
dml-stream history --recent

# View statistics
dml-stream history --stats

# Show configuration
dml-stream config --show
```

### Using the Short Alias

```bash
dmls download --url "URL"
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
```

### Configuration File

The application uses `config.json` for persistent settings:

```json
{
    "default_output_folder": "downloads",
    "default_threads": 4,
    "max_threads": 12,
    "default_method": "normal",
    "log_level": "INFO"
}
```

---

## 🐳 Docker Support

### Pull from Registry

```bash
docker pull dmlabs/dml-stream:latest
```

### Run Interactive Mode

```bash
docker run -it \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/config:/app/config \
  dmlabs/dml-stream:latest
```

### Docker Compose

```yaml
version: '3.8'

services:
  dml-stream:
    image: dmlabs/dml-stream:latest
    container_name: dml-stream
    volumes:
      - ./downloads:/app/downloads
      - ./config:/app/config
      - ./logs:/app/logs
    environment:
      - DML_STREAM_DEFAULT_THREADS=4
    restart: unless-stopped
```

---

## 👨‍💻 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/devmayank-official/dml-stream.git
cd dml-stream

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=dml_stream --cov-report=html
```

---

## 📚 API Reference

### DownloadService

```python
from dml_stream.services import DownloadService

service = DownloadService(output_folder="downloads", threads=4)

# Get video info
yt = service.get_video_info("URL")

# Download video
path = service.download_video(yt, output_format="mp4")

# Download audio
path = service.download_audio(yt, output_format="mp3")
```

### PlaylistService

```python
from dml_stream.services import PlaylistService

service = PlaylistService(output_folder="downloads")

# Get playlist info
info = service.get_playlist_info("URL")

# Download playlist
results = service.download_playlist(url="URL", download_type="video")
```

---

## 🔧 Troubleshooting

### Common Issues

#### FFmpeg Not Found

```
FFmpegNotFoundError: FFmpeg is required for this operation
```

**Solution:** Install FFmpeg and ensure it's in your system PATH.

#### Download Fails with "No Streams Found"

**Solution:** 
- Check if the video URL is valid
- Some videos may have region restrictions
- Try updating pytubefix: `pip install --upgrade pytubefix`

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `pytest`
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

---

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

**Copyright 2026 DML Labs**

---

## 🙏 Acknowledgments

- [pytubefix](https://github.com/JuanBindez/pytubefix) - YouTube data extraction
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal output
- [Click](https://click.palletsprojects.com/) - CLI framework

---

## 📬 Contact

- **GitHub:** [@devmayank-official](https://github.com/devmayank-official)
- **Issues:** [GitHub Issues](https://github.com/devmayank-official/dml-stream/issues)
- **Email:** devmayank.inbox@gmail.com

---

**Made with ❤️ by DML Labs**

*Use responsibly and in compliance with all applicable laws and terms of service!*
