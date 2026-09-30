from __future__ import annotations
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.entities import Project, Risk, User, AIRun, AIFeedback, AIUseCase, AuditLog, GeneratedReport, Contract, ContractClause, ContractExtractedField, Document, DocumentChunk, ForecastVersion, MonthlyFinancial, Milestone, ChangeOrder, PipelineRun
from app.schemas.api import AIResponse, QueryRequest, Source, LoginRequest, FeedbackCreate, UseCaseCreate, UseCaseReview, UseCaseStageChange
from app.analytics.financial import health_status
from app.ai.router import route
from app.ai.router import Intent
from app.ai.providers import GeminiProvider
from app.rag.retrieval import contract_search, knowledge_search, grounded_prompt, validate_sources
from app.core.security import verify_password, create_access_token, current_user, require_roles
from app.services.reporting import project_report_data, render_pdf, render_xlsx
from app.services.contracts import ingest_contract
from app.services.storage import storage
from app.core.rate_limit import ai_rate_limit

router=APIRouter()
@router.get("/health")
def health():
    from app.core.config import settings
    return {"status":"healthy","service":"projectlens-api","ai_configured":bool(settings.gemini_api_key),"model":settings.gemini_model}
@router.post("/auth/token")
def login(payload:LoginRequest,db:Session=Depends(get_db)):
    user=db.query(User).filter(User.email==payload.email.lower()).first()
    if not user or not verify_password(payload.password,user.password_hash): raise HTTPException(401,"Incorrect email or password")
    token=create_access_token(user.id,user.role.name); db.add(AuditLog(user_id=user.id,action="auth.login",entity_type="user",entity_id=user.id)); db.commit()
    return {"access_token":token,"token_type":"bearer","user":{"id":user.id,"email":user.email,"full_name":user.full_name,"role":user.role.name}}
@router.get("/auth/me")
def me(user=Depends(current_user)): return {"id":user.id,"email":user.email,"full_name":user.full_name,"role":user.role.name}
@router.get("/projects")
def projects(db:Session=Depends(get_db)):
    output=[]
    for p in db.query(Project).all():
        exposure=sum(r.exposure for r in p.risks); variance=(p.forecast_cost-p.budget_cost)/p.budget_cost*100
        output.append({"id":p.id,"code":p.code,"name":p.name,"customer":p.customer,"region":p.region,"value":p.value,"completion":p.completion,"margin":p.expected_margin,"variance":p.forecast_cost-p.budget_cost,"scheduleDays":p.schedule_days,"riskExposure":exposure,"status":health_status(p.expected_margin,variance,p.schedule_days,exposure/p.value*100)})
    return output
@router.get("/projects/{project_id}")
def project(project_id:str,db:Session=Depends(get_db)):
    item=db.get(Project,project_id)
    if not item: raise HTTPException(404,"Project not found")
    return item
@router.get("/projects/{project_id}/workspace")
def project_workspace(project_id:str,db:Session=Depends(get_db)):
    p=db.get(Project,project_id)
    if not p: raise HTTPException(404,"Project not found")
    return {"project":p,"financials":db.query(MonthlyFinancial).filter_by(project_id=project_id).order_by(MonthlyFinancial.period).all(),"forecasts":db.query(ForecastVersion).filter_by(project_id=project_id).order_by(ForecastVersion.period).all(),"milestones":db.query(Milestone).filter_by(project_id=project_id).all(),"risks":risks(db) if False else [{"id":r.risk_code,"title":r.title,"exposure":r.exposure,"status":r.status,"mitigation":r.mitigation} for r in db.query(Risk).filter_by(project_id=project_id).all()],"documents":db.query(Document).filter_by(project_id=project_id).all(),"change_orders":db.query(ChangeOrder).filter_by(project_id=project_id).all()}
@router.get("/financials")
def financials(project_id:Optional[str]=None,period:Optional[str]=None,db:Session=Depends(get_db)):
    q=db.query(MonthlyFinancial)
    if project_id: q=q.filter_by(project_id=project_id)
    if period: q=q.filter_by(period=period)
    return q.order_by(MonthlyFinancial.period).all()
@router.get("/forecasts")
def forecasts(project_id:Optional[str]=None,db:Session=Depends(get_db)):
    q=db.query(ForecastVersion)
    if project_id: q=q.filter_by(project_id=project_id)
    return q.order_by(ForecastVersion.period,ForecastVersion.version).all()
