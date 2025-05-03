# app.py

import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="2025 Derby Multi-View", layout="wide")
st.title("🏇 2025 Kentucky Derby Dashboard")

@st.cache_data
def load_csv(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    st.warning(f"⚠️ File not found: {path}")
    return pd.DataFrame()

# Load all views
quick_df   = load_csv("derby_2025_quick_predictions.csv")
rank_df    = load_csv("derby_2025_rank_composite.csv")
pca_df     = load_csv("derby_2025_pca_ranking.csv")
overlay_df = load_csv("derby_2025_overlay_candidates.csv")
cluster_df = load_csv("derby_2025_cluster_analysis.csv")

tabs = st.tabs(["Quick","Rank","PCA","Overlay","Clusters"])

with tabs[0]:
    st.subheader("🔷 Quick Composite")
    st.dataframe(quick_df, use_container_width=True)

with tabs[1]:
    st.subheader("🔶 Rank-Based Composite")
    st.dataframe(rank_df, use_container_width=True)

with tabs[2]:
    st.subheader("♠️ PCA Ranking")
    st.dataframe(pca_df, use_container_width=True)

with tabs[3]:
    st.subheader("💰 Overlay Value Picks")
    st.dataframe(overlay_df, use_container_width=True)

with tabs[4]:
    st.subheader("🔀 Cluster Analysis")
    st.dataframe(cluster_df, use_container_width=True)
