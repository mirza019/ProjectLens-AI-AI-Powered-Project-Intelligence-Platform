from collections import defaultdict,deque
from datetime import datetime,timedelta,timezone
from fastapi import Depends,HTTPException
from app.core.config import settings
from app.core.security import current_user

_calls:dict[str,deque]=defaultdict(deque)
def ai_rate_limit(user=Depends(current_user)):
    now=datetime.now(timezone.utc); window=now-timedelta(minutes=1); calls=_calls[user.id]
    while calls and calls[0]<window: calls.popleft()
    if len(calls)>=settings.ai_rate_limit_per_minute: raise HTTPException(429,"AI request limit exceeded; retry shortly")
    calls.append(now); return user
