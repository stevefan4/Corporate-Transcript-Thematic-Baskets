# -*- coding: utf-8 -*-

"""
Created on Sun Apr  6 17:37:49 2025

@author: Steven.Fandozzi
"""

# =============================================================================
# Thematic Stock Basket Generator
# =============================================================================
# This script clusters companies based on their thematic engagement using
# keyword mentions and transcript embeddings. It outputs labeled datasets
# identifying the "core basket" of companies highly engaged with each theme
# during each quarter.
#
# -----------------------------------------------------------------------------
# Workflow Summary:
# Excel Input --> Feature Matrix per Theme --> Clustering --> Output Basket per Theme per Quarter
# -----------------------------------------------------------------------------
#
# INPUT REQUIREMENTS:
# The input must be an Excel file with the following columns:
# - Ticker: Unique identifier
# - Company Name: Company name
# - Date: Report date
# - Transcript text columns
# - One or more *_keyword_count columns (e.g., AI_keyword_count)
#
# Default file path (can be changed in the script):
# file_path = "S:/Strategy Research/Transcripts/Data/Excel/Raw Tariff Mentions.xlsx"
#
# OUTPUT:
# One output table per theme per quarter, labeling companies as Thematic_Engaged or not.
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

warnings.filterwarnings("ignore")

# -------------------------------------------
#%% STEP 1: LOAD & PREPARE TRANSCRIPT DATA
# -------------------------------------------

import_path = "S:/Strategy Research/Transcripts/Data/Thematic Mentions/Raw Thematic Mentions_part1.xlsx"
export_path = "S:/Strategy Research/Transcripts/Data/Thematic Mentions/Thematic Basket Constiuents.xlsx"

if not os.path.exists(import_path):
    raise FileNotFoundError(f"Excel file not found at {import_path}")

df = pd.read_excel(import_path)
df = df[pd.to_datetime(df["Date"], errors='coerce').notna()]
df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
df["Quarter"] = df["Date"].dt.to_period("Q").astype(str)

keyword_cols = [col for col in df.columns if col.endswith("_keyword_count")]
print("[INFO] Data Imported")

# -------------------------------------------
#%% STEP 2: LOOP OVER THEMES AND PROCESS THEMES INDIVIDUALLY
# -------------------------------------------

from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D

print(f"[INFO] Beginning clustering process for {len(keyword_cols)} themes.")
all_outputs = []

