"""Orchestrates the 5-step explanation pipeline."""

import logging

from app.models.schemas import ExplainResponse, Source
from app.agent.analyzer import analyze_post
from app.agent.query_gen import generate_queries
from app.agent.search import search_context
from app.agent.reranker import rerank_results
from app.agent.synthesizer import synthesize
from app.config import get_settings

logger = logging.getLogger(__name__)


async def run_pipeline(
    post_text: str, image_url: str | None = None
) -> ExplainResponse:
    settings = get_settings()

    # Step 1: Analyze
    logger.info("Step 1: Analyzing post")
    analysis = await analyze_post(post_text, image_url)

    # Step 2: Generate search queries
    logger.info("Step 2: Generating search queries")
    queries = await generate_queries(analysis, post_text)
    logger.info("Generated queries: %s", queries)

    # Step 3: Search
    logger.info("Step 3: Searching for context")
    raw_results = await search_context(queries)
    logger.info("Found %d raw results", len(raw_results))

    # Step 4: Rerank
    logger.info("Step 4: Reranking results")
    ranked_results = await rerank_results(post_text, raw_results)
    logger.info("Kept top %d results", len(ranked_results))

    # Step 5: Synthesize
    logger.info("Step 5: Synthesizing explanation")
    bullets, used_source_ids = await synthesize(post_text, ranked_results, analysis)

    sources = [
        Source(title=ranked_results[i].title, url=ranked_results[i].url)
        for i in used_source_ids
        if i < len(ranked_results)
    ]

    return ExplainResponse(
        bullets=bullets,
        sources=sources,
        metadata={
            "search_queries": queries,
            "model": settings.openai_model,
            "total_results_found": len(raw_results),
            "results_after_rerank": len(ranked_results),
        },
    )
