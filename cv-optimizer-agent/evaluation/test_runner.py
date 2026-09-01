"""
Evaluation Test Runner — measures agent accuracy vs human counselor baseline.
Usage: python -m evaluation.test_runner
"""
import json
from pathlib import Path

TEST_CASES_DIR = Path("data/test_cases")

def run_evaluation():
    """Run all test cases, compare agent output to human labels, print metrics."""
    # TODO: Step 1 — load ground_truth.json
    # TODO: Step 2 — for each CV run extract_text → detect_language → review_cv
    # TODO: Step 3 — compare tier_1 with human_tier_1 using fuzzy match
    # TODO: Step 4 — calculate precision, recall, F1
    # TODO: Step 5 — print summary table
    raise NotImplementedError("run_evaluation not implemented yet")

def calculate_metrics(agent_issues: list, human_issues: list) -> dict:
    """
    Precision = agent_correct / agent_total
    Recall    = agent_correct / human_total
    F1        = 2 * (P * R) / (P + R)
    """
    # TODO: implement fuzzy string matching for issue comparison
    raise NotImplementedError

if __name__ == "__main__":
    run_evaluation()
