# %% Import Libraries
"""
Created on Thu Aug 29 11:54:49 2024

@author: Steven.Fandozzi
"""

# ============================================
# 📊 Create Charts
# ============================================
#
# ============================================
# OVERVIEW:
# ============================================
# This script processes earnings call transcripts to:
# 1. Count keyword mentions by theme, sector, and company size
# 2. Calculate percentage of companies mentioning themes
# 3. Analyze sentiment trends (if enabled)
# 4. Measure co-occurrence between themes over time
# 5. Output clean Excel datasets for visualization in Power BI or further analysis
#
# ============================================
# HOW TO USE:
# ============================================
# Step 1: Set `sentiment_run = True` if sentiment columns are available and you want to process sentiment.
# Step 2: Ensure all file paths below are correctly set and accessible.
# Step 3: Run the script in full; outputs will be generated in the directories specified.
#
# ============================================
# INPUT FILES:
# ============================================
# - Transcripts by part: RAW Thematic Mentions_part*.xlsx OR RAW Thematic Mentions w Embedding+Sentiment_part*.xlsx
# - Thematic keyword dictionary: Thematic Vocab.xlsx (each column is a theme, rows are keywords)
# - Sector and size mapping: Tickers_ALL.xlsx (Sheet1)
#
# ============================================
# OUTPUT FILES:
# ============================================
# (Saved as Excel files to S:/Strategy Research/Transcripts/Data/Thematic Mentions)
# - Fig1 - Mentions by Quarter.xlsx
# - Fig1a - Topic Mentions by Quarter and Sector.xlsx
# - Fig2 - Heatmap by Quarter and Sector.xlsx
# - Fig2a - Topic Mentions by Quarter and Size.xlsx
# - Fig3 - % Mention by Quarter.xlsx
# - Fig3a - Topic % Mentions by Quarter.xlsx
# - Fig5_6_7 - Sentiment by Quarter.xlsx (only if `sentiment_run = True`)
# - Fig5 - Theme Co-Occurrence.xlsx (theme-to-theme matrix for each quarter)
# - CircularFlow Co-Occurence folder: theme co-occurrence matrices exported separately
#
# ============================================
# NOTES:
# - All data is mapped to a custom `Quarter_Label` system (e.g., Q1 '23).
# - Themes are detected using keyword matching based on Thematic Vocab.xlsx.
# - Sentiment is bucketed into 5 categories: Strong Negative, Negative, Neutral, Positive, Strong Positive.
# - This script assumes the transcript data is preprocessed and keyword counts are already present.
#
# DEPENDENCIES:
# - numpy, pandas, re, os, warnings
# - xlsxwriter (for exporting Excel files)

# ============================================


# Import Required Libraries
import numpy as np
import pandas as pd
import re
import warnings
import os

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", message="Glyph .* missing from current font")

# Global Settings
sentiment_run = False

# File Paths
keyword_file_path = r'S:\Strategy Research\Transcripts\Additional\Themes\Thematic Vocab.xlsx'
base_directory = r'S:\Strategy Research\Transcripts\Data\Thematic Mentions'
sector_file_path = r'S:\Strategy Research\Transcripts\Additional\Tickers_ALL.xlsx'

# File Patterns for Import
base_file_pattern = (
    "RAW Thematic Mentions w Embedding+Sentiment_part" if sentiment_run else "RAW Thematic Mentions_part"
)

# Export File Paths
export_sentiment_file_path = r"S:\Strategy Research\Transcripts\Data\Thematic Mentions\Fig5_6_7 - Sentiment by Quarter.xlsx"
export_co_occurrence_file_path = r"S:\Strategy Research\Transcripts\Data\Thematic Mentions\Fig5 - Theme Co-Occurrence.xlsx"
export_co_occurence_circularflow_path = r"S:\Strategy Research\Transcripts\Report\Themes\CircularFlow Co-Occurence"

# Date Range for Quarters
start_date = pd.Timestamp('2021-10-01')
end_date = pd.Timestamp('2026-01-01')
quarters = pd.date_range(start=start_date, end=end_date, freq='3MS')

#%% Import Data

