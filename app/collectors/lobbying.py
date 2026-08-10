import requests,json
from ..config import settings
from ..util import put_event,resolve_ticker,dt,num
BASE="https://lda.senate.gov/api/v1/filings/"
def collect(s,client=None,year=None,pages=5):
    headers={}
    if settings.lda_api_key:headers["Authorization"]=f"Token {settings.lda_api_key}"
    params={}
    if client:params["client_name"]=client
    if year:params["filing_year"]=year
    n=0;url=BASE
    for _ in range(pages):
        r=requests.get(url,params=params if url==BASE else None,headers=headers,timeout=45);r.raise_for_status();j=r.json()
        for x in j.get("results",[]):
            client_obj=x.get("client") or {};name=client_obj.get("name") if isinstance(client_obj,dict) else str(client_obj);amount=num(x.get("income") or x.get("expenses"));sid=str(x.get("filing_uuid") or x.get("id"));n+=put_event(s,source="lda",source_id=sid,event_type="lobbying",ticker=resolve_ticker(s,name),entity_name=name,actor_name=(x.get("registrant") or {}).get("name") if isinstance(x.get("registrant"),dict) else None,side="spend",value=amount,quantity=None,price=None,score=None,event_at=dt(x.get("filing_period_display") or x.get("filing_year")),published_at=dt(x.get("dt_posted") or x.get("date_received")),url=x.get("filing_url"),raw_json=json.dumps(x,default=str))
        url=j.get("next")
        if not url:break
    return n
