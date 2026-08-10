from datetime import datetime,date
import json,re
from sqlalchemy.exc import IntegrityError
from .models import Event,EntityAlias

def dt(x, fallback=None):
    if isinstance(x,datetime): return x.replace(tzinfo=None)
    if isinstance(x,date): return datetime.combine(x,datetime.min.time())
    if not x: return fallback or datetime.utcnow()
    s=str(x).strip().replace("Z","+00:00")
    try: return datetime.fromisoformat(s).replace(tzinfo=None)
    except:
        for f in ("%m/%d/%Y","%Y-%m-%d","%m/%d/%Y %H:%M:%S"):
            try:return datetime.strptime(s[:19],f)
            except:pass
    return fallback or datetime.utcnow()

def num(x):
    if x is None:return None
    s=re.sub(r"[^0-9.\-]","",str(x).replace(",",""))
    try:return float(s)
    except:return None

def resolve_ticker(session,name):
    if not name:return None
    n=name.upper()
    for a in session.query(EntityAlias).all():
        z=a.alias.upper()
        if z in n or n in z:return a.ticker.upper()
    return None

def put_event(session,**kw):
    e=Event(**kw);session.add(e)
    try:session.commit();return 1
    except IntegrityError:session.rollback();return 0
