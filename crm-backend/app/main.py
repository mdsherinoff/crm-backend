from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import init_pool, close_pool
from app.routers import leads

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs on startup — opens the DB connection pool
    await init_pool()
    yield
    # Runs on shutdown — closes the pool cleanly
    await close_pool()

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