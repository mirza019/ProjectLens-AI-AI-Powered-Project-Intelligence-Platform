from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.types import TypeDecorator
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

def uid(): return str(uuid.uuid4())

class PortableVector(TypeDecorator):
    impl = JSON
    cache_ok = True
    def __init__(self, dimensions=768, **kwargs): self.dimensions=dimensions; super().__init__(**kwargs)
    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(Vector(self.dimensions)) if dialect.name=="postgresql" else dialect.type_descriptor(JSON())

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Role(Base, TimestampMixin):
    __tablename__="roles"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    permissions: Mapped[list] = mapped_column(JSON, default=list)
    users: Mapped[list["User"]] = relationship(back_populates="role")

class User(Base, TimestampMixin):
    __tablename__="users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120)); password_hash: Mapped[str] = mapped_column(String(255))
    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id"), index=True); is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[Role] = relationship(back_populates="users")

class Project(Base, TimestampMixin):
    __tablename__="projects"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    code: Mapped[str] = mapped_column(String(24), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    customer: Mapped[str] = mapped_column(String(120)); region: Mapped[str] = mapped_column(String(50))
    value: Mapped[float] = mapped_column(Float); completion: Mapped[float] = mapped_column(Float)
    budget_cost: Mapped[float] = mapped_column(Float); forecast_cost: Mapped[float] = mapped_column(Float)
    expected_margin: Mapped[float] = mapped_column(Float); schedule_days: Mapped[int] = mapped_column(Integer)
    risks: Mapped[list["Risk"]] = relationship(back_populates="project", cascade="all, delete-orphan")

class MonthlyFinancial(Base, TimestampMixin):
    __tablename__="monthly_financials"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    period: Mapped[str] = mapped_column(String(7), index=True); budget: Mapped[float] = mapped_column(Float)
    actual_cost: Mapped[float] = mapped_column(Float); forecast_cost: Mapped[float] = mapped_column(Float)
    forecast_revenue: Mapped[float] = mapped_column(Float); cash_in: Mapped[float] = mapped_column(Float); cash_out: Mapped[float] = mapped_column(Float)
    __table_args__=(Index("ix_financial_project_period","project_id","period",unique=True),)

class ForecastVersion(Base, TimestampMixin):
    __tablename__="forecast_versions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    period: Mapped[str] = mapped_column(String(7)); version: Mapped[int] = mapped_column(Integer)
    total_cost: Mapped[float] = mapped_column(Float); revenue: Mapped[float] = mapped_column(Float); drivers: Mapped[dict] = mapped_column(JSON)
    __table_args__=(UniqueConstraint("project_id","period","version",name="uq_forecast_version"),)

class Milestone(Base, TimestampMixin):
    __tablename__="milestones"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    code: Mapped[str] = mapped_column(String(30)); name: Mapped[str] = mapped_column(String(160))
    planned_date: Mapped[str] = mapped_column(String(10)); forecast_date: Mapped[str] = mapped_column(String(10)); status: Mapped[str] = mapped_column(String(30))

class Risk(Base, TimestampMixin):
    __tablename__="risks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    risk_code: Mapped[str] = mapped_column(String(20), unique=True); title: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(50)); probability: Mapped[float] = mapped_column(Float)
    financial_impact: Mapped[float] = mapped_column(Float); schedule_impact: Mapped[int] = mapped_column(Integer)
    owner: Mapped[str] = mapped_column(String(100)); status: Mapped[str] = mapped_column(String(30)); mitigation: Mapped[str] = mapped_column(Text)
    project: Mapped[Project] = relationship(back_populates="risks")
    @property
    def exposure(self): return self.probability * self.financial_impact

class Document(Base, TimestampMixin):
    __tablename__="project_documents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    title: Mapped[str] = mapped_column(String(200), index=True); document_type: Mapped[str] = mapped_column(String(30), index=True)
    section: Mapped[str] = mapped_column(String(100)); page: Mapped[int] = mapped_column(Integer); content: Mapped[str] = mapped_column(Text)

class Contract(Base, TimestampMixin):
    __tablename__="contracts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200)); effective_date: Mapped[str] = mapped_column(String(10)); currency: Mapped[str] = mapped_column(String(3), default="EUR")
    value: Mapped[float] = mapped_column(Float); file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    contract_number: Mapped[Optional[str]] = mapped_column(String(40), nullable=True, unique=True, index=True)
    customer: Mapped[Optional[str]] = mapped_column(String(160), nullable=True); supplier: Mapped[str] = mapped_column(String(160), default="Aurelius Engineering GmbH")
    status: Mapped[str] = mapped_column(String(30), default="Active"); page_count: Mapped[int] = mapped_column(Integer, default=0)
    delivery_date: Mapped[Optional[str]] = mapped_column(String(10), nullable=True); warranty_months: Mapped[int] = mapped_column(Integer, default=24)
    payment_milestones: Mapped[list] = mapped_column(JSON, default=list); ingestion_status: Mapped[str] = mapped_column(String(30), default="Generated", index=True)

class ContractClause(Base, TimestampMixin):
    __tablename__="contract_clauses"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    contract_id: Mapped[str] = mapped_column(ForeignKey("contracts.id"), index=True)
    section: Mapped[str] = mapped_column(String(100), index=True); clause_number: Mapped[str] = mapped_column(String(20)); page: Mapped[int] = mapped_column(Integer); content: Mapped[str] = mapped_column(Text)

class DocumentChunk(Base, TimestampMixin):
    __tablename__="document_chunks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    document_id: Mapped[str] = mapped_column(String(36), index=True); contract_id: Mapped[str] = mapped_column(ForeignKey("contracts.id"), index=True); project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    section_number: Mapped[Optional[str]] = mapped_column(String(30), nullable=True); section_title: Mapped[str] = mapped_column(String(160)); clause_number: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    page_start: Mapped[int] = mapped_column(Integer); page_end: Mapped[int] = mapped_column(Integer); chunk_index: Mapped[int] = mapped_column(Integer); chunk_text: Mapped[str] = mapped_column(Text); token_count: Mapped[int] = mapped_column(Integer)
    embedding: Mapped[Optional[list]] = mapped_column(PortableVector(768), nullable=True)
    __table_args__=(UniqueConstraint("contract_id","chunk_index",name="uq_contract_chunk_index"),)

class ContractExtractedField(Base, TimestampMixin):
    __tablename__="contract_extracted_fields"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); contract_id: Mapped[str] = mapped_column(ForeignKey("contracts.id"), index=True)
    field_name: Mapped[str] = mapped_column(String(80), index=True); field_value: Mapped[str] = mapped_column(Text); source_chunk_id: Mapped[str] = mapped_column(ForeignKey("document_chunks.id")); page: Mapped[int] = mapped_column(Integer); section: Mapped[str] = mapped_column(String(160)); confidence: Mapped[float] = mapped_column(Float); review_status: Mapped[str] = mapped_column(String(20), default="Extracted")

