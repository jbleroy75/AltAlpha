from datetime import datetime
from sqlalchemy import String,Float,DateTime,Text,Integer,UniqueConstraint,Boolean
from sqlalchemy.orm import Mapped,mapped_column
from .db import Base

class Event(Base):
    __tablename__="events"
    id:Mapped[int]=mapped_column(primary_key=True)
    source:Mapped[str]=mapped_column(String(64),index=True)
    source_id:Mapped[str]=mapped_column(String(300))
    event_type:Mapped[str]=mapped_column(String(64),index=True)
    ticker:Mapped[str|None]=mapped_column(String(32),index=True)
    entity_name:Mapped[str|None]=mapped_column(String(300),index=True)
    actor_name:Mapped[str|None]=mapped_column(String(300),index=True)
    side:Mapped[str|None]=mapped_column(String(32),index=True)
    value:Mapped[float|None]=mapped_column(Float)
    quantity:Mapped[float|None]=mapped_column(Float)
    price:Mapped[float|None]=mapped_column(Float)
    score:Mapped[float|None]=mapped_column(Float,index=True)
    event_at:Mapped[datetime]=mapped_column(DateTime,index=True)
    published_at:Mapped[datetime]=mapped_column(DateTime,index=True)
    url:Mapped[str|None]=mapped_column(Text)
    raw_json:Mapped[str|None]=mapped_column(Text)
    __table_args__=(UniqueConstraint("source","source_id",name="uq_event"),)

class EntityAlias(Base):
    __tablename__="entity_aliases"
    id:Mapped[int]=mapped_column(primary_key=True)
    alias:Mapped[str]=mapped_column(String(300),unique=True,index=True)
    ticker:Mapped[str]=mapped_column(String(32),index=True)
    cik:Mapped[str|None]=mapped_column(String(16),index=True)

class Price(Base):
    __tablename__="prices"
    id:Mapped[int]=mapped_column(primary_key=True)
    ticker:Mapped[str]=mapped_column(String(32),index=True)
    date:Mapped[datetime]=mapped_column(DateTime,index=True)
    close:Mapped[float]=mapped_column(Float)
    volume:Mapped[float|None]=mapped_column(Float)
    __table_args__=(UniqueConstraint("ticker","date",name="uq_price"),)

class AircraftMap(Base):
    __tablename__="aircraft_map"
    id:Mapped[int]=mapped_column(primary_key=True)
    registration:Mapped[str]=mapped_column(String(32),unique=True,index=True)
    ticker:Mapped[str]=mapped_column(String(32),index=True)
    company:Mapped[str|None]=mapped_column(String(300))

class StrategyRun(Base):
    __tablename__="strategy_runs"
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(120),index=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    config_json:Mapped[str]=mapped_column(Text)
    result_json:Mapped[str]=mapped_column(Text)

class Security(Base):
    __tablename__="securities"
    id:Mapped[int]=mapped_column(primary_key=True)
    ticker:Mapped[str]=mapped_column(String(32),index=True)
    cik:Mapped[str|None]=mapped_column(String(16),index=True)
    cusip:Mapped[str|None]=mapped_column(String(16),index=True)
    figi:Mapped[str|None]=mapped_column(String(32),index=True)
    name:Mapped[str|None]=mapped_column(String(300))
    sector:Mapped[str|None]=mapped_column(String(100),index=True)
    exchange:Mapped[str|None]=mapped_column(String(32))
    active:Mapped[bool]=mapped_column(Boolean,default=True)
    valid_from:Mapped[datetime|None]=mapped_column(DateTime,index=True)
    valid_to:Mapped[datetime|None]=mapped_column(DateTime,index=True)

class CorporateAction(Base):
    __tablename__="corporate_actions"
    id:Mapped[int]=mapped_column(primary_key=True)
    ticker:Mapped[str]=mapped_column(String(32),index=True)
    action_type:Mapped[str]=mapped_column(String(32),index=True)
    ex_date:Mapped[datetime]=mapped_column(DateTime,index=True)
    factor:Mapped[float|None]=mapped_column(Float)
    cash_amount:Mapped[float|None]=mapped_column(Float)
    source:Mapped[str|None]=mapped_column(String(64))

class DailyPortfolio(Base):
    __tablename__="daily_portfolio"
    id:Mapped[int]=mapped_column(primary_key=True)
    run_id:Mapped[int]=mapped_column(Integer,index=True)
    date:Mapped[datetime]=mapped_column(DateTime,index=True)
    equity:Mapped[float]=mapped_column(Float)
    gross_exposure:Mapped[float]=mapped_column(Float)
    net_exposure:Mapped[float]=mapped_column(Float)
    turnover:Mapped[float]=mapped_column(Float)
    drawdown:Mapped[float]=mapped_column(Float)

class SyncRun(Base):
    __tablename__="sync_runs"
    id:Mapped[int]=mapped_column(primary_key=True)
    started_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow,index=True)
    finished_at:Mapped[datetime|None]=mapped_column(DateTime,index=True)
    status:Mapped[str]=mapped_column(String(32),default="running",index=True)
    triggered_by:Mapped[str]=mapped_column(String(32),default="manual")

class SyncSourceStatus(Base):
    __tablename__="sync_source_status"
    id:Mapped[int]=mapped_column(primary_key=True)
    run_id:Mapped[int]=mapped_column(Integer,index=True)
    source:Mapped[str]=mapped_column(String(64),index=True)
    status:Mapped[str]=mapped_column(String(32),index=True)
    inserted:Mapped[int]=mapped_column(Integer,default=0)
    message:Mapped[str|None]=mapped_column(Text)
    started_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    finished_at:Mapped[datetime|None]=mapped_column(DateTime)
