@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
echo Starting Go Ai API at http://localhost:8000
echo API docs: http://localhost:8000/docs
python run.py
