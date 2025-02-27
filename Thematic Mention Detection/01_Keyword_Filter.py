# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 10:46:59 2024

@author: Steven.Fandozzi
"""

# Background: Now that we have a structured text dataset, it's time to narrow it down before modeling.
# The goal is to identify thematic mentions in corporate transcripts, filter relevant data, and export the final structured dataset.

# How to Use:
# - Ensure the transcript and keyword files are located in the specified file paths.
# - Run the script to process transcripts, extract thematic mentions, and export results to an Excel file.
# - The final output includes filtered transcripts with keyword counts, structured for further analysis.

# Output: Raw Thematic Mentions.xlsx (exported in parts if it exceeds Excel's row limit)
# Input: Thematic Vocab.xlsx (list of thematic keywords) and multiple transcript files (RAW 2021-2024)


#Import Libraries
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date
import datetime
import re
from tqdm import tqdm
import time
from tqdm import tqdm
tqdm.pandas()  # Enable the tqdm progress bar for pandas

# Define file paths for various datasets involved in the analysis.
transcript_file_path_21 = r'S:\Strategy Research\Transcripts\Data\Excel\RAW 2021-Cal TRANSCRIPT.xlsx'
transcript_file_path_22 = r'S:\Strategy Research\Transcripts\Data\Excel\RAW 2022-Cal TRANSCRIPT.xlsx'
transcript_file_path_23 = r'S:\Strategy Research\Transcripts\Data\Excel\RAW 2023-Cal TRANSCRIPT.xlsx'
transcript_file_path_24 = r'S:\Strategy Research\Transcripts\Data\Excel\RAW 2024-Cal TRANSCRIPT.xlsx'
#transcript_file_path_25 = r'S:\Strategy Research\AI Productivity Estimate\AI Monitor\Dataset\Excel\RAW 2025-Cal TRANSCRIPT.xlsx'
keyword_file_path = r'S:\Strategy Research\Transcripts\Additional\Themes\Thematic Vocab.xlsx'
sector_file_path = r'S:\Strategy Research\Transcripts\Additional\Tickers_ALL.xlsx'


export_mentions_file_path = r'S:\Strategy Research\Transcripts\Data\Thematic Mentions\RAW Thematic Mentions'


#%% Source Data - Load Transcripts and Thematic Vocabulary

#Import Data
transcript_df_21 = pd.read_excel(transcript_file_path_21)
transcript_df_22 = pd.read_excel(transcript_file_path_22)
transcript_df_23 = pd.read_excel(transcript_file_path_23)
transcript_df_24 = pd.read_excel(transcript_file_path_24)
#transcript_df_25 = pd.read_excel(transcript_file_path_25)
thematic_vocab_df = pd.read_excel(keyword_file_path)
sectors_df = pd.read_excel(sector_file_path)

# Concatenate the individual year transcript DataFrames into a single DataFrame for ease of analysis
transcript_df = pd.concat([transcript_df_21, transcript_df_22, transcript_df_23, transcript_df_24], ignore_index=True)
#transcript_df = pd.concat([transcript_df_21, transcript_df_22, transcript_df_23, transcript_df_24, transcript_df_25], ignore_index=True)

#%% Transform Data - Cleaning and Structuring


# Merge text columns in the transcript DataFrame that are split across multiple parts, ensuring no data is lost in the process
# This step combines management discussion and Q&A parts that are separated, filling any missing values with empty strings to prevent errors
transcript_df['Transcript - Mgmt'] = transcript_df['Transcript - Mgmt'].fillna('') + transcript_df['Transcript - Mgmt p2'].fillna('')
transcript_df['Transcript - QA'] = transcript_df['Transcript - QA'].fillna('') + transcript_df['Transcript - QA p2'].fillna('')

# Combine 'Transcript - Mgmt' and 'Transcript - QA' into one column called 'Transcript'
transcript_df['Transcript'] = transcript_df['Transcript - Mgmt'].fillna('') + "\n" + transcript_df['Transcript - QA'].fillna('')

# Reorder DataFrame columns to prioritize important identifiers and the newly created 'Transcript' column, making the DataFrame more organized for analysis
transcript_df = transcript_df[['Ticker', 'Company Name', 'Event Type', 'Date', 'Transcript']]

#%% Extract and Organize Keywords

# Get all column names
column_names = thematic_vocab_df.columns.to_list()

# Loop through column names and extract keywords dynamically
keyword_dict = {}

for col in column_names:
    # Create variable names based on the column name, replacing spaces with underscores
    variable_name = col.replace(' ', '_').lower() + "_keywords"
    
    # Extract non-null, valid string values from the column and include the column name as a keyword
    keywords = [col] + [ele for ele in thematic_vocab_df[col].to_list() if not pd.isna(ele) and isinstance(ele, str)]
    
    # Store the keywords list in the dictionary
    keyword_dict[variable_name] = keywords

#%% Remove Duplicates 

# Copy DF
filtered_transcript = transcript_df.copy()

# Add 'Earnings' column based on the condition
filtered_transcript['Earnings'] = (filtered_transcript['Event Type'].str.lower().str.contains('earnings')).astype(int)

# Split into earnings and non-earnings transcripts using boolean indexing
earnings_transcripts = filtered_transcript[filtered_transcript['Earnings'] == 1]
non_earnings_transcripts = filtered_transcript[filtered_transcript['Earnings'] == 0]

# Drop exact duplicates for non-earnings transcripts
non_earnings_transcripts = non_earnings_transcripts.drop_duplicates(subset=['Ticker', 'Date', 'Event Type'])

# Calculate title length without apply()
earnings_transcripts['Event Type Length'] = earnings_transcripts['Event Type'].str.len()

# Sort and drop duplicates in one line to avoid multiple sorting
earnings_transcripts = (earnings_transcripts.sort_values(by='Event Type Length', ascending=False)
                        .drop_duplicates(subset=['Ticker', 'Date', 'Earnings']))

# Combine the processed DataFrames
final_transcript = pd.concat([non_earnings_transcripts, earnings_transcripts], ignore_index=True)

# Sort once at the end if necessary
final_transcript = final_transcript.sort_values(by=['Ticker', 'Date'])

final_transcript = final_transcript.drop(columns=['Earnings', 'Event Type Length'])

transcript_df = final_transcript.copy()

#%% Split Transcripts By Sentence

# Function to split transcript texts into individual sentences based on common end-of-sentence punctuation
def split_text_optimized(text):
    # Check for non-empty text and split using precompiled regex for better performance
    if len(text) > 0:
        return re.split(r'(?<=[.!?]) +', text)
    return []

# Apply the optimized splitting function and explode the DataFrame
print("Step 1: Splitting transcripts into sentences...")
transcript_df['Transcript'] = transcript_df['Transcript'].apply(split_text_optimized)
transcript_df = transcript_df.explode('Transcript').reset_index(drop=True)

print("Step 1 Complete: Transcripts split into sentences.")

#%% Keyword Counting

# Precompile regex patterns for all keywords
print("Step 2: Precompiling keyword patterns...")
compiled_keyword_dict = {
    variable_name: re.compile(r'\b(?:' + '|'.join(map(re.escape, keywords)) + r')\b', flags=re.IGNORECASE)
    for variable_name, keywords in keyword_dict.items()
}

print("Step 2 Complete: Keyword patterns precompiled.")

# Function to count keywords using precompiled regex
def count_keywords_optimized(s, compiled_patterns):
    if isinstance(s, str):
        return {name: len(pattern.findall(s)) for name, pattern in compiled_patterns.items()}
    return {name: 0 for name in compiled_patterns.keys()}

# Step 3: Apply keyword counting to the DataFrame
print("Step 3: Counting keywords in sentences...")
start_time = time.time()

keyword_counts = transcript_df['Transcript'].progress_apply(
    lambda x: count_keywords_optimized(x, compiled_keyword_dict)
)

# Convert the resulting list of dictionaries into a DataFrame
keyword_counts_df = pd.DataFrame(keyword_counts.tolist())
keyword_counts_df.columns = [name.replace('_keywords', '_keyword_count') for name in compiled_keyword_dict.keys()]

# Merge the keyword counts back to the original DataFrame
transcript_df = pd.concat([transcript_df, keyword_counts_df], axis=1)

print("Step 3 Complete: Keyword Counts Calculated.")

#%% Summing Keyword Counts

print("Step 4: Calculating 'Thematic Term Count'...")
transcript_df['Thematic Term Count'] = keyword_counts_df.sum(axis=1)
print("Step 4 Complete: 'Thematic Term Count' Calculated.")

#%% Final Output and Timing

end_time = time.time()
print(f"Processing completed in {end_time - start_time:.2f} seconds.")

# Optional: Display a sample of the DataFrame to verify results
print(transcript_df.head())


#%% Filter DF for Keyword Hits

# Identify rows where 'Thematic Term Count' > 0
condition = transcript_df['Thematic Term Count'] > 0

# Create a boolean mask to include rows where the condition is True or adjacent rows
mask = condition | condition.shift(1, fill_value=False) | condition.shift(-1, fill_value=False)

# Filter the DataFrame using the mask
filtered_df = transcript_df[mask]

# Assign the filtered DataFrame to a variable for further use or analysis
transcripts_chunks = filtered_df

# Optional: Display the result for verification
print(transcripts_chunks.head())

#%% Combine Sentences

def simple_sent_tokenize(text):
    # Define end-of-sentence markers
    markers = ('.', '?', '!')
    sentences = []
    start = 0

    # Iterate over each character in the text
    for i, char in enumerate(text):
        if char in markers:
            # Add the sentence to the list if an end marker is found
            sentences.append(text[start:i+1].strip())
            start = i+1

    # Check for any remaining text after the last marker
    if start < len(text):
        sentences.append(text[start:].strip())

    return sentences


# Define the columns to group by
group_columns = ['Ticker', 'Company Name', 'Date', 'Event Type']
keyword_count_columns = [variable_name.replace('_keywords', '_keyword_count') for variable_name in keyword_dict.keys()]

# Define the maximum sentence length for combining transcripts
max_sent_length = 10

# Function to combine transcripts within the sentence limit
def combine_transcripts(group):
    combined = []
    current_transcript = ""
    current_sent_count = 0
    batch_keyword_counts = {col: 0 for col in keyword_count_columns}

    # Iterate through each row in the group
    for _, row in group.iterrows():
        transcript = row['Transcript']
        sentences = simple_sent_tokenize(transcript)

        # If adding this transcript exceeds the limit, finalize the current batch
        if current_sent_count + len(sentences) > max_sent_length:
            combined.append({
                **{col: row[col] for col in group_columns},  # Include metadata
                'Combined Transcript': current_transcript.strip(),
                **batch_keyword_counts,  # Add keyword counts
            })
            # Reset for the next batch
            current_transcript = ""
            current_sent_count = 0
            batch_keyword_counts = {col: 0 for col in keyword_count_columns}

        # Add the current transcript and update keyword counts
        current_transcript += " " + transcript
        current_sent_count += len(sentences)

        for col in keyword_count_columns:
            batch_keyword_counts[col] += row[col]

    # Add the last batch
    if current_transcript:
        combined.append({
            **{col: row[col] for col in group_columns},  # Include metadata
            'Combined Transcript': current_transcript.strip(),
            **batch_keyword_counts,  # Add keyword counts
        })

    return pd.DataFrame(combined)

# Apply grouping and aggregation
print("Step 5: Combining transcripts and summing keyword counts")
grouped = transcripts_chunks.groupby(group_columns).apply(combine_transcripts).reset_index(drop=True)

# No need to explode here since the grouping logic already creates rows for each combined transcript
print("Step 6: Finalizing DataFrame structure")
grouped['Thematic Term Count'] = grouped[keyword_count_columns].sum(axis=1)

print("Processing complete. Final DataFrame created.")

# Assign the result to transcripts_chunks
transcripts_chunks = grouped

#%% Export to CSV

# Export All Hits
transcripts_chunks = transcripts_chunks[transcripts_chunks['Thematic Term Count']>0]

# Define the chunk size (Excel limit)
chunk_size = 1048576
num_chunks = len(transcripts_chunks) // chunk_size + 1

for i in range(num_chunks):
    start = i * chunk_size
    end = (i + 1) * chunk_size
    chunk = transcripts_chunks[start:end]
    chunk.to_excel(f'{export_mentions_file_path}_part{i + 1}.xlsx', index=False)

