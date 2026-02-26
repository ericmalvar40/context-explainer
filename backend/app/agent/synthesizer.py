"""Step 5: Synthesize search results into 3-5 cited bullet points."""

import json

from openai import AsyncOpenAI

from app.config import get_settings
from app.agent.search import SearchResult

SYNTHESIS_PROMPT = """\
You are an expert at explaining social media posts. Given a post and relevant context
from web searches, produce a clear explanation as 3-5 bullet points.

Rules:
- Each bullet should explain one aspect of the post that requires context.
- Ground every claim in the provided sources. Do NOT hallucinate facts.
- Include inline citations as markdown links: [source title](url).
- Write for someone who has no prior knowledge of the references in the post.
- Be concise but informative. Each bullet should be 1-2 sentences.
- If the post contains slang, memes, or cultural references, explain them.

Respond in JSON with keys:
- "bullets": list of strings (each is one bullet point with inline citations)
- "source_ids": list of integers (0-indexed) indicating which sources were actually used
"""


async def synthesize(
    post_text: str,
    results: list[SearchResult],
    analysis: dict,
) -> tuple[list[str], list[int]]:
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    context_block = "\n\n".join(
        f"[Source {i}] {r.title}\nURL: {r.url}\n{r.content[:1500]}"
        for i, r in enumerate(results)
    )

    user_msg = (
        f"## Post to explain\n{post_text}\n\n"
        f"## Post analysis\n{json.dumps(analysis, indent=2)}\n\n"
        f"## Search context\n{context_block}"
    )

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": SYNTHESIS_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )

    raw = json.loads(response.choices[0].message.content or "{}")
    bullets = raw.get("bullets", [])
    source_ids = raw.get("source_ids", list(range(len(results))))
    return bullets, source_ids
