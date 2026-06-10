import os
import subprocess
import sys
from pathlib import Path

def main():
    print("Preparing to build Go Ai Executable...")
    
    # Ensure pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
    # Check for .env file
    if not Path('.env').exists() and Path('.env.example').exists():
        import shutil
        print("Copying .env.example to .env...")
        shutil.copy('.env.example', '.env')

    print("Running PyInstaller...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=GoAi",
        "--noconfirm",
        "--onefile", # Package into a single EXE
        "--add-data=static;static",
        "--add-data=.env;.",
        "--add-data=logo.png;.",
        "--icon=logo.png",
        "run.py"
    ]
    
    # Run the command
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print("\n\n[SUCCESS] Build successful! You can find GoAi.exe in the 'dist' folder.")
    else:
        print("\n\n[ERROR] Build failed.")

if __name__ == "__main__":
    main()
