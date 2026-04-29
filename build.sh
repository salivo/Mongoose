#!/bin/bash
# Build Mongoose as a standalone executable (Linux)
# For Windows, run: python build.py

echo "Installing PyInstaller..."
pip install pyinstaller

echo "Building Mongoose..."
pyinstaller mongoose.spec --clean

echo ""
echo "Done! Binary is at: dist/Mongoose"