# Loop through each theme column in the list of keyword columns
for theme_col in keyword_cols:
    # Remove the '_keyword_count' suffix to get the raw theme name
    theme = theme_col.replace("_keyword_count", "")
    print(f"[PROCESSING THEME: {theme.upper()}]")

    # Extract relevant columns and rename
    theme_df = df[["Ticker", "Company Name", "Quarter", theme_col]].copy()
    theme_df = theme_df.rename(columns={theme_col: "Theme_Mentions"})

    # Aggregate mentions per company per quarter
    theme_df = theme_df.groupby(["Ticker", "Company Name", "Quarter"], as_index=False).sum()
    theme_df = theme_df[theme_df["Theme_Mentions"] > 0]  # Filter out zeros

    # Compute share of mentions per quarter
    total_by_quarter = theme_df.groupby("Quarter")["Theme_Mentions"].transform("sum")
    theme_df["Share_Mentions"] = theme_df["Theme_Mentions"] / total_by_quarter

    # Sort for momentum calculation
    theme_df = theme_df.sort_values(["Ticker", "Quarter"])
    
    # Compute rolling mean of previous 2 quarters (excluding current)
    rolling_mean_prev_2 = theme_df.groupby("Ticker")["Theme_Mentions"].shift(1).rolling(window=2).mean()
    
    # Compute momentum as percent change vs avg of last 2 quarters
    theme_df["Mention_Momentum"] = (
        (theme_df["Theme_Mentions"] - rolling_mean_prev_2) / rolling_mean_prev_2
    ).replace([np.inf, -np.inf], 0).fillna(0)

    # Define numeric features
    feature_cols = ["Theme_Mentions", "Share_Mentions", "Mention_Momentum"]

    # Log transform mentions and share to reduce skew
    theme_df["Theme_Mentions"] = np.log1p(theme_df["Theme_Mentions"])
    theme_df["Share_Mentions"] = np.log1p(theme_df["Share_Mentions"])
    
    # Cap momentum to avoid outliers dominating the score (e.g. within +/-5 range)
    # theme_df["Mention_Momentum"] = theme_df["Mention_Momentum"].clip(lower=-5, upper=5)
    
    # Standardize momentum to avoid outliers dominating the score (e.g. within +/-5 range)
    theme_df["Mention_Momentum"] = np.tanh(theme_df["Mention_Momentum"])  # compress but retain direction

    
    # Prepare features for scoring
    feature_cols = ["Theme_Mentions", "Share_Mentions", "Mention_Momentum"]
    X = theme_df[feature_cols].values
    
    # Standardize features
    X_scaled = StandardScaler().fit_transform(X)
    
    # Assign custom weights if desired (equal weights for now)
    weights = np.array([1.0, 1.0, 1.0])
    theme_df["Engagement_Score"] = (X_scaled @ weights) / weights.sum()
    
    # Mark top 100 per quarter
    theme_df["Thematic_Engaged"] = 0
    for quarter, group in theme_df.groupby("Quarter"):
        top_idx = group.sort_values("Engagement_Score", ascending=False).head(100).index
        theme_df.loc[top_idx, "Thematic_Engaged"] = 1

    theme_df["Theme"] = theme

    # Summary table
    summary_table = []
    for quarter, group in theme_df.groupby("Quarter"):
        top_3 = group.sort_values("Engagement_Score", ascending=False).head(3)
        company_names = list(top_3["Ticker"].values)
        while len(company_names) < 3:
            company_names.append("")
        summary_table.append([
            quarter,
            group[group["Thematic_Engaged"] == 1]["Ticker"].nunique(),
            *company_names
        ])
    summary_df = pd.DataFrame(summary_table, columns=["Quarter", "# Thematic Companies", "Top 1", "Top 2", "Top 3"])
    print(f"\n===== {theme.upper()} THEME SUMMARY =====")
    print(summary_df.to_string(index=False))
    print("=" * 50)

    # === 3D + 2D PLOTS FOR PREVIOUS QUARTER ===
    all_quarters = sorted(theme_df["Quarter"].unique())
    if len(all_quarters) < 2:
        print("[WARN] Not enough quarters for previous quarter visualization.")
        continue
    prev_quarter = all_quarters[-2]
    prev_mask = theme_df["Quarter"] == prev_quarter
    prev_q_df = theme_df[prev_mask].copy()
    X_prev = X_scaled[prev_mask.values]

    labels = prev_q_df["Thematic_Engaged"].map({1: "Engaged", 0: "Not Engaged"})
    colors = prev_q_df["Thematic_Engaged"].map({1: "tab:blue", 0: "lightgray"})

    # 3D plot
    fig = plt.figure(figsize=(7, 5))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(X_prev[:, 0], X_prev[:, 1], X_prev[:, 2], c=colors, alpha=0.6)
    ax.set_title(f"{theme} Engagement – 3D View (Previous Quarter: {prev_quarter})")
    ax.set_xlabel("Theme_Mentions")
    ax.set_ylabel("Share_Mentions")
    ax.set_zlabel("Mention_Momentum")
    ax.legend(handles=[
        Line2D([0], [0], marker='o', color='w', label='Engaged', markerfacecolor='tab:blue', markersize=8),
        Line2D([0], [0], marker='o', color='w', label='Not Engaged', markerfacecolor='lightgray', markersize=8)
    ])
    plt.tight_layout()
    plt.show()

    # 2D marginalized plots
    fig2, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig2.suptitle(f"{theme} Engagement – 2D Marginalized Views ({prev_quarter})")
    axes[0].scatter(X_prev[:, 0], X_prev[:, 1], c=colors, alpha=0.6)
    axes[0].set_title("Mentions vs Share")
    axes[0].set_xlabel("Theme_Mentions")
    axes[0].set_ylabel("Share_Mentions")

    axes[1].scatter(X_prev[:, 0], X_prev[:, 2], c=colors, alpha=0.6)
    axes[1].set_title("Mentions vs Momentum")
    axes[1].set_xlabel("Theme_Mentions")
    axes[1].set_ylabel("Mention_Momentum")

    axes[2].scatter(X_prev[:, 1], X_prev[:, 2], c=colors, alpha=0.6)
    axes[2].set_title("Share vs Momentum")
    axes[2].set_xlabel("Share_Mentions")
    axes[2].set_ylabel("Mention_Momentum")

    for ax in axes:
        ax.grid(True)
    fig2.legend(handles=[
        Line2D([0], [0], marker='o', color='w', label='Engaged', markerfacecolor='tab:blue', markersize=8),
        Line2D([0], [0], marker='o', color='w', label='Not Engaged', markerfacecolor='lightgray', markersize=8)
    ], loc='upper right')
    plt.tight_layout(rect=[0, 0, 0.95, 0.95])
    plt.show()

    # Save relevant columns
    final_cols = ["Ticker", "Company Name", "Quarter", "Theme", "Theme_Mentions",
                  "Share_Mentions", "Mention_Momentum", "Engagement_Score", "Thematic_Engaged"]
    all_outputs.append(theme_df[final_cols])

# -------------------------------------------
# %% STEP 3: COMBINE, DISPLAY & EXPORT OUTPUT
# -------------------------------------------

final_df = pd.concat(all_outputs, ignore_index=True)
print("[INFO] Final thematic baskets created")

# Export each theme to a separate sheet
with pd.ExcelWriter(export_path, engine="xlsxwriter") as writer:
    for theme_name, group in final_df.groupby("Theme"):
        export_cols = ["Quarter", "Ticker", "Company Name", "Theme_Mentions", 
                       "Share_Mentions", "Mention_Momentum", "Engagement_Score", "Thematic_Engaged"]
        group[export_cols].to_excel(writer, sheet_name=theme_name[:31], index=False)

print("[INFO] Excel export completed")

