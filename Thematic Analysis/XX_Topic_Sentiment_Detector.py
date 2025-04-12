# -*- coding: utf-8 -*-
"""
Created on Fri Apr 11 21:16:47 2025

@author: Steven.Fandozzi
"""

# -------------------------------
# 📚 Import necessary libraries
# -------------------------------
import pandas as pd
import openai
from tqdm import tqdm
import json
import os

# -------------------------------
# STEP 1: Set your Topic, OpenAI API 🔐, and Define 📁 Paths
# -------------------------------

current_theme = 'AI' # Replace with your Current Theme
openai.api_key = "YOUR_OPENAI_API_KEY" # Replace with your actual API key
input_path = r'S:\Strategy Research\Transcripts\Data\Thematic Mentions\RAW {current_theme} Mentionss.xlsx'  
output_path = r'S:\Strategy Research\Transcripts\Data\Thematic Mentions\Proccessed {current_theme} Mentionss.xlsx'  

# -------------------------------
#%% 📥 STEP 2: Load the Excel data
# -------------------------------
print("📥 Loading transcript mentions from Excel...")
if not os.path.exists(input_path):
    raise FileNotFoundError(f"❌ File not found at path: {input_path}")

df = pd.read_excel(input_path)

# Preview the first few rows
print("\n✅ Preview of loaded data:")
print(df.head())

# Validate required column
if "transcript_text" not in df.columns:
    raise KeyError("❌ Column 'transcript_text' not found in the Excel file. Please check your input file.")

# -------------------------------
#%% 🧠 STEP 3: Define function to extract subthemes + sentiment
# -------------------------------------------------------------
def get_subthemes_and_sentiment(text):
    """
    Given one transcript excerpt, this sends a well-structured prompt to the OpenAI model (GPT-4 or 3.5).
    
    It returns:
    - subthemes: A list of specific subtopics or angles mentioned in the passage
    - sentiment: "Positive", "Neutral", or "Negative" tone classification
    - reasoning: A short natural-language rationale explaining why that sentiment was chosen
    """

    # -----------------------------
    # 🧠 Prompt Engineering Block
    # -----------------------------
    # Use clear roles, instructions, and constraints to guide the LLM response format and tone
    prompt = f"""
You are a professional equity strategist analyzing earnings call transcripts for thematic trends.

Your task is to identify:
1. Subthemes (1–3) — These are specific, concrete ideas or concepts within the broader topic being discussed. Use concise noun phrases.
2. Sentiment — Classify tone as one of the following:
   - "Positive" if the language is optimistic, confident, or constructive.
   - "Negative" if the language is concerned, cautious, or pessimistic.
   - "Neutral" if the tone is factual, mixed, or uncertain.
3. Reasoning — Explain briefly (in one sentence) *why* the sentiment is what it is, referencing the tone or intent in the statement.

Requirements:
- Always return a valid JSON object, with keys: "subthemes", "sentiment", "reasoning"
- Keep subthemes short and specific (e.g., ["Cost Reduction", "Internal GenAI Tools"])
- Avoid generalities like "AI", "Strategy", "Technology"

Here is the text to analyze:
\"\"\"{text}\"\"\"

Respond only in the following JSON format:
{{
  "subthemes": [...],
  "sentiment": "...",
  "reasoning": "..."
}}
"""

    try:
        # Send prompt to OpenAI and get response
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use gpt-3.5-turbo for faster, cheaper runs
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2  # Low = deterministic, reproducible answers
        )

        # Extract the actual message text from the response
        content = response.choices[0].message["content"].strip()

        # Optional: Check that the response begins with '{' to ensure clean JSON
        # This can prevent parsing errors if the model adds extra explanation
        if not content.startswith("{"):
            json_start = content.find("{")
            content = content[json_start:]

        # Parse the JSON string into a Python dictionary
        result = json.loads(content)

        # Extract relevant fields, providing defaults in case any are missing
        subthemes = result.get("subthemes", [])
        sentiment = result.get("sentiment", "")
        reasoning = result.get("reasoning", "")

        return subthemes, sentiment, reasoning

    except Exception as e:
        # Gracefully handle API errors, parsing issues, or formatting problems
        print(f"⚠️ Error during LLM processing: {e}")
        return [], "Error", str(e)


# -------------------------------
#%% 🧪 STEP 4: Run test on 1st row
# -------------------------------
print("\n🧪 Running a single-row test to verify everything works...")

sample_text = df["transcript_text"].iloc[0]
print("\n📌 Sample transcript text:")
print(sample_text)

sample_subthemes, sample_sentiment, sample_reasoning = get_subthemes_and_sentiment(sample_text)

print("\n✅ Sample LLM Output:")
print("Subthemes:", sample_subthemes)
print("Sentiment:", sample_sentiment)
print("Reasoning:", sample_reasoning)

# Ask the user if they want to continue
proceed = input("\n⚠️ Proceed with full run? This will use OpenAI credits. (y/n): ")
if proceed.lower() != "y":
    print("🚪 Exiting script.")
    exit()

# -------------------------------
#%% 🔄 STEP 5: Run on all rows
# -------------------------------
print("\n🚀 Processing full dataset. This may take a few minutes...\n")

subthemes_list = []
sentiment_list = []
reasoning_list = []

# tqdm adds a progress bar
for idx, row in tqdm(df.iterrows(), total=len(df)):
    text = row["transcript_text"]
    subthemes, sentiment, reasoning = get_subthemes_and_sentiment(text)

    # Join list of subthemes into a single string for easier display
    subthemes_list.append(", ".join(subthemes))
    sentiment_list.append(sentiment)
    reasoning_list.append(reasoning)

    # Optional: Print intermediate output every 10 rows for sanity check
    if idx % 10 == 0:
        print(f"\nRow {idx} | Sentiment: {sentiment} | Subthemes: {subthemes}")

# -------------------------------
#%% 🧱 STEP 6: Add results to DataFrame
# -------------------------------
df["subthemes"] = subthemes_list
df["sentiment"] = sentiment_list
df["reasoning"] = reasoning_list

# Preview the final result
print("\n📊 Preview of final enhanced DataFrame:")
print(df.head())

# -------------------------------
#%% 💾 STEP 7: Export to Excel
# -------------------------------
df.to_excel(output_path, index=False)
print(f"\n✅ Finished! Enriched transcript mentions saved to: {output_path}")
