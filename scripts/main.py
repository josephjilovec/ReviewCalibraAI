#!/usr/bin/env python
"""
ReviewCalibraAI – Fair reviewer-to-paper matching tool
Entry point and CLI
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

# Local imports
from utils.helper import load_data, compute_affinity_scores, assign_reviewers


def run_demo() -> None:
    """Run the tool on the included dummy dataset."""
    data_path = Path(__file__).parent.parent / "data"
    reviewers_file = data_path / "sample_reviewers.json"
    submissions_file = data_path / "submissions.json"

    if not reviewers_file.exists() or not submissions_file.exists():
        print("Demo data not found. Did you clone the full repo?")
        sys.exit(1)

    reviewers, submissions = load_data(reviewers_file, submissions_file)
    assignments = assign_reviewers(reviewers, submissions)

    print("\n=== ReviewCalibraAI – Suggested Assignments ===\n")
    print(f"{'Paper ID':<10} {'Title':<40} {'Reviewer':<20} {'Expertise':<10} {'New Load':<10}")
    print("-" * 90)

    total_score = 0.0
    total_assignments = 0
    loads = []

    for paper_id, assignment in assignments.items():
        paper = submissions[paper_id]
        assigned_list = assignment["assigned"]

        if not assigned_list:
            print(f"{paper_id:<10} {paper['title'][:38]:<40} {'(no suitable reviewer)':<20} {'—':<10} {'—':<10}")
            continue

        for rev in assigned_list:
            reviewer = reviewers[rev["reviewer_id"]]
            score = rev["score"]
            new_load = reviewer["current_load"] + loads.count(rev["reviewer_id"]) + 1

            print(
                f"{paper_id:<10} "
                f"{paper['title'][:38]:<40} "
                f"{reviewer['name']:<20} "
                f"{score:.3f}     "
                f"{new_load}/{reviewer['max_load']}"
            )

            total_score += score
            total_assignments += 1
            loads.append(rev["reviewer_id"])

    print("-" * 90)
    if total_assignments > 0:
        print(f"Average expertise score : {total_score / total_assignments:.3f}")
        print(f"Load std deviation      : {pd.Series([loads.count(r) for r in set(loads)]).std():.2f}")
    print(f"Total assigned reviews   : {total_assignments}")
    print(f"Papers covered           : {len([a for a in assignments.values() if a['assigned']])} / {len(assignments)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ReviewCalibraAI – transparent reviewer matching for conferences"
    )
    parser.add_argument(
        "--demo", action="store_true", help="Run on included dummy data"
    )
    parser.add_argument(
        "--reviewers", type=str, help="Path to reviewers JSON"
    )
    parser.add_argument(
        "--submissions", type=str, help="Path to submissions JSON"
    )

    args = parser.parse_args()

    if args.demo or not (args.reviewers or args.submissions):
        run_demo()
    else:
        reviewers, submissions = load_data(args.reviewers, args.submissions)
        assignments = assign_reviewers(reviewers, submissions)
        # Simple CSV output for now – can be extended
        pd.DataFrame.from_dict(assignments, orient="index").to_csv("assignments.csv")
        print("Assignments written to assignments.csv")


if __name__ == "__main__":
    main()
