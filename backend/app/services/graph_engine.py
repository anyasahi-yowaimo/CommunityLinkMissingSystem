import networkx as nx
from sqlalchemy.orm import Session
from ..models import Club, Need, Collaboration

def build_graph(db: Session) -> nx.MultiDiGraph:
    graph=nx.MultiDiGraph()
    clubs=db.query(Club).order_by(Club.id).all(); needs=db.query(Need).order_by(Need.id).all()
    for c in clubs:
        graph.add_node(f'club:{c.id}', kind='club', name=c.name, active=c.active)
        for skill in c.skills or []:
            sid='skill:'+skill.casefold().replace(' ','-')
            graph.add_node(sid,kind='skill',name=skill)
            graph.add_edge(f'club:{c.id}',sid,relationship='OFFERS',verified=skill in (c.verified_skills or []),source_id=c.id)
        for resource in c.resources or []:
            rid='resource:'+resource.casefold().replace(' ','-')
            graph.add_node(rid,kind='resource',name=resource)
            graph.add_edge(f'club:{c.id}',rid,relationship='OWNS',permission=(c.resource_permissions or {}).get(resource,'unknown'),source_id=c.id)
    for n in needs:
        graph.add_node(f'need:{n.id}',kind='need',title=n.title,status=n.status)
        graph.add_edge(f'club:{n.club_id}',f'need:{n.id}',relationship='NEEDS',source_id=n.id)
        for skill in n.required_skills or []:
            sid='skill:'+skill.casefold().replace(' ','-')
            graph.add_node(sid,kind='skill',name=skill)
            graph.add_edge(f'need:{n.id}',sid,relationship='REQUIRES',source_id=n.id)
    for collab in db.query(Collaboration).all():
        if collab.status in ('accepted','active','completed'):
            for a in collab.participant_ids:
                for b in collab.participant_ids:
                    if a!=b: graph.add_edge(f'club:{a}',f'club:{b}',relationship='COLLABORATED_WITH',status=collab.status,source_id=collab.id)
    return graph
