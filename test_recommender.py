import json
from schemas.models import RecommendRequest, PersonaInput, ContextInput
from agents.task_recommender import recommend

# Test 1 — existing user
with open("data/processed/review_slice.json") as f:
    first_user = json.loads(f.readline())["user_id"]

print("=== TEST 1: EXISTING USER ===")
result1 = recommend(RecommendRequest(
    user_persona=PersonaInput(user_id=first_user),
    context=ContextInput(intent="dinner tonight"),
    k=5
))
print(f"Cold start: {result1.is_cold_start}")
for r in result1.recommendations:
    print(f"  {r.name} | {r.stars}★ | {r.reason[:80]}")

print("\n=== TEST 2: COLD START ===")
result2 = recommend(RecommendRequest(
    user_persona=PersonaInput(
        description="I love spicy street food, budget-conscious, rate strictly"
    ),
    context=ContextInput(intent="quick lunch in Lagos"),
    k=5
))
print(f"Cold start: {result2.is_cold_start}")
for r in result2.recommendations:
    print(f"  {r.name} | {r.stars}★ | {r.reason[:80]}")
if result2.clarifying_questions:
    print(f"Clarifying: {result2.clarifying_questions}")