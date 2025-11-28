# ReviewCalibraAI

**Fair, transparent, and expertise-aware reviewer assignment for conference peer review**

ReviewCalibraAI is a lightweight, open-source tool designed to assist program chairs and area chairs in creating balanced and conflict-free reviewer assignments — especially valuable for large-scale conferences like NeurIPS, ICML, ICLR, etc.

Instead of manual spreadsheet juggling or opaque commercial systems, ReviewCalibraAI uses a simple, auditable scoring model that jointly optimizes:

- Subject-area expertise (via keyword/topic overlap)
- Workload balancing across reviewers
- Avoidance of conflicts of interest (COI)
- Optional seniority or quota constraints

Perfect for rapid prototyping of fair assignments and for building trust through transparency.

## Why ReviewCalibraAI?

- **Fully transparent** — every matching decision is explainable and reproducible
- **No black-box ML** — uses a clean, configurable integer-linear-programming-free heuristic (greedy + rebalancing) that runs in seconds even on 1000+ submissions
- **Zero external dependencies beyond pandas/numpy** — runs anywhere
- **Easy to audit** — all logic lives in < 300 lines of readable Python
- **Designed for real-world program chairs** — inspired by pain points from NeurIPS, ICML, and ICLR

## Quick Start (less than 2 minutes)

```bash
git clone https://github.com/josephjilovec/ReviewCalibraAI.git
cd ReviewCalibraAI
pip install -r requirements.txt   # or: pip install reviewcalibraai
python scripts/main.py --demo     # runs on included dummy data
