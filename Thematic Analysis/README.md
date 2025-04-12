# 🧠 Thematic Analysis (LLM-Powered)

Welcome to the **LLM-Powered Thematic Analysis** module. 

Built on top of filtered earnings transcript data (e.g. AI, Tariffs, Supply Chains), this module leverages the power of large language models to automatically extract **subthemes** and assess **sentiment** with a high level of contextual understanding. Rather than just counting how many times a keyword is mentioned, we dive into *what’s actually being said*—and *how* it's being said.

---

## 🔎 Purpose

Keyword counts are a blunt instrument. This module provides surgical precision.

### This tool answers:
- **What** specifically is being discussed about a theme?  
  → *Are companies discussing AI in the context of automation, internal tools, or competitive threats?*
- **How** are they discussing it?  
  → *Are they optimistic, cautious, or concerned?*

By enriching transcript datasets with subthemes and sentiment, this module enables:
- Faster detection of tone shifts and language inflections
- Discovery of granular management priorities within broad themes
- More structured, scalable thematic research across quarters and sectors

Whether you're a strategist tracking macro trends or a PM surfacing sector rotation opportunities, this gives you the linguistic edge.

---

## 🗂️ Subtheme Classification

Traditional NLP pipelines may tell you that “AI” was mentioned 120 times. This module tells you that:
- 30 of those were about **cost savings**
- 25 about **product integration**
- 20 about **internal tooling**
- 10 about **regulatory risks**  
…and whether management was bullish or bearish in each case.

### How it works:
Each transcript mention tied to a major theme is analyzed using a transformer-based LLM, which returns:
- `subtheme`: A concise label describing the specific topic discussed within the broader theme
- `sentiment`: A directional tone (positive, negative, neutral)
- `confidence_score`: A probability-weighted measure of classification accuracy

**Example**  
Input:  
> “We increased investment in internal GenAI tools to streamline productivity.”  
Output:  
```json
{ 
  "subthemes": ["GenAI Tools", "Investment", "Productivity"], 
  "sentiment": "Positive",
  "confidence_score": 0.94 
}
```

---

## 🎭 Sentiment Analysis

Understanding **how** something is said is just as important as knowing **what** was said.

This module uses LLMs to assign sentiment labels to each mention of a theme in earnings transcripts, providing an intuitive signal on management’s tone—without relying on naive word lists or rigid rule-based systems.

### How it works:
For every theme mention, the model returns:
- `sentiment`: One of three values — `Positive` (+1), `Neutral` (0), or `Negative` (-1)
- `reasoning` (optional): A short natural-language explanation capturing the rationale behind the classification

**Example**  
Input:  
> “Cost cuts have delayed progress on AI initiatives.”  
Output:  
```json
{
  "sentiment": "Negative",
  "reasoning": "Delays due to cost cuts."
}
```

This contextual sentiment analysis captures nuances like optimism despite challenges, concern despite progress, or neutral corporate-speak hiding caution.


---

## 🛠️ Requirements

Get started in minutes. The module is lightweight and modular.

**Core Requirements**  
- Python 3.8+
- [OpenAI API](https://platform.openai.com/docs/) (or your own hosted LLM)
- `pandas` for data handling
- `tqdm` for progress tracking

**Optional Enhancements**  
- `langchain` or `transformers` for advanced LLM chaining and custom prompts
- `matplotlib`, `plotly`, or `seaborn` for bespoke visualizations

**Installation**  
```bash
pip install -r requirements.txt
```

---

## 🔄 Workflow Overview

1. **Input**: A filtered transcript DataFrame with rows tagged by theme (e.g., AI, Tariffs)
2. **Subtheme & Sentiment Extraction**: Processed via LLM, adding structured context
3. **Output**: Enhanced DataFrame with subtheme, sentiment, and reasoning columns
4. **Visualization**: Optional chart generation or export to dashboard platform

---

## 📄 License

**MIT License**  
Copyright (c) 2025  
Created and maintained by **Steven Fandozzi**

---
