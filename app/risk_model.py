from __future__ import annotations
import numpy as np, pandas as pd
from .models import Price,Security

def returns_matrix(session,tickers,start,end,min_obs=60):
    series={}
    for t in tickers:
        rows=(session.query(Price).filter(Price.ticker==t.upper(),Price.date>=start,Price.date<=end).order_by(Price.date).all())
        if len(rows)>=min_obs:
            px=pd.Series({x.date.date():x.close for x in rows},name=t.upper()).sort_index();series[t.upper()]=px.pct_change()
    return pd.DataFrame(series).dropna(how="all") if series else pd.DataFrame()

def statistical_factors(ret,n_factors=5):
    x=ret.fillna(0.0)
    if x.empty:return {"exposures":pd.DataFrame(),"factor_returns":pd.DataFrame(),"specific_var":pd.Series(dtype=float)}
    xc=x-x.mean();cov=xc.cov().values
    vals,vecs=np.linalg.eigh(cov);idx=np.argsort(vals)[::-1][:min(n_factors,len(vals))];vals=vals[idx];vecs=vecs[:,idx]
    exposures=pd.DataFrame(vecs*np.sqrt(np.maximum(vals,0)),index=x.columns,columns=[f"PC{i+1}" for i in range(len(idx))])
    f=np.linalg.pinv(exposures.values)@xc.T.values;factor_returns=pd.DataFrame(f.T,index=xc.index,columns=exposures.columns)
    fitted=factor_returns.values@exposures.values.T;resid=xc.values-fitted
    specific_var=pd.Series(np.var(resid,axis=0,ddof=1),index=x.columns)
    return {"exposures":exposures,"factor_returns":factor_returns,"specific_var":specific_var}

def fundamental_exposures(session,tickers,asof):
    rows=session.query(Security).filter(Security.ticker.in_([x.upper() for x in tickers])).all()
    sector={r.ticker:r.sector or "Unknown" for r in rows if (r.valid_from is None or r.valid_from<=asof) and (r.valid_to is None or r.valid_to>=asof)}
    sectors=sorted(set(sector.values()));df=pd.DataFrame(0.0,index=[x.upper() for x in tickers],columns=[f"sector:{s}" for s in sectors])
    for t,s in sector.items():
        if t in df.index:df.loc[t,f"sector:{s}"]=1.0
    return df

def risk_report(weights,ret,model):
    w=pd.Series(weights,dtype=float).reindex(ret.columns).fillna(0);cov=ret.cov()*252
    vol=float(np.sqrt(max(w.values@cov.values@w.values,0)))
    exp=model["exposures"].reindex(ret.columns).fillna(0).T@w if not model["exposures"].empty else pd.Series(dtype=float)
    marginal=(cov.values@w.values)/vol if vol else np.zeros(len(w));component=pd.Series(w.values*marginal,index=w.index)
    return {"annualized_volatility":vol,"factor_exposure":{k:float(v) for k,v in exp.items()},"component_risk":{k:float(v) for k,v in component.items()}}
