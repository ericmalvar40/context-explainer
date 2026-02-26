"""Step 4: Rerank search results using embedding similarity."""

import numpy as np
from openai import AsyncOpenAI

from app.config import get_settings
from app.agent.search import SearchResult


async def _get_embeddings(texts: list[str]) -> list[list[float]]:
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    response = await client.embeddings.create(
        model=settings.embedding_model,
        input=texts,
    )
    return [item.embedding for item in response.data]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    a_arr = np.array(a)
    b_arr = np.array(b)
    return float(np.dot(a_arr, b_arr) / (np.linalg.norm(a_arr) * np.linalg.norm(b_arr) + 1e-10))


async def rerank_results(
    post_text: str, results: list[SearchResult]
) -> list[SearchResult]:
    if not results:
        return []

    settings = get_settings()
    top_k = settings.reranker_top_k

    texts_to_embed = [post_text] + [r.content[:1000] for r in results]
    embeddings = await _get_embeddings(texts_to_embed)

    post_embedding = embeddings[0]
    result_embeddings = embeddings[1:]

    scored = []
    for result, emb in zip(results, result_embeddings):
        sim = _cosine_similarity(post_embedding, emb)
        scored.append((sim, result))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored[:top_k]]
