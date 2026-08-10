import pandas as pd,json,hashlib
from ..models import AircraftMap
from ..util import put_event,dt,num
def import_flights(s,path):
    df=pd.read_csv(path);n=0;maps={x.registration.upper():x for x in s.query(AircraftMap).all()}
    for _,r in df.iterrows():
        d=r.to_dict();reg=str(d.get("registration") or d.get("tail") or d.get("n_number") or "").upper();m=maps.get(reg)
        if not m:continue
        dep=d.get("departure_time") or d.get("firstSeen") or d.get("date");arr=d.get("arrival_time") or d.get("lastSeen") or dep;sid=hashlib.sha1(f"{reg}:{dep}:{arr}:{d.get('origin')}:{d.get('destination')}".encode()).hexdigest()
        n+=put_event(s,source="corporate_flights",source_id=sid,event_type="corporate_flight",ticker=m.ticker,entity_name=m.company,actor_name=reg,side="flight",value=num(d.get("distance_km")),quantity=None,price=None,score=None,event_at=dt(dep),published_at=dt(d.get("published_at") or arr),url=None,raw_json=json.dumps(d,default=str))
    return n
