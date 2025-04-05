# 📄 FactSet Transcript Scraper

This Python script automates the downloading of earnings call transcripts from the **FactSet Document Search** portal, based on a given ticker symbol.

---

## 🎯 Objectives

- Automate transcript collection from FactSet for tickers in the Russell 3000 or other indices.
- Handle UI differences between full-screen and compact FactSet layouts.
- Choose "Save All Documents to One File" as the download option.
- Automatically move the resulting PDF to the correct folder based on ticker.

---

## 🚀 How It Works

1. **Opens FactSet’s Document Search** in a Microsoft Edge WebDriver session.
2. **Inputs the ticker symbol** into the "All Identifiers" field.
3. **Selects all results** using the top-left checkbox.
4. **Clicks the correct download button**, handling both full-screen and compact views.
5. **Chooses the option to save all documents as one file**.
6. **Waits for the file to appear** in the system’s Downloads folder.
7. **Moves the PDF to a pre-defined destination folder** named after the ticker.

---

## 🛠️ Prerequisites

- Windows OS
- [Microsoft Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)
- `selenium` Python library
- Access to [FactSet](https://www.factset.com/) with login permissions

Install the dependencies:

```bash
pip install selenium
```

---

## 📂 Folder Structure

```
/Raw Factset PDF/
    └── TICKER/
          └── TICKER_Timestamp.pdf
```

For example:
```
S:\Strategy Research\Transcripts\Data\Raw Factset PDF\AAPL\AAPL_20250401_153022.pdf
```

---

## 🧪 How to Use

1. Clone this repository.
2. Open `00_Factset Scraper - Web.py`.
3. Replace the `email` variable and `ticker` list with your details.
4. Run the script.

```python
# Example loop
tickers = ["AAPL-US", "MSFT-US", "GOOGL-US"]
for t in tickers:
    download_ticker_pdf(t)
```

The script will:
- Navigate FactSet,
- Download the transcript,
- And move it to the appropriate folder.

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
