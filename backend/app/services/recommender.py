import hashlib, json
from sqlalchemy.orm import Session
from ..models import Club, Need, Collaboration, Recommendation

WEIGHTS={'need_match':.35,'complementarity':.25,'feasibility':.20,'actionability':.15,'redundancy':.05}
ACTIVE_STATUSES={'proposed','accepted','active','completed'}

def fingerprint(need, ids, clubs):
    payload={'need':need.id,'need_version':need.version,'participants':sorted(ids),'club_versions':[(i,clubs[i].profile_version) for i in sorted(ids)]}
    return hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()

def generate(db: Session):
    created=[]; excluded=[]
    clubs={c.id:c for c in db.query(Club).all()}
    for need in db.query(Need).filter(Need.status=='open').order_by(Need.id).all():
        owner=clubs.get(need.club_id)
        if not owner or not owner.active: continue
        for partner in sorted(clubs.values(),key=lambda c:c.id):
            if partner.id==owner.id: continue
            reasons=[]
            if not partner.active: reasons.append('CLUB_INACTIVE')
            if not partner.willing: reasons.append('COLLABORATION_NOT_WELCOME')
            if need.availability!='flexible' and partner.availability not in ('flexible',need.availability): reasons.append('AVAILABILITY_MISMATCH')
            if need.workload=='high' and partner.workload=='high': reasons.append('WORKLOAD_CONFLICT')
            if not need.required_skills: reasons.append('INSUFFICIENT_EVIDENCE')
            matched=[s for s in need.required_skills if s.casefold() in [x.casefold() for x in (partner.verified_skills or [])]]
            if len(matched)<len(need.required_skills): reasons.append('SKILL_EVIDENCE_MISSING')
            res_matches=[]
            for req in need.required_resources or []:
                if req not in (partner.resources or []):
                    reasons.append('RESOURCE_UNAVAILABLE')
                else:
                    permission=(partner.resource_permissions or {}).get(req,'unknown')
                    if permission!='permitted': reasons.append('RESOURCE_PERMISSION_MISSING' if permission!='unavailable' else 'RESOURCE_UNAVAILABLE')
                    else: res_matches.append(req)
            ids=sorted([owner.id,partner.id]); scope=need.title.casefold().strip()
            existing=db.query(Collaboration).filter(Collaboration.need_id==need.id,Collaboration.status.in_(ACTIVE_STATUSES)).all()
            if any(sorted(x.participant_ids)==ids and x.scope.casefold().strip()==scope for x in existing): reasons.append('DUPLICATE_ACTIVE_PARTNERSHIP' if any(x.status!='completed' for x in existing if sorted(x.participant_ids)==ids and x.scope.casefold().strip()==scope) else 'DUPLICATE_COMPLETED_SCOPE')
            if reasons:
                excluded.append({'need_id':need.id,'participant_ids':ids,'reasons':sorted(set(reasons))}); continue
            N=len(matched)/max(1,len(need.required_skills))
            C=min(1.0,(len(set(partner.verified_skills)-set(owner.verified_skills)) + len(res_matches))/max(1,len(need.required_skills)+len(need.required_resources or [])))
            F=1.0 if partner.availability=='flexible' or partner.availability==need.availability else .7
            A=.85 if need.title and need.description else .6
            R=0.0
            score=WEIGHTS['need_match']*N+WEIGHTS['complementarity']*C+WEIGHTS['feasibility']*F+WEIGHTS['actionability']*A-WEIGHTS['redundancy']*R
            fp=fingerprint(need,ids,clubs)
            existing_rec=db.query(Recommendation).filter_by(fingerprint=fp).first()
            if existing_rec:
                continue
            evidence={'skill_matches':[{'skill':s,'club_id':partner.id,'verified':True} for s in matched], 'resource_matches':[{'resource':r,'club_id':partner.id,'permission':'permitted'} for r in res_matches], 'source_need_id':need.id,'source_club_ids':ids}
            title=f'{need.title}: {owner.name} × {partner.name}'
            proposal={'title':title,'problem_statement':need.description,'need_id':need.id,'participants':[{'club_id':owner.id,'club':owner.name,'contribution':'Define the problem, constraints and acceptance criteria.'},{'club_id':partner.id,'club':partner.name,'contribution':'Provide verified '+', '.join(matched)+' capability.'}], 'required_skills':need.required_skills,'required_resources':need.required_resources or [],'deliverable':f'Working prototype for {need.title}','first_milestone':'Hold a 30-minute scope and feasibility review; confirm data and responsibilities.','suggested_timeline_weeks':need.duration_weeks,'risks':['Confirm participant availability and ownership of deliverables.'],'unanswered_questions':['Do both coordinators approve the proposed scope?'],'next_action':'Ask both coordinators to review this proposal.'}
            rec=Recommendation(need_id=need.id,participant_ids=ids,title=title,scores={'need_match':round(N,4),'complementarity':round(C,4),'feasibility':round(F,4),'actionability':round(A,4),'redundancy':R,'final':round(score,4)},evidence=evidence,explanation=f'{partner.name} has verified evidence for {", ".join(matched)}. The need is open. Availability and willingness checks passed using stored profile fields. Coordinator confirmation is still required.',proposal=proposal,fingerprint=fp)
            db.add(rec); db.flush(); created.append(rec)
    db.commit()
    return {'generated':len(created),'excluded':excluded,'recommendations':[serialize(r,clubs,need_map={n.id:n for n in db.query(Need).all()}) for r in created]}

def serialize(r, clubs=None, need_map=None):
    clubs=clubs or {}
    return {'id':r.id,'need_id':r.need_id,'participant_ids':r.participant_ids,'title':r.title,'scores':r.scores,'evidence':r.evidence,'explanation':r.explanation,'proposal':r.proposal,'status':r.status,'model_version':r.model_version,'clubs':[clubs[i].name for i in r.participant_ids if i in clubs]}
