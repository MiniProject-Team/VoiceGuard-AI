from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from mlops.model_registry import ModelRegistry
def main():
 p=argparse.ArgumentParser();p.add_argument("--type",required=True);a=p.parse_args();print(json.dumps(ModelRegistry(ROOT/f"models/registry/{a.type}/registry.json").rollback(a.type),indent=2))
if __name__=="__main__":main()
