from datetime import datetime, timezone
from sqlalchemy import String, Text, Boolean, Float, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

def now(): return datetime.now(timezone.utc)
class Club(Base):
    __tablename__='clubs'
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(120), unique=True, index=True)
    category: Mapped[str]=mapped_column(String(80), default='General')
    description: Mapped[str]=mapped_column(Text, default='')
    skills: Mapped[list]=mapped_column(JSON, default=list)
    verified_skills: Mapped[list]=mapped_column(JSON, default=list)
    resources: Mapped[list]=mapped_column(JSON, default=list)
    resource_permissions: Mapped[dict]=mapped_column(JSON, default=dict)
    active: Mapped[bool]=mapped_column(Boolean, default=True)
    willing: Mapped[bool]=mapped_column(Boolean, default=True)
    availability: Mapped[str]=mapped_column(String(80), default='flexible')
    workload: Mapped[str]=mapped_column(String(30), default='medium')
    profile_version: Mapped[int]=mapped_column(default=1)
    synthetic: Mapped[bool]=mapped_column(Boolean, default=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)

class Need(Base):
    __tablename__='needs'
    id: Mapped[int]=mapped_column(primary_key=True)
    club_id: Mapped[int]=mapped_column(ForeignKey('clubs.id', ondelete='CASCADE'), index=True)
    title: Mapped[str]=mapped_column(String(180))
    description: Mapped[str]=mapped_column(Text, default='')
    required_skills: Mapped[list]=mapped_column(JSON, default=list)
    required_resources: Mapped[list]=mapped_column(JSON, default=list)
    status: Mapped[str]=mapped_column(String(30), default='open', index=True)
    priority: Mapped[str]=mapped_column(String(20), default='medium')
    duration_weeks: Mapped[int]=mapped_column(default=6)
    availability: Mapped[str]=mapped_column(String(80), default='flexible')
    workload: Mapped[str]=mapped_column(String(30), default='medium')
    version: Mapped[int]=mapped_column(default=1)
    synthetic: Mapped[bool]=mapped_column(Boolean, default=True)

class Collaboration(Base):
    __tablename__='collaborations'
    id: Mapped[int]=mapped_column(primary_key=True)
    need_id: Mapped[int]=mapped_column(ForeignKey('needs.id', ondelete='CASCADE'), index=True)
    participant_ids: Mapped[list]=mapped_column(JSON)
    status: Mapped[str]=mapped_column(String(30), default='proposed')
    scope: Mapped[str]=mapped_column(String(250), default='')
    rejection_fingerprint: Mapped[str|None]=mapped_column(String(80), nullable=True)
    __table_args__=(UniqueConstraint('need_id','scope','status',name='uq_collab_scope_status'),)

class Recommendation(Base):
    __tablename__='recommendations'
    id: Mapped[int]=mapped_column(primary_key=True)
    need_id: Mapped[int]=mapped_column(ForeignKey('needs.id', ondelete='CASCADE'), index=True)
    participant_ids: Mapped[list]=mapped_column(JSON)
    title: Mapped[str]=mapped_column(String(240))
    scores: Mapped[dict]=mapped_column(JSON)
    evidence: Mapped[dict]=mapped_column(JSON)
    explanation: Mapped[str]=mapped_column(Text)
    proposal: Mapped[dict]=mapped_column(JSON)
    fingerprint: Mapped[str]=mapped_column(String(80), index=True)
    status: Mapped[str]=mapped_column(String(30), default='suggested')
    model_version: Mapped[str]=mapped_column(String(30), default='baseline-1.0')

class Feedback(Base):
    __tablename__='feedback'
    id: Mapped[int]=mapped_column(primary_key=True)
    recommendation_id: Mapped[int]=mapped_column(ForeignKey('recommendations.id', ondelete='CASCADE'))
    category: Mapped[str]=mapped_column(String(60))
    explanation: Mapped[str]=mapped_column(Text, default='')
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
