from abc import ABC, abstractmethod
import json
import httpx
from app.core.config import settings

class AIProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> dict: ...
class GeminiProvider(AIProvider):
    async def generate(self, prompt: str) -> dict:
        if not settings.gemini_api_key: raise RuntimeError("GEMINI_API_KEY is not configured")
        url=f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent"
        schema={"type":"OBJECT","properties":{"summary":{"type":"STRING"},"key_findings":{"type":"ARRAY","items":{"type":"STRING"}},"risks":{"type":"ARRAY","items":{"type":"STRING"}},"recommended_attention":{"type":"ARRAY","items":{"type":"STRING"}},"source_ids":{"type":"ARRAY","items":{"type":"STRING"}},"confidence":{"type":"NUMBER"}},"required":["summary","key_findings","risks","recommended_attention","source_ids","confidence"]}
        payload={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.15,"responseMimeType":"application/json","responseSchema":schema}}
        async with httpx.AsyncClient(timeout=45) as client:
            response=await client.post(url,params={"key":settings.gemini_api_key},json=payload)
            response.raise_for_status()
        text=response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text)
    async def embed(self, text: str) -> list[float]:
        if not settings.gemini_api_key: raise RuntimeError("GEMINI_API_KEY is not configured")
        url=f"https://generativelanguage.googleapis.com/v1beta/models/{settings.embedding_model}:embedContent"
        payload={"model":f"models/{settings.embedding_model}","content":{"parts":[{"text":text}]},"taskType":"RETRIEVAL_DOCUMENT","outputDimensionality":settings.embedding_dimensions}
        async with httpx.AsyncClient(timeout=45) as client:
            response=await client.post(url,params={"key":settings.gemini_api_key},json=payload); response.raise_for_status()
        return response.json()["embedding"]["values"]
    async def assess_opportunity(self, payload: dict) -> dict:
        if not settings.gemini_api_key: raise RuntimeError("GEMINI_API_KEY is not configured")
        url=f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent"
        schema={"type":"OBJECT","properties":{"recommended_approach":{"type":"STRING"},"ai_needed":{"type":"BOOLEAN"},"automation_needed":{"type":"BOOLEAN"},"analytics_needed":{"type":"BOOLEAN"},"rag_needed":{"type":"BOOLEAN"},"human_review_required":{"type":"BOOLEAN"},"complexity":{"type":"STRING","enum":["Low","Medium","High"]},"rationale":{"type":"ARRAY","items":{"type":"STRING"}},"security_considerations":{"type":"ARRAY","items":{"type":"STRING"}},"prototype_recommendation":{"type":"STRING"},"success_metrics":{"type":"ARRAY","items":{"type":"STRING"}}},"required":["recommended_approach","ai_needed","automation_needed","analytics_needed","rag_needed","human_review_required","complexity","rationale","security_considerations","prototype_recommendation","success_metrics"]}
        prompt="Assess this enterprise AI opportunity. Recommend AI only when justified; distinguish deterministic automation, analytics, RAG and generative AI. Require human review for material AI outputs. Return only the requested JSON. Input:\n"+json.dumps(payload)
        body={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.1,"responseMimeType":"application/json","responseSchema":schema}}
        async with httpx.AsyncClient(timeout=45) as client:
            response=await client.post(url,params={"key":settings.gemini_api_key},json=body); response.raise_for_status()
        return json.loads(response.json()["candidates"][0]["content"]["parts"][0]["text"])
class PrivateLLMProvider(AIProvider):
    async def generate(self, prompt: str) -> dict: raise NotImplementedError("Future architecture option; no private model is implemented")