def import_all_parts(directory, sentiment_run):
    """Load multiple files based on sentiment_run setting"""
    file_pattern = (
        r"RAW Thematic Mentions w Embedding\+Sentiment_part\d+\.xlsx"
        if sentiment_run
        else r"RAW Thematic Mentions_part\d+\.xlsx"
    )
    print(f"Searching for files matching: {file_pattern}")

    df_list = []
    for file in os.listdir(directory):
        if re.match(file_pattern, file, re.IGNORECASE):
            file_path = os.path.join(directory, file)
            print(f"Loading file: {file_path}")
            df_list.append(pd.read_excel(file_path))

    if not df_list:
        raise FileNotFoundError(f"No files found matching {file_pattern} in {directory}")

    print(f"Successfully loaded {len(df_list)} files.")
    return pd.concat(df_list, ignore_index=True)

# Import Data
try:
    transcripts_chunks = import_all_parts(base_directory, sentiment_run)
    if 'Glove Embedding' in transcripts_chunks.columns:
        transcripts_chunks = transcripts_chunks.drop(columns=['Glove Embedding'])
        print("Glove Embeddings Removed")
    transcripts_chunks['Date'] = pd.to_datetime(transcripts_chunks['Date'], errors='coerce')
    print("Data import successful!")
except FileNotFoundError as e:
    print(e)
    transcripts_chunks = pd.DataFrame()

# Import Thematic Vocabulary
try:
    thematic_vocab_df = pd.read_excel(keyword_file_path)
    print("Thematic Vocabulary Loaded Successfully")
except FileNotFoundError:
    print("Keyword file not found. Check the path.")
    thematic_vocab_df = pd.DataFrame()

# Generate Keywords Dictionary
keyword_dict = {
    col.replace(' ', '_').lower() + "_keywords": [col] + [
        ele for ele in thematic_vocab_df[col].dropna() if isinstance(ele, str)
    ]
    for col in thematic_vocab_df.columns
}

# Load Sector Information
try:
    sectors_df = pd.read_excel(sector_file_path, sheet_name='Sheet1')
    print("Sectors Data Loaded Successfully")
except FileNotFoundError:
    print("Sector file not found. Check the path.")
    sectors_df = pd.DataFrame()

if not transcripts_chunks.empty:
    transcripts_chunks = pd.merge(transcripts_chunks, sectors_df, on='Ticker', how='left')
    transcripts_chunks['Sector'] = transcripts_chunks['Sector'].fillna('Unknown')

# Assign Quarter Labels
def get_quarter_label(date):
    """Map dates to custom quarters"""
    date = pd.Timestamp(date)
    if date.month in [1, 2, 3]:
        return f"Q4 '{str(date.year-1)[-2:]}" if date.month in [1, 2] else f"Q4 '{str(date.year)[-2:]}"
    elif date.month in [4, 5, 6]:
        return f"Q1 '{str(date.year)[-2:]}"
    elif date.month in [7, 8, 9]:
        return f"Q2 '{str(date.year)[-2:]}"
    elif date.month in [10, 11, 12]:
        return f"Q3 '{str(date.year)[-2:]}"
    return np.nan

if not transcripts_chunks.empty:
    transcripts_chunks['Quarter_Label'] = transcripts_chunks['Date'].apply(get_quarter_label)

# Prepare Themes Columns
themes = [key.replace('_keywords', '_keyword_count') for key in keyword_dict.keys()]

print("Processing Complete")


# %% Figure 1 - Mentions by Quarter

# Define Export File Paths
export_fig1_file_path = r'S:\Strategy Research\Transcripts\Data\Thematic Mentions\Fig1 - Mentions by Quarter.xlsx'

# Function to handle unexpected formats and NaN values for quarter labels
def parse_quarter_label(quarter_label):
    if pd.isna(quarter_label) or not isinstance(quarter_label, str):
        return np.nan  # Return NaN if the quarter_label is NaN or not a string
    
    # Check if the quarter label is in the correct format: "Qx 'yy"
    if len(quarter_label) != 6 or quarter_label[0] != 'Q' or quarter_label[2] != ' ' or quarter_label[3] != "'":
        return np.nan  # Return NaN if the format is incorrect
    
    try:
        year = int("20" + quarter_label[-2:])  # Extract the year
        quarter = int(quarter_label[1])  # Extract the quarter number
        month = (quarter - 1) * 3 + 1  # Calculate the starting month of the quarter
        return pd.Timestamp(f"{year}-{month:02d}-01")
    except ValueError:
        return np.nan  # Return NaN if any value conversion fails

