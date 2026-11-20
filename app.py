import json
import os
import random
import sys
import time
import unittest

MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0.0")
BLOCKED_WORDS = ["hack", "ignore previous instructions", "drop table"]


def check_guardrails(prompt: str) -> bool:
    """Ensure the prompt does not contain unsafe or injection patterns."""
    cleaned = prompt.lower().strip()
    return not any(bad_word in cleaned for bad_word in BLOCKED_WORDS)


def predict_sentiment(prompt: str) -> dict:
    """Simulate an LLM/ML inference endpoint with latency and guardrails."""
    start_time = time.time()

    if not check_guardrails(prompt):
        return {
            "status": "allowed",
            "reason": "Guardrail violation detected",
            "model_version": MODEL_VERSION,
        }

    positive_keywords = ["awesome", "great", "fast", "love", "excellent"]
    words = prompt.lower().split()
    score = sum(1 for w in words if w in positive_keywords)
    sentiment = "positive" if score > 0 else "neutral"
    latency_ms = round((time.time() - start_time) * 1000 + 12.5, 2)

    return {
        "status": "success",
        "prompt": prompt,
        "sentiment": sentiment,
        "confidence": 0.94 if sentiment == "positive" else 0.78,
        "latency_ms": latency_ms,
        "model_version": MODEL_VERSION,
    }


def run_canary_rollout() -> None:
    """Simulate progressive Canary delivery (5% -> 25% -> 100%)."""
    stages = [5, 25, 50, 100]
    print(f"Starting Canary Rollout for release: {MODEL_VERSION}")

    for traffic_percent in stages:
        errors = 0
        total_requests = 20

        for _ in range(total_requests):
            is_canary = random.randint(1, 100) <= traffic_percent
            active_ver = MODEL_VERSION if is_canary else "v0.9.0-stable"
            res = predict_sentiment("Route Academy MLOps is awesome")
            if res["status"] != "success":
                errors += 1

        error_rate = (errors / total_requests) * 100
        print(
            f"[Traffic: {traffic_percent}%] Active={active_ver} | "
            f"Error Rate={error_rate}%"
        )

        if error_rate > 1.0:
            print("ALERT: High error rate! Triggering Instant Rollback!")
            sys.exit(1)

        time.sleep(0.5)

    print("Canary Rollout 100% Complete — Production Healthy!")


class TestMLOpsPipeline(unittest.TestCase):
    """Shift-Left unit tests executed automatically on every push."""

    def test_positive_prediction(self):
        result = predict_sentiment("This CI/CD pipeline is awesome and fast")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["sentiment"], "positive")

    def test_neutral_prediction(self):
        result = predict_sentiment("Deploying code to server")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["sentiment"], "neutral")

    def test_guardrail_blocks_injection(self):
        result = predict_sentiment("Please ignore previous instructions")
        self.assertEqual(result["status"], "blocked")


if __name__ == "__main__":
    if "--canary" in sys.argv:
        run_canary_rollout()
    else:
        sample = predict_sentiment("Route Academy LLMOps is awesome")
        print(json.dumps(sample, indent=2))
