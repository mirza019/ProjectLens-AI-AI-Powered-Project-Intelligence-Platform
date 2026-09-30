from __future__ import annotations
import hashlib
import re
from pathlib import Path
from typing import Iterable
import fitz
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from sqlalchemy.orm import Session
from app.models.entities import Contract, ContractClause, ContractExtractedField, DocumentChunk


SECTIONS = [
    ("1", "Parties and purpose", "This Agreement is between {customer} (Customer) and Aurelius Engineering GmbH (Supplier) for execution of {project}. Contract number {number}."),
    ("2", "Definitions and interpretation", "Business Day means a day on which banks are open in Berlin. Contract Documents include this Agreement, technical schedules, approved change orders and the agreed programme."),
    ("3", "Scope of work", "Supplier shall engineer, manufacture, inspect, test, deliver, install and commission the equipment described in the technical schedules, including all documentation and training required for safe operation."),
    ("4", "Contract price", "The firm contract price is EUR {value:,.2f}, exclusive of value added tax. Price adjustment is permitted only through an approved written change order."),
    ("5", "Payment milestones", "Payment is 20% at effectiveness, 30% at design approval, 30% at equipment delivery, 10% at provisional acceptance and 10% at final acceptance. Valid invoices are payable within 30 calendar days."),
    ("6", "Security and retention", "Supplier shall provide a performance security equal to 10% of contract price. Customer may retain 5% until provisional acceptance unless replaced by an acceptable bank guarantee."),
    ("7", "Programme and reporting", "The baseline programme is binding. Supplier shall submit a monthly progress report identifying critical path, earned progress, forecast dates, constraints and recovery actions."),
    ("8", "Delivery", "Delivery shall occur no later than {delivery}. Delivery is complete only when equipment, shipping records, certificates and quality dossiers arrive at the agreed site."),
    ("9", "Delay notice", "A party becoming aware of delay shall notify the other party within seven days, describing cause, expected impact, mitigation and the decision required."),
    ("10", "Liquidated damages", "For culpable delay, damages accrue at 0.5% of the delayed portion for each completed week, capped at 10% of total contract price. This is without prejudice to termination rights."),
    ("11", "Testing", "Factory and site acceptance tests shall follow the approved procedures. Customer may witness testing on ten Business Days' notice. Failed tests shall be repeated at Supplier cost."),
    ("12", "Acceptance", "Provisional acceptance requires successful commissioning, delivery of as-built records and closure of material punch-list items. Final acceptance follows completion of the reliability period."),
    ("13", "Warranty", "The warranty period is {warranty} months from provisional acceptance or 30 months from delivery, whichever occurs first. Supplier shall promptly correct defects at its cost."),
    ("14", "Change management", "No change is binding unless a written change order records revised scope, price and schedule and is signed by authorised representatives. Potential changes require notice within 14 days."),
    ("15", "Claims", "A claim shall identify the event, contractual basis, contemporaneous records, cost and time impact, and mitigation. Detailed particulars are due within 21 days after awareness."),
    ("16", "Quality and compliance", "Supplier shall maintain an ISO 9001-aligned quality system, comply with applicable law, retain inspection records and promptly report any material non-conformance."),
    ("17", "Confidentiality and data", "Confidential information may be used only to perform this Agreement. Each party shall apply appropriate technical and organisational safeguards and notify material data incidents."),
    ("18", "Liability and insurance", "Aggregate Supplier liability is limited to 100% of contract price, except for fraud, wilful misconduct, confidentiality breach and liability that cannot lawfully be limited."),
    ("19", "Termination", "Material breach not cured within 30 days after written notice permits termination for cause. Customer may terminate for convenience on 30 days' notice and pay verified work performed."),
    ("20", "Dispute resolution", "Disputes escalate first to project directors, then executive negotiation, mediation and finally binding arbitration seated in Berlin in the English language."),
]


def _page(canvas, doc):
    canvas.saveState(); width, height = A4
    canvas.setFillColor(colors.HexColor("#0B1F3A")); canvas.rect(0, height-18*mm, width, 18*mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white); canvas.setFont("Helvetica-Bold", 9); canvas.drawString(18*mm, height-11*mm, "PROJECTLENS AI  |  SYNTHETIC CONTRACT")
    canvas.setFillColor(colors.HexColor("#667085")); canvas.setFont("Helvetica", 8); canvas.drawString(18*mm, 12*mm, "Synthetic demonstration document — not legally binding")
    canvas.drawRightString(width-18*mm, 12*mm, f"Page {doc.page} of 5"); canvas.restoreState()


