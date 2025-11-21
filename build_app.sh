#!/bin/bash
# Activate virtual environment
source venv/bin/activate

# Install PyInstaller if not present
pip install pyinstaller

# Clean previous builds
rm -rf build dist

# Run PyInstaller
pyinstaller --clean BirdHunt.spec

echo "Build complete. Executable is in dist/BirdHunt.app"
