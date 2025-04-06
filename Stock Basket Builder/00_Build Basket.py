# -*- coding: utf-8 -*-
"""
Created on Sun Apr  6 17:37:49 2025

@author: Steven.Fandozzi
"""

# =============================================================================
# Thematic Stock Basket Generator
# =============================================================================
# This script clusters companies based on their thematic engagement using
# keyword mentions and transcript embeddings. It outputs a labeled dataset
# identifying the "core basket" of companies highly engaged with a selected theme.
#
# -----------------------------------------------------------------------------
# Workflow Summary:
# Excel Input --> Embed Transcripts --> Feature Matrix --> PCA --> Clustering --> Output Basket
# -----------------------------------------------------------------------------
#
# INPUT REQUIREMENTS:
# The input must be an Excel file with the following columns:
# - Company: Name or unique ID of the company
# - Transcript_Text: Full transcript text for the company
# - Total_Mentions: Number of theme-related keyword mentions
# - Share_Mentions: This company’s share of total mentions across all companies
# - Mention_Momentum: QoQ or YoY change in theme mentions (as a decimal or %)
#
# Default file path (can be changed in the script):
# file_path = "S:/Strategy Research/Transcripts/Data/Processed_Transcript_Features.xlsx"
#
# -----------------------------------------------------------------------------
# OUTPUTS:
# 1. Feature Matrix: Numeric and embedding features per company
# 2. Cluster Assignments:
#    - Thematic_Engaged = 1 --> High engagement (Core Basket)
#    - Thematic_Engaged = 0 --> Low/no engagement (Background Universe)
# 3. Visualizations:
#    - PCA Explained Variance Line Plot
#    - 2D Scatter Plot of Clusters
# 4. Final Output Table (can be exported to Excel if desired)
#
# -----------------------------------------------------------------------------
# OPTIONAL ENHANCEMENTS:
# - Swap out "all-MiniLM-L6-v2" for a more powerful embedding model
# - Add export functionality to CSV/Excel
# - Expand with time-series analysis for mentions across quarters
#
# This script is modular and designed to plug into your transcript analysis pipeline.
# =============================================================================

import pandas as pd
import numpy as np
import os
import warnings
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import plotly.express as px
from sentence_transformers import SentenceTransformer

warnings.filterwarnings("ignore")

# =============================================================================
# Thematic Stock Basket Generator
# =============================================================================
# This script clusters companies into high vs. low thematic engagement using:
# - Total mentions
# - Share of mentions
# - Mention momentum (QoQ)
# - Transcript embeddings
# - PCA + KMeans clustering
#
# OUTPUT: Core basket = companies most engaged in the theme
# =============================================================================

# -------------------------------------------
# STEP 1: LOAD & PREPARE TRANSCRIPT DATA
# -------------------------------------------

file_path = "S:/Strategy Research/Transcripts/Data/Excel/Raw Tariff Mentions.xlsx"
if not os.path.exists(file_path):
    raise FileNotFoundError(f"Excel file not found at {file_path}")

df = pd.read_excel(file_path)
df["Date"] = pd.to_datetime(df["Date"])
df["Quarter"] = df["Date"].dt.to_period("Q").astype(str)

keyword_cols = [col for col in df.columns if col.endswith("_keyword_count")]

# -------------------------------------------
# STEP 2: CREATE FEATURE MATRIX
# -------------------------------------------

# 7.1 Total keyword mentions per company
agg = df.groupby(["Ticker", "Company Name", "Quarter"], as_index=False)[keyword_cols].sum()
agg["Total_Keyword_Mentions"] = agg[keyword_cols].sum(axis=1)

# 7.2 Share of mentions vs peers (per quarter)
total_by_quarter = agg.groupby("Quarter")["Total_Keyword_Mentions"].transform("sum")
agg["Share_Mentions"] = agg["Total_Keyword_Mentions"] / total_by_quarter

# 7.3 Mention momentum (QoQ)
agg = agg.sort_values(["Ticker", "Quarter"])
agg["Mention_Momentum"] = agg.groupby("Ticker")["Total_Keyword_Mentions"].pct_change().fillna(0)

# Display intermediate output
import ace_tools as tools; tools.display_dataframe_to_user(name="Feature Matrix: Mentions, Share, Momentum", dataframe=agg)

