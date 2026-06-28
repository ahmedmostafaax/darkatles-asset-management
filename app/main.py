from fastapi import FastAPI
from .database import engine, Base
from .routers import assets, relationships

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DarkAtlas Asset Management",
    description="Asset Management API for DarkAtlas ASM Platform",
    version="1.0.0"
)

app.include_router(assets.router)
app.include_router(relationships.router)

@app.get("/")
def root():
    return {"message": "DarkAtlas Asset Management API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}