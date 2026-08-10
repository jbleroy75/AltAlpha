import json

from fastapi import FastAPI,Depends,HTTPException,BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func
from pathlib import Path
from .db import init_db,SessionLocal
from .models import Event,StrategyRun
from .strategy import run
from .portfolio import run_portfolio
from .discovery import discover
from .risk_model import returns_matrix,statistical_factors,risk_report
from .optimizer import optimize
from .validation import deflated_sharpe_ratio,probabilistic_sharpe_ratio,bootstrap_sharpe_ci
from .sync_manager import create_sync,run_sync,snapshot
from .config import settings

app=FastAPI(title="AltAlpha Terminal",version="0.8.0")
STATIC=Path(__file__).parent/"static"
app.mount("/static",StaticFiles(directory=STATIC),name="static")

@app.on_event("startup")
def startup():
    init_db()
    if settings.auto_sync_on_first_run:
        from threading import Thread
        from .models import SyncRun
        with SessionLocal() as s:
            existing=s.query(SyncRun).order_by(SyncRun.id.desc()).first()
        if existing is None:
            run_id=create_sync("first_run")
            Thread(target=run_sync,args=(run_id,),daemon=True,name="altalpha-first-sync").start()
def db():
    s=SessionLocal()
    try:yield s
    finally:s.close()

@app.get("/")
def terminal(): return FileResponse(STATIC/"index.html")
@app.get("/health")
def health():return {"ok":True,"version":"0.8.0"}

@app.get("/events")
def events(source:str|None=None,ticker:str|None=None,limit:int=100,s:Session=Depends(db)):
    q=s.query(Event)
    if source:q=q.filter(Event.source==source)
    if ticker:q=q.filter(Event.ticker==ticker.upper())
    xs=q.order_by(Event.published_at.desc()).limit(min(limit,1000)).all()
    return [{"id":x.id,"source":x.source,"type":x.event_type,"ticker":x.ticker,"entity":x.entity_name,"actor":x.actor_name,"side":x.side,"value":x.value,"score":x.score,"event_at":x.event_at,"published_at":x.published_at,"url":x.url} for x in xs]

@app.get("/sources")
def sources(s:Session=Depends(db)):
    rows=s.query(Event.source,func.count(Event.id),func.max(Event.published_at)).group_by(Event.source).all();return [{"source":a,"events":b,"latest":c} for a,b,c in rows]

@app.get("/screener")
def screener(days:int=30,min_score:float=-999,limit:int=100,s:Session=Depends(db)):
    from datetime import datetime,timedelta
    since=datetime.utcnow()-timedelta(days=days)
    rows=(s.query(Event.ticker,func.count(Event.id),func.sum(func.coalesce(Event.score,0)),func.max(Event.published_at)).filter(Event.ticker.isnot(None),Event.published_at>=since).group_by(Event.ticker).order_by(func.count(Event.id).desc()).limit(min(limit,500)).all())
    out=[]
    for ticker,n,score,latest in rows:
        src=[x[0] for x in s.query(Event.source).filter(Event.ticker==ticker,Event.published_at>=since).distinct().all()];score=float(score or 0)
        if score>=min_score:out.append({"ticker":ticker,"events":n,"score":score,"latest":latest,"sources":src})
    return out

@app.get("/companies/{ticker}")
def company(ticker:str,s:Session=Depends(db)):
    t=ticker.upper();xs=s.query(Event).filter(Event.ticker==t).order_by(Event.published_at.desc()).limit(300).all()
    if not xs: raise HTTPException(404,"Ticker not found in event database")
    by={}
    for x in xs:by[x.source]=by.get(x.source,0)+1
    return {"ticker":t,"event_count":len(xs),"sources":by,"latest":[{"source":x.source,"type":x.event_type,"actor":x.actor_name,"side":x.side,"value":x.value,"score":x.score,"published_at":x.published_at,"url":x.url} for x in xs[:100]]}

@app.post("/strategies/run")
def strategy(config:dict,s:Session=Depends(db)):return run(s,config)
@app.get("/strategies/runs")
def runs(limit:int=20,s:Session=Depends(db)):
    xs=s.query(StrategyRun).order_by(StrategyRun.created_at.desc()).limit(limit).all();return [{"id":x.id,"name":x.name,"created_at":x.created_at,"config":json.loads(x.config_json),"result":json.loads(x.result_json)} for x in xs]
@app.post("/portfolio/run")
def portfolio(config:dict,s:Session=Depends(db)):return run_portfolio(s,config)
@app.post("/discovery/run")
def alpha_discovery(config:dict,s:Session=Depends(db)):return discover(s,config)
@app.post("/risk/analyze")
def risk_analyze(payload:dict,s:Session=Depends(db)):
    from datetime import datetime
    tickers=list(payload["weights"]);ret=returns_matrix(s,tickers,datetime.fromisoformat(payload["start"]),datetime.fromisoformat(payload["end"]));model=statistical_factors(ret,int(payload.get("n_factors",5)));return risk_report(payload["weights"],ret,model)
@app.post("/optimizer/run")
def optimizer_run(payload:dict):
    import numpy as np
    return optimize(payload["expected_returns"],np.array(payload["covariance"]),max_position=float(payload.get("max_position",.1)),gross_limit=float(payload.get("gross_limit",1)),net_target=float(payload.get("net_target",1)),risk_aversion=float(payload.get("risk_aversion",5)),turnover_penalty=float(payload.get("turnover_penalty",.001)),previous=payload.get("previous"),long_short=bool(payload.get("long_short",False)))
@app.post("/validation/analyze")
def validate(payload:dict):
    r=payload["returns"];n=int(payload.get("n_trials",1));return {"probabilistic_sharpe":probabilistic_sharpe_ratio(r),"deflated_sharpe":deflated_sharpe_ratio(r,n),"bootstrap_sharpe_95":bootstrap_sharpe_ci(r,int(payload.get("bootstrap",1000)))}
@app.post("/sync/all")
def sync_all(background_tasks:BackgroundTasks):
    run_id=create_sync("web");background_tasks.add_task(run_sync,run_id);return {"run_id":run_id,"status":"running"}
@app.get("/sync/latest")
def sync_latest():return snapshot()
@app.get("/sync/status/{run_id}")
def sync_status(run_id:int):return snapshot(run_id)
