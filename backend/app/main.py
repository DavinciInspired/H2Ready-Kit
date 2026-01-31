from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.init_db import init_db
from app.routes import health,pipelines,segments,scoring,bulk,reports

app=FastAPI(title="H2Ready Full MVP API",version="0.7.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

app.include_router(health.router,tags=["health"])
app.include_router(pipelines.router,prefix="/pipelines",tags=["pipelines"])
app.include_router(segments.router,prefix="/segments",tags=["segments"])
app.include_router(scoring.router,tags=["scoring"])
app.include_router(bulk.router,tags=["bulk"])
app.include_router(reports.router,tags=["reports"])
