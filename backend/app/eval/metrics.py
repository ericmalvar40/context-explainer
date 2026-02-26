"""Evaluation metrics: heuristic checks and LLM-as-judge scoring."""

import json
import re

from openai import AsyncOpenAI

from app.config import get_settings

LLM_JUDGE_PROMPT = """\
You are evaluating an AI agent that explains social media posts. Given the original post,
the agent's bullet-point explanation, and a human-written description of what the post means,
score the agent's output on four dimensions.

Score each from 1-5:
- **factual_accuracy**: Are the claims in the bullets factually correct? (5 = all correct, 1 = mostly wrong)
- **relevance**: Do the bullets explain what the post is actually about? (5 = highly relevant, 1 = off-topic)
- **completeness**: Does the explanation cover all key aspects? (5 = comprehensive, 1 = misses most context)
- **citation_quality**: Are sources cited inline and do they support the claims? (5 = well-cited, 1 = no citations)

Respond in JSON with keys: factual_accuracy, relevance, completeness, citation_quality, reasoning.
"""


def check_bullet_count(bullets: list[str], min_count: int = 3, max_count: int = 5) -> dict:
    count = len(bullets)
    return {
        "pass": min_count <= count <= max_count,
        "bullet_count": count,
        "expected_range": f"{min_count}-{max_count}",
    }


def check_topic_coverage(bullets: list[str], expected_topics: list[str]) -> dict:
    text = " ".join(bullets).lower()
    hits = []
    misses = []
    for topic in expected_topics:
        if topic.lower() in text:
            hits.append(topic)
        else:
            misses.append(topic)
    coverage = len(hits) / len(expected_topics) if expected_topics else 0.0
    return {
        "coverage": round(coverage, 2),
        "hits": hits,
        "misses": misses,
    }


def check_citations(bullets: list[str]) -> dict:
    """Check that bullets contain markdown-style citations."""
    link_pattern = re.compile(r"\[([^\]]+)\]\((https?://[^\)]+)\)")
    bullets_with_citations = 0
    all_urls: list[str] = []

    for bullet in bullets:
        links = link_pattern.findall(bullet)
        if links:
            bullets_with_citations += 1
            all_urls.extend(url for _, url in links)

    return {
        "bullets_with_citations": bullets_with_citations,
        "total_bullets": len(bullets),
        "citation_ratio": round(bullets_with_citations / max(len(bullets), 1), 2),
        "unique_urls": list(set(all_urls)),
    }


async def llm_judge(
    post_text: str,
    bullets: list[str],
    reference_description: str,
) -> dict:
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    user_msg = (
        f"## Original post\n{post_text}\n\n"
        f"## Agent explanation\n" + "\n".join(f"- {b}" for b in bullets) + "\n\n"
        f"## Reference description\n{reference_description}"
    )

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": LLM_JUDGE_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )

    return json.loads(response.choices[0].message.content or "{}")


def compute_aggregate_score(result: dict) -> float:
    """Weighted average of all metric dimensions (0-100 scale)."""
    judge = result.get("llm_judge", {})
    topic = result.get("topic_coverage", {})
    citation = result.get("citations", {})
    bullet = result.get("bullet_count", {})

    scores = []

    for key in ["factual_accuracy", "relevance", "completeness", "citation_quality"]:
        val = judge.get(key)
        if isinstance(val, (int, float)):
            scores.append(val / 5.0 * 100)

    topic_score = topic.get("coverage", 0) * 100
    scores.append(topic_score)

    cite_score = citation.get("citation_ratio", 0) * 100
    scores.append(cite_score)

    if bullet.get("pass"):
        scores.append(100)
    else:
        scores.append(0)

    return round(sum(scores) / max(len(scores), 1), 1)
