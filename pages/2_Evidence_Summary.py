# 1_evidence_summary.py ──────────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd

# ---------- basic configuration ----------
st.set_page_config(layout="wide")
st.title("Overview of Published TRUST Versions")

# create a 3-column layout and place content in the center
col1, col2, col3 = st.columns([3, 1, 1])  # Adjust the ratio as desired (wide-narrow-narrow)

with col1:
    # introduction text
    st.markdown("""
                This table summarizes the psychometric properties and validation evidence of the **Test of Regulation and Understanding of 
                    Social Situations in Teaching (TRUST)** and its adapted versions across different languages and educational contexts.  
                It highlights key aspects of scope, factor structure, convergent validity, and internal reliability for each study, providing 
                    a comparative foundation for selecting or interpreting TRUST in diverse research or practical settings.
                """)

# define the data for the comparison table
data = {
    "Study / Version": [
        "Original TRUST (Aldrup et al., 2020)",
        "TRUST-PS (Sidera et al., 2025)",
        "Spanish TRUST (Antón et al., 2024)",
        "English TRUST (Glass, 2022)",
        "Portuguese TRUST (Irala et al., 2022)"
    ],
    "Language": [
        "German",
        "Catalan",
        "Spanish",
        "English",
        "Portuguese"
    ],
    "School Type": [
        "Secondary; pre-/in-service",
        "Primary",
        "Primary & Secondary",
        "Pre-service (incl. counselors)",
        "Pre-service"
    ],
    "Sample": [
        "Germany",
        "143 teachers in Catalonia/València",
        "503 teachers in Castilla y León",
        "U.S.; education students",
        "Brazil"
    ],
    "Factorial Validity": [
        "CFA; two-factor; good model fit",
        "CFA; two-factor; supportive but no detailed fit indices",
        "CFA; excellent fit: CFI=.93, TLI=.92, RMSEA=.049",
        "CFA supported two-factor; no detailed indices",
        "No CFA/EFA reported"
    ],
    "Criterion Validity": [
        "Related to MSCEIT, personality, well-being",
        "Correlated with TEIQue-SF (emotional intelligence)",
        "Correlated with ICQ-15, TEIQue-SF, ERQ",
        "Correlated with emotional intelligence",
        "Not tested; focused on descriptive responses"
    ],
    "Reliability": [
        "Acceptable; scenario-level tested",
        "α = .83 (ER), α = .87 (RM)",
        "Good; McDonald's Omega used",
        "Not numeric; consistent with prior findings",
        "Not reported"
    ]
}

# convert to DataFrame
df = pd.DataFrame(data)

# display the table
with col1:
    st.dataframe(df)

