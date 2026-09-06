from __future__ import annotations
import json
from pathlib import Path
from typing import Any
import pandas as pd
def write_json(path:str|Path,value:Any)->None:target=Path(path);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(value,indent=2,default=str),encoding="utf-8")
def write_csv(path:str|Path,rows:list[dict])->None:target=Path(path);target.parent.mkdir(parents=True,exist_ok=True);pd.DataFrame(rows).to_csv(target,index=False)
