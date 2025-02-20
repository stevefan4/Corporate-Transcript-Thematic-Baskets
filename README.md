📊 Corporate Transcript Thematic Baskets
Pipeline to input themes and generate a basket of stocks for an index.

This project enables users to analyze corporate transcripts by identifying mentions of a given theme, tracking subthemes, and ultimately constructing a thematic stock basket.

🚀 Features
Input a theme and extract relevant mentions from corporate transcripts
Identify subthemes associated with the given theme
Construct a stock basket based on companies most engaged with the theme
🏗️ Workflow
Input a Theme – Specify a broad theme (e.g., AI, Supply Chain, Inflation)
Extract Mentions – Identify and quantify how often the theme appears in corporate transcripts
Subtheme Detection – Recognize common subthemes related to the primary theme
Basket Construction – Generate a stock basket based on companies frequently discussing the theme
📂 Repository Structure
bash
Copy
Edit
📦 Corporate-Transcript-Thematic-Baskets
├── 📁 data              # Raw transcript data and preprocessed outputs  
├── 📁 notebooks         # Jupyter notebooks for exploration and testing  
├── 📁 src              # Main pipeline scripts  
│   ├── extract.py      # Extract mentions of a theme  
│   ├── subthemes.py    # Identify subthemes  
│   ├── basket.py       # Generate stock basket  
├── 📜 requirements.txt  # Dependencies  
├── 📜 README.md         # Project documentation  
⚙️ Installation
Clone the repository and install dependencies:

bash
Copy
Edit
git clone https://github.com/your-repo/Corporate-Transcript-Thematic-Baskets.git
cd Corporate-Transcript-Thematic-Baskets
pip install -r requirements.txt
🛠️ Usage
Run the pipeline by specifying a theme:

bash
Copy
Edit
python src/extract.py --theme "AI"
python src/subthemes.py --theme "AI"
python src/basket.py --theme "AI"
📈 Example Output
Top 10 Companies Discussing the Theme
Key Subthemes & Their Frequency
Generated Stock Basket & Weightings
💡 Future Enhancements
Support for multiple transcript sources
Sentiment analysis for theme mentions
Weighting stock baskets based on importance of mentions
👨‍💻 Contributions welcome! Feel free to open issues or submit pull requests.

