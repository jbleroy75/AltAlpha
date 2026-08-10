import numpy as np
from app.optimizer import optimize
from app.validation import deflated_sharpe_ratio,bootstrap_sharpe_ci,purged_kfold_indices
def test_optimizer_constraints():
    mu={"A":.1,"B":.08,"C":.05};cov=np.diag([.04,.03,.02]);r=optimize(mu,cov,max_position=.5,gross_limit=1,net_target=1);assert r["success"];assert abs(sum(r["weights"].values())-1)<1e-6;assert max(r["weights"].values())<=.500001
def test_validation_tools():
    rng=np.random.default_rng(1);x=rng.normal(.001,.01,300);d=deflated_sharpe_ratio(x,10);ci=bootstrap_sharpe_ci(x,100);assert 0<=d<=1 and ci["low"]<=ci["median"]<=ci["high"];folds=purged_kfold_indices(100,5,3,3);assert len(folds)==5
