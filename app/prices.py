from io import StringIO
import requests,pandas as pd
from sqlalchemy.exc import IntegrityError
from .models import Price
def fetch(s,ticker,start,end):
    sym=ticker.lower() if "." in ticker else ticker.lower()+".us"
    u=f"https://stooq.com/q/d/l/?s={sym}&d1={start:%Y%m%d}&d2={end:%Y%m%d}&i=d"
    r=requests.get(u,timeout=30);r.raise_for_status();df=pd.read_csv(StringIO(r.text));n=0
    if "Date" not in df:return 0
    for x in df.itertuples():
        s.add(Price(ticker=ticker.upper(),date=pd.Timestamp(x.Date).to_pydatetime(),close=float(x.Close),volume=float(x.Volume) if hasattr(x,"Volume") else None))
        try:s.commit();n+=1
        except IntegrityError:s.rollback()
    return n