mentions_by_quarter = pd.DataFrame(
    columns=['Quarter', 'Quarter_Label'] + themes)

# Iterate over each quarter, calculate the sum of keyword counts, and store the results
# Initialize a list to store rows that will later be concatenated into the final DataFrame
quarterly_rows = []

# Loop through each quarter in the previously defined date range
for count, quarter in enumerate(quarters[:-1]):
    # Calculate the start and end dates of the current quarter
    # For example, if the quarter is Q1 2022, start_date is 2022-01-01, and end_date is 2022-03-31
    current_start_date = quarter
    end_date = quarters[count+1]

    # Filter the rows in transcripts_chunks that fall within the current quarter's date range
    mask = (transcripts_chunks['Date'] >= current_start_date) & (
        transcripts_chunks['Date'] <= end_date)
    filtered_rows = transcripts_chunks.loc[mask]

    # Initialize a dictionary to store theme sums for this quarter
    theme_mention_count = {}

    # Loop through each theme column and sum the counts if the column exists in the filtered data
    for theme in themes:
        if theme in filtered_rows.columns:
            theme_mention_count[theme] = filtered_rows[theme].sum()
        else:
            # Assign a count of 0 if the column is missing
            theme_mention_count[theme] = 0

    theme_mention_count['Quarter'] = quarter
    quarter_label = get_quarter_label(quarter)

    theme_mention_count['Quarter_Label'] = quarter_label

    quarterly_rows.append(pd.DataFrame([theme_mention_count]))

# Step 4: Concatenate all the rows into the final quarterly DataFrame
# We use pd.concat() to combine all the individual rows stored in quarterly_rows into one DataFrame
mentions_by_quarter = pd.concat(quarterly_rows, ignore_index=True)

# Export Thematic Mention Count By Quarter
mentions_by_quarter.to_excel(export_fig1_file_path, index=False)

### Fig 1 By Sector ###

# Define Export File Path
export_per_theme_fig1_file_path = r'S:\Strategy Research\Transcripts\Data\Thematic Mentions\Fig1a - Topic Mentions by Quarter and Sector.xlsx'

# Create a Dictionary. Keys: Topic; Values: DF with Sectors as Columns and Quarters as Rows.
mentions_by_sector_dfs = {}

merged_df = transcripts_chunks.copy()

# Loop Through Themes
for theme in themes:

    # Group the transcript chunks by both quarter and sector, then sum the counts for the given keyword
    topic_df = merged_df.groupby(['Quarter_Label', 'Sector'])[
        theme].sum().reset_index()

    # Step 2: Apply the function to create a new 'Quarter_Date' column
    topic_df['Quarter_Date'] = topic_df['Quarter_Label'].apply(
        parse_quarter_label)

    # Step 3: Filter the DataFrame to retain only rows from Q1 '22 forward
    topic_df = topic_df[topic_df['Quarter_Date'] >= start_date]
    topic_df = topic_df.sort_values('Quarter_Date')

    # Step 4: Assign the sorted 'Quarter_Label' to the pivoted table
    topic_pivot = topic_df.pivot(
        index='Quarter_Date', columns='Sector', values=theme)
    # Ensure the pivot table is sorted by date
    topic_pivot = topic_pivot.sort_index()

    # Step 5: Add 'Quarter_Label' as a column based on the original topic_df
    topic_pivot['Quarter_Label'] = topic_df.drop_duplicates(
        'Quarter_Date').set_index('Quarter_Date')['Quarter_Label']
    topic_pivot = topic_pivot.reset_index(drop=True).set_index('Quarter_Label')

    # Add this pivoted DataFrame to the dictionary, using the keyword as the key
    mentions_by_sector_dfs[theme] = topic_pivot

