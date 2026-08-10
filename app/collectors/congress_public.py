from __future__ import annotations
from datetime import datetime, timedelta
import hashlib, json, re, requests
from sqlalchemy.orm import Session
from ..config import settings
from ..util import put_event, dt, num

def _amount_midpoint(value):
    if value is None:return None
    nums=[float(x.replace(",","")) for x in re.findall(r"\$?([\d,]+(?:\.\d+)?)",str(value))]
    if not nums:return None
    return sum(nums[:2])/min(len(nums),2)

def collect(session:Session,chamber:str|None=None,days:int=90,max_pages:int=1,page_size:int=50)->int:
    """
    Keyless public gateway for recent STOCK Act disclosures.
    Provider records are sourced from official House Clerk / Senate eFD filings.
    The local DB is for research use; raw records are not redistributed by AltAlpha.

    The default page size is deliberately capped at 50 so one House + one Senate
    sync stays within the public gateway's 100-row keyless allowance.
    """
    base=settings.congress_public_api_url.rstrip("/")+"/trades"
    since=(datetime.utcnow()-timedelta(days=days)).date().isoformat()
    inserted=0
    page_size=max(1,min(int(page_size),50))
    max_pages=max(1,int(max_pages))
    for page in range(max_pages):
        params={"limit":page_size,"page":page,"from":since}
        if chamber: params["chamber"]=chamber.lower()
        r=requests.get(base,params=params,timeout=45)
        r.raise_for_status()
        body=r.json()
        rows=body.get("trades",body if isinstance(body,list) else [])
        if not rows:break
        for x in rows:
            ch=str(x.get("chamber") or chamber or "").lower()
            ticker=str(x.get("ticker") or "").upper() or None
            member=x.get("member") or x.get("politician")
            trade_date=x.get("transaction_date") or x.get("trade_date") or x.get("date")
            disclosure=x.get("disclosure_date") or x.get("filed_date") or x.get("published_at")
            side=str(x.get("type") or x.get("transaction_type") or "").lower()
            amount=x.get("amount_range") or x.get("amount")
            stable=x.get("id") or "|".join(map(str,[member,ticker,trade_date,disclosure,side,amount,x.get("asset")]))
            sid=hashlib.sha1(stable.encode()).hexdigest()
            source="congress_house" if ch=="house" else "congress_senate" if ch=="senate" else "congress"
            inserted+=put_event(session,source=source,source_id=sid,event_type="congress_trade",ticker=ticker,
                entity_name=x.get("asset") or x.get("company"),actor_name=member,side=side,
                value=_amount_midpoint(amount),quantity=None,price=num(x.get("est_price")),score=None,
                event_at=dt(trade_date),published_at=dt(disclosure),
                url=x.get("filing_portal") or x.get("filing_url"),
                raw_json=json.dumps({"provider":"Bargo public Congress API",**x},default=str))
        if len(rows)<page_size:break
    return inserted
