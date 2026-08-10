import requests,json,hashlib
from ..config import settings
from ..util import put_event,dt,num
H=lambda:{"User-Agent":settings.sec_user_agent}
def collect_companyfacts(s,cik,ticker):
    cik=str(cik).zfill(10);u=f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    r=requests.get(u,headers=H(),timeout=30);r.raise_for_status();j=r.json();n=0
    facts=j.get("facts",{}).get("us-gaap",{});concepts=["Revenues","RevenueFromContractWithCustomerExcludingAssessedTax","NetIncomeLoss","EarningsPerShareDiluted"]
    for concept in concepts:
        fact=facts.get(concept)
        if not fact:continue
        for unit,rows in fact.get("units",{}).items():
            for x in rows:
                if x.get("form") not in ("10-Q","10-K","8-K"):continue
                filed=x.get("filed");end=x.get("end");val=num(x.get("val"));sid=hashlib.sha1(f"{cik}:{concept}:{unit}:{end}:{filed}:{x.get('accn')}".encode()).hexdigest()
                n+=put_event(s,source="sec_companyfacts",source_id=sid,event_type="earnings_fact",ticker=ticker.upper(),entity_name=j.get("entityName"),actor_name=None,side=concept,value=val,quantity=None,price=None,score=None,event_at=dt(end),published_at=dt(filed),url=None,raw_json=json.dumps({"concept":concept,"unit":unit,**x},default=str))
    return n
