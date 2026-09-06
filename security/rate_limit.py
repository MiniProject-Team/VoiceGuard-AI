from __future__ import annotations
from collections import defaultdict,deque
from time import monotonic
class SlidingWindowRateLimiter:
    def __init__(self):self.windows=defaultdict(deque)
    def allow(self,key:str,limit:int,window_seconds:float=60)->bool:
        now=monotonic();window=self.windows[key]
        while window and now-window[0]>=window_seconds:window.popleft()
        if len(window)>=limit:return False
        window.append(now);return True
