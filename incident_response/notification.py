class NotificationHooks:
 def __init__(self):self.hooks={}
 def register(self,audience,callback):self.hooks.setdefault(audience,[]).append(callback)
 def emit(self,audience,event,external_enabled=False):
  if not external_enabled:return {"status":"SUPPRESSED_NOT_CONFIGURED","audience":audience}
  for callback in self.hooks.get(audience,[]):callback(event)
  return {"status":"DISPATCHED","audience":audience,"hook_count":len(self.hooks.get(audience,[]))}
