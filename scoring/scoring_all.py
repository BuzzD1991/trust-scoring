# scoring [all items].py  ────────────────────────────────────────────────────────────────
"""
Calculates the score.
• Input:  Dataset with ratings (1 to 5) for all Items (B1_1 to B8_4).
• Output: Score (float).
"""
from pathlib import Path
import argparse
import math
import pandas as pd

# ---------------------------------------------------------------------------
# 1) Item groups
EFFECTIVE = [
    "B1_3", "B2_1", "B2_4", "B3_4", "B4_1", "B4_3",
    "B5_1", "B5_3", "B6_1", "B7_2", "B7_3"]

INEFFECTIVE = ["B1_2", "B3_3", "B5_4", "B6_3", "B7_4", "B8_1"]

# Pairwise comparisons – first element = more effective, second element = less effective
DIFFS_ADJACENT = [
    # B1
    ("B1_3", "B1_1"), ("B1_3", "B1_4"),
    # B2
    ("B2_1", "B2_3"), ("B2_4", "B2_3"),
    # B3
    ("B3_4", "B3_1"), ("B3_4", "B3_2"),
    # B4
    ("B4_1", "B4_2"), ("B4_3", "B4_2"),
    # B5
    ("B5_1", "B5_2"), ("B5_3", "B5_2"),
    # B6
    ("B6_1", "B6_2"), ("B6_1", "B6_4"),
    # B7
    ("B7_1", "B7_4"),
    # B8
    ("B8_3", "B8_1")
]

DIFFS_DISTANT = [
    # B1
    ("B1_1", "B1_2"), ("B1_4", "B1_2"),
    # B2
    ("B2_1", "B2_2"), ("B2_4", "B2_2"),
    # B3
    ("B3_1", "B3_3"), ("B3_2", "B3_3"),
    # B4
    ("B4_1", "B4_4"), ("B4_3", "B4_4"),
    # B5
    ("B5_2", "B5_4"),
    # B6
    ("B6_2", "B6_3"), ("B6_4", "B6_3"),
    # B7
    ("B7_2", "B7_1"), ("B7_3", "B7_1"),
    # B8
    ("B8_2", "B8_1"), ("B8_4", "B8_1")
]

# ---------------------------------------------------------------------------
# 2) recode functions
def recode_effective(r: int) -> float:
    if r == 5: return 1.0
    if r == 4: return 0.5
    return 0.0

def recode_ineffective(r: int) -> float:
    if r == 1: return 1.0
    if r == 2: return 0.5
    return 0.0

def recode_adjacent(diff: int) -> float:
    if diff == 0: return 0.5
    if diff > 0:  return 1.0
    return 0.0

def recode_distant(diff: int) -> float:
    if diff == 1: return 0.5
    if diff > 1:  return 1.0
    return 0.0

# score function for each individual
def score_row(row: pd.Series) -> float:
    score = 0.0

    # (a) clearly (in-)effective strategies
    for item in EFFECTIVE:
        score += recode_effective(int(row[item]))
    for item in INEFFECTIVE:
        score += recode_ineffective(int(row[item]))

    # (b) ambivalent strategies – adjacent
    for better, worse in DIFFS_ADJACENT:
        diff = int(row[better]) - int(row[worse])
        score += recode_adjacent(diff)

    # (c) ambivalent strategies – distant
    for better, worse in DIFFS_DISTANT:
        diff = int(row[better]) - int(row[worse])
        score += recode_distant(diff)

    return score

# ---------------------------------------------------------------------------
# 3) CLI – `python scoring.py input.csv output.csv`
def main():
    parser = argparse.ArgumentParser(description="Calculate TRUST Score")
    parser.add_argument("infile",  help="CSV with ratings on each item (coloumns B1_1 to B8_4)")
    parser.add_argument("outfile", help="Path for CSV output with TRUST Score")
    args = parser.parse_args()

    df = pd.read_csv(args.infile)
    df["Score"] = df.apply(score_row, axis=1)
    df.to_csv(args.outfile, index=False)
    print(f"✓ Calculated – File saved: {args.outfile}")

if __name__ == "__main__":
    main()