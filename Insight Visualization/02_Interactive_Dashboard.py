# -*- coding: utf-8 -*-
"""
Created on Mon Apr 14 14:18:24 2025

@author: Steven.Fandozzi
"""

# ==========================================
# 📊 Plotly + Dash Dashboard: Thematic Mentions
# ==========================================
# This script builds a local web dashboard using Dash (by Plotly) to explore
# keyword mentions in company earnings call transcripts.
#
# You'll be able to:
# - Choose a theme (e.g. AI, China, Inflation)
# - View how often that theme was mentioned each quarter (overall)
# - View how frequently it's mentioned *by sector*, normalized to highlight
#   which sectors are relatively more engaged each quarter.
#
# You can run this script in a Python IDE or terminal, and then interact
# with the dashboard in your web browser.

# ==========================================
# Setup and Imports
# ==========================================
import pandas as pd               # For working with tabular data
import plotly.express as px       # For interactive visualizations
import dash                       # Main Dash library for building the dashboard
from dash import dcc, html        # Dash components for layout
from dash.dependencies import Input, Output  # For callbacks
import socket                     # To print your local IP address for access

# ==========================================
#  Step 1: Load and Process Data
# ==========================================
# Define the Excel file that contains keyword mentions
input_path = r'S:/Strategy Research/Transcripts/Data/Thematic Mentions/RAW Thematic Mentions_part1.xlsx'

# Load the Excel file
raw_transcript_data = pd.read_excel(input_path)

# Identify which columns represent theme keyword counts (ending with '_keyword_count')
available_keywords = [col for col in raw_transcript_data.columns if col.endswith('_keyword_count')]

# Initialize a dictionary to store filtered data for each theme
raw_transcript_dict = {}

# Loop over each keyword column and preprocess the data
for keyword_col in available_keywords:
    theme = keyword_col.replace('_keyword_count', '')  # Extract theme name
    df = raw_transcript_data[raw_transcript_data[keyword_col] > 0].copy()

    # Keep only necessary columns
    columns_to_keep = ['Ticker', 'Company Name', 'Date', 'Sector', 'Combined Transcript', keyword_col]
    df = df[[col for col in columns_to_keep if col in df.columns]]

    # Parse and clean the Date column
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])

    # Add a "Quarter" column for grouping
    df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)

    # Store the cleaned DataFrame in the dictionary
    raw_transcript_dict[theme] = df

# ==========================================
# Step 2: Define Dashboard Layout
# ==========================================
# Dash is a web framework built by the makers of Plotly.
# It uses Python to define the entire layout and logic for a web app.
# You build the layout using HTML-like elements from dash.html,
# and attach interactive charts with dash_core_components (dcc).

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "📈 Thematic Mentions Dashboard" # Appears in browser tab

# Define the page layout using Dash's HTML elements
app.layout = html.Div([

    # Page Header - Main Title
    html.H1("📊 Thematic Keyword Mentions Dashboard", style={"textAlign": "center"}),

    # Dropdown Menu to select a theme (AI, China, Inflation, etc.)
    html.Div([
        html.Label("Select a Theme:"),
        dcc.Dropdown(
            id="theme-dropdown",
            options=[{"label": theme, "value": theme} for theme in raw_transcript_dict.keys()],
            value=list(raw_transcript_dict.keys())[0],  # Default to first theme
            style={"width": "300px"}
        )
    ], style={"padding": "20px"}),

    # First chart: Time series chart of total mentions
    dcc.Graph(id="mentions-over-time-chart"),

    # Second chart: Sector-clustered normalized mentions chart
    dcc.Graph(id="mentions-by-sector-chart"),

    # Summary block at the bottom
    html.Div(id="mention-summary", style={"padding": "20px", "fontSize": "16px"})

])

# ==========================================
# STEP 3: DEFINE INTERACTIVITY (CALLBACKS)
# ==========================================
# Dash lets you define *callbacks* that automatically run when inputs change.
# Here, when the dropdown value changes, we'll update:
#   - The mentions-over-time chart
#   - The sector-level normalized chart
#   - The summary text

@app.callback(
    Output("mentions-over-time-chart", "figure"),
    Output("mentions-by-sector-chart", "figure"),
    Output("mention-summary", "children"),
    Input("theme-dropdown", "value")
)
def update_charts(selected_theme):
    # Load the relevant data
    df = raw_transcript_dict[selected_theme].copy()
    keyword_col = f"{selected_theme}_keyword_count"

    # -------------------------------
    # Chart 1: Mentions Over Time
    # -------------------------------
    mentions_by_quarter = df.groupby("Quarter")[keyword_col].sum().reset_index()

    fig_time = px.bar(
        mentions_by_quarter,
        x="Quarter",
        y=keyword_col,
        title=f"Mentions of '{selected_theme}' Over Time",
        labels={keyword_col: "Mentions", "Quarter": "Quarter"}
    )

    # -------------------------------
    # Chart 2: Normalized Sector Mentions
    # -------------------------------
    if "Sector" in df.columns:
        sector_mentions = df.groupby(["Sector", "Quarter"])[keyword_col].sum().reset_index()

        # Normalize within each sector
        sector_mentions["MaxInSector"] = sector_mentions.groupby("Sector")[keyword_col].transform("max")
        sector_mentions["Normalized_Mentions"] = sector_mentions[keyword_col] / sector_mentions["MaxInSector"]

        # Ensure quarters sort properly
        sector_mentions["Quarter"] = pd.Categorical(
            sector_mentions["Quarter"],
            categories=sorted(sector_mentions["Quarter"].unique()),
            ordered=True
        )

        fig_sector = px.bar(
            sector_mentions,
            x="Quarter",
            y="Normalized_Mentions",
            color="Sector",
            barmode="group",
            title=f"Normalized Mentions of '{selected_theme}' by Sector",
            labels={"Normalized_Mentions": "Normalized Mentions", "Quarter": "Quarter"}
        )
    else:
        fig_sector = {}

    # -------------------------------
    # Summary Section
    # -------------------------------
    total_mentions = df[keyword_col].sum()
    unique_companies = df["Ticker"].nunique()
    summary = f"Total mentions: {total_mentions:,} across {unique_companies:,} unique companies."

    return fig_time, fig_sector, summary

# ==========================================
# ▶️ Run the App
# ==========================================
# This will launch a web server on http://127.0.0.1:8050
# Open that URL in a browser to view the dashboard.

if __name__ == '__main__':
    # Print helpful URL for local access
    ip_address = socket.gethostbyname(socket.gethostname())
    print("🚀 Dash app is running!")
    print(f"🌐 Open your browser and go to: http://{ip_address}:8050 or http://127.0.0.1:8050")

    # Start the server
    app.run(debug=True)
