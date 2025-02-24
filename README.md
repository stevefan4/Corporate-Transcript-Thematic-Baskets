
# 📊 Corporate Transcript Thematic Baskets  

> **A complete pipeline to analyze corporate transcripts, detect thematic mentions, build charts, identify stock basket constiuents, identify subtopics, and identify sentiment.**  

This project enables investors and researchers to **track how companies discuss specific themes in earnings calls**. By integrating **structured and unstructured data sources**, **LLM-powered keyword generation**, **context-aware NLP models**, and **dashboard visualizations**, the pipeline allows for **granular thematic analysis** of corporate transcripts.  

---

## 🚀 **Key Features**  

✅ **Thematic Mention Identification** – Scrape **corporate transcripts** for mentions of a particular theme. 

✅ **Stock Basket Creation** – Build **custom stock baskets** based on company engagement with themes.  

✅ **Subtheme Breakdown** – Classify mentions into **detailed subthemes** for deeper insights.  

✅ **Sentiment Analysis** – Determine whether mentions are **positive, negative, or neutral**.  

✅ **Thematic Trends & Charts** – Track **how themes evolve over time**, across sectors, and by company size.  

✅ **Interactive Dashboard** – Filter by **company, theme, sentiment**, and more for flexible analysis.  

---

## 🏗️ **How It Works**  

### **📂 Step 1: Data Collection**  
1️⃣ **Scrape Transcripts** – Extract **earnings call transcripts** from **FactSet** into PDF format.  
2️⃣ **Convert to Structured Data** – Process PDFs into structured **Excel datasets** for analysis.  

### **🔍 Step 2: Themematic Mention Detection**  
3️⃣ **Find Theme Mentions** – Use a **keyword-based filter** to detect sentences related to key themes.  
4️⃣ **Remove False Positives (LLM-powered)** – Ensure that keyword hits are **truly** relevant to the theme.  
5️⃣ **Extract Context** – Identify surrounding sentences that provide **additional context** to theme mentions.  

### **🎯 Step 3: Thematic Analysis**
6️⃣ **Classify Themes & Subthemes** – Organize mentions into **detailed subthemes**.  
7️⃣ **Analyze Sentiment (LLM-powered)** – Determine whether mentions are **positive, negative, or neutral**.  

### **📊 Step 4: Data Presentation & Visualization**  
8️⃣ **Stock Basket Generation** – Identify companies with **high thematic engagement**.  
9️⃣ **Trend & Chart Analysis** – Visualize **theme trends, sector engagement, and company size comparisons**.  
🔟 **Interactive Dashboard** – Explore data with **filters for theme, sentiment, and companies**.  

---

## 📂 Repository Structure  

```
📦 Corporate-Transcript-Thematic-Baskets
├── 📁 data                # Raw transcript data & preprocessed structured data  
├── 📁 notebooks           # Jupyter notebooks for exploration and testing  
├── 📁 src                 # Core pipeline scripts  
│   ├── extract.py        # Scrapes & extracts transcripts from FactSet & PDFs  
│   ├── keyword_builder.py # Uses LLM to generate theme-specific keywords  
│   ├── keyword_finder.py  # Identifies keyword matches & validates theme relevance  
│   ├── context_model.py   # Detects surrounding context of a theme discussion  
│   ├── subthemes.py       # Identifies subthemes within transcripts  
│   ├── basket.py          # Generates a stock basket based on theme mentions  
│   ├── dashboard.py       # Builds a Power BI or Streamlit dashboard for visualization  
├── 📜 requirements.txt     # Dependencies  
├── 📜 README.md            # Project documentation  
```

---

## ⚙️ Installation  

Clone the repository and install dependencies:  

```bash
git clone https://github.com/your-repo/Corporate-Transcript-Thematic-Baskets.git
cd Corporate-Transcript-Thematic-Baskets
pip install -r requirements.txt
```

---

## 🛠️ Usage  

Run the pipeline in sequential steps:  

### 1️⃣ **Scrape & Process Transcripts**  
```bash
python src/extract.py --source "FactSet" --pdf_folder "data/pdfs/"
```

### 2️⃣ **Generate Keywords (LLM-Powered)**  
```bash
python src/keyword_builder.py --theme "AI"
```

### 3️⃣ **Identify Keyword Matches & Validate Context**  
```bash
python src/keyword_finder.py --theme "AI"
```

### 4️⃣ **Analyze Theme Context**  
```bash
python src/context_model.py --theme "AI"
```

### 5️⃣ **Identify Subthemes**  
```bash
python src/subthemes.py --theme "AI"
```

### 6️⃣ **Generate Thematic Stock Basket**  
```bash
python src/basket.py --theme "AI"
```

### 7️⃣ **Launch the Interactive Dashboard**  
```bash
python src/dashboard.py
```

---

## 📈 Example Output (Theme: AI)  

### 🔹 **Top 10 Companies Discussing the Theme**  
| Rank | Company      | Mentions | Confidence |
|------|------------|----------|------------|
| 1    | Microsoft  | 142      | 95%        |
| 2    | Tesla      | 125      | 92%        |
| 3    | Nvidia     | 119      | 88%        |
| 4    | Alphabet   | 98       | 85%        |
| 5    | Meta       | 87       | 82%        |

### 🔹 **Key Subthemes & Frequency**  
```
AI Theme:  
   • "Generative AI" (74 mentions)  
   • "AI in Automation" (58 mentions)  
   • "AI Regulation" (32 mentions)  
   • "AI & Cloud Computing" (29 mentions)  
```

### 🔹 **Generated Stock Basket & Weightings**  
```
AI Thematic Basket:  
   • Nvidia - 35%  
   • Microsoft - 25%  
   • Alphabet - 20%  
   • Tesla - 10%  
   • Meta - 10%  
```

---

## 📊 Dashboard Preview  

The dashboard provides **real-time filtering by company & theme**:  

- **Company-Specific View** – Select a company to see its **mentions & sentiment trends**.  
- **Theme-Level Analysis** – Explore **subtheme frequencies & contextual insights**.  
- **Historical Trends** – Track **quarterly engagement** with themes over time.  

```bash
python src/dashboard.py
```

---

## 🔮 Future Enhancements  

🔜 **Multi-source Support** – Expand coverage beyond earnings transcripts.  
🔜 **Sentiment Analysis** – Determine **positive/negative tone** behind mentions.  
🔜 **Real-time Updates** – Automate data retrieval and basket adjustments.  
🔜 **API Integration** – Connect with financial APIs for enhanced insights.  

---

## 🤝 Contributing  

🛠 **Want to contribute?** Follow these steps:  

1. **Fork the repository**  
2. **Create a new branch** (`git checkout -b feature-branch`)  
3. **Commit your changes** (`git commit -m "Added a new feature"`)  
4. **Push to the branch** (`git push origin feature-branch`)  
5. **Submit a Pull Request**  

---

## 📜 License  

This project is licensed under the **MIT License** – free to use, modify, and distribute.  

---

🚀 **Start analyzing corporate transcripts and building dynamic stock baskets today!** 🏆  

---

