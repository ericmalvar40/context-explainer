"""Step 3: Search for relevant context using Tavily."""

from dataclasses import dataclass

from tavily import AsyncTavilyClient

from app.config import get_settings


@dataclass
class SearchResult:
    title: str
    url: str
    content: str
    score: float


async def search_context(queries: list[str]) -> list[SearchResult]:
    settings = get_settings()
    client = AsyncTavilyClient(api_key=settings.tavily_api_key)

    all_results: list[SearchResult] = []
    seen_urls: set[str] = set()

    for query in queries:
        response = await client.search(
            query=query,
            search_depth="advanced",
            max_results=7,
        )

        for r in response.get("results", []):
            url = r.get("url", "")
            if url in seen_urls:
                continue
            seen_urls.add(url)
            all_results.append(
                SearchResult(
                    title=r.get("title", ""),
                    url=url,
                    content=r.get("content", ""),
                    score=r.get("score", 0.0),
                )
            )

    return all_results
