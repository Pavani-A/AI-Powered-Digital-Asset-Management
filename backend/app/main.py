from fastapi import FastAPI
from sqlalchemy import text

from backend.app.db.database import engine

app = FastAPI(
    title="AI-Powered Digital Asset Management",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "ai-dam-api",
    }


@app.get("/health/database")
def database_health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": "postgresql",
    }