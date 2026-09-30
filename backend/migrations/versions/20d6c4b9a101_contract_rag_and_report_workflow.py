"""contract RAG and report workflow

Revision ID: 20d6c4b9a101
Revises: 10f5074cfd9e
"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision="20d6c4b9a101"; down_revision="10f5074cfd9e"; branch_labels=None; depends_on=None

def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    for name,column in [
        ("contract_number",sa.Column("contract_number",sa.String(40),nullable=True)),("customer",sa.Column("customer",sa.String(160),nullable=True)),("supplier",sa.Column("supplier",sa.String(160),nullable=False,server_default="Aurelius Engineering GmbH")),("status",sa.Column("status",sa.String(30),nullable=False,server_default="Active")),("page_count",sa.Column("page_count",sa.Integer(),nullable=False,server_default="0")),("delivery_date",sa.Column("delivery_date",sa.String(10),nullable=True)),("warranty_months",sa.Column("warranty_months",sa.Integer(),nullable=False,server_default="24")),("payment_milestones",sa.Column("payment_milestones",sa.JSON(),nullable=False,server_default="[]")),("ingestion_status",sa.Column("ingestion_status",sa.String(30),nullable=False,server_default="Generated"))]: op.add_column("contracts",column)
    op.create_index("ix_contracts_contract_number","contracts",["contract_number"],unique=True); op.create_index("ix_contracts_ingestion_status","contracts",["ingestion_status"])
    op.create_table("document_chunks",sa.Column("id",sa.String(36),primary_key=True),sa.Column("document_id",sa.String(36),nullable=False),sa.Column("contract_id",sa.String(36),sa.ForeignKey("contracts.id"),nullable=False),sa.Column("project_id",sa.String(36),sa.ForeignKey("projects.id"),nullable=False),sa.Column("section_number",sa.String(30)),sa.Column("section_title",sa.String(160),nullable=False),sa.Column("clause_number",sa.String(30)),sa.Column("page_start",sa.Integer(),nullable=False),sa.Column("page_end",sa.Integer(),nullable=False),sa.Column("chunk_index",sa.Integer(),nullable=False),sa.Column("chunk_text",sa.Text(),nullable=False),sa.Column("token_count",sa.Integer(),nullable=False),sa.Column("embedding",Vector(768)),sa.Column("created_at",sa.DateTime(),nullable=False),sa.Column("updated_at",sa.DateTime(),nullable=False),sa.UniqueConstraint("contract_id","chunk_index",name="uq_contract_chunk_index"))
    op.create_index("ix_document_chunks_contract_id","document_chunks",["contract_id"]); op.create_index("ix_document_chunks_project_id","document_chunks",["project_id"])
    op.create_index("ix_document_chunks_embedding_hnsw","document_chunks",["embedding"],postgresql_using="hnsw",postgresql_ops={"embedding":"vector_cosine_ops"})
    op.create_table("contract_extracted_fields",sa.Column("id",sa.String(36),primary_key=True),sa.Column("contract_id",sa.String(36),sa.ForeignKey("contracts.id"),nullable=False),sa.Column("field_name",sa.String(80),nullable=False),sa.Column("field_value",sa.Text(),nullable=False),sa.Column("source_chunk_id",sa.String(36),sa.ForeignKey("document_chunks.id"),nullable=False),sa.Column("page",sa.Integer(),nullable=False),sa.Column("section",sa.String(160),nullable=False),sa.Column("confidence",sa.Float(),nullable=False),sa.Column("review_status",sa.String(20),nullable=False,server_default="Extracted"),sa.Column("created_at",sa.DateTime(),nullable=False),sa.Column("updated_at",sa.DateTime(),nullable=False))
    op.create_index("ix_contract_extracted_fields_contract_id","contract_extracted_fields",["contract_id"])
    for column in [sa.Column("xlsx_path",sa.String(500)),sa.Column("version",sa.Integer(),nullable=False,server_default="1"),sa.Column("parent_report_id",sa.String(36)),sa.Column("created_by",sa.String(36)),sa.Column("reviewed_by",sa.String(36)),sa.Column("reviewed_at",sa.DateTime()),sa.Column("approved_by",sa.String(36)),sa.Column("approved_at",sa.DateTime()),sa.Column("rejected_by",sa.String(36)),sa.Column("rejected_at",sa.DateTime()),sa.Column("review_comments",sa.Text())]: op.add_column("generated_reports",column)

def downgrade():
    op.drop_table("contract_extracted_fields"); op.drop_table("document_chunks")
