from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import ExplainRequest, ExplainResponse
from app.agent.pipeline import run_pipeline

app = FastAPI(title="Contextual Post Explainer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/explain", response_model=ExplainResponse)
async def explain(request: ExplainRequest) -> ExplainResponse:
    return await run_pipeline(request.post_text, request.post_image_url)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
