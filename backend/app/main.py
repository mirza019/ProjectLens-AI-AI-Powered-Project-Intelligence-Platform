from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import settings
from app.core.database import Base, engine

app=FastAPI(title=settings.app_name,version="1.0.0",description="Evidence-first project intelligence API")
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins.split(","),allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(router,prefix="/api/v1")
@app.on_event("startup")
def startup(): Base.metadata.create_all(bind=engine)

