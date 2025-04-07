# 🧠 Thematic Analysis (LLM-Powered)

This module enriches filtered earnings transcript data (e.g. AI, Tariffs, Supply Chains) by using large language models (LLMs) to extract **subthemes** and **sentiment** across mentions. 

---

## 🔎 Purpose

Go beyond keyword counts. This tool answers:
- *What* specifically was said about a theme? (Subthemes)
- *How* was it said? (Sentiment)

It helps you detect tone shifts, emerging subtopics, and management focus—quarter by quarter.

---

## 🗂️ Subtheme Classification

Analyzes the mentions of a topic and generates a set of more granular categories using GPT.

**Example**  
Input:  
> “We increased investment in internal GenAI tools.”  
Output:  
```json
{ "subtheme": "GenAI Tools", "Investment", "confidence_score": 0.94 }
```

---

## 🎭 Sentiment Analysis

Labels each mention with a sentiment score `Positive` (+1), `Neutral` (0), or `Negative` (-1), with optional reasoning.

**Example**  
Input:  
> “Cost cuts have delayed progress on AI initiatives.”   
Output:  
```json
{ "sentiment": "Negative", "reasoning": "Delays due to cost cuts." }
```

---

## 🖼️ Visual Outputs

- 📊 Subtheme frequency over time (e.g., GenAI vs. AI Chips)
- 🎭 Sentiment trends across companies or sectors
- 🧩 Theme x Subtheme matrices


---

## 🛠️ Requirements

- Python 3.8+
- `openai`, `pandas`, `tqdm`
- Optional: `langchain`, `transformers` for model handling

```bash
pip install -r requirements.txt
```

---


## 📄 License

MIT License  
Copyright (c) 2025 Steven Fandozzi

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT) – free to use, modify, and distribute with attribution.
---
