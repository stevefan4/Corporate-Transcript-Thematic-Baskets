# 📄 Transcript Scraper

Factset provides a document search functionality through their application and website. This Python script automates the downloading of earnings call transcripts from the **FactSet Document Search** portal, based on a given ticker symbol. Then converts the downloaded pdfs into a structured dataset. 

---

## 🎯 Objectives

- Automate transcript collection from FactSet for tickers in the Russell 3000 or other indices.
- Handle UI differences between full-screen and compact FactSet layouts.
- Automatically move the resulting PDF to the correct folder based on ticker.
- Extract unstructured text from PDFs and create a structured dataset.

---

## 🚀 How To Operate

1. **Set Universe of Tickers** in an Excel to be imported. Should be Factset Tickers (pulled from constiuents) with -{country}.
2. **Set Parameters** like date range and email. 
3. **Open FactSet’s Document Search** either automatically in a Microsoft Edge WebDriver session or using the platform.
4. **Loops over ticker symbols** and downloads into destination folder
5. **Extract Text** from PDFs and move to an Excel where each row corresponds w/ a transcript for further analysis

---

## 🛠️ Prerequisites

- Windows OS
- [Microsoft Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)
- Access to [FactSet](https://www.factset.com/) or application with login permissions

---

## 📂 Folder Structure

```
/Transcripts
    └── Additional/
          └── Tickers.xlsx
          └── All_Tickers.xlsx
    └── Data/
        └── Excel/
        └── Raw Factset PDF/
            └── NVDA/
            └── MSFT/
            └── ETC/
    └── Python/
          └── Data Scrape/
              └── 00_Factset Scraper - PC.py
              └── 00_Factset Scraper - Web.py
              └── 01_PDF Scraper.py

```

For example:
```
S:\Strategy Research\Transcripts\Data\Raw Factset PDF\AAPL\AAPL_20250401_153022.pdf
```

---

## 🧩 Notes

- Make sure **FactSet is allowed in your browser pop-up settings**.
- If you’re using VPN or dual-authentication, you may need to log in manually.
- Downloads are identified by `"smart search"` or `"transcript"` in the file name.

---

## 🙋‍♂️ Support

Found a bug or want to add enhancements? Open an issue or submit a pull request!

---

Let me know if you'd like this to include screenshots, a GIF demo, or a badge-style status panel for GitHub.
