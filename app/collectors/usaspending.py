import requests,json
from datetime import date,timedelta,datetime
from ..util import put_event,resolve_ticker,dt,num
API="https://api.usaspending.gov/api/v2/search/spending_by_transaction/"
def collect(s,recipient,days=365,pages=5):
    end=date.today();start=end-timedelta(days=days);n=0
    for page in range(1,pages+1):
        payload={"subawards":False,"limit":100,"page":page,"fields":["Award ID","Recipient Name","Transaction Amount","Action Date","Awarding Agency","Award Type","Description","generated_subawards_id"],"filters":{"time_period":[{"start_date":start.isoformat(),"end_date":end.isoformat()}],"award_type_codes":["A","B","C","D"],"recipient_search_text":[recipient]}};r=requests.post(API,json=payload,timeout=45);r.raise_for_status();rows=r.json().get("results",[])
        if not rows:break
        for row in rows:
            aid=str(row.get("Award ID") or row.get("generated_subawards_id") or "");action=str(row.get("Action Date") or end.isoformat());sid=f"{aid}:{action}:{row.get('Transaction Amount')}";name=row.get("Recipient Name");n+=put_event(s,source="usaspending",source_id=sid,event_type="government_contract",ticker=resolve_ticker(s,name),entity_name=name,actor_name=row.get("Awarding Agency"),side="award",value=num(row.get("Transaction Amount")),quantity=None,price=None,score=None,event_at=dt(action),published_at=datetime.utcnow(),url=f"https://www.usaspending.gov/award/{aid}",raw_json=json.dumps(row,default=str))
    return n
