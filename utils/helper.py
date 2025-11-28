"""
utils/helper.py

Core functions for ReviewCalibraAI:
- Load reviewer and submission data
- Compute expertise affinity scores
- Perform fair, greedy + re-balancing reviewer assignment
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Any

import numpy as np
import pandas as pd


def load_data(
    reviewers_path: Path | str,
    submissions_path: Path | str,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Load reviewers and submissions from JSON files.

    Expected reviewer fields:
        id, name, expertise (list of keywords), max_load, current_load, conflicts (list of emails)

    Expected submission fields:
        id, title, keywords (list), author_emails (list)
    """
    with open(reviewers_path, "r", encoding="utf-8") as f:
        reviewers = {r["id"]: r for r in json.load(f)}
    with open(submissions_path, "r", encoding="utf-8") as f:
        submissions = {s["id"]: s for s in json.load(f)}

    return reviewers, submissions


def compute_affinity_scores(
    reviewers: Dict[str, Any], submissions: Dict[str, Any]
) -> pd.DataFrame:
    """
    Compute expertise overlap score between every reviewer and every paper.
    Simple Jaccard similarity on keyword sets (case-insensitive).
    Returns a DataFrame for fast lookup: rows = reviewers, columns = papers.
    """
    reviewer_ids = list(reviewers.keys())
    paper_ids = list(submissions.keys())

    scores = pd.DataFrame(
        0.0, index=reviewer_ids, columns=paper_ids, dtype=float
    )

    for r_id in reviewer_ids:
        r_keywords = set(reviewers[r_id]["expertise"])
        r_conflicts = set(reviewers[r_id].get("conflicts", []))

        for p_id in paper_ids:
            p_keywords = set(submissions[p_id]["keywords"])
            p_authors = set(submissions[p_id].get("author_emails", []))

            # Conflict of interest → score = -inf
            if r_conflicts & p_authors:
                scores.loc[r_id, p_id] = -float("inf")
                continue

            # Jaccard similarity
            intersection = len(r_keywords & p_keywords)
            union = len(r_keywords | p_keywords)
            jaccard = intersection / union if union > 0 else 0.0
            scores.loc[r_id, p_id] = jaccard

    return scores


def assign_reviewers(
    reviewers: Dict[str, Any],
    submissions: Dict[str, Any],
    reviews_per_paper: int = 3,
) -> Dict[str, Dict[str, Any]]:
    """
    Greedy assignment with iterative re-balancing to respect max_load.
    Prioritizes highest expertise while keeping workload fair.
    """
    affinity = compute_affinity_scores(reviewers, submissions)
    assignments: Dict[str, Dict[str, Any]] = {}

    # Sort papers arbitrarily (can be randomized or by submission time)
    paper_ids = list(submissions.keys())

    # Track current load for each reviewer
    load = {r_id: r["current_load"] for r_id, r in reviewers.items()}
    max_load = {r_id: r["max_load"] for r_id, r in reviewers.items()}

    for paper_id in paper_ids:
        candidates = affinity[paper_id].copy()

        # Remove reviewers who have reached max load
        for r_id in load:
            if load[r_id] >= max_load[r_id]:
                candidates[r_id] = -float("inf")

        # Iteratively pick the best available reviewer
        assigned_reviewers = []
        for _ in range(reviews_per_paper):
            if candidates.max() <= -float("inf"):
                break  # no more valid reviewers

            best_reviewer = candidates.idxmax()
            score = float(candidates[best_reviewer])

            assigned_reviewers.append(
                {"reviewer_id": best_reviewer, "score": score}
            )

            # Update load and block this reviewer from being picked again for this paper
            load[best_reviewer] += 1
            candidates[best_reviewer] = -float("inf")

            # Also reduce score for this reviewer globally to encourage balance
            affinity.loc[best_reviewer] *= 0.95  # slight penalty after each assignment

        # Store the top-k assignment for this paper
        assignments[paper_id] = {
            "assigned