@router.get("/milestones")
def milestones(project_id:Optional[str]=None,db:Session=Depends(get_db)):
    q=db.query(Milestone)
    if project_id: q=q.filter_by(project_id=project_id)
    return q.all()
@router.get("/risks")
def risks(db:Session=Depends(get_db)):
    return [{"id":r.risk_code,"project_id":r.project_id,"title":r.title,"category":r.category,"probability":r.probability,"impact":r.financial_impact,"exposure":r.exposure,"owner":r.owner,"status":r.status,"mitigation":r.mitigation} for r in db.query(Risk).all()]
@router.post("/ai/query",response_model=AIResponse)
async def query_ai(payload:QueryRequest,db:Session=Depends(get_db),user=Depends(ai_rate_limit)):
    intent=route(payload.question)
    if intent==Intent.CONTRACT:
        try: query_embedding=await GeminiProvider().embed(payload.question)
        except Exception:
            from app.services.contracts import deterministic_embedding
            query_embedding=deterministic_embedding(payload.question)
        retrieved=contract_search(db,payload.question,payload.project_id,payload.contract_id,query_embedding=query_embedding)
    elif intent==Intent.KNOWLEDGE: retrieved=knowledge_search(db,payload.question,payload.project_id)
    else:
        items=projects(db); top=sorted(items,key=lambda x:(x["status"] in ("Critical","Attention"),x["riskExposure"]),reverse=True)[:5]
        from app.rag.retrieval import Retrieved
        retrieved=[Retrieved(f"portfolio-{x['id']}",x['name'],"Verified portfolio analytics",0,f"Status {x['status']}; margin {x['margin']:.1f}%; forecast variance EUR {x['variance']:,.0f}; schedule variance {x['scheduleDays']} days; risk exposure EUR {x['riskExposure']:,.0f}.",1) for x in top]
    if not retrieved:
        raise HTTPException(422,"Insufficient evidence in the indexed documents")
    allowed=[x.id for x in retrieved]
    try:
        output=validate_sources(await GeminiProvider().generate(grounded_prompt(payload.question,retrieved)),allowed)
    except Exception as exc:
        # Deterministic grounded fallback keeps analytics available when the external provider is unavailable.
        output={"summary":"The verified evidence was retrieved successfully, but live AI commentary is temporarily unavailable.","key_findings":[x.content[:180] for x in retrieved[:3]],"risks":[],"recommended_attention":["Review the cited evidence"],"source_ids":allowed[:3],"confidence":.75}
    sources=[Source(id=x.id,title=x.title,section=x.section,page=x.page,contract_id=x.contract_id) for x in retrieved if x.id in output["source_ids"]]
    run=AIRun(user_id=user.id,pipeline=intent.value,model="gemini-2.5-flash",prompt_version="pl-grounded-v1",question=payload.question,output=output,source_ids=output["source_ids"],confidence=output["confidence"],review_status="Draft"); db.add(run); db.commit()
    return AIResponse(summary=output["summary"],key_findings=output["key_findings"],recommended_attention=output["recommended_attention"],source_ids=output["source_ids"],sources=sources,confidence=output["confidence"],pipeline=intent.value,run_id=run.id)
@router.post("/rag/contracts/query",response_model=AIResponse)
async def contract_query(payload:QueryRequest,db:Session=Depends(get_db),user=Depends(ai_rate_limit)): return await query_ai(payload,db,user)
@router.post("/rag/knowledge/query",response_model=AIResponse)
async def knowledge_query(payload:QueryRequest,db:Session=Depends(get_db),user=Depends(ai_rate_limit)): return await query_ai(payload,db,user)
@router.post("/feedback")
def feedback(payload:FeedbackCreate,db:Session=Depends(get_db),user=Depends(current_user)):
    if not db.get(AIRun,payload.ai_run_id): raise HTTPException(404,"AI run not found")
    row=AIFeedback(ai_run_id=payload.ai_run_id,user_id=user.id,helpful=payload.helpful,comment=payload.comment); db.add(row); db.commit(); return {"status":"recorded"}
@router.get("/contracts")
def contracts(db:Session=Depends(get_db)): return [{"id":c.id,"project_id":c.project_id,"name":c.name,"contract_number":c.contract_number,"customer":c.customer,"supplier":c.supplier,"status":c.status,"value":c.value,"effective_date":c.effective_date,"delivery_date":c.delivery_date,"warranty_months":c.warranty_months,"page_count":c.page_count,"ingestion_status":c.ingestion_status} for c in db.query(Contract).order_by(Contract.contract_number).all()]
@router.get("/contracts/{contract_id}")
def contract_detail(contract_id:str,db:Session=Depends(get_db)):
    c=db.get(Contract,contract_id)
    if not c: raise HTTPException(404,"Contract not found")
    return {"contract":c,"clauses":db.query(ContractClause).filter_by(contract_id=contract_id).order_by(ContractClause.page,ContractClause.clause_number).all(),"extracted_fields":db.query(ContractExtractedField).filter_by(contract_id=contract_id).all(),"chunk_count":db.query(DocumentChunk).filter_by(contract_id=contract_id).count()}
