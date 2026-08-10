from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.models import SyncRun, SyncSourceStatus

def test_sync_models_persist_status():
    engine=create_engine('sqlite:///:memory:');Base.metadata.create_all(engine);S=sessionmaker(bind=engine)
    with S() as s:
        run=SyncRun(status='running',triggered_by='test');s.add(run);s.commit();s.refresh(run);row=SyncSourceStatus(run_id=run.id,source='sec_form4',status='synced',inserted=3);s.add(row);s.commit();assert s.query(SyncSourceStatus).filter_by(run_id=run.id).one().inserted==3
