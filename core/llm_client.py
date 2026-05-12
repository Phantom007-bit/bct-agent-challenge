import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL   = "claude-sonnet-4-6"

def generate(messages: list, system: str = "", max_tokens: int = 1000) -> str:
    """
    Single entry point for all LLM calls.
    
    messages: list of {"role": "user"/"assistant", "content": "..."}
    system:   system prompt (optional)
    returns:  response text as string
    """
    response = _client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=messages
    )
    return response.content[0].text