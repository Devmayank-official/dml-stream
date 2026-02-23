#!/usr/bin/env bash
# =============================================================================
# DML Stream - Setup Script
# =============================================================================
# Developed by DML Labs
# Lead Engineer: @devmayank-official
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}DML Stream - Setup Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
major_version=$(echo $python_version | cut -d'.' -f1)
minor_version=$(echo $python_version | cut -d'.' -f2)

if [ "$major_version" -lt 3 ] || ([ "$major_version" -eq 3 ] && [ "$minor_version" -lt 9 ]); then
    echo -e "${RED}Error: Python 3.9 or higher is required (found $python_version)${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $python_version found${NC}"
echo ""

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
cd "$PROJECT_ROOT"
python3 -m venv .venv
echo -e "${GREEN}✓ Virtual environment created${NC}"
echo ""

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip
echo -e "${GREEN}✓ pip upgraded${NC}"
echo ""

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -e .[dev,docs]
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Install pre-commit hooks
echo -e "${YELLOW}Installing pre-commit hooks...${NC}"
pre-commit install
echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"
echo ""

# Check FFmpeg
echo -e "${YELLOW}Checking FFmpeg...${NC}"
if command -v ffmpeg &> /dev/null; then
    ffmpeg_version=$(ffmpeg -version | head -n1)
    echo -e "${GREEN}✓ FFmpeg found: $ffmpeg_version${NC}"
else
    echo -e "${YELLOW}⚠ FFmpeg not found. Install FFmpeg for format conversion:${NC}"
    echo -e "  macOS: brew install ffmpeg"
    echo -e "  Ubuntu: sudo apt install ffmpeg"
    echo -e "  Windows: choco install ffmpeg"
fi
echo ""

# Run tests
echo -e "${YELLOW}Running tests...${NC}"
pytest tests/unit -v --tb=short || echo -e "${YELLOW}⚠ Some tests failed${NC}"
echo ""

# Print summary
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "To activate the virtual environment, run:"
echo -e "  ${YELLOW}source .venv/bin/activate${NC}"
echo ""
echo -e "To start the application:"
echo -e "  ${YELLOW}dml-stream interactive${NC}"
echo -e "  ${YELLOW}# OR${NC}"
echo -e "  ${YELLOW}dmls interactive${NC}"
echo ""
echo -e "To run tests:"
echo -e "  ${YELLOW}pytest${NC}"
echo ""
echo -e "To run linters:"
echo -e "  ${YELLOW}pre-commit run --all-files${NC}"
echo ""