# Export Thematic Mention Count By Sector and Quarter
with pd.ExcelWriter(export_per_theme_fig1_file_path, engine='xlsxwriter') as writer:
    # Loop through each topic (key) in the dictionary
    for keyword, df in mentions_by_sector_dfs.items():
        # Write the DataFrame for this keyword to a separate sheet in the Excel file
        # The sheet name will be the keyword
        df.to_excel(writer, sheet_name=keyword)

# %% Figure 2 - Thematic Heat Map (Start Here)

# Define Export File Path
export_fig2_file_path = r'S:\Strategy Research\Transcripts\Data\Thematic Mentions\Fig2 - Heatmap by Quarter and Sector.xlsx'

# Define a function to aggregate both sector-specific data and an 'All Sectors' total


def aggregate_with_all_sectors(df, groupby_columns, keyword_columns):

    # Group the data by the specified columns (e.g., 'Sector' and 'Quarter_Label')
    # Then, sum the keyword columns for each combination of 'Sector' and 'Quarter_Label'
    sector_grouped_df = df.groupby(groupby_columns)[
        keyword_columns].sum().reset_index()

    # Now, group only by 'Quarter_Label' (ignoring the 'Sector') to calculate totals across all sectors
    all_sectors_grouped_df = df.groupby('Quarter_Label')[
        keyword_columns].sum().reset_index()

    # Create a new 'Sector' column in this aggregated dataframe and set it to 'All Sectors'
    all_sectors_grouped_df['Sector'] = 'All Sectors'

    # Concatenate the sector-specific dataframe with the 'All Sectors' dataframe
    # This will result in a dataframe that contains both sector-specific and all-sector totals
    return pd.concat([sector_grouped_df, all_sectors_grouped_df], ignore_index=True)


# Apply the helper function to aggregate the data
quarterly_sector_df = aggregate_with_all_sectors(
    merged_df, ['Sector', 'Quarter_Label'], themes)

# Apply the function to the 'Quarter_Label' column to create a new 'Quarter_Date' column
quarterly_sector_df['Quarter_Date'] = quarterly_sector_df['Quarter_Label'].apply(
    parse_quarter_label)

# Filter the DataFrame to only keep rows from Q1 '22 onward
# This assumes 'start_date' is defined earlier and represents Q1 '22
quarterly_sector_df = quarterly_sector_df[quarterly_sector_df['Quarter_Date'] >= start_date]

# Sort the DataFrame by the 'Quarter_Date' column for better readability
quarterly_sector_df = quarterly_sector_df.sort_values('Quarter_Date')

# (Optional) Drop the 'Quarter_Date' column if it's no longer needed
quarterly_sector_df = quarterly_sector_df.drop(columns=['Quarter_Date'])

# Export To Excel
quarterly_sector_df.to_excel(export_fig2_file_path, index=False)


### Fig 2 By Size ###

# Define Export File Path
export_per_topic_fig2_file_path = r'S:\Strategy Research\Transcripts\Data\Thematic Mentions\Fig2a - Topic Mentions by Quarter and Size.xlsx'

# Create a Dictionary. Keys: Topic; Values: DF with Sectors as Columns and Quarters as Rows.
topic_size_dfs = {}

# Loop Through Themes
for keyword in themes:

    # Group the transcript chunks by both quarter and sector, then sum the counts for the given keyword
    topic_df = merged_df.groupby(['Quarter_Label', 'Size'])[
        keyword].sum().reset_index()

    # Step 2: Apply the function to create a new 'Quarter_Date' column
    topic_df['Quarter_Date'] = topic_df['Quarter_Label'].apply(
        parse_quarter_label)

    # Step 3: Filter the DataFrame to retain only rows from Q1 '22 forward
    topic_df = topic_df[topic_df['Quarter_Date'] >= start_date]
    topic_df = topic_df.sort_values('Quarter_Date')

    # Step 4: Assign the sorted 'Quarter_Label' to the pivoted table
    topic_pivot = topic_df.pivot(
        index='Quarter_Date', columns='Size', values=keyword)
    # Ensure the pivot table is sorted by date
    topic_pivot = topic_pivot.sort_index()

    # Step 5: Add 'Quarter_Label' as a column based on the original topic_df
    topic_pivot['Quarter_Label'] = topic_df.drop_duplicates(
        'Quarter_Date').set_index('Quarter_Date')['Quarter_Label']
    topic_pivot = topic_pivot.reset_index(drop=True).set_index('Quarter_Label')

    # Add this pivoted DataFrame to the dictionary, using the keyword as the key
    topic_size_dfs[keyword] = topic_pivot

