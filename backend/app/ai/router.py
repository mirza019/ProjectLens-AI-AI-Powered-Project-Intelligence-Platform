from enum import Enum

class Intent(str, Enum):
    FINANCIAL="financial_analytics"; FORECAST="forecast_analysis"; RISK="risk_analysis"; CONTRACT="contract_rag"; KNOWLEDGE="knowledge_rag"; PORTFOLIO="portfolio_analytics"; SUMMARY="project_summary"

KEYWORDS={Intent.CONTRACT:("contract","warranty","payment terms","penalt","clause","acceptance"),Intent.FORECAST:("forecast","eac","variance","cost increase"),Intent.RISK:("risk","exposure","mitigation"),Intent.KNOWLEDGE:("meeting","agreed","lesson","previous","last month"),Intent.FINANCIAL:("margin","revenue","cash","actual cost","budget"),Intent.PORTFOLIO:("which projects","portfolio","largest")}
def route(question: str) -> Intent:
    q=question.lower(); scores={intent:sum(term in q for term in terms) for intent,terms in KEYWORDS.items()}
    best=max(scores,key=scores.get)
    return best if scores[best] else Intent.SUMMARY

