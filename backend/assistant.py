"""
backend/assistant.py

AI Assistant for NoFishyBusiness.

Provides a free-form conversational interface with session memory, RAG
retrieval, and topic filtering.

Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 10.4, 11.1, 11.2
"""

import openai

from backend import logger, token_budget
from backend.rag import RAGError, retrieve
from backend.topic_guard import check_topic

# ---------------------------------------------------------------------------
# OpenAI client — lazy singleton (reads OPENAI_API_KEY from environment)
# ---------------------------------------------------------------------------

_client: openai.OpenAI | None = None


def _get_client() -> openai.OpenAI:
    """Return the shared OpenAI client, creating it on first use."""
    global _client
    if _client is None:
        _client = openai.OpenAI()
    return _client

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_INSUFFICIENT_INFO_REPLY = (
    "I don't have sufficient information on that topic in my knowledge base. "
    "Please try asking about a specific fish species, water chemistry, or tank maintenance."
)

_UNAVAILABLE_REPLY = (
    "The assistant is temporarily unavailable. Please try again later."
)

_AMBIGUOUS_SYSTEM_INSTRUCTION = (
    "The user's question may contain off-topic elements. "
    "Answer ONLY if the question is aquarium-related. "
    "If it is not aquarium-related, politely decline and redirect to aquarium topics."
)

# App sections the LLM can suggest
_SECTIONS = (
    "Volume Calculator, Species Tool, Maintenance Guide, "
    "Setup Guide, Chemistry Analyzer, Image Scanner"
)

_SYSTEM_PROMPT_TEMPLATE = """\
You are a knowledgeable aquarium care assistant for the NoFishyBusiness app.
Answer the user's question using ONLY the information provided in the context below.
Be concise, accurate, and helpful.

If the answer relates to a specific feature of this app, include a "suggested_section"
field in your response naming the most relevant section from this list:
{sections}

Context:
{context}

{ambiguous_instruction}
Respond with a JSON object in this exact format (no markdown, no extra text):
{{
  "reply": "<your answer as a string>",
  "suggested_section": "<section name or null>"
}}
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_assistant_reply(message: str, history: list[dict]) -> dict:
    """Generate an AI assistant reply for the given message and conversation history.

    Flow:
    1. Run ``topic_guard.check_topic(message)``; return refusal if refused.
    2. Call ``rag.retrieve(message)`` for context; return "insufficient
        information" message if no records are found.
    3. Truncate context via ``token_budget.truncate_context(context, 2000)``.
    4. Build the messages array: prepend the last 10 history items, then
        add the system message and the current user message.
    5. Call OpenAI with ``max_tokens=1500``; parse ``reply`` and
        ``suggested_section`` from the response.
    6. On any OpenAI error, log it and return the "temporarily unavailable"
        message.

    Args:
        message: The user's current message.
        history: Conversation history as a list of ``{"role": ..., "content": ...}``
                dicts. The backend uses the last 10 items (5 pairs).

    Returns:
        A dict with keys ``"reply"`` (str) and ``"suggested_section"`` (str | None).
    """
    # 1. Topic guard ----------------------------------------------------------
    topic_result = check_topic(message)

    if topic_result.status == "refused":
        logger.log_error("TopicRefused", f"Query refused by topic guard: {message!r}")
        return {"reply": topic_result.message, "suggested_section": None}

    # "error" status means the DB was unavailable — treat as ambiguous and
    # forward to LLM with a cautious system instruction rather than hard-failing.
    ambiguous_instruction = ""
    if topic_result.status in ("ambiguous", "error"):
        ambiguous_instruction = _AMBIGUOUS_SYSTEM_INSTRUCTION

    # 2. RAG retrieval --------------------------------------------------------
    # Extract meaningful keywords from the message for better FTS5 matching.
    # Common stop words like "tell", "me", "about", "what", "how" don't exist
    # in the knowledge base and cause FTS5 to return zero results.
    _STOP_WORDS = {
        "tell", "me", "about", "what", "how", "is", "are", "the", "a", "an",
        "do", "does", "can", "could", "would", "should", "will", "my", "your",
        "for", "to", "in", "of", "and", "or", "with", "on", "at", "by",
        "good", "best", "need", "want", "like", "get", "have", "has", "had",
        "some", "any", "all", "this", "that", "these", "those", "it", "its",
        "please", "help", "give", "show", "explain", "describe", "list",
    }
    import re as _re
    words = _re.findall(r"[a-z0-9]+", message.lower())
    keywords = [w for w in words if w not in _STOP_WORDS and len(w) > 2]
    rag_query = " ".join(keywords) if keywords else message

    try:
        records = retrieve(rag_query)
        # If keyword query returns nothing, fall back to the full message
        if not records and rag_query != message:
            records = retrieve(message)
    except RAGError as exc:
        logger.log_error("RAGError", str(exc))
        return {
            "reply": _INSUFFICIENT_INFO_REPLY,
            "suggested_section": None,
        }

    if not records:
        return {
            "reply": _INSUFFICIENT_INFO_REPLY,
            "suggested_section": None,
        }

    # 3. Build and truncate context -------------------------------------------
    raw_context = "\n\n".join(record.content for record in records)
    context = token_budget.truncate_context(raw_context, 2000)

    system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(
        sections=_SECTIONS,
        context=context,
        ambiguous_instruction=ambiguous_instruction,
    )

    # 4. Build messages array -------------------------------------------------
    # Prepend the last 10 history items (= 5 user/assistant pairs) before the
    # system message so the LLM has conversation context.
    recent_history = history[-10:] if len(history) > 10 else history

    messages = (
        recent_history
        + [{"role": "system", "content": system_prompt}]
        + [{"role": "user", "content": message}]
    )

    # 5. OpenAI call ----------------------------------------------------------
    try:
        response = _get_client().chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1500,
            messages=messages,
        )
    except openai.OpenAIError as exc:
        logger.log_error(type(exc).__name__, str(exc))
        return {"reply": _UNAVAILABLE_REPLY, "suggested_section": None}

    # 6. Log successful call --------------------------------------------------
    usage = response.usage
    if usage:
        logger.log_llm_call(
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
        )

    # 7. Parse and return the response ----------------------------------------
    raw_text = response.choices[0].message.content or ""

    # Strip markdown code fences if the model wraps the JSON
    stripped = raw_text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        lines = lines[1:] if lines[0].startswith("```") else lines
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()

    try:
        import json
        parsed = json.loads(stripped)
        return {
            "reply": str(parsed.get("reply", "")),
            "suggested_section": parsed.get("suggested_section") or None,
        }
    except (json.JSONDecodeError, AttributeError) as exc:
        logger.log_error("JSONDecodeError", f"Failed to parse LLM response: {exc}")
        # Fall back to returning the raw text as the reply
        return {"reply": raw_text.strip(), "suggested_section": None}
