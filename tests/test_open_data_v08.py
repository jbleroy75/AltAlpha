from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.models import Event
from app.collectors import congress_public, finra_live

class Resp:
    def __init__(self,data): self.data=data
    def raise_for_status(self): pass
    def json(self): return self.data

def session():
    e=create_engine("sqlite:///:memory:");Base.metadata.create_all(e);return sessionmaker(bind=e)()

def test_congress_public_point_in_time(monkeypatch):
    s=session()
    monkeypatch.setattr(congress_public.requests,"get",lambda *a,**k:Resp({"trades":[{
      "member":"Jane Doe","chamber":"house","ticker":"NVDA","asset":"NVIDIA","type":"purchase",
      "amount_range":"$1,001 - $15,000","transaction_date":"2026-05-12","disclosure_date":"2026-06-02"}]}))
    n=congress_public.collect(s,"house",90,1)
    e=s.query(Event).one()
    assert n==1 and e.event_at.date().isoformat()=="2026-05-12" and e.published_at.date().isoformat()=="2026-06-02"

def test_finra_public(monkeypatch):
    s=session()
    monkeypatch.setattr(finra_live.requests,"post",lambda *a,**k:Resp([{
      "symbolCode":"NVDA","issueName":"NVIDIA","currentShortPositionQuantity":100,
      "previousShortPositionQuantity":80,"changePercent":25,"settlementDate":"2026-07-31","accountingYearMonthNumber":20260731}]))
    n=finra_live.collect(s,["NVDA"],10)
    e=s.query(Event).one()
    assert n==1 and e.ticker=="NVDA" and abs(e.score-.25)<1e-12
