# core/persona_parser.py
import json
from collections import defaultdict

# ── Runtime persona resolver ───────────────────────────────────────────────────
def resolve_persona(persona_input: dict, retriever=None) -> dict:
    """
    Takes whatever persona shape arrives at the API and returns
    a clean, consistent persona dict the agents can use.
    """
    # Case 1 — existing user
    if "user_id" in persona_input and retriever:
        persona = retriever.get_persona(persona_input["user_id"])
        if persona:
            return persona

    # Case 2 — cold-start via description
    if "description" in persona_input and retriever:
        description = persona_input["description"]
        similar_users = retriever.find_similar_users(description, k=3)
        if similar_users:
            return blend_personas(similar_users, description)

    # Case 3 — full persona object passed directly
    if "avg_rating" in persona_input:
        return _normalise(persona_input)

    # Fallback
    return default_persona()

# ── Blend multiple personas for cold-start ────────────────────────────────────
def blend_personas(similar_users: list, description: str) -> dict:
    avg_rating = round(
        sum(u.get("avg_rating", 3.5) for u in similar_users) / len(similar_users), 2
    )
    from collections import Counter
    all_tags = [tag for u in similar_users for tag in u.get("tone_tags", [])]
    common_tags = [tag for tag, count in Counter(all_tags).items()
                   if count >= len(similar_users) // 2 + 1]

    all_cats = [cat for u in similar_users for cat in u.get("top_categories", [])]
    top_cats = [cat for cat, _ in Counter(all_cats).most_common(5)]

    recent_reviews = similar_users[0].get("recent_reviews", []) if similar_users else []

    return {
        "user_id":           "cold_start",
        "description":       description,
        "avg_rating":        avg_rating,
        "rating_variance":   0.8,
        "avg_review_length": 80,
        "total_reviews":     0,
        "tone_tags":         common_tags or ["balanced_rater"],
        "top_categories":    top_cats,
        "recent_reviews":    recent_reviews,
        "is_cold_start":     True
    }

# ── Normalise a partial persona object ────────────────────────────────────────
def _normalise(persona: dict) -> dict:
    return {
        "user_id":           persona.get("user_id", "unknown"),
        "avg_rating":        persona.get("avg_rating", 3.5),
        "rating_variance":   persona.get("rating_variance", 0.8),
        "avg_review_length": persona.get("avg_review_length", 80),
        "total_reviews":     persona.get("total_reviews", 0),
        "tone_tags":         persona.get("tone_tags", ["balanced_rater"]),
        "top_categories":    persona.get("top_categories", ["Restaurants"]),
        "recent_reviews":    persona.get("recent_reviews", []),
        "is_cold_start":     persona.get("is_cold_start", False)
    }

# ── Default persona fallback ───────────────────────────────────────────────────
def default_persona() -> dict:
    return {
        "user_id":           "default",
        "avg_rating":        3.8,
        "rating_variance":   0.9,
        "avg_review_length": 85,
        "total_reviews":     0,
        "tone_tags":         ["balanced_rater", "consistent_rater"],
        "top_categories":    ["Restaurants", "Fast Food", "Nigerian"],
        "recent_reviews":    [],
        "is_cold_start":     True
    }