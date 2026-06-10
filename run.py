import sys
import multiprocessing
import uvicorn
from app.main import app

if __name__ == "__main__":
    multiprocessing.freeze_support()
    if getattr(sys, 'frozen', False):
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