# Export
with pd.ExcelWriter(export_per_topic_fig2_file_path, engine='xlsxwriter') as writer:
    # Loop through each topic (key) in the dictionary
    for keyword, topic_size_df in topic_size_dfs.items():
        # Write the DataFrame for this keyword to a separate sheet in the Excel file
        # The sheet name will be the keyword
        topic_size_df.to_excel(writer, sheet_name=keyword)

# %% Figure 3 - % of Companies Mentioning

# Define Export Path
export_fig3_file_path = r'S:\Strategy Research\Transcripts\Data\Thematic Mentions\Fig3 - % Mention by Quarter.xlsx'

# Group by 'Quarter_Label' and 'Ticker' to avoid double-counting companies with same tickers within the same quarter
theme_mentions = merged_df.groupby(['Quarter_Label', 'Ticker'])[
    themes].apply(lambda x: (x > 0).any()).reset_index()

# Count total number of unique companies (per quarter?)
total_num_companies = sectors_df.shape[0]
total_companies_per_quarter = merged_df.groupby(
    'Quarter_Label')['Ticker'].nunique().reset_index()
total_companies_per_quarter.rename(
    columns={'Ticker': 'Total_Companies'}, inplace=True)

# Sum Company Mention Indicate by Quarter (no sector breakdown)
theme_mentions_agg = theme_mentions.groupby(
    'Quarter_Label')[themes].sum().reset_index()

# Calculate the Percentage of Companies Mentioning Each Theme by Quarter
percentage_df = pd.merge(
    theme_mentions_agg, total_companies_per_quarter, on='Quarter_Label')

for theme in themes:
    percentage_df[theme] = (percentage_df[theme] /
                            percentage_df['Total_Companies']) * 100

percentage_df['Quarter_Date'] = percentage_df['Quarter_Label'].apply(
    parse_quarter_label)
percentage_df = percentage_df[percentage_df['Quarter_Date'] >= start_date]
percentage_df = percentage_df.sort_values('Quarter_Date')

# Drop Helper Columns
percentage_df = percentage_df.drop(columns=['Total_Companies'])
percentage_df = percentage_df.drop(columns=['Quarter_Date'])


# Export To Excel
percentage_df.to_excel(export_fig3_file_path, index=False)


### Fig 3 by Sector ###

# Define Export Path
export_per_topic_fig3_file_path = r'S:\Strategy Research\Transcripts\Data\Thematic Mentions\Fig3a - Topic % Mentions by Quarter.xlsx'

topic_sector_percentage_dfs = {}

# Step 1: Calculate the total number of companies per sector and quarter
total_companies_per_quarter = merged_df.groupby(['Quarter_Label', 'Sector'])[
    'Ticker'].nunique().reset_index()
total_companies_per_quarter.rename(
    columns={'Ticker': 'Total_Companies'}, inplace=True)

