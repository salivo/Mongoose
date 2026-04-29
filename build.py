"""
Build script for Mongoose - works on both Windows and Linux.
Usage: python build.py
"""
import subprocess
import sys

# Install requirements and pyinstaller
print("Installing dependencies...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

# Build
print("Building executable...")
subprocess.check_call([sys.executable, "-m", "PyInstaller", "mongoose.spec", "--clean"])

print("\nBuild complete!")
print("Output: dist/Mongoose" + (".exe" if sys.platform == "win32" else ""))
