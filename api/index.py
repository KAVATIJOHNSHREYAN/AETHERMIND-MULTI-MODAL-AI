import sys
import os

# Add root directory to sys.path so app imports work in Vercel Serverless Functions
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.main import app

# Export FastAPI instance directly for Vercel Python Serverless ASGI Engine
app = app
