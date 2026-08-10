from __future__ import annotations
from datetime import datetime
from pathlib import Path
import requests
from .db import SessionLocal, init_db
from .models import SyncRun, SyncSourceStatus, EntityAlias
from .config import settings

IMPORT_DIR = Path(__file__).resolve().parents[1] / "data" / "imports"

def seed_watchlist(s):
    wanted={x.strip().upper() for x in settings.watchlist.split(",") if x.strip()}
    if not wanted:return 0
    r=requests.get("https://www.sec.gov/files/company_tickers.json",headers={"User-Agent":settings.sec_user_agent},timeout=30);r.raise_for_status();created=0
    for v in r.json().values():
        ticker=str(v.get("ticker","")).upper()
        if ticker not in wanted:continue
        title=str(v.get("title") or ticker);cik=str(v.get("cik_str") or "");row=s.query(EntityAlias).filter(EntityAlias.ticker==ticker).first()
        if row:
            if not row.cik:row.cik=cik
            if row.alias==ticker:row.alias=title
        else:s.add(EntityAlias(alias=title,ticker=ticker,cik=cik));created+=1
    s.commit();return created

SOURCES=["sec_form4","sec_13f","sec_companyfacts","lda","usaspending","bluesky","google_trends","congress_house","congress_senate","uspto","options_flow","finra_short_interest","corporate_flights","earnings_transcript","market_prices"]
def _row(s,run_id,source):
    x=SyncSourceStatus(run_id=run_id,source=source,status="running",inserted=0,started_at=datetime.utcnow());s.add(x);s.commit();s.refresh(x);return x
def _finish(s,row,status,inserted=0,message=None):row.status=status;row.inserted=int(inserted or 0);row.message=message;row.finished_at=datetime.utcnow();s.commit()
def _aliases(s,limit=50):return s.query(EntityAlias).filter(EntityAlias.ticker.isnot(None)).limit(limit).all()
def _first_existing(*names):
    for name in names:
        p=IMPORT_DIR/name
        if p.exists():return p
    return None

