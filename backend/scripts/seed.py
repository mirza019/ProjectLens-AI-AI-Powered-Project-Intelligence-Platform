from datetime import date,timedelta
from pathlib import Path
from app.core.database import Base,SessionLocal,engine
from app.core.security import hash_password
from app.generators.synthetic import generate_projects
from app.models.entities import *
from app.services.contracts import generate_contract_pdf, ingest_contract
from app.services.storage import storage

SECTIONS={"Scope":"The supplier shall engineer, manufacture, test, deliver, install, and commission the equipment in the technical schedules.","Price":"The contract price is firm except for approved changes under the change management procedure.","Payment Terms":"Payment is milestone-based: 20 percent at effectiveness, 50 percent across delivery milestones, 20 percent at provisional acceptance, and 10 percent at final acceptance. Valid invoices are payable within 30 calendar days.","Milestones":"Milestone dates are binding and schedule threats require prompt written notice.","Delivery":"Delivery requires equipment at the agreed site with shipping and quality documents.","Acceptance":"Provisional acceptance requires successful commissioning tests, as-built documents, and closure of material punch-list items. Final acceptance follows the reliability period.","Liquidated Damages":"Delay damages accrue at 0.5 percent of the delayed portion per completed week, capped at 10 percent of contract price.","Warranty":"The warranty is 24 months from provisional acceptance or 30 months from delivery, whichever occurs first.","Change Management":"A change binds only after a written change order states scope, price, schedule impact, and authorized signatures. Potential changes require notice within 14 days.","Claims":"Claims must state the event, contractual basis, impact, and mitigation within 21 days of awareness.","Termination":"A material breach not cured within 30 days after written notice permits termination for cause.","Confidentiality":"Confidential information may be used only for contract performance and requires appropriate safeguards.","Dispute Resolution":"Disputes escalate to executive negotiation, then mediation, then binding arbitration."}

