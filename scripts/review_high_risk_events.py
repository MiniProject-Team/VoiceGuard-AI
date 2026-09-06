from pathlib import Path
import argparse,json
def main():
 parser=argparse.ArgumentParser(description="List privacy-safe high-risk decision records for authorized review.");parser.add_argument("path",type=Path);args=parser.parse_args()
 for line in args.path.read_text(encoding="utf-8").splitlines():
  item=json.loads(line)
  if item.get("ai_risk_level") in {"HIGH","CRITICAL"}:print(json.dumps({k:v for k,v in item.items() if k not in {"raw_audio","speaker_embedding"}}))
if __name__=="__main__":main()
