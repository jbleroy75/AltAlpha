from __future__ import annotations
import math,numpy as np,pandas as pd
from scipy.stats import norm

def sharpe(returns,periods=252):
    r=np.asarray(returns,float);return float(np.mean(r)/np.std(r,ddof=1)*math.sqrt(periods)) if len(r)>2 and np.std(r,ddof=1)>0 else None

def deflated_sharpe_ratio(returns,n_trials=1,periods=252):
    r=np.asarray(returns,float);r=r[np.isfinite(r)]
    if len(r)<10:return None
    sr=np.mean(r)/np.std(r,ddof=1);skew=pd.Series(r).skew();kurt=pd.Series(r).kurt()+3;em=norm.ppf(1-1/max(n_trials,2))*1/math.sqrt(max(len(r)-1,1));denom=math.sqrt(max((1-skew*sr+(kurt-1)/4*sr*sr)/(len(r)-1),1e-12));return float(norm.cdf((sr-em)/denom))

def probabilistic_sharpe_ratio(returns,benchmark_sr=0):
    r=np.asarray(returns,float);r=r[np.isfinite(r)]
    if len(r)<10:return None
    sr=np.mean(r)/np.std(r,ddof=1);sk=pd.Series(r).skew();ku=pd.Series(r).kurt()+3;den=math.sqrt(max((1-sk*sr+(ku-1)/4*sr*sr)/(len(r)-1),1e-12));return float(norm.cdf((sr-benchmark_sr/math.sqrt(252))/den))

def bootstrap_sharpe_ci(returns,n_boot=1000,seed=42):
    r=np.asarray(returns,float);r=r[np.isfinite(r)]
    if len(r)<10:return None
    rng=np.random.default_rng(seed);vals=[]
    for _ in range(n_boot):
        sample=rng.choice(r,size=len(r),replace=True);v=sharpe(sample)
        if v is not None:vals.append(v)
    return {"low":float(np.percentile(vals,2.5)),"median":float(np.percentile(vals,50)),"high":float(np.percentile(vals,97.5))}

def purged_kfold_indices(n,k=5,purge=5,embargo=5):
    idx=np.arange(n);folds=np.array_split(idx,k);out=[]
    for test in folds:
        lo=max(0,test[0]-purge);hi=min(n,test[-1]+embargo+1);train=np.concatenate([idx[:lo],idx[hi:]]);out.append((train,test))
    return out

def overfit_diagnostics(candidate_returns):
    if not candidate_returns:return {}
    df=pd.DataFrame(candidate_returns).dropna()
    if len(df)<30:return {"error":"insufficient observations"}
    folds=purged_kfold_indices(len(df),k=min(5,max(2,len(df)//20)));winners=[];test_scores=[]
    for tr,te in folds:
        train_sr={c:sharpe(df[c].iloc[tr]) or -99 for c in df};winner=max(train_sr,key=train_sr.get);winners.append(winner);test_scores.append(sharpe(df[winner].iloc[te]) or -99)
    negative=sum(x<0 for x in test_scores)/len(test_scores);return {"fold_winners":winners,"oos_sharpes":test_scores,"p_oos_negative":negative,"winner_stability":max(winners.count(x) for x in set(winners))/len(winners)}
