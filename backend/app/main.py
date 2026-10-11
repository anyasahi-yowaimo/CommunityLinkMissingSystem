from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text
from .db import Base, engine, get_db
from .models import Club, Need, Recommendation, Feedback, Collaboration
from .services.recommender import generate, serialize
from .services.graph_engine import build_graph

Base.metadata.create_all(bind=engine)
app=FastAPI(title='LinkMissing API',version='1.0.0',description='Evidence-based cross-community collaboration discovery. Seed records are synthetic.')
STATIC=Path(__file__).resolve().parents[2]/'frontend'/'static'
app.mount('/static',StaticFiles(directory=str(STATIC)),name='static')
@app.get('/',include_in_schema=False)
def home(): return FileResponse(STATIC/'index.html')
@app.get('/health')
def health(): return {'status':'ok','service':'linkmissing'}
@app.get('/health/ready')
def ready(db:Session=Depends(get_db)):
    try: db.execute(text('SELECT 1')); return {'status':'ready','database':'connected'}
    except Exception as e: raise HTTPException(503,detail={'code':'DATABASE_UNAVAILABLE','message':'Database is unavailable'}) from e

class ClubIn(BaseModel):
    name:str=Field(min_length=2,max_length=120); category:str='General'; description:str=''; skills:list[str]=[]; verified_skills:list[str]=[]; resources:list[str]=[]; resource_permissions:dict[str,str]={}; active:bool=True; willing:bool=True; availability:str='flexible'; workload:str='medium'
class NeedIn(BaseModel):
    club_id:int; title:str=Field(min_length=3,max_length=180); description:str=''; required_skills:list[str]=[]; required_resources:list[str]=[]; status:str='open'; priority:str='medium'; duration_weeks:int=Field(default=6,ge=1,le=52); availability:str='flexible'; workload:str='medium'
class FeedbackIn(BaseModel): category:str=Field(min_length=2,max_length=60); explanation:str=''
class DecisionIn(BaseModel): note:str=''

def club_json(c): return {'id':c.id,'name':c.name,'category':c.category,'description':c.description,'skills':c.skills,'verified_skills':c.verified_skills,'resources':c.resources,'resource_permissions':c.resource_permissions,'active':c.active,'willing':c.willing,'availability':c.availability,'workload':c.workload,'profile_version':c.profile_version,'synthetic':c.synthetic}
def need_json(n, db):
    c=db.get(Club,n.club_id); return {'id':n.id,'club_id':n.club_id,'club':c.name if c else 'Unknown','title':n.title,'description':n.description,'required_skills':n.required_skills,'required_resources':n.required_resources,'status':n.status,'priority':n.priority,'duration_weeks':n.duration_weeks,'availability':n.availability,'workload':n.workload,'version':n.version}
@app.get('/api/clubs')
def clubs(q:str|None=None,limit:int=Query(100,ge=1,le=200),db:Session=Depends(get_db)):
    rows=db.query(Club).order_by(Club.name).all()
    if q: rows=[c for c in rows if q.casefold() in c.name.casefold() or q.casefold() in c.category.casefold()]
    return {'items':[club_json(c) for c in rows[:limit]],'total':len(rows)}
@app.post('/api/clubs',status_code=201)
def create_club(body:ClubIn,db:Session=Depends(get_db)):
    if db.query(Club).filter_by(name=body.name).first(): raise HTTPException(409,'Club name already exists')
    c=Club(**body.model_dump(),synthetic=False); db.add(c); db.commit(); db.refresh(c); return club_json(c)
@app.get('/api/clubs/{club_id}')
def get_club(club_id:int,db:Session=Depends(get_db)):
    c=db.get(Club,club_id)
    if not c: raise HTTPException(404,'Club not found')
    return club_json(c)
@app.patch('/api/clubs/{club_id}')
def patch_club(club_id:int,body:dict,db:Session=Depends(get_db)):
    c=db.get(Club,club_id)
    if not c: raise HTTPException(404,'Club not found')
    allowed=set(ClubIn.model_fields)
    unknown=set(body)-allowed
    if unknown: raise HTTPException(422,detail={'code':'INVALID_FIELDS','fields':sorted(unknown)})
    for k,v in body.items(): setattr(c,k,v)
    c.profile_version+=1; db.commit(); db.refresh(c); return club_json(c)
@app.get('/api/needs')
def needs(status:str|None=None,db:Session=Depends(get_db)):
    q=db.query(Need)
    if status: q=q.filter_by(status=status)
    return {'items':[need_json(n,db) for n in q.order_by(Need.id).all()]}
