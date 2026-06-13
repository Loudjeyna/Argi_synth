"""
SynthAI — Mode C: FastAPI backend entry point.

Usage:
    uvicorn main:app --host 127.0.0.1 --port 8001 --reload
"""

import sys
import os

# must be set before importing sdv to avoid pickle errors in thread pools
os.environ["JOBLIB_SINGLE_THREADED"] = "1"
os.environ["LOKY_MAX_CPU_COUNT"] = "1"

# ensure project root is on sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from synthai.api.app import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=False)
