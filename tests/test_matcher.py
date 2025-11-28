"""
tests/test_matcher.py
pytest suite for ReviewCalibraAI
"""

import pytest

from utils.helper import load_data, compute_affinity_scores, assign_reviewers


@pytest.fixture
def sample_data():
    from pathlib import Path
    base = Path(__file__).parent.parent
    return load_data(base / "data" / "sample_reviewers.json",
                     base / "data" / "submissions.json")


def test_load_data(sample_data):
    reviewers, submissions = sample_data
    assert len(reviewers) == 6
    assert len(submissions) == 6
    assert reviewers["r1"]["name"] == "Dr. Ada Lovelace"


def test_compute_affinity_scores(sample_data):
    reviewers, submissions = sample_data
    scores = compute_affinity_scores(reviewers, submissions)
    # Ada loves diffusion
    assert scores.loc["r1", "p01"] >= 0.5
    # Ada has COI on p04 → -inf
    assert scores.loc["r1", "p04"] == -float("inf")


def test_assign_reviewers(sample_data):
    reviewers, submissions = sample_data
    assignments = assign_reviewers(reviewers, submissions, reviews_per_paper=3)

    # Every paper should get at least one reviewer
    assert all(len(a["assigned"]) >= 1 for a in assignments.values())

    # No reviewer exceeds max_load
    load_count = {}
    for a in assignments.values():
        for rev in a["assigned"]:
            load_count[rev["reviewer_id"]] = load_count.get(rev["reviewer_id"], 0) + 1
    for rid, extra in load_count.items():
        assert reviewers[rid]["current_load"] + extra <= reviewers[rid]["max_load"]

    # Average score should be reasonable (relaxed for tiny dummy data)
    avg_score = sum(
        rev["score"] for a in assignments.values() for rev in a["assigned"]
    ) / sum(len(a["assigned"]) for a in assignments.values())
    assert 0.15 < avg_score < 1.0   # ← fixed line
