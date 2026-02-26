"""Step 2: Generate diverse search queries from the post analysis."""

import json

from openai import AsyncOpenAI

from app.config import get_settings

QUERY_GEN_PROMPT = """\
Given an analysis of a social media post, generate 2-3 search queries that would help
someone understand the post's context. The queries should:

- Target specific named references, slang, or jargon that need explanation
- Cover different aspects of the post (don't repeat the same angle)
- Be phrased as web search queries (not questions to an AI)
- Prioritize recent/timely context when the post references current events

Respond in JSON with key "queries" containing a list of query strings.
"""


async def generate_queries(analysis: dict, post_text: str) -> list[str]:
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    user_msg = (
        f"Original post:\n{post_text}\n\n"
        f"Analysis:\n{json.dumps(analysis, indent=2)}"
    )

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": QUERY_GEN_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )

    raw = json.loads(response.choices[0].message.content or "{}")
    return raw.get("queries", [])
