# test_retriever.py
from retrieval.retriever import get_persona, search_businesses, find_similar_users

# Test 1 — fetch a real persona
import json
with open("data/processed/review_slice.json") as f:
    first_user = json.loads(f.readline())["user_id"]

persona = get_persona(first_user)
print("PERSONA:", persona["summary"])
print("TONE:", persona["tone_tags"])

# Test 2 — semantic business search
results = search_businesses("spicy Nigerian food casual Lagos", k=5)
for r in results:
    print(f"{r['name']} | {r['categories']} | {r['stars']}★")

# Test 3 — cold start
similar = find_similar_users("User who loves fast food, rates generously, writes short reviews", k=3)
for u in similar:
    print(u["summary"])