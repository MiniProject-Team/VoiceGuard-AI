from __future__ import annotations
import hashlib,json
from pathlib import Path
from typing import Any,Iterable

def canonical_json(value:Any)->bytes:return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha256_file(path:str|Path)->str:
    digest=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda:stream.read(65536),b""):digest.update(chunk)
    return digest.hexdigest()
def config_hash(paths:Iterable[str|Path])->str:
    digest=hashlib.sha256()
    for path in sorted(map(Path,paths),key=lambda p:str(p)):
        digest.update(str(path).replace("\\","/").encode());digest.update(Path(path).read_bytes())
    return digest.hexdigest()
