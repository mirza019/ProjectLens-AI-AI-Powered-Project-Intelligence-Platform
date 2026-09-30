def expected_margin(revenue: float, forecast_cost: float) -> float:
    if revenue <= 0: raise ValueError("Revenue must be positive")
    return (revenue - forecast_cost) / revenue * 100

def forecast_variance(current: float, previous: float) -> dict:
    absolute = current - previous
    return {"absolute": absolute, "percentage": (absolute / previous * 100) if previous else 0}

def risk_exposure(probability: float, financial_impact: float) -> float:
    if not 0 <= probability <= 1: raise ValueError("Probability must be between 0 and 1")
    return probability * financial_impact

def health_status(margin: float, variance_pct: float, schedule_days: int, exposure_pct: float) -> str:
    score = (margin < 10) * 2 + (margin < 14) + (variance_pct > 3) * 2 + (variance_pct > 1) + (schedule_days > 20) * 2 + (schedule_days > 7) + (exposure_pct > 4) * 2
    return "Critical" if score >= 5 else "Attention" if score >= 3 else "Monitor" if score >= 1 else "Healthy"

