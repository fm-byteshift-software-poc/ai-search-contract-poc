from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes.search import router as search_router


app = FastAPI(
    title="AI Product Search PoC",
    description="Contract-first prototype for structured AI search integration.",
    version="0.1.0-poc",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS aligned with standard local Next.js/React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router)


@app.get("/health", tags=["System"])
def health_check():
    """Fast validation endpoint. Confirms runtime without triggering search pipeline."""
    return {"status": "ok", "version": "0.1.0-poc"}