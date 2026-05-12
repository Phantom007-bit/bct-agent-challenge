from schemas.models import SimulateReviewRequest, PersonaInput, ItemInput
from agents.task_simulator import simulate_review 

request = SimulateReviewRequest(
    user_persona=PersonaInput(
        description="I love spicy Nigerian food, rate generously, write detailed reviews"
    ),
    item=ItemInput(
        name="Glover Court Suya",
        categories="Suya, Street Food, Nigerian",
        city="Lagos"
    )
)

print("🚀 Firing up the LangGraph agent...")
result = simulate_review(request)

print("\n=== RESULTS ===")
print(f"Rating: {result.rating}★")
print(f"Review: {result.review_text}")
print(f"Reasoning: {result.reasoning_trace}")