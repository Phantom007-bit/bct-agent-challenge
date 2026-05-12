import json, os
from collections import defaultdict

RAW_DIR = os.path.join("data", "raw")
PROCESSED_DIR = os.path.join("data", "processed")

# The Safety Caps
MIN_REVIEWS_PER_USER = 15
TARGET_USERS = 1000  

os.makedirs(PROCESSED_DIR, exist_ok=True)

# --- PASS 1: Count & Cap ---
print("Scanning user activity...")
user_counts = defaultdict(int)
with open(os.path.join(RAW_DIR, "yelp_academic_dataset_review.json"), encoding="utf-8") as f:
    for line in f:
        user_counts[json.loads(line)["user_id"]] += 1

# 1. Filter for 15+ reviews
# 2. Sort so the most active users are at the top
# 3. Slice exactly the top 500
sorted_valid_users = sorted(
    [(uid, count) for uid, count in user_counts.items() if count >= MIN_REVIEWS_PER_USER],
    key=lambda x: x[1], 
    reverse=True
)

selected_users = {uid for uid, count in sorted_valid_users[:TARGET_USERS]}
print(f"🔒 Locked in exactly {len(selected_users)} VIP users.")

# --- PASS 2: Extract Reviews ---
print("Extracting reviews...")
reviews, biz_ids = [], set()
with open(os.path.join(RAW_DIR, "yelp_academic_dataset_review.json"), encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        if r["user_id"] in selected_users:
            reviews.append(r)
            biz_ids.add(r["business_id"])

reviews.sort(key=lambda r: r["date"])

# --- PASS 3: Extract Businesses ---
print("Extracting businesses...")
businesses = []
with open(os.path.join(RAW_DIR, "yelp_academic_dataset_business.json"), encoding="utf-8") as f:
    for line in f:
        b = json.loads(line)
        if b["business_id"] in biz_ids:
            businesses.append(b)

# --- SAVE ---
print("Saving lightweight slices...")
with open(os.path.join(PROCESSED_DIR, "review_slice.json"), "w") as f:
    for r in reviews: f.write(json.dumps(r) + "\n")

with open(os.path.join(PROCESSED_DIR, "business_slice.json"), "w") as f:
    for b in businesses: f.write(json.dumps(b) + "\n")

print(f"✅ FINAL STATS: {len(reviews)} reviews | {len(selected_users)} users | {len(businesses)} businesses")