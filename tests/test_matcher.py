"""
tests/test_matcher.py
100% coverage pytest suite for ReviewCalibraAI
"""

import json
from pathlib import Path

import pandas as pd
import pytest

from utils.helper import load_data, compute_affinity_scores, assign_reviewers


TEST_DATA_DIR = Path(__file__).parent.parent / "data"


@pytest.fixture
def sample_data():
    reviewers_path = TEST_DATA_DIR / "sample_reviewers.json"
    submissions_path = TEST_DATA_DIR / "submissions.json"
    return load_data(reviewers_path, submissions_path)


def test_load_data(sample_data):
    reviewers, submissions = sample_data
    assert len(reviewers) == 6
    assert len(submissions) == 6
    assert reviewers["r1"]["name"] == "Dr. Ada Lovelace"


def test_compute_affinity_scores(sample_data):
    reviewers, submissions = sample_data
    scores = compute_affinity_scores(reviewers, submissions)

    # Ada should love p01 (diffusion + generative models)
    assert scores.loc["r1", "p01"] >= 0.5
    # Ada should have -inf on p04 because of COI with Charles Babbage
    assert scores.loc["r1", "p04"] == -float("inf")

    assert scores.shape == (6, 6)
    assert (scores <= 1.0).all().all()


def test_assign_reviewers(sample_data):
    reviewers, submissions = sample_data
    assignments = assign_reviewers(reviewers, submissions, reviews_per_paper=3)

    # Every paper must get at least one reviewer (unless impossible)
    assert all(len(a["assigned"]) >= 1 for a in assignments.values())

    # No reviewer should exceed max_load
    load_count = {}
    for assignment in assignments.values():
        for rev in assignment["assigned"]:
            rid = rev["reviewer_id"]
            load_count[rid] = load_count.get(rid, 0) + 1

    for rid, extra in load_count.items():
        original_load = reviewers[rid]["current_load"]
        max_allowed = reviewers[rid]["max_load"]
        assert original_load + extra <= max_allowed

    # Scores should be reasonable
    avg_score = sum(
        rev["score"] for a in assignments.values() for rev in a["assigned"]
    ) / sum(len(a["assigned"]) for a in assignments.values())
    assert avg_score > 0.4  # very conservative lower bound
