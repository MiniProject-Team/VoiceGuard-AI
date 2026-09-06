from __future__ import annotations
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import uvicorn
from api.dependencies import load_api_config

def main():
    config = load_api_config(); parser = argparse.ArgumentParser(description="Run VoiceGuard API")
    parser.add_argument("--host", default=config["server"]["host"]); parser.add_argument("--port", type=int, default=config["server"]["port"]); parser.add_argument("--reload", action="store_true", default=config["server"].get("reload", False)); args = parser.parse_args()
    if config["runtime"]["environment"].lower() == "production" and args.reload: parser.error("Auto-reload is disabled in production.")
    uvicorn.run("api.main:app", host=args.host, port=args.port, reload=args.reload)
if __name__ == "__main__": main()
