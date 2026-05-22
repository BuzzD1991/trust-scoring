"""
Dynamic scoring based on item-total correlations.
• Input: DataFrame with columns B1_1 to B8_4 (1–5 scale)
• Output: Individual scores based on items with rit ≥ .15
• Side effect: Shows item-total correlations and removed items
"""

import pandas as pd
import numpy as np
import streamlit as st

ITEMS = [
    f"B{i}_{j}" for i in range(1, 9) for j in range(1, 5)
]

CORRELATION_THRESHOLD = 0.15

def score_row(row, valid_items):
    values = row[valid_items].dropna().astype(int)
    if len(values) == 0:
        return np.nan
    return values.mean()


def score_dynamic(df: pd.DataFrame) -> pd.Series:
    # 1. Filter for valid items
    df_items = df[ITEMS].apply(pd.to_numeric, errors="coerce")
    
    # 2. Compute total scores per person (excluding each item)
    total_scores = df_items.sum(axis=1, skipna=True)

    # 3. Compute item-total correlations
    item_total_corrs = {}
    for item in ITEMS:
        item_scores = df_items[item]
        temp_total = total_scores - item_scores  # exclude self
        corr = item_scores.corr(temp_total)
        item_total_corrs[item] = corr

    # 4. Determine valid items
    valid_items = [item for item, r in item_total_corrs.items() if r is not None and r >= CORRELATION_THRESHOLD]
    excluded_items = [item for item in ITEMS if item not in valid_items]

    # 5. Show diagnostics
    st.subheader("📊 Item-total correlations (r ≥ 0.15 retained)")
    corr_df = (
        pd.Series(item_total_corrs)
        .sort_values(ascending=False)
        .rename("Item-total correlation")
        .to_frame()
    )
    st.dataframe(corr_df.style.format("{:.2f}"))

    st.markdown(f"**🟢 Items retained ({len(valid_items)}):** {', '.join(valid_items)}")
    st.markdown(f"**🔴 Items excluded ({len(excluded_items)}):** {', '.join(excluded_items)}")

    # 6. Calculate scores
    scores = df.apply(lambda row: score_row(row, valid_items), axis=1)
    return scores
