#!/usr/bin/env python3
"""
eval/eval.py
─────────────────────────────────────────────────────────────────────────────
Evaluation runner for NoFishyBusiness.

Reads labeled test cases from eval/test_cases.json, sends each one to the
running backend, and checks whether the response contains (or doesn't contain)
an expected keyword.

Usage:
    python eval/eval.py
    python eval/eval.py --backend-url http://localhost:8000

Exit codes:
    0 — all tests passed
    1 — one or more tests failed, or backend unreachable
─────────────────────────────────────────────────────────────────────────────
"""

import json      # For loading test_cases.json and serialising responses
import os        # For building the path to test_cases.json
import sys       # For sys.exit() with a non-zero code on failure
import argparse  # For the optional --backend-url command-line argument

import requests  # HTTP library for calling the backend endpoints

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

# Default backend URL — can be overridden with --backend-url
DEFAULT_BACKEND_URL = "http://localhost:8000"

# Absolute path to the test cases file, relative to this script's directory
TEST_CASES_PATH = os.path.join(os.path.dirname(__file__), "test_cases.json")


# ─────────────────────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────────────────────

def check_health(backend_url: str) -> bool:
    """
    Ping the backend's /health endpoint to confirm it is running.

    Returns True if the server responds with a 2xx status, False otherwise.
    A RequestException (connection refused, timeout, etc.) also returns False.
    """
    try:
        resp = requests.get(f"{backend_url}/health", timeout=5)
        return resp.ok   # True for 2xx status codes
    except requests.RequestException:
        return False   # Server not reachable


def run_test_case(backend_url: str, case: dict) -> tuple[bool, str]:
    """
    Execute a single test case and return (passed, reason).

    Each test case dict has:
        endpoint            — URL path, e.g. "/species"
        method              — "GET" or "POST" (default "POST")
        input               — JSON payload for POST requests (None for GET)
        assert_keyword      — string that MUST appear in the response body
        assert_absent_keyword — string that must NOT appear in the response body

    Returns:
        (True, "OK")                    — test passed
        (False, "<reason string>")      — test failed with explanation
    """
    # Extract fields from the test case dict
    endpoint             = case["endpoint"]
    method               = case.get("method", "POST").upper()
    payload              = case.get("input")           # None for GET requests
    assert_keyword       = case.get("assert_keyword")
    assert_absent_keyword = case.get("assert_absent_keyword")

    # ── Send the HTTP request ─────────────────────────────────────────────
    try:
        if method == "GET":
            # GET requests have no body — used for /health
            resp = requests.get(f"{backend_url}{endpoint}", timeout=30)
        else:
            # POST requests send the payload as JSON
            resp = requests.post(f"{backend_url}{endpoint}", json=payload, timeout=60)
    except requests.RequestException as exc:
        # Network error — backend may have crashed or timed out
        return False, f"Request failed: {exc}"

    # ── Serialise the response body for keyword searching ─────────────────
    try:
        body     = resp.json()          # Parse JSON response
        body_str = json.dumps(body)     # Re-serialise to a flat string for searching
    except Exception:
        body_str = resp.text            # Fall back to raw text if not valid JSON

    # ── Keyword assertions ────────────────────────────────────────────────
    # Check that the expected keyword IS present
    if assert_keyword and assert_keyword not in body_str:
        return False, f"Expected keyword '{assert_keyword}' not found in response"

    # Check that the forbidden keyword is NOT present
    if assert_absent_keyword and assert_absent_keyword in body_str:
        return False, f"Absent keyword '{assert_absent_keyword}' was found in response"

    return True, "OK"   # All assertions passed


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    # ── Parse command-line arguments ──────────────────────────────────────
    parser = argparse.ArgumentParser(description="NoFishyBusiness evaluation runner")
    parser.add_argument(
        "--backend-url",
        default=DEFAULT_BACKEND_URL,
        help=f"Backend URL (default: {DEFAULT_BACKEND_URL})",
    )
    args = parser.parse_args()
    backend_url = args.backend_url.rstrip("/")   # Remove trailing slash if present

    # ── Step 1: Health check ──────────────────────────────────────────────
    # Abort immediately if the backend isn't running — no point running tests
    print(f"Checking backend at {backend_url}/health ...")
    if not check_health(backend_url):
        print(
            f"ERROR: Backend could not be reached at {backend_url}. "
            "Please start the backend before running the evaluation."
        )
        sys.exit(1)   # Non-zero exit signals failure to any CI system
    print("Backend is reachable.\n")

    # ── Step 2: Load test cases ───────────────────────────────────────────
    try:
        with open(TEST_CASES_PATH, "r", encoding="utf-8") as fh:
            test_cases = json.load(fh)   # Parse the JSON array of test case dicts
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"ERROR: Could not load test cases from {TEST_CASES_PATH}: {exc}")
        sys.exit(1)

    # ── Step 3: Run each test case ────────────────────────────────────────
    passed = 0              # Counter for passing tests
    total  = len(test_cases)

    for case in test_cases:
        test_name = case.get("test_name", "unnamed")
        label     = case.get("expected_label", "")

        ok, reason = run_test_case(backend_url, case)   # Execute the test

        # Print one line per test in the required format
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {test_name} ({label}): {reason}")

        if ok:
            passed += 1   # Increment pass counter

    # ── Step 4: Print summary ─────────────────────────────────────────────
    print(f"\nPassed: {passed} / Total: {total}")

    # Exit with code 1 if any test failed (signals failure to grading scripts)
    if passed < total:
        sys.exit(1)


# Only run main() when this script is executed directly (not imported)
if __name__ == "__main__":
    main()
