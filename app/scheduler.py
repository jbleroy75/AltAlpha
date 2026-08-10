from apscheduler.schedulers.background import BackgroundScheduler
from .db import SessionLocal
from .collectors.sec import collect_form4

def sec_job():
    with SessionLocal() as s:
        try:collect_form4(s,100)
        except Exception as e:print("SEC scheduler:",e)

scheduler=BackgroundScheduler(timezone="UTC")
def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(sec_job,"interval",minutes=30,id="sec_form4",replace_existing=True,max_instances=1);scheduler.start()
