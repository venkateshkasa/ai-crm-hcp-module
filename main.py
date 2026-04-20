from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine, SessionLocal
from app.routers import agent, hcps, interactions
from app.seed import seed_hcps

Base.metadata.create_all(bind=engine)
_db = SessionLocal()
try:
    seed_hcps(_db)
finally:
    _db.close()

app = FastAPI(title="HCP CRM API", version="0.1.0")

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hcps.router, prefix="/api")
app.include_router(interactions.router, prefix="/api")
app.include_router(agent.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok", "agent_enabled": bool(settings.groq_api_key)}
