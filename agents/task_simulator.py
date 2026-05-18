import re
import json

from dotenv import load_dotenv
load_dotenv()


import schemas.models as schemas_models
from schemas.models import SimulateReviewRequest, SimulateReviewResponse, PersonaInput, ItemInput, ContextInput
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
from typing import TypedDict

import retrieval.retriever as retriever_module
from retrieval.retriever import get_user_reviews
from core.persona_parser import resolve_persona
from core.naija_layer import (
    NAIJA_SYSTEM_PROMPT,
    build_cultural_context,
    get_style_instructions
)



# ── State ─────────────────────────────────────────────────────────────────────
class SimulatorState(TypedDict):
    # Inputs
    raw_persona:  dict
    raw_item:     dict
    raw_context:  dict

    # Built during graph execution
    persona:            dict
    user_reviews:       list
    cultural_context:   str
    style_instructions: str
    raw_response:       str

    # Final outputs
    rating:          int
    review_text:     str
    reasoning_trace: str

# ── LLM ───────────────────────────────────────────────────────────────────────
llm = ChatAnthropic(model="claude-sonnet-4-6", max_tokens=1000)


# ── Node 1: Resolve persona ───────────────────────────────────────────────────
def parse_persona_node(state: SimulatorState) -> dict:
    print("Resolving user persona...")
    persona = resolve_persona(state["raw_persona"], retriever_module)
    return {"persona": persona}


# ── Node 2: Retrieve context ──────────────────────────────────────────────────
def retrieve_context_node(state: SimulatorState) -> dict:
    print("🔍 Retrieving context...")
    persona = state["persona"]
    item    = state["raw_item"]

    # Extract city from item OR from the full description
    city = item.get("city")
    if not city or city == "Lagos":
        description = state["raw_persona"].get("description", "")
        item_name   = item.get("name", "")
        full_text   = f"{description} {item_name}".lower()

        city_map = {
            "abuja": "Abuja", "wuse": "Abuja", "maitama": "Abuja",
            "garki": "Abuja", "asokoro": "Abuja",
            "port harcourt": "Port Harcourt", "ph": "Port Harcourt",
            "ibadan": "Ibadan", "bodija": "Ibadan",
            "kano": "Kano", "sabon gari": "Kano",
            "lekki": "Lagos", "vi": "Lagos", "victoria island": "Lagos",
            "ikeja": "Lagos", "surulere": "Lagos", "yaba": "Lagos",
            "ikoyi": "Lagos", "ajah": "Lagos"
        }

        detected = None
        for keyword, mapped_city in city_map.items():
            if keyword in full_text:
                detected = mapped_city
                break

        city = detected or item.get("city", "Lagos")

    # Rest of the function
    user_reviews = get_user_reviews(
        user_id=persona.get("user_id", ""),
        query=f"{item.get('name', '')} {item.get('categories', '')}",
        k=5
    )

    cultural_context   = build_cultural_context(
        city=city,
        categories=item.get("categories", ""),
        persona_top_categories=persona.get("top_categories", [])
    )

    style_instructions = get_style_instructions(
        tone_tags=persona.get("tone_tags", []),
        avg_review_length=persona.get("avg_review_length", 80)
    )

    return {
        "user_reviews":       user_reviews,
        "cultural_context":   cultural_context,
        "style_instructions": style_instructions,
        "resolved_city":      city    # pass city forward to generate node
    }


# ── Node 3: Generate review ───────────────────────────────────────────────────
def generate_review_node(state: SimulatorState) -> dict:
    print("✍️  Generating review...")
    persona     = state["persona"]
    item        = state["raw_item"]
    reviews     = state["user_reviews"]
    city        = state.get("resolved_city", "Lagos")
    description = state["raw_persona"].get("description", "")

    # Determine how Nigerian to be
    from core.naija_layer import get_naija_tone_level
    tone_level  = get_naija_tone_level(description)

    tone_instruction = {
        "full":     "Write in natural Nigerian English with Pidgin where it fits naturally.",
        "moderate": "Write in Nigerian English with occasional Nigerian expressions.",
        "subtle":   "Write in clean English. Only use very light Nigerian phrasing if it fits."
    }[tone_level]

    examples = ""
    if reviews:
        examples = "\n\nReal examples of how this user writes:\n"
        for i, r in enumerate(reviews[:3], 1):
            examples += f"{i}. ({r['stars']}★) \"{r['text'][:200]}\"\n"

    prompt = f"""You are simulating a review written by a specific user.

USER BEHAVIORAL PROFILE:
- Average rating: {persona['avg_rating']} stars
- Writing style: {state['style_instructions']}
- Frequently visits: {', '.join(persona.get('top_categories', [])[:3])}

LANGUAGE TONE: {tone_instruction}

LOCATION CONTEXT: {state['cultural_context']}
IMPORTANT: This business is located in {city}. 
Do not reference any other city. All location context must be specific to {city}.

CUISINE/CATEGORY: {item.get('categories', 'Restaurant')}
Write your review referencing the actual type of food/service this place offers.
Do not substitute with unrelated cuisine types.

WRITING LENGTH: {state['style_instructions']}
You MUST respect the review length stated above. If it says 30 words, write 30 words maximum.
{examples}

ITEM BEING REVIEWED:
Name: {item.get('name', '')}
Categories: {item.get('categories', '')}
City: {city}

Respond ONLY in this JSON format:
{{
    "rating": <integer 1-5>,
    "review_text": "<the simulated review>",
    "reasoning_trace": "<why this rating and tone based on the profile>"
}}"""

    response = llm.invoke([
        SystemMessage(content=NAIJA_SYSTEM_PROMPT),
        HumanMessage(content=prompt)
    ])
    return {"raw_response": response.content}


# ── Node 4: Parse output ──────────────────────────────────────────────────────
def parse_output_node(state: SimulatorState) -> dict:
    print("Parsing output...")
    raw = state.get("raw_response", "")

    try:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return {
                "rating":          int(data.get("rating", 3)),
                "review_text":     data.get("review_text", ""),
                "reasoning_trace": data.get("reasoning_trace", "")
            }
    except Exception:
        pass

    # Fallback if JSON parsing fails
    return {
        "rating":          3,
        "review_text":     raw,
        "reasoning_trace": "Could not parse structured output"
    }


# ── Build graph ───────────────────────────────────────────────────────────────
def build_simulator_graph():
    graph = StateGraph(SimulatorState)

    graph.add_node("parse_persona",     parse_persona_node)
    graph.add_node("retrieve_context",  retrieve_context_node)
    graph.add_node("generate_review",   generate_review_node)
    graph.add_node("parse_output",      parse_output_node)

    graph.set_entry_point("parse_persona")
    graph.add_edge("parse_persona",    "retrieve_context")
    graph.add_edge("retrieve_context", "generate_review")
    graph.add_edge("generate_review",  "parse_output")
    graph.add_edge("parse_output",     END)

    return graph.compile()


# Singleton — compiled once, reused on every request
_graph = None

def get_graph():
    global _graph
    if _graph is None:
        _graph = build_simulator_graph()
    return _graph


# ── Public API — called by FastAPI ────────────────────────────────────────────
def simulate_review(request: SimulateReviewRequest) -> SimulateReviewResponse:
    graph  = get_graph()
    result = graph.invoke({
        "raw_persona": request.user_persona.model_dump(),
        "raw_item":    request.item.model_dump(),
        "raw_context": request.context.model_dump() if request.context else {}
    })

    return SimulateReviewResponse(
        rating=result["rating"],
        review_text=result["review_text"],
        reasoning_trace=result["reasoning_trace"]
    )