# -*- coding: utf-8 -*-
"""
Created on Sat Apr 12 12:40:18 2025

@author: Steven.Fandozzi
"""

# ==============================================
# Thematic Stock Weight Allocation
# ==============================================
# This script builds weighted investment baskets using:
# 1. Engagement data by theme (e.g., mentions, momentum).
# 2. Fundamental metrics vs history and sector (e.g., valuation, ROE, growth).
#
# Input:
#   - `engagement_df`: Theme engagement scores per company and quarter.
#   - `fundamentals_df`: Quant metrics like valuation vs 5Y avg, ROE vs sector.
#
# Process:
#   - Standardize and winsorize key metrics.
#   - Apply multiple scoring methods (PCA, ranks, min, geometric avg, etc.).
#   - Combine each with thematic engagement score.
#   - Generate portfolio weights per theme and quarter.
#
# Output:
#   - CSV with weights and composite scores per company.
#   - Visualization of score distributions across strategies.

#%% STEP 1: LOAD AND MERGE DATA
# --------------------------------------------------
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Load theme engagement output (combined across themes)
theme_output_path = "path_to_engagement_outputs.csv"  # Replace with actual path
engagement_df = pd.read_csv(theme_output_path)

# Load quant metrics (valuation, ROE, earnings growth)
quant_fundamentals_path = "path_to_quant_fundamentals.csv"  # Replace with actual path
fundamentals_df = pd.read_csv(quant_fundamentals_path)

# Merge on Ticker and Quarter (or Date)
merged_df = pd.merge(
    engagement_df,
    fundamentals_df,
    on=["Ticker", "Quarter"],
    how="inner"
)

#%% STEP 2: CLEAN AND PREP FEATURES
# --------------------------------------------------
# Required quant columns (6 inputs)
quant_cols = [
    "Valuation_5YZ", "Valuation_SectorZ",
    "ROE_5YZ", "ROE_SectorZ",
    "Growth_5YZ", "Growth_SectorZ"
]

# Drop missing data
merged_df = merged_df.dropna(subset=quant_cols + ["Engagement_Score"])

# Winsorize outliers
for col in quant_cols:
    merged_df[col] = merged_df[col].clip(lower=merged_df[col].quantile(0.01), upper=merged_df[col].quantile(0.99))

# Standardize quant features
scaler = StandardScaler()
quant_scaled = scaler.fit_transform(merged_df[quant_cols])
quant_scaled_df = pd.DataFrame(quant_scaled, columns=quant_cols)

#%% STEP 3: DEFINE MULTIPLE FUNDAMENTAL SCORE METHODS
# --------------------------------------------------
def simple_average(df):
    return df.mean(axis=1)

def weighted_sum(df, weights):
    return df @ np.array(weights)

def pca_score(df, n_components=1):
    pca = PCA(n_components=n_components)
    return pca.fit_transform(df)[:, 0], pca.components_

def min_across_dimensions(df):
    return df.min(axis=1)

def multiplicative_score(df):
    return df.prod(axis=1) ** (1.0 / df.shape[1])

def rank_based_score(df):
    return df.rank(pct=True).mean(axis=1)

# Apply each method
merged_df["Fundamental_SimpleAvg"] = simple_average(quant_scaled_df)
merged_df["Fundamental_Min"] = min_across_dimensions(quant_scaled_df)
merged_df["Fundamental_Multiplicative"] = multiplicative_score(quant_scaled_df)
merged_df["Fundamental_RankAvg"] = rank_based_score(quant_scaled_df)
merged_df["Fundamental_Weighted"] = weighted_sum(quant_scaled_df, [0.4, 0.2, 0.15, 0.1, 0.1, 0.05])
merged_df["Fundamental_PCA"], pca_components = pca_score(quant_scaled_df)

#%% STEP 4: COMBINE WITH ENGAGEMENT AND COMPARE
# --------------------------------------------------
def create_composite_score(fund_score):
    return 0.5 * merged_df["Engagement_Score"] + 0.5 * fund_score

score_methods = [
    "Fundamental_SimpleAvg",
    "Fundamental_Weighted",
    "Fundamental_Min",
    "Fundamental_Multiplicative",
    "Fundamental_RankAvg",
    "Fundamental_PCA"
]

# Store results
final_outputs = []

for method in score_methods:
    label = f"Composite_{method.split('_')[-1]}"
    merged_df[label] = create_composite_score(merged_df[method])
    merged_df[f"Weight_{label}"] = merged_df.groupby(["Theme", "Quarter"])[label].transform(
        lambda x: np.clip(x, a_min=0, a_max=None) / np.clip(x, a_min=0, a_max=None).sum()
    )
    final_outputs.append((label, f"Weight_{label}"))

#%% STEP 5: VISUALIZE COMPARISON
# --------------------------------------------------
plt.figure(figsize=(10, 6))
for label, _ in final_outputs:
    plt.hist(merged_df[label], bins=50, alpha=0.5, label=label)
plt.legend()
plt.title("Comparison of Composite Score Distributions")
plt.xlabel("Score")
plt.ylabel("Frequency")
plt.tight_layout()
plt.show()

#%% STEP 6: EXPORT SAMPLE OUTPUT
# --------------------------------------------------
out_cols = ["Theme", "Quarter", "Ticker", "Company Name"] + [f for _, f in final_outputs]
merged_df[out_cols].to_csv("path_to_composite_scores.csv", index=False)
print("[INFO] Composite scores and weights exported for review.")
