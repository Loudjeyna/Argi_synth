"""
Main entry point for the Synthetic Agricultural Data Generator
Run with: streamlit run app.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    import streamlit
    streamlit.run("app", width="full")