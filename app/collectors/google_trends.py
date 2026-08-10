import requests,json,hashlib
from ..config import settings
from ..util import put_event,dt,num
def collect(s,term,ticker=None,geo="US"):
    if not settings.google_trends_api_url:raise RuntimeError("Google Trends official API is limited-access alpha. Set GOOGLE_TRENDS_API_URL and GOOGLE_TRENDS_API_KEY after acceptance.")
    headers={"Authorization":f"Bearer {settings.google_trends_api_key}"} if settings.google_trends_api_key else {};r=requests.get(settings.google_trends_api_url,params={"term":term,"geo":geo},headers=headers,timeout=45);r.raise_for_status();j=r.json();n=0;rows=j.get("data",j if isinstance(j,list) else [])
    for x in rows:
        ts=x.get("date") or x.get("time");v=num(x.get("value") or x.get("interest"));sid=hashlib.sha1(f"{term}:{geo}:{ts}".encode()).hexdigest();n+=put_event(s,source="google_trends",source_id=sid,event_type="search_interest",ticker=ticker.upper() if ticker else None,entity_name=term,actor_name=None,side="interest",value=v,quantity=None,price=None,score=v,event_at=dt(ts),published_at=dt(ts),url=None,raw_json=json.dumps(x,default=str))
    return n
