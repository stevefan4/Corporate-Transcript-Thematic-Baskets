# 🔍 Thematic Mention Detection in Corporate Transcripts

### 🌐 Understand Market Narratives, One Sentence at a Time

Have you ever wondered how often company executives talk about **AI**, **Inflation**, or **China**? This part of the project helps you *quantify* those narratives across **thousands of corporate earnings calls**. Whether you're an analyst, investor, strategist, or researcher, this tool will show you **when**, **where**, and **how** key themes are discussed — with *surgical precision*.

---

## ✨ What This Project Does

Now that we have structured data, this portion of the pipeline filters massive volumes of transcripts down to just the **most relevant sections** — the ones that mention your selected **themes**, like:

> “Interest Rates” · “Supply Chains” · “Consumer Weakness” · “ESG” · “Politics” · “AI”

It works in **five steps**:

1. **Keyword Generation** (Optional, but powerful)  
   Use GPT-4 to automatically generate smart, relevant keywords for your theme.

2. **Sentence-Level Analysis**  
   Split transcripts into individual sentences for more accurate keyword matching.

3. **Smart Matching & Context Extraction**  
   Find exact keyword hits, then **pull nearby sentences** to preserve context and narrative flow.

4. **Export Structured Results**  
   Save an analysis-ready Excel file showing which companies talked about your theme — and what they said.

---

## 🧠 Example Use Cases

> You’re researching how companies talk about **AI** in 2025. With this tool, you can:
- 🔍 See how often AI was mentioned per quarter
- 💬 View specific excerpts from transcripts
- 📊 Compare mentions across sectors or companies
- 📁 Export structured data for modeling or visualization

---

## 📦 What’s Inside This Repo?

```
📂 ThematicMentionPipeline
├── generate_keywords.py        # Uses GPT-4 to create keywords for a theme
├── process_transcripts.py      # Main script to clean, match, and export transcript data
├── data/
│   ├── RAW 2021-Cal TRANSCRIPT.xlsx
│   ├── RAW 2022-Cal TRANSCRIPT.xlsx
│   └── RAW 2023/2024/etc...
├── output/
│   └── RAW Thematic Mentions_part1.xlsx  # Final structured outputs
├── README.md
└── requirements.txt
```

---

## ⚙️ How It Works (Step-by-Step)

### 🔧 Step 1: Generate Keywords with GPT-4 *(Optional)*

Want to build a vocabulary for "Supply Chain Disruptions" or "Political Uncertainty"?  
Run:

```bash
python generate_keywords.py
```

You’ll be prompted to enter a **theme** and an optional number of keywords.  
The script uses GPT-4 to generate detailed keywords like:

```
disruption
logistics bottleneck
inventory delays
supplier concentration
```

Keywords are saved as an Excel file for future use.

---

### 📄 Step 2: Clean and Structure Transcripts

The script loads raw Excel transcript files and merges different parts like:

- **Management commentary**
- **Q&A sections**

It combines them into one unified, easy-to-read transcript per company and date.

---

### ✂️ Step 3: Split Into Sentences

We break the transcript into **individual sentences** using punctuation — so we can match **only exact, relevant parts**, not just loose fragments or document-wide matches.

Example:

```
Before: "The company expects higher capex due to AI-related demand in 2024."
After:
1. The company expects higher capex due to AI-related demand in 2024.
```

---

### 🧮 Step 4: Match Keywords + Pull Context

This is the magic step. The script:

1. Looks for your keywords (like "AI", "machine learning", "neural network") in each sentence.
2. Pulls the *nearby sentences* to capture the full context (you set the sentence window).
3. Records the keyword counts in each chunk.

So instead of just a raw keyword match, you get:

> "**AI** will be crucial to our growth next year. We're deploying large-scale LLMs in customer service. That said, hiring remains a challenge."

---

### 📤 Step 5: Export to Excel

The results are structured, chunked by company and date, and ready to analyze:

| Ticker | Date | Company Name | Theme: AI Count | Theme: China Count |  Transcript Mention|
|--------|------|--------------|------------------|---------------------|---------------------|
| AAPL   | Q2-24| Apple        | 3                | 0                   | “We’re using AI in…”|

Results are saved in the `output/` folder. If the file is too big, it will automatically break into smaller chunks (`part1`, `part2`, etc).

---

## 📥 Input Files

Ensure the following files are placed in the `data/` directory:

- `RAW 20XX-Cal TRANSCRIPT.xlsx`  
  *(Your base transcript files for each year)*

- `Thematic Vocab.xlsx`  
  *(Columns = Themes; Rows = Keywords)*

- `Tickers_ALL.xlsx`  
  *(Optional sector metadata to group companies)*

---

## 🧰 Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

Includes:
- `openai` – For GPT-4 keyword generation
- `pandas`, `tqdm`, `numpy` – For data handling and speed
- `openpyxl`, `xlrd` – For Excel export/import
- `re`, `os`, `datetime` – For core Python functionality

---

## 🔐 OpenAI API Key

To use GPT-4 keyword generation, add your API key here in `generate_keywords.py`:

```python
openai.api_key = "YOUR_OPENAI_KEY"
```

Or set it securely using environment variables.

---

## 🧭 Future Improvements

- 🔍 Add GPT-powered **false positive filtering**
- 💬 Incorporate **sentiment analysis**
- 📈 Add charts of theme frequency over time
- 🕸️ Add **co-occurrence mapping** of themes (e.g., AI + Efficiency)

---

## 🙌 Contributing

Want to help make this even more powerful?

Feel free to fork, open issues, or submit pull requests!  
Whether it’s fixing bugs, adding features, or improving documentation — all contributions are welcome.

---

## 📄 License

This project is open-sourced under the **MIT License** — feel free to use, adapt, and share.

---

## 💬 Final Thoughts

This project was built to help **cut through the noise** in a sea of transcripts and **zero in on what really matters** — the words that shape markets.

If you ever thought “I wish I knew what companies were *really* saying about [insert theme],” this is your tool.

> 🚀 Let’s make narrative alpha measurable.

---

Let me know if you want to turn this into a GitHub Pages site, add charts, or embed example screenshots.
