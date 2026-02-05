import sys
from pathlib import Path

# Add parent directory to path so we can import main
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from mangum import Mangum

# Vercel serverless function handler - wrap FastAPI with Mangum
handler = Mangum(app, lifespan="off")