def generate_contract_pdf(contract: Contract, project_name: str, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(str(output), pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=25*mm, bottomMargin=20*mm)
    doc.addPageTemplates(PageTemplate(id="contract", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body")], onPage=_page))
    styles=getSampleStyleSheet(); styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=24, leading=29, textColor=colors.HexColor("#0B1F3A"), alignment=TA_CENTER, spaceAfter=16))
    styles.add(ParagraphStyle(name="Clause", parent=styles["BodyText"], fontSize=9.2, leading=13, textColor=colors.HexColor("#27364B"), spaceAfter=10))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontSize=12, leading=15, textColor=colors.HexColor("#0B65D8"), spaceBefore=5, spaceAfter=5))
    story=[Spacer(1,28*mm),Paragraph("ENGINEERING, DELIVERY<br/>AND COMMISSIONING AGREEMENT",styles["CoverTitle"]),Spacer(1,8*mm)]
    metadata=[["Contract number",contract.contract_number],["Project",project_name],["Customer",contract.customer],["Supplier",contract.supplier],["Effective date",contract.effective_date],["Contract price",f"EUR {contract.value:,.2f}"],["Status",contract.status]]
    table=Table(metadata,colWidths=[48*mm,105*mm]); table.setStyle(TableStyle([("BACKGROUND",(0,0),(0,-1),colors.HexColor("#EAF2FC")),("TEXTCOLOR",(0,0),(0,-1),colors.HexColor("#0B1F3A")),("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),("FONTNAME",(1,0),(1,-1),"Helvetica"),("FONTSIZE",(0,0),(-1,-1),9),("GRID",(0,0),(-1,-1),.4,colors.HexColor("#CBD5E1")),("VALIGN",(0,0),(-1,-1),"TOP"),("PADDING",(0,0),(-1,-1),7)])); story += [table,Spacer(1,12*mm),Paragraph("This is synthetic demonstration data created for ProjectLens AI. It is not a real contract and must not be used as legal advice.",styles["Clause"]),PageBreak()]
    values={"customer":contract.customer,"project":project_name,"number":contract.contract_number,"value":contract.value,"delivery":contract.delivery_date,"warranty":contract.warranty_months}
    # Four clauses on each of pages 2–5 guarantees exactly five pages.
    for idx,(number,title,text) in enumerate(SECTIONS):
        story += [Paragraph(f"{number}. {title}",styles["Section"]),Paragraph(text.format(**values),styles["Clause"])]
        if idx in (3,7,11): story.append(PageBreak())
    doc.build(story)
    pages=fitz.open(str(output)).page_count
    if pages != 5: raise RuntimeError(f"Expected exactly 5 pages, generated {pages}")
    return output


def _chunks(page_text: str) -> Iterable[tuple[str,str,str]]:
    matches=list(re.finditer(r"(?m)^\s*(\d+)\.\s+([^\n]+)\n",page_text))
    for i,m in enumerate(matches):
        end=matches[i+1].start() if i+1<len(matches) else len(page_text)
        body=re.sub(r"\s+"," ",page_text[m.end():end]).strip()
        if body: yield m.group(1),m.group(2).strip(),body


def deterministic_embedding(text: str, dimensions: int=768) -> list[float]:
    vector=[0.0]*dimensions
    for token in re.findall(r"[a-z0-9]+",text.lower()):
        digest=hashlib.sha256(token.encode()).digest(); pos=int.from_bytes(digest[:4],"big")%dimensions
        vector[pos] += 1.0 if digest[4]%2 else -1.0
    norm=sum(x*x for x in vector)**.5 or 1.0
    return [x/norm for x in vector]


def ingest_contract(db: Session, contract: Contract) -> int:
    path=Path(contract.file_path); pdf=fitz.open(str(path))
    db.query(DocumentChunk).filter_by(contract_id=contract.id).delete(); db.query(ContractClause).filter_by(contract_id=contract.id).delete(); db.query(ContractExtractedField).filter_by(contract_id=contract.id).delete()
    index=0; created=[]
    for page_no,page in enumerate(pdf,1):
        for number,title,body in _chunks(page.get_text("text")):
            chunk=DocumentChunk(document_id=contract.id,contract_id=contract.id,project_id=contract.project_id,section_number=number,section_title=title,clause_number=number,page_start=page_no,page_end=page_no,chunk_index=index,chunk_text=body,token_count=len(body.split()),embedding=deterministic_embedding(title+" "+body)); db.add(chunk); db.flush(); created.append(chunk)
            db.add(ContractClause(contract_id=contract.id,section=title,clause_number=number,page=page_no,content=body)); index+=1
    contract.page_count=pdf.page_count; contract.ingestion_status="Indexed"
    lookup={x.section_title.lower():x for x in created}
    fields=[("contract_number",contract.contract_number,"parties and purpose"),("contract_value",f"EUR {contract.value:,.2f}","contract price"),("delivery_date",contract.delivery_date,"delivery"),("warranty_period",f"{contract.warranty_months} months","warranty"),("payment_terms","20/30/30/10/10 milestones; net 30 days","payment milestones"),("liquidated_damages","0.5% weekly; 10% cap","liquidated damages")]
    for name,value,section in fields:
        source=lookup.get(section)
        if source: db.add(ContractExtractedField(contract_id=contract.id,field_name=name,field_value=str(value),source_chunk_id=source.id,page=source.page_start,section=source.section_title,confidence=.97,review_status="Extracted"))
    db.flush(); return index