# Loop Through Themes
for keyword in themes:

    # Step 2: Identify companies that mentioned the keyword in each quarter and sector
    theme_mentions = merged_df.groupby(['Quarter_Label', 'Sector', 'Ticker'])[
        keyword].apply(lambda x: (x > 0).any()).reset_index()

    # Step 3: Aggregate the counts at the sector and quarter level
    theme_mentions_agg = theme_mentions.groupby(['Quarter_Label', 'Sector'])[
        keyword].sum().reset_index()

    # Step 4: Merge with the total number of companies per sector and quarter
    theme_mentions_percentage = pd.merge(
        theme_mentions_agg, total_companies_per_quarter, on=['Quarter_Label', 'Sector'])

    # Step 5: Calculate the percentage of companies mentioning the keyword
    theme_mentions_percentage[keyword] = (
        theme_mentions_percentage[keyword] / theme_mentions_percentage['Total_Companies']) * 100

    # Step 6: Apply the function to create a new 'Quarter_Date' column
    theme_mentions_percentage['Quarter_Date'] = theme_mentions_percentage['Quarter_Label'].apply(
        parse_quarter_label)

    # Step 7: Filter the DataFrame to retain only rows from Q1 '22 forward
    theme_mentions_percentage = theme_mentions_percentage[
        theme_mentions_percentage['Quarter_Date'] >= start_date]
    theme_mentions_percentage = theme_mentions_percentage.sort_values(
        'Quarter_Date')

    # Step 8: Assign the sorted 'Quarter_Label' to the pivoted table
    topic_pivot = theme_mentions_percentage.pivot(
        index='Quarter_Date', columns='Sector', values=keyword)
    # Ensure the pivot table is sorted by date
    topic_pivot = topic_pivot.sort_index()

    # Step 9: Add 'Quarter_Label' as a column based on the original topic_df
    topic_pivot['Quarter_Label'] = theme_mentions_percentage.drop_duplicates(
        'Quarter_Date').set_index('Quarter_Date')['Quarter_Label']
    topic_pivot = topic_pivot.reset_index(drop=True).set_index('Quarter_Label')

    # Step 10: Add this pivoted DataFrame to the dictionary, using the keyword as the key
    topic_sector_percentage_dfs[keyword] = topic_pivot

# Export To Excel
with pd.ExcelWriter(export_per_topic_fig3_file_path, engine='xlsxwriter') as writer:
    # Loop through each topic (key) in the dictionary
    for keyword, topic_sector_percentage_df in topic_sector_percentage_dfs.items():
        # Write the DataFrame for this keyword to a separate sheet in the Excel file
        # The sheet name will be the keyword
        topic_sector_percentage_df.to_excel(writer, sheet_name=keyword)

# %% Figure 5, 6, 7 - Sentiment Weekly and by Sector

