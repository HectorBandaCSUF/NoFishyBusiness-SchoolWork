#!/usr/bin/env python3
"""
eval/eval.py

Evaluation runner for NoFishyBusiness.

Usage:
    python eval/eval.py [--backend-url http://localhost:8000]

Reads test cases from eval/test_cases.json, runs each against the backend,
and prints pass/fail results.

Exit codes:
    0 — all tests passed
    1 — one or more tests failed, or backend unreachable
"""

import json
import os
import sys
import argparse

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_BACKEND_URL = "http://localhost:8000"
TEST_CASES_PATH = os.path.join(os.path.dirname(__file__), "test_cases.json")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def check_health(backend_url: str) -> bool:
    """Return True if the backend /health endpoint is reachable."""
    try:
        resp = requests.get(f"{backend_url}/health", timeout=5)
        return resp.ok
    except requests.RequestException:
        return False


def run_test_case(backend_url: str, case: dict) -> tuple[bool, str]:
    """
    Execute a single test case against the backend.

    Returns:
        (passed: bool, reason: str)
    """
    endpoint = case["endpoint"]
    method = case.get("method", "POST").upper()
    payload = case.get("input")
    assert_keyword = case.get("assert_keyword")
    assert_absent_keyword = case.get("assert_absent_keyword")

    try:
        if method == "GET":
            resp = requests.get(f"{backend_url}{endpoint}", timeout=30)
        else:
            resp = requests.post(f"{backend_url}{endpoint}", json=payload, timeout=60)
    except requests.RequestException as exc:
        return False, f"Request failed: {exc}"

    # Convert response to a string for keyword search
    try:
        body = resp.json()
        body_str = json.dumps(body)
    except Exception:
        body_str = resp.text

    # Check assert_keyword
    if assert_keyword and assert_keyword not in body_str:
        return False, f"Expected keyword '{assert_keyword}' not found in response"

    # Check assert_absent_keyword
    if assert_absent_keyword and assert_absent_keyword in body_str:
        return False, f"Absent keyword '{assert_absent_keyword}' was found in response"

    return True, "OK"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="NoFishyBusiness evaluation runner")
    parser.add_argument(
        "--backend-url",
        default=DEFAULT_BACKEND_URL,
        help=f"Backend URL (default: {DEFAULT_BACKEND_URL})",
    )
    args = parser.parse_args()
    backend_url = args.backend_url.rstrip("/")

    # 1. Health check
    print(f"Checking backend at {backend_url}/health ...")
    if not check_health(backend_url):
        print(f"ERROR: Backend could not be reached at {backend_url}. "
              "Please start the backend before running the evaluation.")
        sys.exit(1)
    print("Backend is reachable.\n")

    # 2. Load test cases
    try:
        with open(TEST_CASES_PATH, "r", encoding="utf-8") as fh:
            test_cases = json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"ERROR: Could not load test cases from {TEST_CASES_PATH}: {exc}")
        sys.exit(1)

    # 3. Run test cases
    passed = 0
    total = len(test_cases)

    for case in test_cases:
        test_name = case.get("test_name", "unnamed")
        label = case.get("expected_label", "")

        ok, reason = run_test_case(backend_url, case)

        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {test_name} ({label}): {reason}")

        if ok:
            passed += 1

    # 4. Summary
    print(f"\nPassed: {passed} / Total: {total}")

    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    main()
