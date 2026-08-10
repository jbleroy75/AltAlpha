from datetime import timedelta
import numpy as np,json
from .models import Event,Price,StrategyRun
from .prices import fetch

def _p(s,t,after,n=0):
    rows=s.query(Price).filter(Price.ticker==t.upper(),Price.date>after).order_by(Price.date).limit(n+1).all();return rows[n] if len(rows)>n else None

def run(s,config):
    sources=config.get("sources",[]);lookback=int(config.get("signal_lookback_days",30));hold=int(config.get("holding_days",20));threshold=float(config.get("threshold",1));weights=config.get("weights",{});start=config.get("start");end=config.get("end")
    q=s.query(Event).filter(Event.ticker.isnot(None))
    if sources:q=q.filter(Event.source.in_(sources))
    if start:
        from datetime import datetime
        q=q.filter(Event.published_at>=datetime.fromisoformat(start))
    if end:
        from datetime import datetime
        q=q.filter(Event.published_at<=datetime.fromisoformat(end))
    evs=q.order_by(Event.published_at).all();by={}
    for e in evs:by.setdefault(e.ticker,[]).append(e)
    trades=[]
    for ticker,arr in by.items():
        for e in arr:
            lo=e.published_at-timedelta(days=lookback);relevant=[x for x in arr if lo<=x.published_at<=e.published_at and (not sources or x.source in sources)];score=0;detail={}
            for x in relevant:
                base=x.score if x.score is not None else (1 if x.side in ("purchase","award","holding","publication","mention","interest","earnings","flight") else -1 if x.side=="sale" else 0)
                w=float(weights.get(x.source,1));score+=w*base;detail[x.source]=detail.get(x.source,0)+w*base
            if score<threshold:continue
            ps=e.published_at-timedelta(days=10);pe=e.published_at+timedelta(days=max(60,hold*2))
            if s.query(Price).filter(Price.ticker==ticker,Price.date>=ps,Price.date<=pe).count()==0:
                try:fetch(s,ticker,ps,pe)
                except:continue
            p0=_p(s,ticker,e.published_at,0);p1=_p(s,ticker,e.published_at,hold)
            if not p0 or not p1:continue
            trades.append({"ticker":ticker,"signal_at":e.published_at.isoformat(),"score":score,"components":detail,"entry":p0.date.date().isoformat(),"exit":p1.date.date().isoformat(),"return":p1.close/p0.close-1})
    uniq={(t["ticker"],t["entry"]):t for t in trades};trades=list(uniq.values());rets=[t["return"] for t in trades]
    summary={"n":len(rets),"mean_return":float(np.mean(rets)) if rets else None,"median_return":float(np.median(rets)) if rets else None,"win_rate":float(np.mean([r>0 for r in rets])) if rets else None,"std":float(np.std(rets,ddof=1)) if len(rets)>1 else None}
    out={"summary":summary,"trades":trades};run=StrategyRun(name=config.get("name","strategy"),config_json=json.dumps(config),result_json=json.dumps(out));s.add(run);s.commit();out["run_id"]=run.id;return out
