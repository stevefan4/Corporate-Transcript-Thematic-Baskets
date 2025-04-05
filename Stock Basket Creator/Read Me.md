# 🧺 Thematic Stock Baskets, powered by words — not guesswork.

### Turn Narratives into Portfolios – Automatically Build Custom Stock Baskets from What Companies *Say*

This module helps you go from **text to tradeable insight**, constructing a **live stock basket** each quarter based on how deeply companies are engaging with a particular **theme**.

---

## 🌟 What This Module Does

This workflow is the second part of our thematic analysis engine.  
It starts with the structured Excel file from your `Thematic Mention Detection` process, and ends with:

🎯 A **curated portfolio** of companies deeply engaged with your chosen theme  
⚪ A **background universe** of companies who barely mention it

---

## 🔍 Step-by-Step Overview

| Step | Description |
|------|-------------|
| **Feature Matrix** | Convert keyword data into a structured numeric representation per company |
| **PCA** | Reduce dimensionality while preserving signal |
| **Clustering** | Separate companies into “Engaged” vs. “Not Engaged” groups |
| **Review & Validate** | Visualize, inspect, and confirm quality of the basket |
| ✅ **Output** | Quarterly basket of stocks, ready for modeling, testing, or deployment |

---

## 🧬 Step 1: Build the Feature Matrix

For each company and quarter, we generate a **feature vector** summarizing engagement with the theme.

| Feature | Description |
|---------|-------------|
| `Total Mentions` | Raw count of keyword hits |
| `Mention Share` | Share of mentions vs. sector peers |
| `Mention Momentum` | QoQ and YoY growth in keyword count |
| `Text Embeddings` *(optional)* | Numerical representation of sentence-level context |
| `Final Feature Vector` | Combined numeric profile of a company’s narrative footprint |

---

## 🌀 Step 2: Reduce Dimensionality with PCA

We use **Principal Component Analysis (PCA)** to reduce noise and compress features:

- Normalize with `StandardScaler`
- Reduce to ~10 components while preserving >80–90% variance
- Result: a clean, compressed signal from messy language data

---

## 🤖 Step 3: Cluster into “Engaged” vs. “Not Engaged”

With the PCA output, we run **KMeans** clustering:

- `n_clusters = 2`: One cluster is the thematic core; the other is background noise
- Label companies based on average scores per cluster
- Output is a clear separation of 🎯 "Engaged Companies" and ⚪ "Everyone Else"

---

## 🧪 Step 4: Review and Validate

We don’t just let the algorithm decide — we **check the work**:

- 📉 Visualize in 2D (PCA_1 vs. PCA_2)
- 🧮 Calculate silhouette score and cluster distances
- 👀 Spot-check known leaders to confirm proper assignment

> Example: If you're studying **Reshoring**, you’d expect companies like DE, CAT, and HON to be in the “Engaged” bucket.

---

## 📤 Final Output

The result is a fully exportable Excel file, per quarter, with all company-level stats:

| Ticker | Company | Quarter | Cluster | Term Count | Momentum | PCA_1 | PCA_2 | ... |
|--------|---------|---------|---------|------------|----------|-------|-------|-----|
| NVDA   | Nvidia  | Q1-24   | 🎯 Engaged | 22       | +32%     | 1.02  | 0.87  |     |
| CSCO   | Cisco   | Q1-24   | ⚪ Not Engaged | 4    | -8%      | -0.45 | 0.12  |     |

Save these results to:
```
/output/Thematic_Basket_AI_Q1_2024.xlsx
```

---

## 💼 Use Cases

This tool is built for:

🧠 **Sell-side research analysts**: Back your thematic calls with language data  
📈 **Buy-side PMs**: Build smarter, more relevant baskets  
📊 **Quant teams**: Blend NLP signals into risk models or trade ideas  
🎓 **Researchers**: Study market narratives over time

---

## 📥 Input File

This module requires the structured Excel output from the mention-detection pipeline:
```
RAW Thematic Mentions_part1.xlsx
```

Must include:
- Ticker / Company
- Quarter / Date
- Keyword counts
- Optional: contextual sentence data

---

## ⚙️ How to Use

```bash
python create_stock_basket.py
```

You’ll be guided through:
- Selecting the theme to analyze (e.g., “AI”)
- Choosing one or more quarters
- Reviewing cluster validity
- Saving the final basket

---

## 📊 Coming Soon

- 🧾 Weighting logic (equal weight, momentum weight, market-cap adjusted)
- 🧪 Integration with backtest engine
- 🧠 Use of LLM embeddings to improve feature quality
- 🧰 Bloomberg & Excel export compatibility

---

## 🧰 Requirements

Install the full toolkit with:

```bash
pip install -r requirements.txt
```

Main packages:
- `pandas`, `numpy`, `scikit-learn`, `openpyxl`, `matplotlib`, `seaborn`, `tqdm`

---

## 🤝 Contributing

We’d love your help making this tool even better.

Got an idea for better clustering?  
Want to add a weighting engine or backtest module?  
Open an issue or submit a pull request!

---

## 📄 License

This project is open source under the [MIT License](https://opensource.org/license/mit/).

> Feel free to use, adapt, and expand it — just link back to this repo if it helps you build something cool!

---
