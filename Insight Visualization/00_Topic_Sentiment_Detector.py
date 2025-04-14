# -*- coding: utf-8 -*-
"""
Created on Fri Apr 11 21:16:47 2025

@author: Steven.Fandozzi
"""

# =====================================================================================
# OVERVIEW:
# -------------------------------------------------------------------------------------
# This script enhances thematic transcript chunks with LLM-based annotations.
# For each thematic mention, it extracts:
#   1. Subthemes — granular topics related to the main theme
#   2. Sentiment — a tone classification on a +1 to -1 scale
#   3. Reasoning — a one-line justification for the sentiment
#
# The model is prompted to avoid vague terms (e.g., "AI") and provide short, specific tags.
#
# =====================================================================================
# HOW TO USE:
# -------------------------------------------------------------------------------------
# 1. Place all Excel files in the Thematic Mentions folder, named like:
#       RAW AI Mentions_part1.xlsx, RAW Efficiency Mentions_part1.xlsx, etc.
#
# 2. Ensure OpenAI API access is enabled and valid.
#
# 3. Run the script. It will:
#    - Detect all themes from filenames
#    - Send each row’s transcript excerpt to OpenAI
#    - Append subthemes, sentiment, and reasoning
#    - Export enriched files to "Processed {theme} Mentions.xlsx"
#
# =====================================================================================
# INPUT:
# -------------------------------------------------------------------------------------
# Folder: S:/Strategy Research/Transcripts/Data/Thematic Mentions/
# Files:  RAW {theme} Mentions_part1.xlsx
# Required Column: transcript_text
#
# =====================================================================================
# OUTPUT:
# -------------------------------------------------------------------------------------
# Folder: S:/Strategy Research/Transcripts/Data/Thematic Mentions/
# Files:  Processed {theme} Mentions.xlsx
# Each output includes columns for subthemes, sentiment, and reasoning per excerpt.
# =====================================================================================

# -------------------------------
# Import Required Libraries
# -------------------------------
import pandas as pd  # Used for working with tabular data (Excel, CSV)
#import openai  # Connects to OpenAI to run language model prompts
from tqdm import tqdm  # Shows a progress bar when looping through data
import json  # Helps handle responses in JSON format
import os  # Allows for working with file paths

# -------------------------------
# Define input/output paths
# -------------------------------
input_path = r'S:/Strategy Research/Transcripts/Data/Thematic Mentions/RAW Thematic Mentions_part1.xlsx'
output_path = r'S:/Strategy Research/Transcripts/Data/Thematic Mentions/Processed Thematic Mentions.xlsx'

# -------------------------------
#%% Define Function to Analyze Each Transcript
# -------------------------------
def get_subthemes_and_sentiment(text, theme):
    """
    Sends the transcript excerpt to the OpenAI LLM and extracts:
    - Subthemes: 1–3 specific ideas within the broader theme
    - Sentiment: A score between -1 and +1 (decimal allowed)
    - Reasoning: One-sentence explanation for the sentiment
    """
    
    # Create the prompt that will be sent to the LLM
    prompt = f"""
        You are a professional equity strategist analyzing earnings call transcripts for thematic trends.

        Your task is to identify:
        1. Subthemes (1–3) — short, specific concepts within the theme of {theme}.
        2. Sentiment — classified on a +1 to -1 scale, decimals allowed.
        3. Reasoning — a brief explanation of why that sentiment was chosen.

        Requirements:
        - Respond ONLY in valid JSON format.
        - Use precise phrases (e.g., ["Cost Reduction", "Internal GenAI Tools"])
        - Avoid generic labels like "AI" or "Strategy"

        Here is the text to analyze: {text}

        Respond only in this JSON format:
        {{
          "subthemes": [...],
          "sentiment": "...",
          "reasoning": "..."
        }}
    """

    try:
        # Send the prompt to the GPT-4 model
        response = openai.ChatCompletion.create(
            model="gpt-4",  # You can use "gpt-3.5-turbo" if GPT-4 is unavailable
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2  # Lower temperature = more consistent responses
        )
        
        # Extract the model's response and clean it
        content = response.choices[0].message["content"].strip()
        if not content.startswith("{"):
            content = content[content.find("{"):]  # Fix partial response issues

        # Convert string response into JSON (Python dictionary)
        result = json.loads(content)

        # Return individual fields from the result
        return result.get("subthemes", []), result.get("sentiment", ""), result.get("reasoning", "")
    
    except Exception as e:
        # Handle errors gracefully
        print(f"❌ Error during LLM processing: {e}")
        return [], "Error", str(e)

# -------------------------------
#%% Load Input Excel File
# -------------------------------
print("Loading transcript data from:", input_path)

# Check if the file exists before trying to load it
if not os.path.exists(input_path):
    raise FileNotFoundError(f"❌ File not found: {input_path}")

# Read the Excel file into a pandas DataFrame
raw_transcript_data = pd.read_excel(input_path)

