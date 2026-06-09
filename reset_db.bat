@echo off
echo Stopping any old database lock...
if exist "data\goai.db" del /f "data\goai.db"
if exist "data\goai.db-wal" del /f "data\goai.db-wal"
if exist "data\goai.db-shm" del /f "data\goai.db-shm"
echo Database reset. Now run: python run.py
