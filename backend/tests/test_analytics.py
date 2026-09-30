import pytest
from app.analytics.financial import expected_margin,forecast_variance,health_status,risk_exposure
from app.ai.router import Intent,route
from app.generators.synthetic import generate_projects
from app.rag.retrieval import validate_sources

def test_margin(): assert expected_margin(100,80)==20
def test_variance(): assert forecast_variance(21.7,20.8)["absolute"]==pytest.approx(.9)
def test_exposure(): assert risk_exposure(.6,1_000_000)==600_000
def test_health_rules(): assert health_status(9,4,22,5)=="Critical"
def test_router(): assert route("What does the contract say about warranty?")==Intent.CONTRACT
def test_deterministic_data(): assert generate_projects()==generate_projects() and len(generate_projects())==30
def test_source_validation_accepts_grounded_ids(): assert validate_sources({"source_ids":["a"],"confidence":1.4},["a"])["confidence"]==1
def test_source_validation_rejects_hallucinated_ids():
    with pytest.raises(ValueError): validate_sources({"source_ids":["invented"],"confidence":.8},["real"])