@app.post('/api/needs',status_code=201)
def create_need(body:NeedIn,db:Session=Depends(get_db)):
    if not db.get(Club,body.club_id): raise HTTPException(422,detail={'code':'INVALID_CLUB_ID','message':'club_id does not exist'})
    n=Need(**body.model_dump(),synthetic=False); db.add(n); db.commit(); db.refresh(n); return need_json(n,db)
@app.patch('/api/needs/{need_id}')
def patch_need(need_id:int,body:dict,db:Session=Depends(get_db)):
    n=db.get(Need,need_id)
    if not n: raise HTTPException(404,'Need not found')
    allowed=set(NeedIn.model_fields)-{'club_id'}
    if set(body)-allowed: raise HTTPException(422,detail={'code':'INVALID_FIELDS','fields':sorted(set(body)-allowed)})
    for k,v in body.items(): setattr(n,k,v)
    n.version+=1; db.commit(); db.refresh(n); return need_json(n,db)
@app.get('/api/recommendations')
def recommendations(status:str|None=None,db:Session=Depends(get_db)):
    q=db.query(Recommendation)
    if status: q=q.filter_by(status=status)
    clubs={c.id:c for c in db.query(Club).all()}
    return {'items':[serialize(r,clubs) for r in q.order_by(Recommendation.scores['final'].as_float().desc(),Recommendation.id).all()]}
@app.post('/api/recommendations/generate')
def generate_recommendations(db:Session=Depends(get_db)): return generate(db)
@app.get('/api/recommendations/{rec_id}')
def recommendation(rec_id:int,db:Session=Depends(get_db)):
    r=db.get(Recommendation,rec_id)
    if not r: raise HTTPException(404,'Recommendation not found')
    return serialize(r,{c.id:c for c in db.query(Club).all()})
@app.post('/api/recommendations/{rec_id}/feedback',status_code=201)
def feedback(rec_id:int,body:FeedbackIn,db:Session=Depends(get_db)):
    if not db.get(Recommendation,rec_id): raise HTTPException(404,'Recommendation not found')
    f=Feedback(recommendation_id=rec_id,category=body.category,explanation=body.explanation); db.add(f); db.commit(); db.refresh(f); return {'id':f.id,'recommendation_id':rec_id,'category':f.category,'explanation':f.explanation}
@app.post('/api/recommendations/{rec_id}/accept')
def accept(rec_id:int,body:DecisionIn,db:Session=Depends(get_db)):
    r=db.get(Recommendation,rec_id)
    if not r: raise HTTPException(404,'Recommendation not found')
    if r.status=='accepted': return {'status':'accepted','id':r.id,'idempotent':True}
    r.status='accepted'; need=db.get(Need,r.need_id); scope=need.title if need else r.proposal.get('title',''); existing=db.query(Collaboration).filter_by(need_id=r.need_id,scope=scope,status='accepted').first();
    if not existing: db.add(Collaboration(need_id=r.need_id,participant_ids=r.participant_ids,status='accepted',scope=scope))
    db.commit(); return {'status':'accepted','id':r.id,'idempotent':bool(existing)}
@app.post('/api/recommendations/{rec_id}/reject')
def reject(rec_id:int,body:DecisionIn,db:Session=Depends(get_db)):
    r=db.get(Recommendation,rec_id)
    if not r: raise HTTPException(404,'Recommendation not found')
    r.status='rejected'; db.commit(); return {'status':'rejected','id':r.id,'note':body.note}
@app.get('/api/analytics/overview')
def overview(db:Session=Depends(get_db)):
    return {'clubs':db.query(Club).count(),'active_clubs':db.query(Club).filter_by(active=True).count(),'open_needs':db.query(Need).filter_by(status='open').count(),'recommendations':db.query(Recommendation).count(),'accepted':db.query(Recommendation).filter_by(status='accepted').count(),'synthetic_notice':'All seeded organizations and benchmark records are fictional.'}
@app.get('/api/analytics/graph')
def graph(db:Session=Depends(get_db)):
    g=build_graph(db); return {'nodes':[{'id':n,**d} for n,d in g.nodes(data=True)],'edges':[{'source':a,'target':b,**d} for a,b,d in g.edges(data=True)],'node_count':g.number_of_nodes(),'edge_count':g.number_of_edges()}
@app.get('/api/analytics/quality')
def quality(db:Session=Depends(get_db)):
    rows=db.query(Recommendation).all(); return {'recommendations':len(rows),'mean_score':round(sum(r.scores.get('final',0) for r in rows)/len(rows),4) if rows else None,'explanation_grounding':'Each listed skill/resource match references persisted club and need records; synthetic seed data only.','benchmark_status':'Run python -m evaluation.benchmark.run_benchmark for measured metrics.'}
