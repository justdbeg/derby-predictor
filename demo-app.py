# demo-app.py
# -----------------------------------------------------------------------------
# Derby Predictor Dashboard (Frontend-Only / Portfolio-Safe)
#-----------------------------------------------------------------------------

import os
import io
import time
import pandas as pd
import streamlit as st

# ----------------------------- Page Config -----------------------------------
st.set_page_config(
    page_title="Derby Predictor Dashboard",
    page_icon="🏇",
    layout="wide",
)

# ----------------------------- Constants -------------------------------------
DATA_VIEWS = [
    {"key": "quick",   "title": "Quick Composite",     "emoji": "🔹", "file": "data/quick_predictions.csv"},
    {"key": "rank",    "title": "Model Rankings",      "emoji": "🔸", "file": "data/model_rankings.csv"},
    {"key": "pca",     "title": "PCA Insights",        "emoji": "♠️", "file": "data/pca_summary.csv"},
    {"key": "overlay", "title": "Value Picks",         "emoji": "💰", "file": "data/value_overlay.csv"},
    {"key": "cluster", "title": "Cluster Analysis",    "emoji": "🔄", "file": "data/cluster_insights.csv"},
]

# Columns we *may* show if present. All others remain hidden by default.
DEFAULT_VISIBLE_COLS = ["Horse", "Year", "PP", "Trainer", "Jockey", "CompositeIndex", "Note"]

# Optional lightweight access gate (set in .streamlit/secrets.toml or env)
ACCESS_KEY = st.secrets.get("ACCESS_KEY", os.getenv("DERBY_APP_KEY"))

# ----------------------------- Utilities -------------------------------------
@st.cache_data(show_spinner=False)
def load_csv(path: str) -> pd.DataFrame:
    """Load a CSV if present; otherwise return empty DataFrame."""
    try:
        if os.path.exists(path):
            return pd.read_csv(path)
    except Exception:
        pass
    return pd.DataFrame()

def make_demo_df(kind: str) -> pd.DataFrame:
    """Generate sanitized, non-proprietary demo data for a given view."""
    horses = ["Thunder Lane", "Blue Ribbon", "Crimson Tide", "Midnight Ace", "Golden Harbor"]
    base = pd.DataFrame({
        "Horse": horses,
        "Year": [2025]*5,
        "PP": [3, 7, 11, 5, 9],
        "Trainer": ["Redacted"]*5,
        "Jockey": ["Redacted"]*5,
        # generic, non-revealing placeholders
        "CompositeIndex": [92.3, 90.1, 88.7, 87.9, 86.4],
        "SpeedFigure": [100, 101, 98, 99, 97],
        "FinalFraction": [37.6, 37.9, 38.1, 37.8, 38.2],
        "Note": [f"{kind} (demo)" for _ in range(5)],
    })
    if kind == "pca":
        base["PC1"] = [1.2, 0.9, -0.3, 0.4, -0.7]
        base["PC2"] = [-0.1, 0.5, 1.0, -0.2, 0.3]
    if kind == "cluster":
        base["Cluster"] = ["A", "A", "B", "B", "C"]
    return base

def ensure_demo_if_empty(df: pd.DataFrame, kind: str) -> pd.DataFrame:
    return df if not df.empty else make_demo_df(kind)

def apply_filters(df: pd.DataFrame, year: int | None, query: str | None) -> pd.DataFrame:
    out = df.copy()
    if year and "Year" in out.columns:
        out = out[out["Year"] == year]
    if query and "Horse" in out.columns:
        out = out[out["Horse"].str.contains(query, case=False, na=False)]
    return out

def download_bytes(df: pd.DataFrame) -> bytes:
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")

def render_table(df: pd.DataFrame, title: str):
    if df.empty:
        st.info("No rows to display.")
        return
    # Column selector (only show known-safe cols by default)
    default_cols = [c for c in DEFAULT_VISIBLE_COLS if c in df.columns]
    cols = st.multiselect("Columns", options=list(df.columns), default=default_cols or list(df.columns)[:8])
    st.dataframe(df[cols] if cols else df, use_container_width=True, hide_index=True)
    st.download_button("Download CSV", data=download_bytes(df if not cols else df[cols]),
                       file_name=f"{title.replace(' ', '_').lower()}.csv")

# ----------------------------- Sidebar ---------------------------------------
st.sidebar.header("Derby Predictor")
st.sidebar.caption("Frontend-only dashboard of precomputed outputs.")

# Access control (soft gate): if ACCESS_KEY is set, require it; else allow demo mode.
demo_mode = False
if ACCESS_KEY:
    key = st.sidebar.text_input("Access key", type="password", help="Request access for full datasets.")
    if key != ACCESS_KEY:
        demo_mode = True
        st.sidebar.warning("Demo mode enabled (sanitized sample data).")
    else:
        st.sidebar.success("Access granted.")
else:
    demo_mode = st.sidebar.checkbox("Demo mode", value=True, help="Use sanitized sample data for portfolio.")

# ----------------------------- Header ----------------------------------------
st.title("🏇 Derby Predictor Dashboard")
st.caption("Modular Streamlit interface for reviewing precomputed contender insights. "
           "All modeling logic and raw data are kept private by design.")

# Optional global filters (applied when available in a view)
year_filter = st.sidebar.number_input("Filter by Year (if available)", min_value=1900, max_value=2100, value=2025, step=1)
query_filter = st.sidebar.text_input("Search Horse (if available)")

# ----------------------------- Tabs / Views ----------------------------------
tab_labels = [f"{v['emoji']} {v['title']}" for v in DATA_VIEWS]
tabs = st.tabs(tab_labels)

for tab, view in zip(tabs, DATA_VIEWS):
    with tab:
        st.subheader(view["title"])
        with st.spinner("Loading view…"):
            time.sleep(0.1)  # tiny pause for smooth UX
            df = load_csv(view["file"])
            df = ensure_demo_if_empty(df, view["key"] if view["key"] in {"pca", "cluster"} else view["title"])
            df = apply_filters(df, year_filter, query_filter)

        # Context metrics (shown only if present; no logic revealed)
        cols = st.columns(4)
        if "Horse" in df.columns:
            cols[0].metric("Horses", f"{df['Horse'].nunique():,}")
        if "PP" in df.columns:
            cols[1].metric("PP Range", f"{int(df['PP'].min())}-{int(df['PP'].max())}")
        if "SpeedFigure" in df.columns:
            cols[2].metric("Avg Speed", f"{df['SpeedFigure'].mean():.1f}")
        if "FinalFraction" in df.columns:
            cols[3].metric("Avg Final 3/8", f"{df['FinalFraction'].mean():.2f}s")

        render_table(df, view["title"])

# ----------------------------- Footnote --------------------------------------
st.divider()
st.caption(
    "This is a **frontend-only** demonstration. Model training, feature engineering, and data pipelines "
    "are intentionally excluded. Full demo available privately upon request."
)