import typer,json
from rich import print
from .db import init_db,SessionLocal
from .models import EntityAlias,AircraftMap
app=typer.Typer(no_args_is_help=True)
@app.command("init-db")
def init():init_db();print("[green]DB ready[/green]")
@app.command("alias")
def alias(name:str,ticker:str,cik:str=""):
    init_db()
    with SessionLocal() as s:
        x=s.query(EntityAlias).filter_by(alias=name).first()
        if x:x.ticker=ticker.upper();x.cik=cik or x.cik
        else:s.add(EntityAlias(alias=name,ticker=ticker.upper(),cik=cik or None))
        s.commit()
@app.command("aircraft")
def aircraft(registration:str,ticker:str,company:str=""):
    init_db()
    with SessionLocal() as s:s.add(AircraftMap(registration=registration.upper(),ticker=ticker.upper(),company=company or None));s.commit()
@app.command("sec-form4")
def form4(count:int=40):
    from .collectors.sec import collect_form4
    init_db()
    with SessionLocal() as s:print({"inserted":collect_form4(s,count)})
@app.command("sec-13f")
def f13(cik:str):
    from .collectors.sec import collect_13f
    init_db()
    with SessionLocal() as s:print({"inserted":collect_13f(s,cik)})
@app.command("lobbying")
def lobbying(client:str="",year:int=0,pages:int=5):
    from .collectors.lobbying import collect
    init_db()
    with SessionLocal() as s:print({"inserted":collect(s,client or None,year or None,pages)})
@app.command("contracts")
def contracts(recipient:str,days:int=365):
    from .collectors.usaspending import collect
    init_db()
    with SessionLocal() as s:print({"inserted":collect(s,recipient,days)})
@app.command("bluesky")
def bluesky(query:str,ticker:str="",limit:int=100):
    from .collectors.social import bluesky as go
    init_db()
    with SessionLocal() as s:print({"inserted":go(s,query,ticker or None,limit)})
@app.command("earnings")
def earnings(cik:str,ticker:str):
    from .collectors.earnings import collect_companyfacts
    init_db()
    with SessionLocal() as s:print({"inserted":collect_companyfacts(s,cik,ticker)})
@app.command("import-congress")
def congress(path:str,chamber:str):
    from .collectors.importers import import_congress
    init_db()
    with SessionLocal() as s:print({"inserted":import_congress(s,path,chamber)})
@app.command("import-patents")
def patents(path:str):
    from .collectors.importers import import_patents
    init_db()
    with SessionLocal() as s:print({"inserted":import_patents(s,path)})
@app.command("import-options")
def options(path:str):
    from .collectors.importers import import_options
    init_db()
    with SessionLocal() as s:print({"inserted":import_options(s,path)})
@app.command("import-short-interest")
def short(path:str):
    from .collectors.short_interest import import_finra
    init_db()
    with SessionLocal() as s:print({"inserted":import_finra(s,path)})
@app.command("import-flights")
def flights(path:str):
    from .collectors.flights import import_flights
    init_db()
    with SessionLocal() as s:print({"inserted":import_flights(s,path)})
@app.command("import-transcripts")
def transcripts(path:str):
    from .collectors.importers import import_transcripts
    init_db()
    with SessionLocal() as s:print({"inserted":import_transcripts(s,path)})
@app.command("strategy")
def strategy(path:str):
    import yaml
    from .strategy import run
    init_db();cfg=yaml.safe_load(open(path))
    with SessionLocal() as s:print(json.dumps(run(s,cfg),indent=2))
@app.command("sync-all")
def sync_all():
    from .sync_manager import create_sync,run_sync,snapshot
    init_db();rid=create_sync("cli");print(f"[cyan]Sync run #{rid}[/cyan]");run_sync(rid);print(json.dumps(snapshot(rid),indent=2,default=str))
@app.command("setup")
def setup():
    from pathlib import Path
    init_db();Path("data/imports").mkdir(parents=True,exist_ok=True);env=Path(".env")
    if not env.exists() and Path(".env.example").exists(): env.write_text(Path(".env.example").read_text())
    print("[green]AltAlpha setup complete.[/green]");print("Run: python -m app.cli sync-all");print("Then: uvicorn app.main:app --reload")
if __name__=="__main__":app()
