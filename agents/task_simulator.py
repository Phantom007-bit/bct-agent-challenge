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
    print("Retrieving user history and building context...")
    persona = state["persona"]
    item    = state["raw_item"]

    # Get past reviews most similar to this item type
    user_reviews = get_user_reviews(
        user_id=persona.get("user_id", ""),
        query=f"{item.get('name', '')} {item.get('categories', '')}",
        k=5
    )

    cultural_context   = build_cultural_context(
        city=item.get("city", "Lagos"),
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
        "style_instructions": style_instructions
    }


# ── Node 3: Generate review ───────────────────────────────────────────────────
def generate_review_node(state: SimulatorState) -> dict:
    print("Generating simulated review...")
    persona = state["persona"]
    item    = state["raw_item"]
    reviews = state["user_reviews"]

    # Format past reviews as writing examples for the LLM
    examples = ""
    if reviews:
        examples = "\n\nReal examples of how this user writes:\n"
        for i, r in enumerate(reviews[:3], 1):
            examples += f"{i}. ({r['stars']}★) \"{r['text'][:200]}\"\n"

    prompt = f"""You are simulating a product/restaurant review written by a specific Nigerian user.
USER BEHAVIORAL PROFILE:
- Average rating they give: {persona['avg_rating']} stars
- Writing style: {state['style_instructions']}
- Categories they frequent: {', '.join(persona.get('top_categories', [])[:3])}
- Is cold start (new user): {persona.get('is_cold_start', False)}

{state['cultural_context']}
{examples}

ITEM BEING REVIEWED:
Name: {item.get('name', '')}
Categories: {item.get('categories', '')}
City: {item.get('city', 'Lagos')}

TASK:
Simulate exactly what this user would write if they visited this place.
Capture their tone, their rating tendency, and their cultural voice.

Respond in this exact JSON format — nothing else:
{{
    "rating": <integer 1-5>,
    "review_text": "<the full simulated review>",
    "reasoning_trace": "<why you chose this rating and tone based on their profile>"
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