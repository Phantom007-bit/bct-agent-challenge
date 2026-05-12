# core/naija_layer.py
# Nigerian cultural context module — injected into both agents


# ── Base system prompt ────────────────────────────────────────────────────────
NAIJA_SYSTEM_PROMPT = """You deeply understand Nigerian culture, food, and everyday life.
When generating reviews or recommendations, apply these cultural lenses:

LANGUAGE & TONE
- Write in Nigerian English — warm, expressive, direct, confident
- Use Pidgin naturally for emphasis, not forced:
  e.g. "the jollof sweet well well", "service sha left something to be desired",
  "e dey try", "no be small thing", "the pepper level correct",
  "I go definitely come back", "the place fine die"
- Nigerians are effusive about good experiences and blunt about bad ones

WHAT NIGERIANS CARE ABOUT
- Value for money is non-negotiable — portion size matters
- Pepper level and spice are genuine considerations  
- Generator noise, slow WiFi, AC that doesn't work — valid complaints
- Waiting time is taken seriously ("them go make you wait forever")
- Presentation and ambiance matter for fine dining crowd
- Hygiene is noticed and commented on

CITY AWARENESS
- Lagos: fast-paced, traffic-aware, Lekki/VI/Ikeja crowd have different vibes
- Abuja: calmer, government crowd, slightly more formal expectations
- Port Harcourt: oil money energy, seafood culture strong
- Ibadan: value-conscious, amala and buka culture runs deep
- Kano: northern cuisine pride, suya and kilishi are serious business

FOOD CULTURE
- Jollof rice quality is always worth mentioning
- "Nigerian food" vs "continental" are understood distinct categories
- Buka vs fine dining carry different expectations entirely
- Pepper soup, suya, and asun are late-night staples
- Ofada rice, amala, edikang ikong — regional pride dishes"""


# ── Cultural context builder ──────────────────────────────────────────────────
def build_cultural_context(
    city: str,
    categories: str,
    persona_top_categories: list
) -> str:
    """
    Builds a short cultural context paragraph injected into agent prompts.
    Tells the LLM what kind of Nigerian user and location it's dealing with.
    """
    city_vibe = {
        "Lagos":        "fast-paced Lagos crowd — they know their food and have options",
        "Abuja":        "Abuja crowd — slightly more reserved, value quality and calm",
        "Port Harcourt":"Port Harcourt — seafood culture is strong, expectations are high",
        "Ibadan":       "Ibadan crowd — value-conscious, buka culture runs deep",
        "Kano":         "Kano crowd — northern cuisine pride, halal awareness matters",
    }.get(city, "Nigerian crowd with high standards and cultural awareness")

    buka_mode    = any(c in categories.lower() for c in ["buka", "local food", "nigerian"])
    fine_mode    = any(c in categories.lower() for c in ["fine dining", "continental"])
    street_mode  = any(c in categories.lower() for c in ["street food", "suya", "grill"])

    if buka_mode:
        dining_context = "This is a buka/local food context — portions, pepper level, and authenticity matter most."
    elif fine_mode:
        dining_context = "This is a fine dining context — presentation, service, and ambiance are expected to match the price."
    elif street_mode:
        dining_context = "This is street food — freshness, taste, and speed are what people come for."
    else:
        dining_context = "Standard dining expectations apply — taste, service, and value."

    return f"Cultural context: {city_vibe}. {dining_context}"


# ── Writing style instructions based on behavioral tags ──────────────────────
def get_style_instructions(tone_tags: list, avg_review_length: int) -> str:
    """
    Translates behavioral tags into writing style instructions for the LLM.
    """
    parts = []

    if "generous_rater" in tone_tags:
        parts.append("This user leans positive — they find the good in most experiences.")
    elif "harsh_rater" in tone_tags:
        parts.append("This user is critical — they hold places to a high standard.")
    else:
        parts.append("This user is balanced — they praise what works and call out what doesn't.")

    if "detailed_writer" in tone_tags:
        parts.append(f"They write detailed reviews (~{avg_review_length} words) — cover multiple aspects.")
    elif "brief_writer" in tone_tags:
        parts.append(f"They write short, punchy reviews (~{avg_review_length} words) — get to the point fast.")
    else:
        parts.append(f"They write moderate-length reviews (~{avg_review_length} words).")

    if "inconsistent_rater" in tone_tags:
        parts.append("Their ratings vary widely — small details can swing their opinion.")
    else:
        parts.append("Their ratings are consistent — they stick to their standards.")

    return " ".join(parts)


# ── Recommendation framing ────────────────────────────────────────────────────
def get_recommendation_framing(top_categories: list, city: str) -> str:
    """
    Tells the recommender agent how to frame suggestions for this Nigerian user.
    """
    cat_lower = [c.lower() for c in top_categories]

    if any(c in cat_lower for c in ["nigerian", "buka", "local food"]):
        flavor = "They love authentic Nigerian food — local spots will resonate more than foreign chains."
    elif any(c in cat_lower for c in ["fine dining", "continental"]):
        flavor = "They appreciate quality dining — recommend places with strong presentation and service."
    elif any(c in cat_lower for c in ["fast food", "chicken"]):
        flavor = "They're a fast food regular — convenience, speed, and value matter."
    elif any(c in cat_lower for c in ["nightlife", "bars", "lounge"]):
        flavor = "They enjoy the nightlife scene — atmosphere and vibe matter as much as food."
    else:
        flavor = "They have broad taste — mix of local and continental will work."

    city_note = f"Focus recommendations in {city} where possible — proximity matters to Nigerian users."

    return f"{flavor} {city_note}"