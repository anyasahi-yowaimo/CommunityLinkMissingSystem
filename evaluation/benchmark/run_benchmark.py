"""Small deterministic synthetic smoke benchmark; metrics are not real-world accuracy."""
import json
from pathlib import Path
from statistics import mean
from sqlalchemy.orm import Session
from backend.app.db import SessionLocal, Base, engine
from backend.app.models import Club, Need, Recommendation
from backend.app.services.recommender import generate

def main():
    Base.metadata.create_all(bind=engine)
    db=SessionLocal()
    try:
        result=generate(db)
        recs=db.query(Recommendation).all()
        # This local smoke benchmark deliberately reports only measurable database metrics.
        out={'benchmark':'linkmissing-local-smoke-v1','data_type':'synthetic demo records','generated_new':result['generated'],'returned_candidates':len(recs),'mean_score':round(mean([r.scores['final'] for r in recs]),4) if recs else None,'exclusion_reason_counts':{},'precision_at_5':'not computed: no separately frozen complete ground-truth label set in this MVP build','recall_at_5':'not computed: no separately frozen complete ground-truth label set in this MVP build','warning':'Do not interpret these values as real-campus recommendation accuracy.'}
        for row in result['excluded']:
            for reason in row['reasons']: out['exclusion_reason_counts'][reason]=out['exclusion_reason_counts'].get(reason,0)+1
        dest=Path(__file__).resolve().parents[1]/'results'/'smoke_results.json'; dest.write_text(json.dumps(out,indent=2))
        print(json.dumps(out,indent=2))
    finally: db.close()
if __name__=='__main__': main()
