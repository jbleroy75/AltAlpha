from __future__ import annotations
import numpy as np
from scipy.optimize import minimize

def optimize(expected_returns,covariance,max_position=.10,gross_limit=1.0,net_target=1.0,
             risk_aversion=5.0,turnover_penalty=0.001,previous=None,long_short=False,
             sector_matrix=None,sector_limit=.25):
    tickers=list(expected_returns)
    mu=np.array([expected_returns[t] for t in tickers],float)
    cov=np.asarray(covariance,float)+np.eye(len(tickers))*1e-8
    prev=np.zeros(len(tickers)) if previous is None else np.array([previous.get(t,0) for t in tickers])
    bounds=[(-max_position,max_position) if long_short else (0,max_position) for _ in tickers]
    def obj(w):
        risk=w@cov@w
        turnover=np.sqrt((w-prev)**2+1e-10).sum()
        return -(mu@w)+risk_aversion*risk+turnover_penalty*turnover
    cons=[{"type":"ineq","fun":lambda w:gross_limit-np.abs(w).sum()},{"type":"eq","fun":lambda w:w.sum()-net_target}]
    if sector_matrix is not None and len(sector_matrix):
        sm=np.asarray(sector_matrix,float)
        for i in range(sm.shape[1]):
            cons.append({"type":"ineq","fun":lambda w,i=i:sector_limit-abs(sm[:,i]@w)})
    x0=np.clip(np.repeat(net_target/max(len(tickers),1),len(tickers)),bounds[0][0],bounds[0][1])
    res=minimize(obj,x0,method="SLSQP",bounds=bounds,constraints=cons,options={"maxiter":1000,"ftol":1e-10})
    return {"success":bool(res.success),"message":res.message,"weights":{t:float(w) for t,w in zip(tickers,res.x)},"objective":float(res.fun)}
