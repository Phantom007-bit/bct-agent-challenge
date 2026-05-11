from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas.models import (
    SimulateReviewRequest, SimulateReviewResponse,
    RecommendRequest, RecommendResponse
)
from agents.task_simulator import simulate_review
from agents.task_recommender import recommend

app = FastAPI(
    title="BCT LLM Agent API",
    description="User modeling and recommendation agents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "online", "message": "BCT Agent API is running"}


# ── Task A — simulate ──────────────────────────────────────────────────
@app.post("/simulate-review", response_model=SimulateReviewResponse)
def simulate_review_endpoint(request: SimulateReviewRequest):
    try:
        return simulate_review(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Task B — recommend ────────────────────────────────────────────────────────
@app.post("/recommend", response_model=RecommendResponse)
def recommend_endpoint(request: RecommendRequest):
    try:
        return recommend(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)