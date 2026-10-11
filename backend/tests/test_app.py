import os, tempfile
from fastapi.testclient import TestClient

# Test the app against a temporary SQLite database before importing app modules.
fd,path=tempfile.mkstemp(suffix='.db'); os.close(fd)
os.environ['LINKMISSING_DATABASE_URL']='sqlite:///'+path
from app.main import app
from app.db import Base, engine
client=TestClient(app)

def setup_module():
    Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)
    from app.db import SessionLocal
    from app.models import Club,Need
    db=SessionLocal(); c=Club(name='Need Owner',category='Tech',description='owner',skills=[],verified_skills=[],resources=[],resource_permissions={},active=True,willing=True,availability='flexible',workload='low',synthetic=True); p=Club(name='Verified Partner',category='AI',description='partner',skills=['computer vision'],verified_skills=['computer vision'],resources=[],resource_permissions={},active=True,willing=True,availability='flexible',workload='low',synthetic=True); db.add_all([c,p]); db.flush(); db.add(Need(club_id=c.id,title='Vision prototype',description='Detect objects',required_skills=['computer vision'],required_resources=[],status='open',priority='high',duration_weeks=4,availability='flexible',workload='medium',synthetic=True)); db.commit(); db.close()
def test_health_and_ready():
    assert client.get('/health').json()['status']=='ok'
    assert client.get('/health/ready').status_code==200
def test_candidate_generation_is_persisted_and_grounded():
    result=client.post('/api/recommendations/generate',json={}).json()
    assert result['generated']==1
    recs=client.get('/api/recommendations').json()['items']
    assert len(recs)==1 and recs[0]['scores']['final']>0
    assert recs[0]['evidence']['skill_matches'][0]['skill']=='computer vision'
def test_duplicate_generation_is_idempotent():
    client.post('/api/recommendations/generate',json={})
    assert len(client.get('/api/recommendations').json()['items'])==1
def test_feedback_and_acceptance():
    rec=client.get('/api/recommendations').json()['items'][0]; rid=rec['id']
    assert client.post(f'/api/recommendations/{rid}/feedback',json={'category':'useful','explanation':'clear'}).status_code==201
    assert client.post(f'/api/recommendations/{rid}/accept',json={'note':''}).status_code==200
    assert client.post(f'/api/recommendations/{rid}/accept',json={'note':''}).json()['idempotent'] is True
def test_validation_and_missing_records():
    assert client.post('/api/clubs',json={'name':'x'}).status_code==422
    assert client.get('/api/clubs/99999').status_code==404
def test_graph_is_database_derived():
    data=client.get('/api/analytics/graph').json()
    assert data['node_count']>=3 and any(n['id'].startswith('need:') for n in data['nodes'])
