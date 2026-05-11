# schemas/models.py
from pydantic import BaseModel, Field
from typing import Optional, List


# ── Persona input — flexible, handles all three shapes ────────────────────────
class PersonaInput(BaseModel):
    # Shape 1 — existing user
    user_id: Optional[str] = None

    # Shape 2 — new user, cold-start
    description: Optional[str] = None

    # Shape 3 — full persona object
    avg_rating:        Optional[float]      = None
    rating_variance:   Optional[float]      = None
    avg_review_length: Optional[int]        = None
    tone_tags:         Optional[List[str]]  = None
    top_categories:    Optional[List[str]]  = None
    recent_reviews:    Optional[List[dict]] = None


# ── Item input (used by Task A) ───────────────────────────────────────────────
class ItemInput(BaseModel):
    id:         Optional[str]   = None
    name:       str
    categories: str
    city:       Optional[str]   = "Lagos"
    state:      Optional[str]   = "Lagos"
    stars:      Optional[float] = None
    metadata:   Optional[dict]  = None


# ── Optional context for both tasks ──────────────────────────────────────────
class ContextInput(BaseModel):
    time_of_visit: Optional[str]  = None
    occasion:      Optional[str]  = None
    intent:        Optional[str]  = None
    constraints:   Optional[dict] = None


# ── Task A — simulate review ──────────────────────────────────────────────────
class SimulateReviewRequest(BaseModel):
    user_persona: PersonaInput
    item:         ItemInput
    context:      Optional[ContextInput] = None


class SimulateReviewResponse(BaseModel):
    rating:          int
    review_text:     str
    reasoning_trace: Optional[str] = None


# ── Task B — recommend ────────────────────────────────────────────────────────
class RecommendationItem(BaseModel):
    business_id: str
    name:        str
    categories:  str
    city:        str
    stars:       float
    score:       float
    reason:      str


class RecommendRequest(BaseModel):
    user_persona: PersonaInput
    candidates:   Optional[List[ItemInput]] = None
    context:      Optional[ContextInput]    = None
    k:            int                       = 10


class RecommendResponse(BaseModel):
    recommendations:     List[RecommendationItem]
    is_cold_start:       bool
    clarifying_questions: Optional[List[str]] = None