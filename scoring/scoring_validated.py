# scoring [validated items].py  ────────────────────────────────────────────────────────────────
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
    "B1_3","B2_1","B2_4","B3_4","B4_1","B4_3",
    "B5_1","B5_3","B6_1","B7_2","B7_3"
    # scenario B8 removed
]
INEFFECTIVE = [
    "B1_2","B3_3","B5_4","B6_3","B7_4"
    # scenario B8 removed
]

# Pairwise comparisons – first element = more effective, second element = less effective
DIFFS_ADJACENT = [
    # B2
    ("B2_1", "B2_3"), ("B2_4", "B2_3"),
    # B3
    ("B3_4", "B3_1"),
    # B4
    ("B4_1", "B4_2"), ("B4_3", "B4_2"),
    # B5
    ("B5_1", "B5_2"), ("B5_3", "B5_2"),
    # B6
    ("B6_1", "B6_2"), ("B6_1", "B6_4")
    
    # ("B1_3", "B1_1") removed   
    # ("B1_3", "B1_4") removed
    # ("B3_4", "B3_2") removed
    # ("B7_1", "B7_4") removed
    # B8 completely removed
]

DIFFS_DISTANT = [
    # B1
    ("B1_1", "B1_2"), ("B1_4", "B1_2"),
    # B2
    ("B2_1", "B2_2"),
    # B3
    ("B3_2", "B3_3"),
    # B4
    ("B4_1", "B4_4"), ("B4_3", "B4_4"),
    # B7
    ("B7_2", "B7_1"), ("B7_3", "B7_1")
    
    # ("B2_4", "B2_2") removed 
    # ("B3_1", "B3_3") removed
    # ("B5_2", "B5_4") removed
    # ("B6_2", "B6_3") removed
    # ("B6_4", "B6_3") removed
    # B8 completely removed
]

SCENARIO_VARS = {
    "B1": ["B1_12", "B1_24", "B1_2R", "B1_3R"],
    "B2": ["B2_12", "B2_13", "B2_1R", "B2_34", "B2_4R"],
    "B3": ["B3_14", "B3_23", "B3_3R", "B3_4R"],
    "B4": ["B4_12", "B4_14", "B4_1R", "B4_23", "B4_34", "B4_3R"],
    "B5": ["B5_12", "B5_1R", "B5_23", "B5_3R", "B5_4R"],
    "B6": ["B6_12", "B6_14", "B6_1R", "B6_3R"],
    "B7": ["B7_12", "B7_13", "B7_2R", "B7_3R", "B7_4R"]
    }

SCENARIO_MIN = {"B1": 3, "B2": 4, "B3": 3, "B4": 5, 
                "B5": 4, "B6": 3, "B7": 4}

def mean_if(row, cols, min_valid):
    vals = [row[c] for c in cols if c == c and not pd.isna(c)]
    return sum(vals)/len(vals) if len(vals) >= min_valid else math.nan

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