from __future__ import annotations
from datetime import datetime
import json, requests
from sqlalchemy.orm import Session
from ..util import put_event, dt, num

BASE="https://api.finra.org/data/group/otcMarket/name/consolidatedShortInterest"

def collect(session:Session,tickers:list[str]|None=None,limit:int=500)->int:
    """Collect FINRA Consolidated Short Interest from the public Query API."""
    tickers=[x.upper() for x in (tickers or []) if x]
    inserted=0
    targets=tickers or [None]
    for ticker in targets:
        payload={"limit":min(int(limit),5000),
                 "fields":["symbolCode","issueName","currentShortPositionQuantity",
                           "previousShortPositionQuantity","averageDailyVolumeQuantity",
                           "daysToCoverQuantity","changePercent","settlementDate",
                           "accountingYearMonthNumber","stockSplitFlag","revisionFlag"]}
        if ticker:
            payload["compareFilters"]=[{"compareType":"equal","fieldName":"symbolCode","fieldValue":ticker}]
        r=requests.post(BASE,json=payload,timeout=45)
        r.raise_for_status()
        rows=r.json() if isinstance(r.json(),list) else []
        for x in rows:
            symbol=str(x.get("symbolCode") or ticker or "").upper()
            if not symbol: continue
            settle=x.get("settlementDate")
            sid=f"{symbol}:{settle}:{x.get('accountingYearMonthNumber')}"
            current=num(x.get("currentShortPositionQuantity"))
            change=num(x.get("changePercent"))
            inserted+=put_event(session,source="finra_short_interest",source_id=sid,event_type="short_interest",
                ticker=symbol,entity_name=x.get("issueName"),actor_name="FINRA",side="short",
                value=current,quantity=current,price=None,score=(change/100.0 if change is not None else None),
                event_at=dt(settle),published_at=datetime.utcnow(),
                url="https://otce.finra.org/otce/equityShortInterest",raw_json=json.dumps(x,default=str))
    return inserted
