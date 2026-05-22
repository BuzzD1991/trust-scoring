# pages/3_Scoring.py ──────────────────────────────────────────────────────────────
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import plotly.express as px

from scoring import scoring_all, scoring_validated
from scoring.scoring_dynamic import score_dynamic

# ---------- Page config ----------
st.set_page_config(page_title="TRUST Scoring", layout="wide")
st.title("TRUST — Automated Scoring")

# ---------- Item structure ----------
SCENARIOS = {
    "B1": ["B1_1", "B1_2", "B1_3", "B1_4"],
    "B2": ["B2_1", "B2_2", "B2_3", "B2_4"],
    "B3": ["B3_1", "B3_2", "B3_3", "B3_4"],
    "B4": ["B4_1", "B4_2", "B4_3", "B4_4"],
    "B5": ["B5_1", "B5_2", "B5_3", "B5_4"],
    "B6": ["B6_1", "B6_2", "B6_3", "B6_4"],
    "B7": ["B7_1", "B7_2", "B7_3", "B7_4"],
    "B8": ["B8_1", "B8_2", "B8_3", "B8_4"],
}
ALL_ITEMS = [it for lst in SCENARIOS.values() for it in lst]

# ---------- Scoring method ----------
st.subheader("1 · Choose scoring method")
scoring_option = st.radio(
    "Which scoring method shall be applied?",
    (
        "(a) All items",
        "(b) Validated items (Aldrup et al., 2020)",
        "(c) Dynamic – retain items with r_it ≥ .15 (requires CSV with ≥ 2 participants)",
    ),
    label_visibility="collapsed",
)

IS_DYNAMIC = scoring_option.startswith("(c)")

if scoring_option.startswith("(a)"):
    score_row = scoring_all.score_row
elif scoring_option.startswith("(b)"):
    score_row = scoring_validated.score_row
# For (c) we use score_dynamic(df) on the whole dataframe – no score_row needed.

# ---------- Helper: show results ----------
def show_results(df: pd.DataFrame, score_col: str = "Score"):
    st.success("✅ Scores calculated.")

    # --- summary stats ---
    scores = df[score_col].dropna()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("N", len(scores))
    col2.metric("Mean", f"{scores.mean():.2f}")
    col3.metric("SD",   f"{scores.std():.2f}")
    col4.metric("Range", f"{scores.min():.1f} – {scores.max():.1f}")

    # --- histogram ---
    fig = px.histogram(
        df, x=score_col, nbins=20,
        title="Score Distribution",
        labels={score_col: "TRUST Score", "count": "Frequency"},
        color_discrete_sequence=["#4C72B0"],
    )
    fig.update_layout(bargap=0.05, plot_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

    # --- full table ---
    with st.expander("Show full data table"):
        st.dataframe(df, use_container_width=True)

    # --- download ---
    st.download_button(
        "⬇️ Download results as CSV",
        df.to_csv(index=False).encode("utf-8"),
        "TRUST_scores.csv",
        mime="text/csv",
    )

# ════════════════════════════════════════════════════════════════════
st.subheader("2 · Input data")
mode = st.radio(
    "Choose input mode",
    ["CSV Upload", "Manual Input"],
    horizontal=True,
    label_visibility="collapsed",
)

# Note: Dynamic scoring is not available for manual input
if IS_DYNAMIC and mode == "Manual Input":
    st.warning(
        "⚠️ Dynamic scoring requires at least 2 participants to compute "
        "item-total correlations. Please use CSV upload or choose a different scoring method."
    )
    st.stop()

# ════════════════════════════════════════════════════════════════════
#  A) CSV UPLOAD
# ════════════════════════════════════════════════════════════════════
if mode == "CSV Upload":
    file = st.file_uploader("Upload CSV", type="csv")

    if file:
        # Robust reading with auto-separator detection
        try:
            df = pd.read_csv(file, sep=None, engine="python")
        except Exception as e:
            file.seek(0)
            try:
                df = pd.read_csv(file, sep=";", engine="python")
            except Exception as e2:
                st.error(f"❌ Could not read CSV.\n\nError: {e}\n{e2}")
                st.stop()

        # Fill missing item columns with NA
        missing = [c for c in ALL_ITEMS if c not in df.columns]
        if missing:
            st.warning(f"⚠️ Missing columns (filled with NA): {', '.join(missing)}")
            for m in missing:
                df[m] = pd.NA

        # Calculate scores
        if IS_DYNAMIC:
            if len(df) < 2:
                st.error("❌ Dynamic scoring requires at least 2 participants.")
                st.stop()
            df["Score"] = score_dynamic(df)
        else:
            df["Score"] = df.apply(score_row, axis=1)

        show_results(df)

# ════════════════════════════════════════════════════════════════════
#  B) MANUAL INPUT
# ════════════════════════════════════════════════════════════════════
else:
    st.info("Enter ratings from **1 – 5** for each item. Each row = one participant.")

    n_rows = st.number_input("Number of participants (rows)", 1, 200, 5, step=1)

    if "table" not in st.session_state or st.session_state.table.shape[0] != n_rows:
        st.session_state.table = pd.DataFrame(
            [[None] * len(ALL_ITEMS)] * n_rows,
            columns=ALL_ITEMS,
        )

    col_cfg = {
        col: st.column_config.NumberColumn(label=col, min_value=1, max_value=5, step=1)
        for col in ALL_ITEMS
    }

    edited_df = st.data_editor(
        st.session_state.table,
        column_config=col_cfg,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="data_editor",
    )

    if st.button("▶️ Calculate Score"):
        df = edited_df.copy()

        # Validate: no empty cells
        empty_mask = df[ALL_ITEMS].isnull().any(axis=1)
        if empty_mask.any():
            bad_rows = empty_mask[empty_mask].index.tolist()
            st.error(
                f"❌ Missing values in row(s): {[r + 1 for r in bad_rows]}. "
                "Please fill in all cells before calculating."
            )
            st.stop()

        df["Score"] = df.apply(score_row, axis=1)
        show_results(df)
