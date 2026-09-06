from dataclasses import dataclass,asdict
@dataclass(frozen=True)
class LimitationRegistry:
 version:str;limitations:tuple[str,...];release_version:str|None=None
 def to_dict(self):return asdict(self)
DEFAULT_LIMITATIONS=LimitationRegistry("phase13-limitations-v1",("unseen generators","noisy audio","short speech","cross-language differences","speaker verification limitations","replay attacks","probability calibration"))
