from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import leads


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Creates all tables on startup if they don't already exist
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables ready")
    yield
    # Nothing to clean up — SQLAlchemy manages the connection pool


app = FastAPI(
    title="Sales CRM API",
    description="FastAPI backend for the Oracle APEX Sales Pipeline CRM",
    version="1.0.0",
    lifespan=lifespan
)

# Register routers
app.include_router(leads.router)


@app.get("/")
def root():
    return {"message": "Sales CRM API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}