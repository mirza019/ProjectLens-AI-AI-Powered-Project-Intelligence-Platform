"""Generate the reviewable 30-document synthetic contract corpus without a database."""
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace
from app.generators.synthetic import generate_projects
from app.services.contracts import generate_contract_pdf

def main():
    root=Path("output/documents/contracts"); root.mkdir(parents=True,exist_ok=True)
    for i,project in enumerate(generate_projects()):
        contract=SimpleNamespace(contract_number=f"PL-{2025+i:04d}-{project['code']}",customer=project["customer"],supplier="Aurelius Engineering GmbH",effective_date="2025-01-15",delivery_date=(date(2026,3,1)+timedelta(days=i*9)).isoformat(),warranty_months=24,value=project["value"],status="Active")
        generate_contract_pdf(contract,project["name"],root/f"{project['code'].lower()}.pdf")
    print(f"Generated {len(list(root.glob('*.pdf')))} synthetic contracts in {root}")

if __name__=="__main__": main()