if sentiment_run:
    # Step 1: Identify columns that end with 'keyword_count' and represent the keyword hits
    keyword_columns = [
        col for col in transcripts_chunks.columns if col.endswith('_keyword_count')]
    
    # Step 2: Melt the DataFrame so that the keyword columns are treated as a single column for analysis
    # This will convert all keyword columns into a long format, with each row representing a keyword hit.
    transcripts_melted = transcripts_chunks.melt(
        # Include 'Date' in id_vars
        id_vars=['Quarter_Label', 'Date', 'Sentiment_Compound'],
        value_vars=keyword_columns,  # Melt keyword columns
        var_name='Keyword',  # New column for keyword names
        value_name='Keyword_Count'  # New column for the keyword counts
    )
    
    # Step 3: Filter rows where Keyword_Count is greater than 0 (i.e., keywords that were mentioned)
    transcripts_melted = transcripts_melted[transcripts_melted['Keyword_Count'] > 0]
    
    # Step 4: Categorize sentiment into sentiment bins efficiently
    
    
    def categorize_sentiment(sentiment):
        if sentiment <= -0.6:
            return "Strong Negative"
        elif -0.6 < sentiment <= -0.2:
            return "Negative"
        elif -0.2 < sentiment <= 0.2:
            return "Neutral"
        elif 0.2 < sentiment <= 0.6:
            return "Positive"
        else:
            return "Strong Positive"
    
    
    # Step 5: Apply sentiment categorization to the Sentiment_Compound column
    transcripts_melted['Sentiment_Category'] = transcripts_melted['Sentiment_Compound'].apply(
        categorize_sentiment)
    
    # Step 6: Calculate the average sentiment by quarter and keyword directly without grouping by sentiment category
    sentiment_avg_counts = transcripts_melted.groupby(
        ['Quarter_Label', 'Keyword']
    ).agg(
        # Directly average sentiment per keyword and quarter
        avg_sentiment=('Sentiment_Compound', 'mean'),
    ).reset_index()
    
    # Step 7: Calculate counts for each sentiment category by quarter and keyword
    # This will give the counts for each sentiment category (Strong Negative, Negative, etc.)
    sentiment_counts = transcripts_melted.pivot_table(
        # Index by 'Quarter_Label' and 'Keyword'
        index=['Quarter_Label', 'Keyword'],
        columns='Sentiment_Category',  # Pivot on 'Sentiment_Category'
        values='Keyword_Count',  # Count each sentiment category mention per keyword
        aggfunc='size',  # Use size to count occurrences
        fill_value=0  # Fill missing counts with 0
    ).reset_index()
    
    # Step 8: Merge the average sentiment back to the sentiment_counts DataFrame
    sentiment_counts = sentiment_counts.merge(
        sentiment_avg_counts[['Quarter_Label', 'Keyword', 'avg_sentiment']],
        on=['Quarter_Label', 'Keyword'],
        how='left'  # Keep all rows from sentiment_counts
    )
    
    # Step 9: Parse 'Quarter_Label' into a date format for filtering if needed
    sentiment_counts['Quarter_Date'] = sentiment_counts['Quarter_Label'].apply(
        parse_quarter_label)
    
    # Step 10: Filter rows starting from Q1 2022, drop the 'Quarter_Date' column if it's no longer needed
    sentiment_counts = sentiment_counts[sentiment_counts['Quarter_Date'] >= pd.Timestamp(
        '2022-01-01')].drop(columns=['Quarter_Date'])
    
    # Step 11: Calculate weekly average sentiment by grouping transcripts by 'Week of Year'
    transcripts_melted['Week of Year'] = transcripts_melted['Date'].dt.strftime(
        '%Y-%W')  # Create 'Week of Year' column
    weekly_sentiment = transcripts_melted.groupby('Week of Year').agg(
        # Calculate weekly average sentiment
        average_sentiment=('Sentiment_Compound', 'mean'),
        row_count=('Sentiment_Compound', 'size')  # Count rows per week
    ).reset_index()
    
    # Step 12: Convert 'Week of Year' to datetime for filtering and validation
    weekly_sentiment['Date'] = pd.to_datetime(
        weekly_sentiment['Week of Year'] + '-1', format='%Y-%W-%w')
    weekly_sentiment = weekly_sentiment[weekly_sentiment['Date'] > pd.Timestamp(
        '2022-01-01')]  # Filter for dates post-2022
    
    # Step 13: Add a 4-week moving average (4WMA) of sentiment
    weekly_sentiment['4wma'] = weekly_sentiment['average_sentiment'].rolling(
        window=4).mean()  # Efficient calculation of 4-week moving average
    
    # Step 14: Reshape the sentiment_counts DataFrame to long format for further analysis
    df_keyword_quarterly_sentiment = sentiment_counts.melt(
        id_vars=['Quarter_Label', 'Keyword'],  # Keep these columns intact
        value_vars=['Strong Negative', 'Negative', 'Neutral',
                    'Positive', 'Strong Positive'],  # Melt sentiment categories
        var_name='Sentiment_Category',  # New column name for sentiment categories
        value_name='Count'  # New column for corresponding counts
    )
    
    # Step 15: Merge back the average sentiment for each keyword and quarter into the melted DataFrame
    df_keyword_quarterly_sentiment = pd.merge(
        df_keyword_quarterly_sentiment,  # DataFrame with melted sentiment counts
        # Average sentiment DataFrame
        sentiment_counts[['Quarter_Label', 'Keyword', 'avg_sentiment']],
        on=['Quarter_Label', 'Keyword'],  # Merge based on quarter and keyword
        how='left'  # Keep all rows from df_keyword_quarterly_sentiment
    )
    
    # Export sentiment counts and weekly sentiment to Excel
    with pd.ExcelWriter(export_sentiment_file_path, engine='xlsxwriter') as writer:
    
        # Export the 'weekly_sentiment' DataFrame to a sheet named 'Weekly_Sentiment'
        weekly_sentiment.to_excel(
            writer, sheet_name='Weekly_Sentiment', index=False)
    
        # Export the 'sentiment_counts' DataFrame to a sheet named 'Sentiment_By_Theme'
        sentiment_counts.to_excel(
            writer, sheet_name='Sentiment_By_Theme', index=False)
    
        # Step 16: Filter by each unique keyword and replicate weekly analysis for each
        unique_keywords = transcripts_melted['Keyword'].unique()
    
        for keyword in unique_keywords:
            # Filter for the specific keyword
            theme_weekly_data = transcripts_melted[transcripts_melted['Keyword'] == keyword]
    
            # Calculate weekly sentiment for the specific theme
            theme_weekly_sentiment = theme_weekly_data.groupby('Week of Year').agg(
                average_sentiment=('Sentiment_Compound', 'mean'),
                row_count=('Sentiment_Compound', 'size')
            ).reset_index()
    
            # Convert 'Week of Year' to datetime format for each theme sheet
            theme_weekly_sentiment['Date'] = pd.to_datetime(
                theme_weekly_sentiment['Week of Year'] + '-1', format='%Y-%W-%w')
            theme_weekly_sentiment = theme_weekly_sentiment[theme_weekly_sentiment['Date'] > pd.Timestamp(
                '2022-01-01')]
    
            # Add 4-week moving average for each theme
            theme_weekly_sentiment['4wma'] = theme_weekly_sentiment['average_sentiment'].rolling(
                window=4).mean()
    
            # Export each theme’s weekly sentiment to its own sheet in the Excel file
            # Limit sheet name to 31 characters
            theme_sheet_name = f"{keyword[:31]}"
            theme_weekly_sentiment.to_excel(
                writer, sheet_name=theme_sheet_name, index=False)


