
---

# 📊 Corporate Transcript Thematic Baskets  

> **A pipeline to analyze corporate transcripts, detect thematic mentions, identify subthemes, and generate a stock basket based on company engagement.**  

This project helps investors and researchers **track how companies discuss specific themes in earnings calls**. By analyzing transcript mentions, we can **quantify company engagement**, detect **emerging subthemes**, and **construct a stock basket** that reflects the most thematically engaged companies.  

---

## 🚀 Features  

✅ **Thematic Identification** – Input a broad theme (e.g., `"AI"`, `"Inflation"`, `"Reshoring"`) and detect its mentions in earnings transcripts.  

✅ **Subtheme Detection** – Identify **related subtopics** that emerge organically in corporate discussions.  

✅ **Stock Basket Construction** – Generate a list of companies based on their engagement with the theme.  

✅ **Dynamic Analysis** – Track trends over time and across different industries.  

---

## 🏗️ How It Works  

📌 **Step 1: Input a Theme**  
Specify a **theme keyword** to analyze (e.g., `"Cloud Computing"`, `"De-dollarization"`, `"Labor Costs"`).  

📌 **Step 2: Extract Mentions**  
The pipeline scans corporate transcripts to **count occurrences, identify trends, and extract key passages**.  

📌 **Step 3: Detect Subthemes**  
Common **subtopics** that emerge in discussions are detected and ranked based on their frequency.  

📌 **Step 4: Construct a Stock Basket**  
Companies most engaged in the theme are included in a **custom thematic stock basket**, useful for investment screening.  

---

## 📂 Repository Structure  

```
📦 Corporate-Transcript-Thematic-Baskets
├── 📁 data              # Raw transcript data and preprocessed outputs  
├── 📁 notebooks         # Jupyter notebooks for exploration and testing  
├── 📁 src              # Core pipeline scripts  
│   ├── extract.py      # Extract mentions of a theme  
│   ├── subthemes.py    # Identify subthemes within transcripts  
│   ├── basket.py       # Generate stock basket based on company mentions  
├── 📜 requirements.txt  # Dependencies  
├── 📜 README.md         # Project documentation  
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

### 🔍 **Extract Theme Mentions**  
```bash
python src/extract.py --theme "AI"
```

### 🔎 **Identify Subthemes**  
```bash
python src/subthemes.py --theme "AI"
```

### 📊 **Generate Thematic Stock Basket**  
```bash
python src/basket.py --theme "AI"
```

---

## 📈 Example Output (Theme: AI)

### 🔹 **Top 10 Companies Discussing the Theme**  
| Rank | Company      | Mentions |
|------|------------|----------|
| 1    | Microsoft  | 142      |
| 2    | Tesla      | 125      |
| 3    | Nvidia     | 119      |
| 4    | Alphabet   | 98       |
| 5    | Meta       | 87       |
| 6    | Amazon     | 74       |
| 7    | IBM        | 63       |
| 8    | Oracle     | 52       |
| 9    | Salesforce | 47       |
| 10   | Adobe      | 39       |

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

## 🔮 Future Enhancements  

🔜 **Multi-source Support** – Expand coverage beyond earnings transcripts.  
🔜 **Sentiment Analysis** – Determine **positive/negative tone** behind mentions.  
🔜 **Real-time Updates** – Automate data retrieval and basket adjustments.  
🔜 **API Integration** – Connect with financial data sources for enhanced insights.  

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

🚀 **Start analyzing corporate transcripts and build your own stock baskets today!** 🏆  

---

This version is **optimized for GitHub readability**, ensuring clear **headings, bullet points, code blocks, tables, and emojis** for an engaging and professional look. Let me know if you want any tweaks! 🚀

