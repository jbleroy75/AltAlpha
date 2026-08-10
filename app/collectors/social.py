import requests,json,hashlib
from datetime import datetime
from ..config import settings
from ..util import put_event
POS={"beat","growth","record","strong","upgrade","bullish","profit","buy"};NEG={"miss","weak","downgrade","bearish","loss","sell","fraud","cut"}
def sentiment(text):
    toks={x.strip(".,!?$#").lower() for x in text.split()};return (len(toks&POS)-len(toks&NEG))/max(1,len(toks&POS)+len(toks&NEG))
def bluesky(s,query,ticker=None,limit=100):
    u=settings.bluesky_base_url.rstrip("/")+"/xrpc/app.bsky.feed.searchPosts";r=requests.get(u,params={"q":query,"limit":min(limit,100)},timeout=30);r.raise_for_status();n=0
    for p in r.json().get("posts",[]):
        rec=p.get("record",{});text=rec.get("text","");ts=rec.get("createdAt") or p.get("indexedAt");uri=p.get("uri","");n+=put_event(s,source="bluesky",source_id=hashlib.sha1(uri.encode()).hexdigest(),event_type="social_mention",ticker=ticker.upper() if ticker else None,entity_name=query,actor_name=(p.get("author") or {}).get("handle"),side="mention",value=None,quantity=None,price=None,score=sentiment(text),event_at=datetime.fromisoformat(ts.replace("Z","+00:00")).replace(tzinfo=None),published_at=datetime.fromisoformat((p.get("indexedAt") or ts).replace("Z","+00:00")).replace(tzinfo=None),url=None,raw_json=json.dumps(p,default=str))
    return n