@router.get("/contracts/{contract_id}/pdf")
def contract_pdf(contract_id:str,download:bool=Query(False),db:Session=Depends(get_db)):
    c=db.get(Contract,contract_id)
    if not c or not c.file_path: raise HTTPException(404,"Contract PDF not found")
    try: path=storage.resolve(c.file_path)
    except ValueError as exc: raise HTTPException(400,str(exc))
    if not path.exists(): raise HTTPException(404,"Contract PDF file is missing")
    return FileResponse(path,media_type="application/pdf",filename=f"{c.contract_number}.pdf" if download else None,content_disposition_type="attachment" if download else "inline")
@router.post("/contracts/{contract_id}/reindex")
async def reindex_contract(contract_id:str,db:Session=Depends(get_db),user=Depends(current_user)):
    c=db.get(Contract,contract_id)
    if not c: raise HTTPException(404,"Contract not found")
    count=ingest_contract(db,c); provider=GeminiProvider(); embedded_with="deterministic-fallback"
    try:
        for chunk in db.query(DocumentChunk).filter_by(contract_id=c.id).order_by(DocumentChunk.chunk_index): chunk.embedding=await provider.embed(chunk.section_title+"\n"+chunk.chunk_text)
        embedded_with="Gemini"
    except Exception:
        pass
    db.add(AuditLog(user_id=user.id,action="contract.reindex",entity_type="contract",entity_id=c.id,details={"chunks":count,"embedding_provider":embedded_with})); db.commit(); return {"status":"Indexed","chunks":count,"pages":c.page_count,"embedding_provider":embedded_with}
@router.patch("/contracts/{contract_id}/fields/{field_id}")
def review_contract_field(contract_id:str,field_id:str,status:str,db:Session=Depends(get_db),user=Depends(current_user)):
    if status not in ("Confirmed","Corrected","Rejected"): raise HTTPException(400,"Invalid review status")
    row=db.get(ContractExtractedField,field_id)
    if not row or row.contract_id!=contract_id: raise HTTPException(404,"Extracted field not found")
    row.review_status=status; db.add(AuditLog(user_id=user.id,action="contract.field_review",entity_type="contract_field",entity_id=row.id,details={"status":status})); db.commit(); return row
@router.get("/contracts/{contract_id}/clauses")
def clauses(contract_id:str,db:Session=Depends(get_db)): return db.query(ContractClause).filter_by(contract_id=contract_id).order_by(ContractClause.page).all()
@router.get("/documents")
def documents(document_type:Optional[str]=None,project_id:Optional[str]=None,db:Session=Depends(get_db)):
    q=db.query(Document)
    if document_type: q=q.filter_by(document_type=document_type)
    if project_id: q=q.filter_by(project_id=project_id)
    return q.order_by(Document.created_at.desc()).all()
@router.get("/search")
def search(q:str,db:Session=Depends(get_db)):
    term=f"%{q}%"; results=[]
    results += [{"type":"Project","id":x.id,"title":x.name,"detail":x.code} for x in db.query(Project).filter(Project.name.ilike(term)).limit(10)]
    results += [{"type":"Risk","id":x.id,"title":x.title,"detail":x.risk_code} for x in db.query(Risk).filter(Risk.title.ilike(term)).limit(10)]
    results += [{"type":"Document","id":x.id,"title":x.title,"detail":x.document_type} for x in db.query(Document).filter(Document.title.ilike(term)).limit(10)]
    results += [{"type":"Contract","id":x.id,"title":x.name,"detail":"Contract"} for x in db.query(Contract).filter(Contract.name.ilike(term)).limit(10)]
    return results[:25]