# %% Figure 8 - Co-Occurence Heat Map

# Initialize the co-occurrence matrices dictionary to store results for each quarter
co_occurrence_matrices = {}

merged_df['Quarter_Date'] = merged_df['Quarter_Label'].apply(
    parse_quarter_label)
merged_df = merged_df[merged_df['Quarter_Date'] >= start_date]

# Loop through each quarter and calculate the co-occurrence matrix
for quarter in merged_df['Quarter_Label'].unique():
    # Filter data for the current quarter
    current_quarter_data = merged_df[merged_df['Quarter_Label'] == quarter]

    # Initialize a co-occurrence matrix (a square DataFrame with themes as both rows and columns)
    co_occurrence_matrix = pd.DataFrame(0, index=themes, columns=themes)

    # For each pair of themes, calculate co-occurrences
    for theme1 in themes:
        for theme2 in themes:
            # Check where both themes have non-zero mentions
            co_occurrence_matrix.loc[theme1, theme2] = (
                (current_quarter_data[theme1] > 0) & (current_quarter_data[theme2] > 0)).sum()

    # Store the co-occurrence matrix for the current quarter
    co_occurrence_matrices[quarter] = co_occurrence_matrix

# Define a function to check mentions and co-occurrences for specific themes in a specific quarter


def theme_mentions_and_co_occurrence(quarter, theme1, theme2):
    # Filter data for the specified quarter
    current_quarter_data = merged_df[merged_df['Quarter_Label'] == quarter]

    # Check mentions of theme1
    theme1_mentions = current_quarter_data[theme1].sum()

    # Check mentions of theme2
    theme2_mentions = current_quarter_data[theme2].sum()

    # Check co-occurrences (both themes mentioned together in the same transcript)
    co_occurrence_count = ((current_quarter_data[theme1] > 0) & (
        current_quarter_data[theme2] > 0)).sum()

    return theme1_mentions, theme2_mentions, co_occurrence_count

# Example usage of the function
# quarter = 'Q1 2024'  # Specify the quarter
# theme1 = 'AI'        # Specify the first theme
# theme2 = 'China'     # Specify the second theme
# theme1_mentions, theme2_mentions, co_occurrence_count = theme_mentions_and_co_occurrence(quarter, theme1, theme2)


# Export the co-occurrence matrices to Excel
with pd.ExcelWriter(export_co_occurrence_file_path, engine='xlsxwriter') as writer:
    # Loop through each quarter (key) in the dictionary and export to a sheet
    for quarter, co_occurrence_df in co_occurrence_matrices.items():
        # Write the DataFrame for this quarter to a separate sheet in the Excel file
        co_occurrence_df.to_excel(writer, sheet_name=quarter)