def run_sync(run_id:int):
    init_db()
    with SessionLocal() as s:
        run=s.get(SyncRun,run_id)
        if not run:return
        seed_watchlist(s);aliases=_aliases(s)
        for source in SOURCES:
            row=_row(s,run_id,source)
            try:
                inserted=0
                if source=="sec_form4":
                    from .collectors.sec import collect_form4;inserted=collect_form4(s,100)
                elif source=="sec_13f":
                    from .collectors.sec import collect_recent_13f;inserted=collect_recent_13f(s,20)
                elif source=="sec_companyfacts":
                    from .collectors.earnings import collect_companyfacts
                    targets=[a for a in aliases if a.cik][:25]
                    if not targets:_finish(s,row,"skipped",0,"Add aliases with CIKs to sync SEC Company Facts.");continue
                    for a in targets:inserted+=collect_companyfacts(s,a.cik,a.ticker)
                elif source=="lda":
                    from .collectors.lobbying import collect
                    targets=aliases[:15]
                    if not targets:_finish(s,row,"skipped",0,"Add company aliases to query lobbying disclosures.");continue
                    for a in targets:inserted+=collect(s,a.alias,None,2)
                elif source=="usaspending":
                    from .collectors.usaspending import collect
                    targets=aliases[:15]
                    if not targets:_finish(s,row,"skipped",0,"Add company aliases to query federal contracts.");continue
                    for a in targets:inserted+=collect(s,a.alias,365,2)
                elif source=="bluesky":
                    from .collectors.social import bluesky
                    targets=aliases[:15]
                    if not targets:_finish(s,row,"skipped",0,"Add company aliases to query social mentions.");continue
                    for a in targets:inserted+=bluesky(s,a.alias,a.ticker,50)
                elif source=="google_trends":
                    if not settings.google_trends_api_url:_finish(s,row,"skipped",0,"Google Trends API access is not configured.");continue
                    from .collectors.google_trends import collect
                    for a in aliases[:15]:inserted+=collect(s,a.alias,a.ticker)
                elif source=="congress_house":
                    from .collectors.congress_public import collect
                    inserted=collect(s,"house",90,2)
                elif source=="congress_senate":
                    from .collectors.congress_public import collect
                    inserted=collect(s,"senate",90,2)
                elif source=="uspto":
                    p=_first_existing("patents.csv","uspto.csv")
                    if p:
                        from .collectors.importers import import_patents;inserted=import_patents(s,p)
                    elif not settings.uspto_api_key:
                        _finish(s,row,"skipped",0,"USPTO patent data is public, but ODP API access now requires a USPTO account/API key. Set USPTO_API_KEY or place patents.csv in data/imports/.");continue
                    else:
                        _finish(s,row,"skipped",0,"USPTO_API_KEY detected. Place an ODP export in data/imports/patents.csv until the account-specific ODP endpoint is configured.");continue
                elif source=="options_flow":
                    p=_first_existing("options.csv","options_flow.csv")
                    if not p:_finish(s,row,"missing_import",0,"Consolidated professional options-flow history is generally licensed. Place a legally obtained options.csv in data/imports/.");continue
                    from .collectors.importers import import_options;inserted=import_options(s,p)
                elif source=="finra_short_interest":
                    from .collectors.finra_live import collect
                    inserted=collect(s,[a.ticker for a in aliases[:25]],100)
                elif source=="corporate_flights":
                    p=_first_existing("flights.csv","corporate_flights.csv")
                    if not p:_finish(s,row,"missing_import",0,"Place a legally obtained flights.csv in data/imports/ and map aircraft first.");continue
                    from .collectors.flights import import_flights;inserted=import_flights(s,p)
                elif source=="earnings_transcript":
                    p=_first_existing("transcripts.csv","earnings_transcripts.csv")
                    if not p:_finish(s,row,"missing_import",0,"No uniform official transcript API is available. Place a legally obtained transcripts.csv in data/imports/.");continue
                    from .collectors.importers import import_transcripts;inserted=import_transcripts(s,p)
                elif source=="market_prices":
                    from datetime import timedelta
                    from .prices import fetch
                    end=datetime.utcnow();start=end-timedelta(days=365*max(1,int(settings.bootstrap_price_years)));tickers=sorted({a.ticker.upper() for a in aliases if a.ticker}|{"SPY"})
                    if not tickers:_finish(s,row,"skipped",0,"No watchlist tickers available for price bootstrap.");continue
                    for ticker in tickers:
                        try:inserted+=fetch(s,ticker,start,end)
                        except Exception:continue
                _finish(s,row,"synced",inserted,f"Inserted {inserted} new records.")
            except Exception as e:
                s.rollback();_finish(s,row,"error",0,f"{type(e).__name__}: {e}")
        statuses=s.query(SyncSourceStatus).filter_by(run_id=run_id).all();run.status="completed_with_errors" if any(x.status=="error" for x in statuses) else "completed";run.finished_at=datetime.utcnow();s.commit()

def create_sync(triggered_by="manual"):
    init_db()
    with SessionLocal() as s:
        r=SyncRun(status="running",triggered_by=triggered_by);s.add(r);s.commit();s.refresh(r);return r.id

def snapshot(run_id:int|None=None):
    with SessionLocal() as s:
        run=s.get(SyncRun,run_id) if run_id else s.query(SyncRun).order_by(SyncRun.id.desc()).first()
        if not run:return {"run":None,"sources":[]}
        rows=s.query(SyncSourceStatus).filter_by(run_id=run.id).order_by(SyncSourceStatus.id).all();return {"run":{"id":run.id,"status":run.status,"started_at":run.started_at,"finished_at":run.finished_at,"triggered_by":run.triggered_by},"sources":[{"source":x.source,"status":x.status,"inserted":x.inserted,"message":x.message,"started_at":x.started_at,"finished_at":x.finished_at} for x in rows]}
