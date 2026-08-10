import itertools,random
from datetime import datetime,timedelta
from .portfolio import run_portfolio

def walk_forward_windows(start,end,train_days=730,test_days=180):
    s=datetime.fromisoformat(start);e=datetime.fromisoformat(end);out=[];cursor=s
    while cursor+timedelta(days=train_days+test_days)<=e:
        tr0=cursor;tr1=cursor+timedelta(days=train_days);te1=tr1+timedelta(days=test_days);out.append((tr0,tr1,te1));cursor+=timedelta(days=test_days)
    return out

def discover(s,cfg):
    sources=cfg["candidate_sources"];max_trials=min(int(cfg.get("max_trials",30)),100);thresholds=cfg.get("thresholds",[1.5,2.5,3.5]);holds=cfg.get("holding_days_grid",[5,20,60]);windows=walk_forward_windows(cfg["start"],cfg["end"],int(cfg.get("train_days",730)),int(cfg.get("test_days",180)));candidates=[];combos=[]
    for k in range(1,min(4,len(sources))+1):combos.extend(itertools.combinations(sources,k))
    random.Random(42).shuffle(combos)
    for combo in combos[:max_trials]:
        for th in thresholds[:2]:
            for hold in holds[:2]:
                fold=[]
                for tr0,tr1,te1 in windows:
                    base={**cfg,"name":"discovery","sources":list(combo),"threshold":th,"holding_days":hold,"start":tr1.isoformat(),"end":te1.isoformat()}
                    for x in ("candidate_sources","max_trials","thresholds","holding_days_grid","train_days","test_days"):base.pop(x,None)
                    r=run_portfolio(s,base);fold.append({"start":tr1.date().isoformat(),"end":te1.date().isoformat(),"metrics":r["metrics"]})
                sharpes=[x["metrics"].get("sharpe") for x in fold if x["metrics"].get("sharpe") is not None];dds=[x["metrics"].get("max_drawdown") for x in fold if x["metrics"].get("max_drawdown") is not None];score=(sum(sharpes)/len(sharpes) if sharpes else -99)+(sum(dds)/len(dds) if dds else -1);candidates.append({"sources":list(combo),"threshold":th,"holding_days":hold,"oos_score":score,"folds":fold})
    candidates.sort(key=lambda x:x["oos_score"],reverse=True);return {"method":"walk-forward out-of-sample","tested":len(candidates),"top":candidates[:20]}