def seed():
    Base.metadata.create_all(engine); db=SessionLocal()
    try:
        role_map={}; permissions={"Admin":["manage_users","manage_data","configure_ai","manage_governance","run_pipelines"],"Project Manager":["view_projects","review_financials","use_ai","review_contracts","generate_reports"],"Analyst":["view_analysis","generate_insights","manage_use_cases"]}
        for name,perms in permissions.items():
            role=db.query(Role).filter_by(name=name).first() or Role(name=name,permissions=perms); db.add(role); db.flush(); role_map[name]=role
        for email,full_name,role in [("admin@projectlens.demo","Demo Administrator","Admin"),("manager@projectlens.demo","Maya Riedel","Project Manager"),("analyst@projectlens.demo","Demo Analyst","Analyst")]:
            if not db.query(User).filter_by(email=email).first(): db.add(User(email=email,full_name=full_name,password_hash=hash_password("projectlens-demo"),role_id=role_map[role].id))
        db.flush()
        if not db.query(Project).count():
            for row in generate_projects(): db.add(Project(**{k:v for k,v in row.items() if k!='root_cause'}))
            db.flush()
        for i,p in enumerate(db.query(Project).all()):
            if not db.query(Risk).filter_by(project_id=p.id).first():
                category=("Supplier" if p.schedule_days>7 else ["Engineering","Commercial","Customer","Technical"][i%4])
                db.add(Risk(project_id=p.id,risk_code=f"RX-{p.code}",title=f"{category} delivery uncertainty",category=category,probability=.22+(i%5)*.07,financial_impact=p.value*(.008+(i%4)*.004),schedule_impact=max(2,p.schedule_days),owner=["Elena Rossi","Jonas Weber","Priya Nair","Marc Dubois"][i%4],status="Open" if i%3 else "Mitigating",mitigation="Monthly evidence review, named action owner, and escalation at threshold breach"))
            if not db.query(MonthlyFinancial).filter_by(project_id=p.id).count():
                for m in range(21):
                    period=f"{2025+m//12:04d}-{m%12+1:02d}"; progress=min(1,(m+1)/24)
                    db.add(MonthlyFinancial(project_id=p.id,period=period,budget=p.budget_cost,actual_cost=p.budget_cost*progress*(1.04 if p.schedule_days>7 and m>13 else 1),forecast_cost=p.budget_cost+(p.forecast_cost-p.budget_cost)*progress,forecast_revenue=p.value,cash_in=p.value*progress*.85,cash_out=p.budget_cost*progress))
            if not db.query(ForecastVersion).filter_by(project_id=p.id).count():
                change=p.forecast_cost-p.budget_cost; drivers={"Materials":change*.47,"Engineering":change*.26,"Logistics":change*.13,"Other":change*.14}
                db.add_all([ForecastVersion(project_id=p.id,period="2026-08",version=8,total_cost=p.budget_cost+change*.55,revenue=p.value,drivers={k:v*.55 for k,v in drivers.items()}),ForecastVersion(project_id=p.id,period="2026-09",version=9,total_cost=p.forecast_cost,revenue=p.value,drivers=drivers)])
            if not db.query(Milestone).filter_by(project_id=p.id).count():
                for n,label in enumerate(("Design freeze","Factory acceptance","Equipment delivery","Commissioning","Final acceptance"),1):
                    planned=date(2025,4,1)+timedelta(days=n*100+i*2); forecast=planned+timedelta(days=p.schedule_days if n>=3 else 0)
                    db.add(Milestone(project_id=p.id,code=f"M{n}",name=label,planned_date=planned.isoformat(),forecast_date=forecast.isoformat(),status="Delayed" if p.schedule_days>7 and n>=3 else "On track"))
            if not db.query(Contract).filter_by(project_id=p.id).first():
                delivery=(date(2026,3,1)+timedelta(days=i*9)).isoformat(); contract=Contract(project_id=p.id,name=f"{p.name} Engineering & Delivery Agreement",contract_number=f"PL-{2025+i:04d}-{p.code}",customer=p.customer,supplier="Aurelius Engineering GmbH",effective_date="2025-01-15",delivery_date=delivery,warranty_months=24,value=p.value,status="Active",payment_milestones=[20,30,30,10,10]); db.add(contract); db.flush(); path=storage.path("contracts",f"{p.code.lower()}.pdf"); generate_contract_pdf(contract,p.name,path); contract.file_path=str(path); ingest_contract(db,contract)
            if not db.query(Document).filter_by(project_id=p.id).count():
                issue=f"The critical supplier delay moved equipment delivery by {p.schedule_days} days. Expedited logistics and weekly recovery reviews were agreed." if p.schedule_days>7 else "Delivery remains within tolerance and no material recovery action is required."
                docs=[("meeting_note","Monthly Review",issue),("monthly_report","September Report",f"Completion is {p.completion:.0f} percent. Expected margin is {p.expected_margin:.1f} percent and forecast cost is EUR {p.forecast_cost:,.0f}."),("lesson_learned","Lessons Learned","Early supplier surveillance and formal interface freeze reduce late engineering changes."),("project_update","Weekly Update",f"Schedule variance is {p.schedule_days} days. Forecast variance is EUR {p.forecast_cost-p.budget_cost:,.0f}.")]
                for dtype,title,content in docs: db.add(Document(project_id=p.id,title=f"{p.name} {title}",document_type=dtype,section="Project status",page=1,content=content))
            if p.schedule_days>7 and not db.query(ChangeOrder).filter_by(project_id=p.id).first(): db.add(ChangeOrder(project_id=p.id,code=f"CO-{p.code}",title="Accelerated logistics support",value=p.value*.006,status="Under Review",reason="Protect commissioning milestone"))
        if not db.query(AIUseCase).count(): db.add_all([AIUseCase(title="Monthly reporting automation",business_problem="Manual consolidation takes several hours",current_process="Analysts copy data between files",owner="Finance Transformation",status="Prototype",assessment={"ai_needed":True,"automation_needed":True,"human_review_required":True}),AIUseCase(title="Invoice validation",business_problem="Invoices require repeated field checks",current_process="Rules are checked manually",owner="Shared Services",status="Ready",assessment={"ai_needed":False,"automation_needed":True,"human_review_required":False})])
        db.flush()
        targets={"meeting_note":100,"monthly_report":60,"lesson_learned":50,"project_update":50}; all_projects=db.query(Project).all()
        for dtype,target in targets.items():
            existing=db.query(Document).filter_by(document_type=dtype).count()
            for n in range(existing,target):
                p=all_projects[n%len(all_projects)]; cycle=n//len(all_projects)+1
                content={"meeting_note":f"Review cycle {cycle}: {p.name} team confirmed current schedule variance of {p.schedule_days} days, assigned owners for supplier and engineering actions, and agreed the next evidence review.","monthly_report":f"Reporting cycle {cycle}: {p.name} is {p.completion:.0f}% complete. Forecast cost is EUR {p.forecast_cost:,.0f}, expected margin is {p.expected_margin:.1f}%, and management attention follows transparent thresholds.","lesson_learned":f"Lesson {cycle} from {p.name}: early interface freeze, supplier surveillance, and evidence-based escalation reduce forecast volatility and schedule recovery cost.","project_update":f"Update {cycle}: {p.name} forecast variance is EUR {p.forecast_cost-p.budget_cost:,.0f}; schedule variance is {p.schedule_days} days; linked mitigations remain under owner review."}[dtype]
                db.add(Document(project_id=p.id,title=f"{p.name} {dtype.replace('_',' ').title()} {cycle}",document_type=dtype,section="Project status",page=1,content=content))
        db.commit(); print(f"Seed complete: {db.query(Project).count()} projects, {db.query(Contract).count()} contracts, {db.query(Document).count()} knowledge documents")
    finally: db.close()
if __name__=="__main__": seed()
