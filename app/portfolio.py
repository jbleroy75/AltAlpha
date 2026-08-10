from datetime import datetime,timedelta
import math,numpy as np,pandas as pd,json
from .models import Event,Price,StrategyRun,DailyPortfolio
from .prices import fetch

def _metrics(equity,daily,benchmark=None,rf=0.0):
    if len(equity)<2:return {}
    years=max((equity.index[-1]-equity.index[0]).days/365.25,1/365.25);cagr=(equity.iloc[-1]/equity.iloc[0])**(1/years)-1;vol=daily.std()*math.sqrt(252) if len(daily)>1 else 0;sharpe=((daily.mean()*252-rf)/vol) if vol else None;downside=daily[daily<0].std()*math.sqrt(252);sortino=((daily.mean()*252-rf)/downside) if downside and not np.isnan(downside) else None;peak=equity.cummax();dd=equity/peak-1;maxdd=float(dd.min());calmar=cagr/abs(maxdd) if maxdd else None
    out={"cagr":float(cagr),"volatility":float(vol),"sharpe":float(sharpe) if sharpe is not None else None,"sortino":float(sortino) if sortino is not None else None,"max_drawdown":maxdd,"calmar":float(calmar) if calmar is not None else None}
    if benchmark is not None and len(benchmark)>2:
        z=pd.concat([daily.rename("r"),benchmark.rename("b")],axis=1).dropna()
        if len(z)>2 and z.b.var()>0:
            beta=z.r.cov(z.b)/z.b.var();alpha=(z.r.mean()-beta*z.b.mean())*252;active=z.r-z.b;ir=active.mean()/active.std()*math.sqrt(252) if active.std() else None;out.update({"beta":float(beta),"alpha":float(alpha),"information_ratio":float(ir) if ir is not None else None})
    return out

def run_portfolio(s,cfg):
    start=datetime.fromisoformat(cfg["start"]);end=datetime.fromisoformat(cfg["end"]);sources=cfg.get("sources",[]);threshold=float(cfg.get("threshold",1));hold=int(cfg.get("holding_days",20));maxpos=float(cfg.get("max_position",.1));tc_bps=float(cfg.get("transaction_cost_bps",5));slip_bps=float(cfg.get("slippage_bps",5));long_short=bool(cfg.get("long_short",False));weights=cfg.get("weights",{});lookback=int(cfg.get("signal_lookback_days",30));initial=float(cfg.get("initial_capital",100000))
    ev=s.query(Event).filter(Event.ticker.isnot(None),Event.published_at>=start,Event.published_at<=end)
    if sources:ev=ev.filter(Event.source.in_(sources))
    evs=ev.order_by(Event.published_at).all();tickers=sorted({x.ticker for x in evs}|{cfg.get("benchmark","SPY")})
    for t in tickers:
        if t and s.query(Price).filter(Price.ticker==t,Price.date>=start,Price.date<=end).count()<20:
            try:fetch(s,t,start-timedelta(days=10),end+timedelta(days=10))
            except:pass
    prices={}
    for t in tickers:
        rows=s.query(Price).filter(Price.ticker==t,Price.date>=start,Price.date<=end).order_by(Price.date).all()
        if rows:prices[t]=pd.Series({x.date.date():x.close for x in rows})
    all_dates=sorted(set().union(*[set(x.index) for x in prices.values()])) if prices else [];positions={};equity=initial;curve=[];prev_equity=initial;daily_rets=[]
    for d in all_dates:
        day=datetime.combine(d,datetime.min.time());pnl=0
        for t,pos in list(positions.items()):
            ser=prices.get(t)
            if ser is None or d not in ser.index:continue
            prev_dates=[z for z in ser.index if z<d]
            if prev_dates:pnl+=pos["notional"]*pos["dir"]*(ser[d]/ser[prev_dates[-1]]-1)
            pos["age"]+=1
            if pos["age"]>=hold:positions.pop(t,None)
        equity+=pnl;recent=[x for x in evs if day-timedelta(days=lookback)<=x.published_at<day];scores={}
        for x in recent:
            base=x.score if x.score is not None else (1 if x.side in ("purchase","award","holding","publication","mention","interest","earnings","flight") else -1 if x.side in ("sale","short") else 0);scores[x.ticker]=scores.get(x.ticker,0)+float(weights.get(x.source,1))*base
        candidates=[(t,v) for t,v in scores.items() if abs(v)>=threshold and t in prices and d in prices[t].index and t not in positions];candidates.sort(key=lambda x:abs(x[1]),reverse=True);turnover=0;slots=max(1,int(1/maxpos))
        for t,sc in candidates[:max(0,slots-len(positions))]:
            direction=1 if sc>0 else (-1 if long_short else 0)
            if not direction:continue
            notional=equity*maxpos;cost=notional*(tc_bps+slip_bps)/10000;equity-=cost;turnover+=notional/equity if equity else 0;positions[t]={"notional":notional,"dir":direction,"age":0,"score":sc}
        dr=equity/prev_equity-1 if prev_equity else 0;daily_rets.append((d,dr));prev_equity=equity;curve.append((d,equity,turnover,sum(abs(x["notional"]) for x in positions.values())/equity if equity else 0,sum(x["notional"]*x["dir"] for x in positions.values())/equity if equity else 0))
    es=pd.Series({d:e for d,e,*_ in curve},dtype=float);rs=pd.Series({d:r for d,r in daily_rets},dtype=float);b=None;bt=cfg.get("benchmark","SPY")
    if bt in prices:bp=prices[bt].reindex(es.index).ffill();b=bp.pct_change().fillna(0)
    metrics=_metrics(es,rs,b);peak=es.cummax();monthly=rs.groupby([pd.Index(rs.index).map(lambda x:x.year),pd.Index(rs.index).map(lambda x:x.month)]).apply(lambda x:(1+x).prod()-1);annual=rs.groupby(pd.Index(rs.index).map(lambda x:x.year)).apply(lambda x:(1+x).prod()-1)
    result={"metrics":metrics,"ending_equity":float(equity),"monthly":{f"{y}-{m:02d}":float(v) for (y,m),v in monthly.items()},"annual":{str(y):float(v) for y,v in annual.items()},"equity":[{"date":str(d),"equity":float(e),"turnover":float(to),"gross":float(g),"net":float(n),"drawdown":float(e/peak.loc[d]-1)} for d,e,to,g,n in curve]}
    run=StrategyRun(name=cfg.get("name","portfolio"),config_json=json.dumps(cfg),result_json=json.dumps(result));s.add(run);s.commit()
    for x in result["equity"]:s.add(DailyPortfolio(run_id=run.id,date=datetime.fromisoformat(x["date"]),equity=x["equity"],gross_exposure=x["gross"],net_exposure=x["net"],turnover=x["turnover"],drawdown=x["drawdown"]))
    s.commit();result["run_id"]=run.id;return result
