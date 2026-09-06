from __future__ import annotations
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 print("VOICEGUARD END-TO-END VALIDATION\n");result=subprocess.run([sys.executable,"-m","pytest","tests/end_to_end","tests/api/test_websocket.py","-q"],cwd=ROOT);print("\nREAL MODEL E2E TEST: MANUAL - run the four demo scenarios after model readiness succeeds");raise SystemExit(result.returncode)
if __name__=="__main__":main()