# Check that required column exists in the file
if "Combined Transcript" not in raw_transcript_data.columns:
    raise KeyError("❌ Missing 'Combined Transcript' column in the input file")

# -------------------------------
#%% Transform Excel File
# -------------------------------

# Initialize a blank dictionary to store filtered DataFrames by keyword
raw_transcript_dict = {}

# Identify all keyword columns (those ending in '_keyword_count')
available_keywords = [col for col in raw_transcript_data.columns if col.endswith('_keyword_count')]

print(f"Found {len(available_keywords)} keyword columns.")

# Loop over each keyword column
for keyword_col in available_keywords:
    # Extract the base theme name (remove the '_keyword_count' suffix)
    theme_name = keyword_col.replace('_keyword_count', '')

    # Filter rows where the current keyword count is greater than 0
    filtered_df = raw_transcript_data[raw_transcript_data[keyword_col] > 0].copy()

    # Optional: Keep only relevant columns for analysis
    columns_to_keep = ['Ticker', 'Company Name', 'Quarter', 'Combined Transcript', keyword_col]
    filtered_df = filtered_df[[col for col in columns_to_keep if col in filtered_df.columns]]

    # Save filtered DataFrame to dictionary
    raw_transcript_dict[theme_name] = filtered_df

    print(f"Saved data for theme: {theme_name} ({len(filtered_df)} rows)")

# Preview keys saved
print(f"\n📦 Final dictionary contains {len(raw_transcript_dict)} themes: {list(raw_transcript_dict.keys())}")

# -------------------------------
#%% Run a Sample Test on First Row
# -------------------------------

# Get the first theme name from available keywords (remove '_keyword_count' if present)
first_theme_col = available_keywords[0]
theme_name = first_theme_col.replace("_keyword_count", "")

# Extract the corresponding DataFrame
theme_df = raw_transcript_dict[theme_name]

# Pull the first row's combined transcript
sample_text = theme_df["Combined Transcript"].iloc[0]

# Run the LLM function on the first row
sample_sub, sample_sen, sample_rea = get_subthemes_and_sentiment(sample_text, theme_name)

# Print the results for inspection
print("📝 Sample Text:\n", sample_text)
print("📌 Subthemes:", sample_sub)
print("📈 Sentiment:", sample_sen)
print("💭 Reasoning:", sample_rea)

# Ask the user if they want to proceed
proceed = input("\n✅ Proceed with full run? (y/n): ")
if proceed.lower() != "y":
    print("⛔ Exiting script...")
    exit()

# -------------------------------
#%% Process All Rows for First Theme
# -------------------------------

# Get the first theme name and its associated DataFrame
first_theme_col = available_keywords[0]
theme_name = first_theme_col.replace("_keyword_count", "")
transcript_data = raw_transcript_dict[theme_name]  # This will be processed
print(f"🧠 Processing transcripts for theme: {theme_name}")

# Initialize lists to hold model outputs
all_subthemes = []
all_sentiments = []
all_reasonings = []

# Initialize cost tracking
total_cost = 0
MAX_COST = 50  # 💸 Adjust your safety budget cap here (in USD)
cost_input_per_1k = 0.01  # for GPT-4 Turbo
cost_output_per_1k = 0.03

# Loop through each transcript row using tqdm to track progress
for idx, row in tqdm(transcript_data.iterrows(), total=len(transcript_data)):
    text = row["Combined Transcript"]

    # Estimate token counts (very rough: 1 word ~ 1.3 tokens)
    estimated_input_tokens = len(text.split()) * 1.3
    estimated_output_tokens = 150  # conservative estimate for JSON output

    # Estimate cost for this row
    cost_this_row = (estimated_input_tokens / 1000) * cost_input_per_1k + \
                    (estimated_output_tokens / 1000) * cost_output_per_1k
    total_cost += cost_this_row

    # Budget cap check
    if total_cost > MAX_COST:
        print(f"❌ Stopping early due to budget cap of ${MAX_COST}. Reached ${total_cost:.2f}.")
        break

    # Run LLM analysis
    sub, sen, rea = get_subthemes_and_sentiment(text, theme_name)

    # Store the results
    all_subthemes.append(", ".join(sub))  # Convert list to comma-separated string
    all_sentiments.append(sen)
    all_reasonings.append(rea)

    # Optional progress print
    if idx % 10 == 0:
        print(f"[Row {idx}] Sentiment = {sen} | Subthemes = {sub}")

    # Optional cost print
    if idx % 50 == 0:
        print(f"💰 Estimated total cost so far: ${total_cost:.2f}")

# Done
print(f"✅ Finished theme: {theme_name} | Total estimated cost: ${total_cost:.2f}")

# -------------------------------
#%%  Add LLM Results to the DataFrame
# -------------------------------
transcript_data["subthemes"] = all_subthemes
transcript_data["sentiment"] = all_sentiments
transcript_data["reasoning"] = all_reasonings

# -------------------------------
#%% Save the Results to Excel
# -------------------------------
transcript_data.to_excel(output_path, index=False)
print(f"\n✅ Output saved to: {output_path}")