# -------------------------------------------
# STEP 3: TEXT EMBEDDINGS
# -------------------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(df["Combined Transcript"].tolist(), show_progress_bar=True)

embedding_dim = embeddings.shape[1]
emb_df = pd.DataFrame(embeddings, columns=[f"Embed_{i+1}" for i in range(embedding_dim)])
emb_df["Ticker"] = df["Ticker"]
emb_df["Quarter"] = df["Quarter"]

# 7.4 Text embeddings from full transcript → average by Ticker-Quarter
emb_agg = emb_df.groupby(["Ticker", "Quarter"]).mean().reset_index()

# -------------------------------------------
# STEP 4: MERGE & FINALIZE FEATURE MATRIX
# -------------------------------------------

# 7.5 Concatenate into unified feature vector
features_df = pd.merge(agg, emb_agg, on=["Ticker", "Quarter"])
tools.display_dataframe_to_user(name="Unified Feature Matrix", dataframe=features_df.head())

# -------------------------------------------
# STEP 5: PCA DIMENSIONALITY REDUCTION
# -------------------------------------------

# 8.1 Normalize all numeric features
feature_cols = ["Total_Keyword_Mentions", "Share_Mentions", "Mention_Momentum"] + [col for col in features_df.columns if col.startswith("Embed_")]
X = features_df[feature_cols]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 8.2 Apply PCA
pca = PCA(n_components=10)
X_pca = pca.fit_transform(X_scaled)

# 8.3 Plot explained variance
explained_variance = pca.explained_variance_ratio_.cumsum()
plt.figure(figsize=(7, 4))
plt.plot(range(1, 11), explained_variance, marker='o')
plt.title("Cumulative Variance Explained by PCA")
plt.xlabel("Number of PCA Components")
plt.ylabel("Cumulative Explained Variance")
plt.grid(True)
plt.tight_layout()
plt.show()

# -------------------------------------------
# STEP 6: K-MEANS CLUSTERING
# -------------------------------------------

# 9.1 Set n_clusters = 2
kmeans = KMeans(n_clusters=2, random_state=42)
labels = kmeans.fit_predict(X_pca)

# 9.2 Assign cluster labels
features_df["Cluster"] = labels

# 9.3 Analyze average metrics by cluster
cluster_avg = features_df.groupby("Cluster")[["Total_Keyword_Mentions", "Share_Mentions", "Mention_Momentum"]].mean().reset_index()
tools.display_dataframe_to_user(name="Cluster Averages", dataframe=cluster_avg)

# -------------------------------------------
# STEP 7: REVIEW CLUSTER VALIDITY
# -------------------------------------------

# 10.1 Visualize PCA-reduced clusters in 2D
pca_2d = PCA(n_components=2).fit_transform(X_scaled)
viz_df = pd.DataFrame(pca_2d, columns=["PCA1", "PCA2"])
viz_df["Company"] = features_df["Company Name"]
viz_df["Cluster"] = features_df["Cluster"]

fig = px.scatter(
    viz_df,
    x="PCA1", y="PCA2",
    color=viz_df["Cluster"].astype(str),
    hover_name="Company",
    title="PCA Cluster Visualization (2D)",
    width=700, height=500
)
fig.show()

# 10.2 Silhouette Score
sil_score = silhouette_score(X_pca, labels)
print(f"Silhouette Score: {sil_score:.3f} (0 = poor, 1 = ideal)")

# 10.3 Manually verify samples
for cluster_id in sorted(features_df["Cluster"].unique()):
    sample = features_df[features_df["Cluster"] == cluster_id][["Company Name", "Total_Keyword_Mentions"]].head()
    print(f"\nSample from Cluster {cluster_id}:\n", sample)

# -------------------------------------------
# STEP 8: OUTPUT FINAL BASKET
# -------------------------------------------

# ✅ 🎯 Thematic Core Basket vs ⚪ Background Universe
core_cluster = cluster_avg.loc[cluster_avg["Total_Keyword_Mentions"].idxmax(), "Cluster"]
features_df["Thematic_Engaged"] = (features_df["Cluster"] == core_cluster).astype(int)

# Final output: Label each row
final_output = features_df[["Ticker", "Company Name", "Quarter", "Total_Keyword_Mentions", "Share_Mentions", "Mention_Momentum", "Cluster", "Thematic_Engaged"]]
tools.display_dataframe_to_user(name="Final Thematic Basket", dataframe=final_output)