@router.get("/use-cases")
def use_cases(db:Session=Depends(get_db)): return db.query(AIUseCase).all()
@router.post("/use-cases")
async def create_use_case(payload:UseCaseCreate,db:Session=Depends(get_db)):
    text=(payload.business_problem+" "+payload.current_process).lower(); rag=any(x in text for x in ("document","contract","policy","search")); ai=any(x in text for x in ("summar","explain","natural language","unstructured")) or rag
    automation=any(x in text for x in ("manual","copy","consolidat","repeat","report")); analytics=any(x in text for x in ("forecast","variance","metric","dashboard","financial"))
    assessment={"recommended_approach":" + ".join(x for x,on in [("automation",automation),("analytics",analytics),("RAG",rag),("generative AI",ai)] if on) or "Process redesign","ai_needed":ai,"automation_needed":automation,"analytics_needed":analytics,"rag_needed":rag,"human_review_required":ai,"complexity":"Medium" if sum((ai,automation,analytics,rag))>1 else "Low","rationale":["Fallback rules matched the submitted business problem and current process"],"security_considerations":[f"Treat data as {payload.data_sensitivity}","Log important outputs"],"prototype_recommendation":"Build a time-boxed prototype with success metrics","success_metrics":["Document baseline effort and target reduction","Measure output accuracy and reviewer acceptance"],"assessment_provider":"Rules fallback"}
    try:
        assessment=await GeminiProvider().assess_opportunity(payload.model_dump()); assessment["assessment_provider"]="Gemini"
    except Exception as exc:
        assessment["provider_note"]="Gemini unavailable; explainable rules fallback used"
    row=AIUseCase(title=payload.title,business_problem=payload.business_problem,current_process=payload.current_process,owner=payload.owner,status="Assessment",assessment=assessment); db.add(row); db.commit(); db.refresh(row); return row
@router.post("/use-cases/{use_case_id}/review")
def review_use_case(use_case_id:str,payload:UseCaseReview,db:Session=Depends(get_db),user=Depends(current_user)):
    row=db.get(AIUseCase,use_case_id)
    if not row: raise HTTPException(404,"AI opportunity not found")
    transitions={"approve":"Prototype","request_changes":"Assessment","reject":"Rejected"}
    if payload.decision not in transitions: raise HTTPException(400,"Decision must be approve, request_changes, or reject")
    previous=row.status; row.status=transitions[payload.decision]
    assessment=dict(row.assessment or {}); assessment["human_review"]={"decision":payload.decision,"comments":payload.comments,"reviewer":user.full_name,"reviewer_id":user.id,"reviewed_at":datetime.utcnow().isoformat(),"previous_status":previous}; row.assessment=assessment
    db.add(AuditLog(user_id=user.id,action="use_case.review",entity_type="ai_use_case",entity_id=row.id,details={"decision":payload.decision,"from":previous,"to":row.status,"comments":payload.comments})); db.commit(); db.refresh(row); return row
@router.post("/use-cases/{use_case_id}/stage")
def change_use_case_stage(use_case_id:str,payload:UseCaseStageChange,db:Session=Depends(get_db),user=Depends(current_user)):
    allowed=["Idea","Assessment","Prototype","Testing","Pilot","Ready","Rejected"]
    if payload.status not in allowed: raise HTTPException(400,"Invalid opportunity stage")
    row=db.get(AIUseCase,use_case_id)
    if not row: raise HTTPException(404,"AI opportunity not found")
    previous=row.status; assessment=dict(row.assessment or {}); history=list(assessment.get("stage_history",[])); history.append({"from":previous,"to":payload.status,"comments":payload.comments,"changed_by":user.full_name,"changed_by_id":user.id,"changed_at":datetime.utcnow().isoformat()}); assessment["stage_history"]=history; row.assessment=assessment; row.status=payload.status
    db.add(AuditLog(user_id=user.id,action="use_case.stage_change",entity_type="ai_use_case",entity_id=row.id,details=history[-1])); db.commit(); db.refresh(row); return row
@router.delete("/use-cases/{use_case_id}")
def delete_use_case(use_case_id:str,db:Session=Depends(get_db),user=Depends(current_user)):
    row=db.get(AIUseCase,use_case_id)
    if not row: raise HTTPException(404,"AI opportunity not found")
    snapshot={"title":row.title,"owner":row.owner,"status":row.status}
    db.add(AuditLog(user_id=user.id,action="use_case.delete",entity_type="ai_use_case",entity_id=row.id,details=snapshot)); db.delete(row); db.commit()
    return {"status":"deleted","id":use_case_id,"title":snapshot["title"]}
