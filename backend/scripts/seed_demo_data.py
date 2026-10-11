from app.db import Base, engine, SessionLocal
from app.models import Club, Need, Collaboration, Recommendation, Feedback
Base.metadata.create_all(bind=engine)
CLUBS=[
('Robotics Club','Robotics','Builds autonomous robots and prototypes.',['robotics','embedded systems'],['robotics','embedded systems'],[],{},True,True,'flexible','medium'),
('AI Club','Artificial Intelligence','Works on applied machine learning and computer vision.',['machine learning','computer vision','python'],['machine learning','computer vision','python'],[],{},True,True,'flexible','medium'),
('Photography Club','Arts','Student photography and image curation.',['photography','image curation'],['photography'],['campus image collection'],{'campus image collection':'permitted'},True,True,'flexible','low'),
('Web Development Club','Software','Builds web apps and APIs.',['web development','python','ui design'],['web development','python'],[],{},True,True,'flexible','medium'),
('Environmental Club','Sustainability','Campus sustainability and environmental monitoring.',['sustainability','field research'],['sustainability','field research'],[],{},True,True,'flexible','medium'),
('Entrepreneurship Club','Business','Student founders and product discovery.',['business','pitching'],['business'],[],{},True,True,'flexible','medium'),
('Design Club','Design','Human-centred design and prototyping.',['ui design','accessibility','prototyping'],['ui design','accessibility'],[],{},True,True,'flexible','medium'),
('Electronics Club','Engineering','Sensors and electronics prototyping.',['electronics','sensors'],['electronics','sensors'],['sensor kit'],{'sensor kit':'permitted'},True,True,'flexible','medium'),
('Data Science Club','Data','Data cleaning, statistics and dashboards.',['data analysis','statistics','python'],['data analysis','statistics','python'],[],{},True,True,'flexible','medium'),
('Community Service Club','Service','Community programmes and outreach.',['outreach','field research'],['outreach'],[],{},True,True,'flexible','low'),
('Cybersecurity Club','Security','Security awareness and threat modelling.',['cybersecurity','threat modelling'],['cybersecurity'],[],{},True,True,'flexible','medium'),
('IoT Club','Engineering','Connected devices and sensor networks.',['iot','sensors','embedded systems'],['iot','sensors'],[],{},True,True,'flexible','medium'),
('Gaming Club','Gaming','Game development and student events.',['game development','3d design'],['game development'],[],{},True,True,'flexible','medium'),
('Literary Society','Literature','Writing, editing and storytelling.',['writing','editing'],['writing'],[],{},True,True,'flexible','low'),
('Mathematics Society','Academics','Mathematical modelling and problem solving.',['statistics','optimization'],['statistics','optimization'],[],{},True,True,'flexible','medium'),
('Business Club','Business','Market research and operations.',['market research','business'],['market research'],[],{},True,True,'flexible','medium'),
('Film Society','Film','Short films and visual storytelling.',['video editing','storytelling'],['video editing'],[],{},True,True,'flexible','medium'),
('Health Innovation Club','Health','Student health technology concepts.',['health research','data analysis'],['health research'],[],{},True,True,'flexible','medium'),
('Accessibility Club','Accessibility','Inclusive design and accessibility testing.',['accessibility','user testing'],['accessibility','user testing'],[],{},True,True,'flexible','medium'),
('Astronomy Club','Science','Astronomy observation and science communication.',['astronomy','data analysis'],['astronomy'],[],{},True,True,'flexible','low'),
]
def seed():
 db=SessionLocal()
 try:
  existing={c.name:c for c in db.query(Club).all()}
  for row in CLUBS:
   name,cat,desc,skills,verified,res,perms,active,willing,avail,work=row
   if name not in existing:
    c=Club(name=name,category=cat,description=desc,skills=skills,verified_skills=verified,resources=res,resource_permissions=perms,active=active,willing=willing,availability=avail,workload=work,synthetic=True); db.add(c)
  db.commit(); clubs={c.name:c for c in db.query(Club).all()}
  scenarios=[
   ('Robotics Club','Vision-assisted robot navigation','Robotics needs a computer vision module for object detection.',['computer vision'],[], 'high','flexible'),
   ('Environmental Club','Campus air-quality analysis','Combine environmental field observations with reproducible data analysis.',['data analysis'],[], 'medium','flexible'),
   ('Accessibility Club','Accessible campus event finder','Create an accessible event-finder prototype with usability testing.',['web development','ui design'],[], 'medium','flexible'),
   ('Robotics Club','Sensor telemetry dashboard','Create a dashboard for robot sensor readings.',['web development'],[], 'medium','flexible'),
   ('Photography Club','Permissioned image collection audit','Need to verify image collection use permissions before any model training.',['computer vision'],['campus image collection'],'medium','flexible'),
   ('Astronomy Club','Astronomy outreach site','Build a site for astronomy outreach sessions.',['web development'],[], 'medium','flexible'),
   ('Community Service Club','Community mapping','Map service opportunities with volunteers.',['data analysis'],[], 'medium','weekends'),
  ]
  for owner,title,desc,skills,resources,work,avail in scenarios:
   c=clubs[owner]
   if not db.query(Need).filter_by(club_id=c.id,title=title).first():
    db.add(Need(club_id=c.id,title=title,description=desc,required_skills=skills,required_resources=resources,status='open',priority='high' if title.startswith('Vision') else 'medium',duration_weeks=6,availability=avail,workload=work,synthetic=True))
  db.commit()
  # Explicit edge-case records: unavailable/inactive/unwilling/incomplete, and partnership history.
  clubs['Cybersecurity Club'].willing=False
  clubs['Gaming Club'].active=False
  clubs['Photography Club'].resource_permissions={'campus image collection':'unavailable'}
  # Persist deterministic changes once and ensure profile version reflects seed state.
  db.commit()
  needs={n.title:n for n in db.query(Need).all()}
  for title,participants,status,scope in [
   ('Sensor telemetry dashboard',[clubs['Robotics Club'].id,clubs['Web Development Club'].id],'active','Sensor telemetry dashboard'),
   ('Astronomy outreach site',[clubs['Astronomy Club'].id,clubs['Web Development Club'].id],'completed','Astronomy outreach site')]:
   if not db.query(Collaboration).filter_by(need_id=needs[title].id,status=status,scope=scope).first(): db.add(Collaboration(need_id=needs[title].id,participant_ids=participants,status=status,scope=scope))
  db.commit()
  print(f'Seed complete: {db.query(Club).count()} clubs, {db.query(Need).count()} needs, {db.query(Collaboration).count()} collaboration records. All seed data is synthetic.')
 finally: db.close()
if __name__=='__main__': seed()
