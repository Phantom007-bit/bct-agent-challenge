import json, os
from collections import defaultdict

RAW_DIR = os.path.join("data", "raw")
PROCESSED_DIR = os.path.join("data", "processed")
MIN_REVIEWS_PER_USER = 15    # enough history to build a real persona
TARGET_USERS = 500           # ~500 rich users is plenty for a prototype
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Pass 1 — count reviews per user
print("Scanning user activity...")
user_counts = defaultdict(int)
with open(os.path.join(RAW_DIR, "review.json"), encoding="utf-8") as f:
    for line in f:
        user_counts[json.loads(line)["user_id"]] += 1

# Select top users by review count
selected_users = {
    uid for uid, _ in
    sorted(user_counts.items(), key=lambda x: -x[1])[:TARGET_USERS]
    if user_counts[uid] >= MIN_REVIEWS_PER_USER
}
print(f"Selected {len(selected_users)} users")

# Pass 2 — extract their reviews, sorted by date (important for holdout later)
print("Extracting reviews...")
reviews, biz_ids = [], set()
with open(os.path.join(RAW_DIR, "review.json"), encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        if r["user_id"] in selected_users:
            reviews.append(r)
            biz_ids.add(r["business_id"])

# Sort by date so you can hold out the latest reviews per user for eval
reviews.sort(key=lambda r: r["date"])

# Pass 3 — extract their businesses (you need this for Task B item metadata)
print("Extracting businesses...")
businesses = []
with open(os.path.join(RAW_DIR, "business.json"), encoding="utf-8") as f:
    for line in f:
        b = json.loads(line)
        if b["business_id"] in biz_ids:
            businesses.append(b)

# Save
with open(os.path.join(PROCESSED_DIR, "review_slice.json"), "w") as f:
    for r in reviews:
        f.write(json.dumps(r) + "\n")

with open(os.path.join(PROCESSED_DIR, "business_slice.json"), "w") as f:
    for b in businesses:
        f.write(json.dumps(b) + "\n")

print(f"✅ {len(reviews)} reviews | {len(selected_users)} users | {len(businesses)} businesses")