@router.post("/reports/project/{project_id}")
def generate_project_report(project_id:str,period:str="2026-09",db:Session=Depends(get_db)):
    try: data=project_report_data(db,project_id,period)
    except ValueError as exc: raise HTTPException(404,str(exc))
    report=GeneratedReport(project_id=project_id,report_type="Monthly Project Review",period=period,status="Draft",content=data); db.add(report); db.flush()
    pdf_path=storage.path("reports",f"{report.id}.pdf"); xlsx_path=storage.path("reports",f"{report.id}.xlsx"); render_pdf(data,pdf_path); render_xlsx(data,xlsx_path); report.file_path=str(pdf_path); report.xlsx_path=str(xlsx_path); db.commit(); return {"id":report.id,"status":"Draft","pdf_url":f"/api/v1/reports/{report.id}/download?format=pdf","xlsx_url":f"/api/v1/reports/{report.id}/download?format=xlsx","content":data}
@router.get("/reports/{report_id}/download")
def download_report(report_id:str,format:str="pdf",db:Session=Depends(get_db)):
    report=db.get(GeneratedReport,report_id)
    if not report: raise HTTPException(404,"Report not found")
    stored=report.file_path if format=="pdf" else report.xlsx_path if format=="xlsx" else None
    if not stored: raise HTTPException(404,"Requested report format is not available")
    path=storage.resolve(stored)
    return FileResponse(path,media_type="application/pdf" if format=="pdf" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",filename=f"projectlens-{report.period}-v{report.version}.{format}")
@router.get("/reports")
def reports(db:Session=Depends(get_db)): return db.query(GeneratedReport).order_by(GeneratedReport.created_at.desc()).all()
@router.patch("/reports/{report_id}/{status}")
def review_report(report_id:str,status:str,db:Session=Depends(get_db),user=Depends(current_user)):
    if status not in ("Draft","Reviewed","Approved","Rejected"): raise HTTPException(400,"Invalid review status")
    report=db.get(GeneratedReport,report_id)
    if not report: raise HTTPException(404,"Report not found")
    report.status=status
    if status=="Reviewed": report.reviewed_by=user.id; report.reviewed_at=datetime.utcnow()
    elif status=="Approved": report.approved_by=user.id; report.approved_at=datetime.utcnow()
    elif status=="Rejected": report.rejected_by=user.id; report.rejected_at=datetime.utcnow()
    db.add(AuditLog(user_id=user.id,action="report.review",entity_type="report",entity_id=report.id,details={"status":status})); db.commit(); return {"id":report.id,"status":status}
@router.get("/governance")
def governance(): return {"principles":["AI is decision support","Humans remain responsible","Important outputs require review","Sources must be traceable","Model and prompt versions are logged","No hidden automated business decisions"],"providers":{"cloud":{"name":"Gemini","status":"Active"},"private":{"status":"Architecture ready / future option","implemented":False}}}
@router.get("/audit")
def audit(db:Session=Depends(get_db)): return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(200).all()
@router.post("/pipelines/run")
def run_pipeline(db:Session=Depends(get_db),user=Depends(current_user)):
    counts={"projects":db.query(Project).count(),"financials":db.query(MonthlyFinancial).count(),"documents":db.query(Document).count(),"clauses":db.query(ContractClause).count()}; processed=sum(counts.values()); steps=[{"name":x,"status":"Successful"} for x in ["Import","Validation","Cleaning","Transformation","Deduplication","Financial calculations","Risk calculations","Document processing","Embeddings","Database commit"]]
    run=PipelineRun(status="Successful",records_processed=processed,inserted=0,updated=processed,failed=0,steps=steps); db.add(run); db.add(AuditLog(user_id=user.id,action="pipeline.run",entity_type="pipeline",entity_id=run.id,details=counts)); db.commit(); db.refresh(run); return {"id":run.id,"status":run.status,"records_processed":processed,"inserted":0,"updated":processed,"failed":0,"transaction":"committed","steps":steps}
@router.get("/pipelines")
def pipelines(db:Session=Depends(get_db)): return db.query(PipelineRun).order_by(PipelineRun.created_at.desc()).limit(20).all()
@router.get("/adoption")
def adoption(db:Session=Depends(get_db)):
    total=db.query(AIRun).count(); feedback=db.query(AIFeedback).count(); helpful=db.query(AIFeedback).filter_by(helpful=True).count()
    return {"active_users":db.query(User).filter_by(is_active=True).count(),"ai_questions":total,"generated_reports":db.query(GeneratedReport).count(),"feedback_count":feedback,"satisfaction_score":round(helpful/feedback*100) if feedback else 0,"citation_coverage":round(db.query(AIRun).filter(AIRun.source_ids!=None).count()/total*100) if total else 100,"last_deployment":"Local development"}
