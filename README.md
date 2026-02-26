# Contextual Post Explainer

An AI agent that explains social media posts by searching for and synthesizing relevant context. Paste a cryptic tweet, meme reference, or jargon-heavy post — get 3–5 clear bullet points with source citations.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                      │
│  PostInput → Loading skeleton → ExplanationCard + Sources    │
└────────────────────────┬─────────────────────────────────────┘
                         │ POST /api/explain
┌────────────────────────▼─────────────────────────────────────┐
│                   FastAPI Backend                             │
│                                                              │
│  Step 1: Analyzer ──── GPT-4o (+ Vision if image attached)   │
│       ↓                                                      │
│  Step 2: Query Generator ──── GPT-4o → 2-3 search queries   │
│       ↓                                                      │
│  Step 3: Context Search ──── Tavily Search API (advanced)    │
│       ↓                                                      │
│  Step 4: Reranker ──── text-embedding-3-small + cosine sim   │
│       ↓                                                      │
│  Step 5: Synthesizer ──── GPT-4o → 3-5 cited bullets         │
└──────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key
- Tavily API key ([free tier](https://tavily.com))

### 1. Clone and configure

```bash
git clone <repo-url>
cd RapidCanvas
cp .env.example .env
# Edit .env with your API keys
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`. Check health at `/api/health`.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The Vite dev server proxies `/api/*` to the backend.

### 4. Run evaluation

```bash
cd backend
python -m app.eval.harness              # all 12 test posts
python -m app.eval.harness --post-id ralph-wiggum  # single post
```

Results are saved to `backend/app/eval/eval_results.json`.

## API

### `POST /api/explain`

**Request:**
```json
{
  "post_text": "just mass deployed the ralph wiggum technique across all our repos",
  "post_image_url": null
}
```

**Response:**
```json
{
  "bullets": [
    "The \"Ralph Wiggum technique\" is a method for running AI coding agents in a bash loop... [Source](https://example.com)",
    "..."
  ],
  "sources": [
    { "title": "Article Title", "url": "https://example.com" }
  ],
  "metadata": {
    "search_queries": ["ralph wiggum technique AI coding", "..."],
    "model": "gpt-4o",
    "total_results_found": 18,
    "results_after_rerank": 8
  }
}
```

## Agent Pipeline

### Step 1 — Post Analysis

Sends the post (and optional image) to GPT-4o to extract entities, slang, cultural references, and ambiguities. When an image is attached, GPT-4o Vision reads text from screenshots, identifies memes, and describes visual content — all fed into downstream steps.

### Step 2 — Query Generation

Generates 2–3 diverse search queries from the analysis. Each query targets a different aspect (specific reference, broader topic, recent event) to avoid single-query blindspots.

### Step 3 — Context Search

Executes queries against [Tavily Search API](https://tavily.com) with `search_depth="advanced"`. Tavily returns structured results with titles, URLs, and content snippets — ideal for citation tracking. Results are deduplicated by URL across queries.

### Step 4 — Embedding Reranker (ML module)

Computes `text-embedding-3-small` embeddings for the post and each search result. Ranks by cosine similarity, keeps the top 8. This filters noise from broad queries while capturing semantic relevance that keyword matching misses (important for slang and cultural references).

### Step 5 — Synthesis

Sends the post + top-K context to GPT-4o with a structured prompt enforcing:
- 3–5 bullet points
- Inline markdown citations `[source](url)` in every bullet
- Factual grounding — claims must be supported by retrieved sources

## Evaluation Harness

### Test Suite

12 diverse test posts in [`backend/app/eval/test_posts.json`](backend/app/eval/test_posts.json) covering:

| Category | Example |
|---|---|
| Internet culture | "Ralph Wiggum technique", "enshittification", "dead internet theory" |
| Tech jargon | "vibe coding", "strawberry test", AI hallucination |
| Current events | Devin AI, fediverse migration, GPT-4o multimodal |
| Slang/memes | Twitter ratio language, sigma grindset, "AI slop" |

### Scoring Metrics

1. **Topic Coverage** — Fraction of expected topics found in output (substring/fuzzy match)
2. **LLM-as-Judge** — GPT-4o scores the output on four dimensions (1–5 each):
   - Factual accuracy
   - Relevance
   - Completeness
   - Citation quality
3. **Bullet Count** — Verifies output has 3–5 bullets
4. **Citation Check** — Ratio of bullets containing markdown citation links
5. **Aggregate Score** — Weighted average of all metrics (0–100 scale)

### Why LLM-as-Judge?

Social media explanations are open-ended — exact-match metrics don't work. LLM-as-judge is the standard evaluation approach for free-form text generation, supplemented by heuristic checks (topic coverage, bullet count, citation presence) that catch structural failures the LLM might miss.

## Key Design Decisions

| Decision | Rationale |
|---|---|
| **Tavily over raw Google** | Returns clean extracted text, purpose-built for RAG/agents, avoids HTML parsing |
| **Multi-query strategy** | 2–3 queries cover different post aspects, reducing missed context |
| **Embedding reranker over LLM reranker** | 100x cheaper and faster than an LLM reranking call; sufficient for filtering ~20 results to 8 |
| **GPT-4o for vision + text** | Single model handles the full pipeline; vision used only when image is present |
| **Structured JSON output** | All LLM calls use `response_format=json_object` for reliable parsing |
| **Separate eval from app** | Eval harness runs the same pipeline as the API, ensuring production parity |

## Assumptions

- Posts are in English
- The agent does not fetch the original social media post from a URL — it works with pasted text (and optional images)
- Image understanding relies on base64 data URLs from the frontend file picker
- Tavily's free tier (1000 searches/month) is sufficient for development and evaluation
- The evaluation LLM judge uses the same model as the agent (GPT-4o) — in production you'd want a separate judge model

## Project Structure

```
├── frontend/                    # React (Vite + TypeScript + Tailwind)
│   ├── src/
│   │   ├── components/
│   │   │   ├── PostInput.tsx    # Text area + image upload
│   │   │   └── ExplanationCard.tsx  # Bullets + sources + metadata
│   │   ├── api/client.ts        # API client
│   │   └── App.tsx
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Settings from .env
│   │   ├── agent/
│   │   │   ├── pipeline.py      # 5-step orchestrator
│   │   │   ├── analyzer.py      # Step 1: post analysis + vision
│   │   │   ├── query_gen.py     # Step 2: search query generation
│   │   │   ├── search.py        # Step 3: Tavily search
│   │   │   ├── reranker.py      # Step 4: embedding reranking
│   │   │   └── synthesizer.py   # Step 5: cited bullet synthesis
│   │   ├── models/schemas.py    # Pydantic models
│   │   └── eval/
│   │       ├── harness.py       # CLI evaluation runner
│   │       ├── metrics.py       # Scoring functions
│   │       └── test_posts.json  # 12 test cases
│   └── requirements.txt
├── .env.example
└── README.md
```
