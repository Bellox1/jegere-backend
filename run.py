"""
Start script for Football Prediction FastAPI Backend.
Runs on port 8001 (or fallback 8002).
"""
import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Load .env if present
env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(env_file):
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

import uvicorn

if __name__ == "__main__":
    from backend.api.main import app
    port = int(os.environ.get("PORT", 8001))
    backend_url = os.environ.get("BACKEND_URL", f"http://localhost:{port}")
    print(f"Starting Football AI Prediction Engine on {backend_url}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
