from __future__ import annotations
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 result=subprocess.run([sys.executable,"scripts/validate_project.py"],cwd=ROOT)
 if result.returncode:raise SystemExit("Project validation failed; backend was not started.")
 print("\nVOICEGUARD SIH DEMO\nDemo Mode: HARDENED\nBackend: http://127.0.0.1:8000\nFrontend: http://localhost:5173\n\nOpen a second terminal and run:\n  cd frontend\n  npm run dev\n\nScenarios: demo/scenario_1_genuine through scenario_4_clone_transaction\nStarting backend. Press Ctrl+C to stop.\n")
 subprocess.run([sys.executable,"scripts/run_api.py","--host","127.0.0.1"],cwd=ROOT,check=False)
if __name__=="__main__":main()
