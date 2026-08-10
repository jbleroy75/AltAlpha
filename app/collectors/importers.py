import pandas as pd,json,hashlib
from ..util import put_event,resolve_ticker,dt,num

def _col(row,*names):
    for n in names:
        if n in row and pd.notna(row[n]):return row[n]
    return None

def import_congress(s,path,chamber):
    df=pd.read_csv(path);n=0
    for _,r in df.iterrows():
        d=r.to_dict();member=_col(d,"member","representative","senator","name");asset=_col(d,"asset","asset_name","description");ticker=_col(d,"ticker","symbol") or resolve_ticker(s,asset);tx=_col(d,"transaction_date","transactionDate","date");pub=_col(d,"published_at","filing_date","disclosure_date") or tx;amount=_col(d,"amount","value");side=str(_col(d,"type","transaction_type","side") or "").lower();sid=str(_col(d,"id","doc_id","ptr_id") or hashlib.sha1(json.dumps(d,sort_keys=True,default=str).encode()).hexdigest())
        n+=put_event(s,source=f"congress_{chamber}",source_id=sid,event_type="congress_trade",ticker=str(ticker).upper() if ticker else None,entity_name=str(asset) if asset else None,actor_name=str(member) if member else None,side=side,value=num(amount),quantity=None,price=None,score=None,event_at=dt(tx),published_at=dt(pub),url=_col(d,"url","source_url"),raw_json=json.dumps(d,default=str))
    return n

def import_patents(s,path):
    df=pd.read_csv(path);n=0
    for _,r in df.iterrows():
        d=r.to_dict();assignee=_col(d,"assignee","assignee_organization","company");sid=str(_col(d,"patent_id","publication_number","id"));pub=_col(d,"publication_date","date");n+=put_event(s,source="uspto",source_id=sid,event_type="patent",ticker=_col(d,"ticker") or resolve_ticker(s,assignee),entity_name=str(assignee) if assignee else None,actor_name=None,side="publication",value=None,quantity=None,price=None,score=None,event_at=dt(pub),published_at=dt(pub),url=_col(d,"url"),raw_json=json.dumps(d,default=str))
    return n

def import_options(s,path):
    df=pd.read_csv(path);n=0
    for _,r in df.iterrows():
        d=r.to_dict();ticker=_col(d,"ticker","symbol");ts=_col(d,"timestamp","date");premium=num(_col(d,"premium","notional","value"));cp=str(_col(d,"put_call","type","option_type") or "").lower();side=str(_col(d,"side","sentiment") or cp);sid=str(_col(d,"id") or hashlib.sha1(json.dumps(d,sort_keys=True,default=str).encode()).hexdigest());n+=put_event(s,source="options_flow",source_id=sid,event_type="options_flow",ticker=str(ticker).upper() if ticker else None,entity_name=None,actor_name=None,side=side,value=premium,quantity=num(_col(d,"size","volume","quantity")),price=num(_col(d,"price")),score=num(_col(d,"score")),event_at=dt(ts),published_at=dt(_col(d,"published_at") or ts),url=None,raw_json=json.dumps(d,default=str))
    return n

def import_transcripts(s,path):
    df=pd.read_csv(path);n=0
    for _,r in df.iterrows():
        d=r.to_dict();ticker=_col(d,"ticker","symbol");ts=_col(d,"published_at","date");text=str(_col(d,"text","transcript") or "");sid=str(_col(d,"id") or hashlib.sha1((str(ticker)+str(ts)+text[:1000]).encode()).hexdigest());n+=put_event(s,source="earnings_transcript",source_id=sid,event_type="earnings_transcript",ticker=str(ticker).upper() if ticker else None,entity_name=_col(d,"company"),actor_name=None,side="earnings",value=None,quantity=None,price=None,score=num(_col(d,"sentiment","score")),event_at=dt(ts),published_at=dt(ts),url=_col(d,"url"),raw_json=json.dumps({"text":text,"meta":d},default=str))
    return n
