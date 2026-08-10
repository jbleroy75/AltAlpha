from datetime import datetime,timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.models import Event,Price
from app.strategy import run
def test_strategy_enters_after_publication():
    e=create_engine("sqlite:///:memory:");Base.metadata.create_all(e);S=sessionmaker(bind=e);s=S();pub=datetime(2026,2,10)
    s.add(Event(source="congress_house",source_id="1",event_type="congress_trade",ticker="TEST",entity_name="X",actor_name="M",side="purchase",value=100000,quantity=None,price=None,score=2,event_at=datetime(2026,1,1),published_at=pub,url=None,raw_json=None));s.add(Price(ticker="TEST",date=datetime(2026,1,2),close=10,volume=1))
    for i in range(1,25):s.add(Price(ticker="TEST",date=pub+timedelta(days=i),close=100+i,volume=1))
    s.commit();out=run(s,{"name":"t","sources":["congress_house"],"threshold":1,"holding_days":5,"benchmark":None});assert out["trades"][0]["entry"]=="2026-02-11"
