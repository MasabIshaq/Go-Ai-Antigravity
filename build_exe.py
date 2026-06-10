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
        "--clean",
        "--onefile",
        # Bundle static files, .env, and logo
        "--add-data=static;static",
        "--add-data=.env;.",
        "--add-data=logo.png;.",
        "--icon=logo.png",
        # Explicitly collect all submodules that PyInstaller misses
        "--collect-all", "uvicorn",
        "--collect-all", "fastapi",
        "--collect-all", "starlette",
        "--collect-all", "anyio",
        "--collect-all", "httpx",
        "--collect-all", "pydantic",
        "--collect-all", "email_validator",
        "--collect-all", "bcrypt",
        "--collect-all", "jwt",
        # Hidden imports for the app package itself
        "--hidden-import", "app",
        "--hidden-import", "app.main",
        "--hidden-import", "app.config",
        "--hidden-import", "app.database",
        "--hidden-import", "app.auth",
        "--hidden-import", "app.openrouter",
        "--hidden-import", "app.email_service",
        "--hidden-import", "app.brain",
        "--hidden-import", "app.storage",
        "--hidden-import", "app.admin_guard",
        "--hidden-import", "app.api_keys",
        # uvicorn runtime needs
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "uvicorn.loops",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "uvicorn.loops.asyncio",
        "--hidden-import", "uvicorn.protocols",
        "--hidden-import", "uvicorn.protocols.http",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.protocols.http.h11_impl",
        "--hidden-import", "uvicorn.protocols.http.httptools_impl",
        "--hidden-import", "uvicorn.protocols.websockets",
        "--hidden-import", "uvicorn.protocols.websockets.auto",
        "--hidden-import", "uvicorn.protocols.websockets.websockets_impl",
        "--hidden-import", "uvicorn.lifespan",
        "--hidden-import", "uvicorn.lifespan.off",
        "--hidden-import", "uvicorn.lifespan.on",
        "--hidden-import", "multiprocessing",
        "--hidden-import", "sqlite3",
        "run.py",
    ]

    result = subprocess.run(cmd)
    if result.returncode == 0:
        print("\n\n[SUCCESS] Build successful! You can find GoAi.exe in the 'dist' folder.")
        print("Run it by double-clicking GoAi.exe, then open http://localhost:8000")
    else:
        print("\n\n[ERROR] Build failed. See output above for details.")


if __name__ == "__main__":
    main()
