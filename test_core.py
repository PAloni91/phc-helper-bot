from knowledge import load_chunks, top_chunks
from llm import build_messages
from rate_limit import RateLimiter


def test_rate_limiter_blocks_then_recovers():
    now = [0.0]
    limiter = RateLimiter(2, 60, clock=lambda: now[0])
    assert limiter.allow(1) and limiter.allow(1)
    assert not limiter.allow(1)          # third call inside the window is blocked
    assert limiter.allow(2)              # other users are not affected
    now[0] = 61.0
    assert limiter.allow(1)              # window has passed


def test_retrieval_finds_ors():
    chunks = load_chunks("knowledge")
    best = top_chunks("How do I make ORS?", chunks, k=1)
    assert best and "ORS" in best[0]


def test_retrieval_empty_question_returns_nothing():
    assert top_chunks("the a is", load_chunks("knowledge")) == []


def test_build_messages_includes_context_and_question():
    msgs = build_messages("what is ors", ["ORS info"])
    assert msgs[0]["role"] == "system"
    assert "ORS info" in msgs[1]["content"] and "what is ors" in msgs[1]["content"]
