import sys
from pathlib import Path

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import with error handling
try:
    from main import app
    from mangum import Mangum

    # Create handler
    handler = Mangum(app, lifespan="auto", api_gateway_base_path="/")

except Exception as e:
    # Fallback handler for debugging
    from fastapi import FastAPI
    from mangum import Mangum

    debug_app = FastAPI()

    @debug_app.get("/")
    async def root():
        return {
            "error": "Import failed",
            "message": str(e),
            "type": type(e).__name__
        }

    handler = Mangum(debug_app)
