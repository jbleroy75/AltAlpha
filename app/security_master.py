import pandas as pd
from sqlalchemy.exc import IntegrityError
from .models import Security,CorporateAction
from .util import dt,num

def import_securities(s,path):
    df=pd.read_csv(path);n=0
    for _,r in df.iterrows():
        d=r.to_dict();x=Security(ticker=str(d.get("ticker","")).upper(),cik=str(d.get("cik")) if pd.notna(d.get("cik")) else None,cusip=str(d.get("cusip")) if pd.notna(d.get("cusip")) else None,figi=str(d.get("figi")) if pd.notna(d.get("figi")) else None,name=d.get("name"),sector=d.get("sector"),exchange=d.get("exchange"),active=str(d.get("active","true")).lower() not in ("false","0"),valid_from=dt(d.get("valid_from")) if pd.notna(d.get("valid_from")) else None,valid_to=dt(d.get("valid_to")) if pd.notna(d.get("valid_to")) else None);s.add(x)
        try:s.commit();n+=1
        except IntegrityError:s.rollback()
    return n

def import_actions(s,path):
    df=pd.read_csv(path);n=0
    for _,r in df.iterrows():
        d=r.to_dict();s.add(CorporateAction(ticker=str(d["ticker"]).upper(),action_type=str(d["action_type"]),ex_date=dt(d["ex_date"]),factor=num(d.get("factor")),cash_amount=num(d.get("cash_amount")),source=d.get("source")));s.commit();n+=1
    return n