class ChangeOrder(Base, TimestampMixin):
    __tablename__="change_orders"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True); code: Mapped[str] = mapped_column(String(30), unique=True)
    title: Mapped[str] = mapped_column(String(180)); value: Mapped[float] = mapped_column(Float); status: Mapped[str] = mapped_column(String(30)); reason: Mapped[str] = mapped_column(Text)

class AIUseCase(Base, TimestampMixin):
    __tablename__="ai_use_cases"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    title: Mapped[str] = mapped_column(String(180)); business_problem: Mapped[str] = mapped_column(Text); current_process: Mapped[str] = mapped_column(Text)
    owner: Mapped[str] = mapped_column(String(120)); status: Mapped[str] = mapped_column(String(30), index=True); assessment: Mapped[dict] = mapped_column(JSON, default=dict)

class AIFeedback(Base, TimestampMixin):
    __tablename__="ai_feedback"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); ai_run_id: Mapped[str] = mapped_column(ForeignKey("ai_runs.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True); helpful: Mapped[bool] = mapped_column(Boolean); comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

class AuditLog(Base):
    __tablename__="audit_logs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True); action: Mapped[str] = mapped_column(String(80), index=True)
    entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True); entity_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True); details: Mapped[dict] = mapped_column(JSON, default=dict)

class GeneratedReport(Base, TimestampMixin):
    __tablename__="generated_reports"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid); project_id: Mapped[Optional[str]] = mapped_column(ForeignKey("projects.id"), nullable=True, index=True)
    report_type: Mapped[str] = mapped_column(String(40)); period: Mapped[str] = mapped_column(String(7)); status: Mapped[str] = mapped_column(String(20), default="Draft"); content: Mapped[dict] = mapped_column(JSON); file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    xlsx_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True); version: Mapped[int] = mapped_column(Integer, default=1); parent_report_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True); reviewed_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True); reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True); approved_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True); approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True); rejected_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True); rejected_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True); review_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

class AIRun(Base, TimestampMixin):
    __tablename__="ai_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(String(36), index=True); pipeline: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(60)); prompt_version: Mapped[str] = mapped_column(String(30))
    question: Mapped[str] = mapped_column(Text); output: Mapped[dict] = mapped_column(JSON); source_ids: Mapped[list] = mapped_column(JSON)
    confidence: Mapped[float] = mapped_column(Float); review_status: Mapped[str] = mapped_column(String(20), default="Draft")

class PipelineRun(Base, TimestampMixin):
    __tablename__="pipeline_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    status: Mapped[str] = mapped_column(String(20), index=True); records_processed: Mapped[int] = mapped_column(Integer, default=0)
    inserted: Mapped[int] = mapped_column(Integer, default=0); updated: Mapped[int] = mapped_column(Integer, default=0); failed: Mapped[int] = mapped_column(Integer, default=0)
    steps: Mapped[list] = mapped_column(JSON, default=list); error_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
