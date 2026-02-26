"""Step 1: Analyze a social media post to extract entities, references, and context."""

from openai import AsyncOpenAI

from app.config import get_settings

ANALYSIS_PROMPT = """\
You are analyzing a social media post to prepare for a contextual search.
Extract the following from the post:

1. **Key entities**: Named people, projects, companies, events, technologies
2. **References & slang**: Internet culture references, memes, abbreviations, jargon
3. **Core topic**: What is this post fundamentally about?
4. **Ambiguities**: What parts of this post would confuse someone without context?

Respond in JSON with keys: entities, references, core_topic, ambiguities, summary.
Keep the summary to 1-2 sentences.
"""


async def analyze_post(
    post_text: str, image_url: str | None = None
) -> dict:
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    messages: list[dict] = [{"role": "system", "content": ANALYSIS_PROMPT}]

    user_content: list[dict] = [{"type": "text", "text": post_text}]
    if image_url:
        user_content.append(
            {"type": "image_url", "image_url": {"url": image_url, "detail": "high"}}
        )

    messages.append({"role": "user", "content": user_content})

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.2,
    )

    import json

    raw = response.choices[0].message.content or "{}"
    return json.loads(raw)
