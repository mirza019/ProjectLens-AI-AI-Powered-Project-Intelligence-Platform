from __future__ import annotations
import math
import re
from dataclasses import dataclass
from sqlalchemy.orm import Session
from app.models.entities import Contract, Document, DocumentChunk, Project
from app.services.contracts import deterministic_embedding

STOP={"the","a","an","is","are","what","which","for","of","to","in","and","does","did","was","were","project"}
def tokens(text:str)->set[str]: return {x for x in re.findall(r"[a-z0-9]+",text.lower()) if len(x)>2 and x not in STOP}
def lexical_score(query:str,text:str)->float:
    q=tokens(query); d=tokens(text)
    return len(q&d)/(len(q) or 1)

@dataclass
class Retrieved:
    id:str; title:str; section:str; page:int; content:str; score:float; contract_id:str|None=None

def _cosine(a,b): return sum(x*y for x,y in zip(a,b))/(math.sqrt(sum(x*x for x in a))*math.sqrt(sum(y*y for y in b)) or 1)

def contract_search(db:Session,query:str,project_id:str|None=None,contract_id:str|None=None,limit:int=6,query_embedding:list[float]|None=None)->list[Retrieved]:
    rows=db.query(DocumentChunk,Contract,Project).join(Contract,DocumentChunk.contract_id==Contract.id).join(Project,DocumentChunk.project_id==Project.id)
    if project_id: rows=rows.filter(DocumentChunk.project_id==project_id)
    if contract_id: rows=rows.filter(DocumentChunk.contract_id==contract_id)
    data=rows.all(); qvec=query_embedding or deterministic_embedding(query)
    lexical=sorted(data,key=lambda row:lexical_score(query,row[0].chunk_text+" "+row[0].section_title),reverse=True)
    if db.bind and db.bind.dialect.name=="postgresql":
        vector_query=rows.order_by(DocumentChunk.embedding.cosine_distance(qvec)).limit(max(limit*5,30))
        vector=vector_query.all()
    else:
        vector=sorted(data,key=lambda row:_cosine(qvec,row[0].embedding or []),reverse=True)
    fused={}
    for ranking in (lexical,vector):
        for rank,row in enumerate(ranking[:max(limit*5,30)],1): fused[row[0].id]=fused.get(row[0].id,0)+1/(60+rank)
    by_id={row[0].id:row for row in data}; ordered=sorted(fused,key=fused.get,reverse=True)[:limit]
    return [Retrieved(cid,by_id[cid][1].name,by_id[cid][0].section_title,by_id[cid][0].page_start,by_id[cid][0].chunk_text,fused[cid],by_id[cid][0].contract_id) for cid in ordered if lexical_score(query,by_id[cid][0].chunk_text+" "+by_id[cid][0].section_title)>0]

def knowledge_search(db:Session,query:str,project_id:str|None=None,limit:int=5)->list[Retrieved]:
    rows=db.query(Document,Project).join(Project,Document.project_id==Project.id)
    if project_id: rows=rows.filter(Project.id==project_id)
    found=[Retrieved(d.id,d.title,d.section,d.page,d.content,lexical_score(query,d.content+" "+d.title+" "+p.name)) for d,p in rows.all()]
    return [x for x in sorted(found,key=lambda x:x.score,reverse=True)[:limit] if x.score>0]

def grounded_prompt(question:str,sources:list[Retrieved],synthetic=True)->str:
    context="\n\n".join(f"SOURCE_ID: {s.id}\nCONTRACT_ID: {s.contract_id or ''}\nTITLE: {s.title}\nSECTION: {s.section}\nPAGE: {s.page}\nCONTENT: {s.content}" for s in sources)
    ids=[s.id for s in sources]
    return f"""You are ProjectLens AI. Answer only from verified context below. All data is {'synthetic demonstration data' if synthetic else 'enterprise data'}. Never invent facts or source IDs. Use only these IDs: {ids}. Cite every factual finding. If evidence does not answer the question, state: Insufficient evidence in the indexed documents. Separate facts from interpretation. Return the required JSON structure.\n\nQUESTION: {question}\n\nVERIFIED CONTEXT:\n{context}"""

def validate_sources(output:dict,allowed:list[str])->dict:
    cited=output.get("source_ids",[])
    invalid=[x for x in cited if x not in allowed]
    if invalid: raise ValueError(f"Model returned unsupported sources: {invalid}")
    output["source_ids"]=cited
    output["confidence"]=min(max(float(output.get("confidence",0)),0),1)
    return output
