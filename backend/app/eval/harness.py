"""Evaluation harness: runs the agent pipeline on test posts and scores results."""

import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.agent.pipeline import run_pipeline
from app.eval.metrics import (
    check_bullet_count,
    check_citations,
    check_topic_coverage,
    compute_aggregate_score,
    llm_judge,
)


TEST_POSTS_PATH = Path(__file__).parent / "test_posts.json"
RESULTS_PATH = Path(__file__).parent / "eval_results.json"


def load_test_posts(post_id: str | None = None) -> list[dict]:
    with open(TEST_POSTS_PATH) as f:
        posts = json.load(f)
    if post_id:
        posts = [p for p in posts if p["id"] == post_id]
        if not posts:
            print(f"No test post found with id '{post_id}'")
            sys.exit(1)
    return posts


async def evaluate_single(post: dict) -> dict:
    print(f"\n{'='*60}")
    print(f"Evaluating: {post['id']} ({post['category']})")
    print(f"Post: {post['text'][:80]}...")

    start = time.time()
    try:
        response = await run_pipeline(post["text"], post.get("image_url"))
    except Exception as e:
        print(f"  PIPELINE ERROR: {e}")
        return {
            "id": post["id"],
            "error": str(e),
            "aggregate_score": 0,
        }
    elapsed = time.time() - start

    bullets = response.bullets

    bullet_check = check_bullet_count(bullets)
    topic_check = check_topic_coverage(bullets, post.get("expected_topics", []))
    citation_check = check_citations(bullets)

    print(f"  Bullets: {len(bullets)}")
    for i, b in enumerate(bullets):
        print(f"    {i+1}. {b[:100]}...")
    print(f"  Topic coverage: {topic_check['coverage']} (hits: {topic_check['hits']})")
    print(f"  Citations: {citation_check['bullets_with_citations']}/{citation_check['total_bullets']} bullets")

    print("  Running LLM judge...")
    judge_result = await llm_judge(
        post["text"],
        bullets,
        post.get("description", ""),
    )
    print(f"  Judge scores: acc={judge_result.get('factual_accuracy')}, "
          f"rel={judge_result.get('relevance')}, "
          f"comp={judge_result.get('completeness')}, "
          f"cite={judge_result.get('citation_quality')}")

    result = {
        "id": post["id"],
        "category": post["category"],
        "bullets": bullets,
        "sources": [s.model_dump() for s in response.sources],
        "metadata": response.metadata,
        "bullet_count": bullet_check,
        "topic_coverage": topic_check,
        "citations": citation_check,
        "llm_judge": judge_result,
        "elapsed_seconds": round(elapsed, 1),
    }
    result["aggregate_score"] = compute_aggregate_score(result)
    print(f"  Aggregate score: {result['aggregate_score']}/100 ({elapsed:.1f}s)")

    return result


async def run_evaluation(post_id: str | None = None):
    posts = load_test_posts(post_id)
    print(f"Running evaluation on {len(posts)} test post(s)...")

    results = []
    for post in posts:
        result = await evaluate_single(post)
        results.append(result)

    print(f"\n{'='*60}")
    print("EVALUATION SUMMARY")
    print(f"{'='*60}")
    print(f"{'ID':<25} {'Score':>6} {'Topics':>7} {'Cites':>6} {'Time':>6}")
    print(f"{'-'*25} {'-'*6} {'-'*7} {'-'*6} {'-'*6}")

    scores = []
    for r in results:
        if "error" in r:
            print(f"{r['id']:<25} {'ERROR':>6}")
            continue
        score = r["aggregate_score"]
        topics = r["topic_coverage"]["coverage"]
        cites = r["citations"]["citation_ratio"]
        elapsed = r["elapsed_seconds"]
        scores.append(score)
        print(f"{r['id']:<25} {score:>5.1f} {topics:>6.0%} {cites:>5.0%} {elapsed:>5.1f}s")

    if scores:
        avg = sum(scores) / len(scores)
        print(f"\nAverage score: {avg:.1f}/100 across {len(scores)} posts")

    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_PATH}")


def main():
    post_id = None
    args = sys.argv[1:]
    if "--post-id" in args:
        idx = args.index("--post-id")
        if idx + 1 < len(args):
            post_id = args[idx + 1]

    asyncio.run(run_evaluation(post_id))


if __name__ == "__main__":
    main()
