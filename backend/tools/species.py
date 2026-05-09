"""
backend/tools/species.py

Species Tool for NoFishyBusiness.

Provides fish care sheet information by combining RAG retrieval from the
local knowledge base with an OpenAI LLM call to produce a structured
species response.

Requirements: 4.1, 4.2, 4.3, 4.5, 11.1, 11.3, 11.4
"""

import json

import openai
from fastapi.responses import JSONResponse

from backend import logger, token_budget
from backend.rag import RAGError, retrieve


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
# System prompt template
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT_TEMPLATE = """\
You are an expert aquarium care assistant. Using ONLY the information provided
in the context below, return a JSON object describing the requested fish species.

Context:
{context}

Return ONLY valid JSON matching this exact schema (no markdown, no extra text):
{{
  "species_name": "<string>",
  "behavior": "<string>",
  "compatible_tank_mates": ["<string>", ...],
  "temperature_f": {{"min": <float>, "max": <float>}},
  "ph": {{"min": <float>, "max": <float>}},
  "hardness_dgh": {{"min": <float>, "max": <float>}},
  "min_tank_gallons": <int>,
  "difficulty": "easy" | "moderate" | "advanced",
  "maintenance_notes": "<string>"
}}
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_species_info(species_name: str) -> dict | JSONResponse:
    """Return a structured care sheet for the requested fish species.

    Flow:
      1. Call ``rag.retrieve(species_name)`` to fetch relevant KB records.
      2. If no records are found, return a 404 not-found response.
      3. If a RAGError occurs, return a 503 rag-error response.
      4. Truncate the concatenated context to 2000 tokens.
      5. Call OpenAI (gpt-4o-mini, max_tokens=1500) with the context.
      6. Parse the JSON response and return it.
      7. On any OpenAI error, log it and return a 502 api-error response.

    Args:
        species_name: The common or scientific name of the fish species.

    Returns:
        A dict with the structured species care sheet on success, or a
        :class:`fastapi.responses.JSONResponse` with an appropriate error
        status code and body on failure.
    """
    # 1. RAG retrieval --------------------------------------------------------
    try:
        records = retrieve(species_name)
    except RAGError as exc:
        logger.log_error("RAGError", str(exc))
        return JSONResponse(
            status_code=503,
            content={
                "message": f"Knowledge base unavailable: {exc}",
                "error_type": "rag_error",
            },
        )

    # 2. Not found ------------------------------------------------------------
    if not records:
        return JSONResponse(
            status_code=404,
            content={
                "message": f"No information found for species '{species_name}'.",
                "error_type": "not_found",
            },
        )

    # 3. Build and truncate context -------------------------------------------
    raw_context = "\n\n".join(record.content for record in records)
    context = token_budget.truncate_context(raw_context, 2000)

    system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(context=context)

    # 4. OpenAI call ----------------------------------------------------------
    try:
        response = _get_client().chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1500,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Provide the care sheet for: {species_name}",
                },
            ],
        )
    except openai.OpenAIError as exc:
        logger.log_error(type(exc).__name__, str(exc))
        return JSONResponse(
            status_code=502,
            content={
                "message": f"API error: {type(exc).__name__}",
                "error_type": "api_error",
            },
        )

    # 5. Log successful call --------------------------------------------------
    usage = response.usage
    if usage:
        logger.log_llm_call(
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
        )

    # 6. Parse and return the JSON response -----------------------------------
    raw_text = response.choices[0].message.content or ""

    # Strip markdown code fences if the model wraps the JSON
    stripped = raw_text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        # Remove opening fence (```json or ```) and closing fence (```)
        lines = lines[1:] if lines[0].startswith("```") else lines
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()

    try:
        return json.loads(stripped)
    except json.JSONDecodeError as exc:
        logger.log_error("JSONDecodeError", f"Failed to parse LLM response: {exc}")
        return JSONResponse(
            status_code=502,
            content={
                "message": "API error: invalid JSON in LLM response",
                "error_type": "api_error",
            },
        )
