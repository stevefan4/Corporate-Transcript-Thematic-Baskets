#%% Import Libraries & Define Inputs
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 12:07:46 2024

@author: Steven.Fandozzi
"""

# Background: Now that we have a dataset of PDFs, now we need to convert the unstructured text to a structured dataset
# Output: xyz-Cal Transcript
# Input: Current Year

#Import Libraries
import numpy as np
import pandas as pd
from PyPDF2 import PdfReader
import re
import os

#Set Year
year = "2024"
export_file_path = rf'S:\Strategy Research\Transcripts\Data\Excel\RAW {year}-Cal TRANSCRIPT.xlsx'

#%% Import Tickers

# Base directory path
base_directory = r'S:\Strategy Research\Transcripts'
directory_path = os.path.join(base_directory, r"Additional\Tickers.xlsx")

#Import Data
ticker_list = pd.read_excel(directory_path)
ticker_list = ticker_list.iloc[:, 0].tolist()

#%% Helper Functions

#Create Helper Function: Text Cleaner
def clean_text(text):
    text = text.replace("\n", "")
    text = text.replace("..", "")
    text = re.sub(r'https?:\/\/\S+|www\.\S+', '', text)
    text = re.sub(r'(©|Copyright)\s*\d{4}\s*-\s*\d{4}', '', text)
    text = text.replace("Corrected Transcript", "")
    text = text.replace("CORPORATE PARTICIPANTS", "")
    text = text.replace("OTHER PARTICIPANTS", "")
    text = text.replace("Copyright", "")
    text = text.replace("1-877-FACTSET", "")
    text = text.replace("FactSet", "")
    text = text.replace("CallStreet, LLC", "")
    text = text.replace('THE INFORMATION PROVIDED TO YOU HEREUNDER IS PROVIDED "AS IS," AND TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW,    AND ITS LICENSORS, BUSINESS ASSOCIATES AND SUPPLIERS DISCLAIM ALL WARRANTIES WITH RESPECT TO THE SAME, EXPRESS, IMPLIED AND STATUTORY, INCLUDING  WITHOUT LIMITATION ANY IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, ACCURACY, COMPLETENESS, AND NON -INFRINGEMENT. TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, NEITHER FACTSET CALLSTREET, LLC NOR ITS OFFICERS, MEMBERS, DIRECTORS, PARTNERS, AFFILIATES, BUSINESS ASSOCIATES, LICENSO RS OR SUPPLIERS WILL BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL OR PUNITIVE DAMAGES, INCLUDING WITHOUT LIMITATION DAMAGES FOR LOST PROFITS OR RE VENUES, GOODWILL, WORK STOPPAGE, SECURITY BREACHES, VIRUSES, COMPUTER FAILURE OR MALFUNCTION, USE, DATA OR OTHER INTANGIBLE LOSSES OR COMMERCIAL DAMAGES, EVEN IF ANY OF SUCH PARTIES IS ADVISED OF THE POSSIBILITY OF SUCH LOSSES, ARISING UNDER OR IN CONNECTION WITH THE INFORMATION PROVIDED HEREIN OR ANY OTHER SUBJECT M ATTER HEREOF.   The contents and appearance of this report are Copyrig hted   2023  CallStreet and   are trademarks and service marks of  . All other trademarks mentioned are trademarks of their respective companies. All rights reserved.            ', "")
    text = text.replace('The information herein is based on sources we believe to be reliable but is not guaranteed by us and does not purport to be a complete or error -free statement or summary of the available data. As such, we do not warrant, endorse or guarantee the completeness, accuracy, integrity, or timeliness of the information. You must evaluate, and bear all risks associated with, the use of any information provided hereunder, including any reliance on the accuracy, completeness, safety or usefulness of such informatio n. This information is not intended to be used as the primary basis of investment decisions. It should not be construed as advice designed to meet the particular investment needs of any investor. This report is published solely for information p urposes, and is not to be construed as financial or other advice or as an offer to sell or the solicitation of an offer to buy any security in any state where such an offer or solicitation would be illegal. Any information expressed herein on this date is subject to change without notice. Any opinions or assertions contained in this i nformation do not represent the opinions or beliefs of . , or one or more of its employees, including the writer of this report, may have a po sition in any of the securities discussed herein.', "")
    text = re.sub(r'Q[1-4]\s+\d{4}\s+Earnings\s+Call\s+\d{2}-[A-Za-z]{3}-\d{4}\s+\d+\s*', '', text)
    text = text.replace("          .  ", "")
    text = text.replace("            ", "")
    text = re.sub(r'\d{2}-[A-Za-z]{3}-\d{4}\s+\d+\s*', '', text)
    text = text.strip()
    return text

# Function to extract ticker symbol using regular expression
def extract_ticker(company_str):
    # Define adjustments dictionary
    adjustments_dict = {
        'GOOG': 'GOOGL',
        'NWS': 'NWSA',
        'FISV': 'FI', 
        'FOX': 'FOXA',
        'PKI': 'RVTY',
        'PFHC': 'ACDC',
        'FB': 'META', 
        'Z': 'ZG',
        'AUP.CA': 'AUPH',
        'BIPC.CA': 'BIPC',
        'BORR.NO': 'BIPC',
        'CAL.CA': 'CMCL',
        'PDSB': 'PEAK',
        'PEAK': 'DOC', 
        'EU.CA': 'EU', 
        'FRX.CA': 'FENC',
        'FERG.GB': 'FERG',
        'IAU.CA': 'IAUX', 
        'LILA': 'LILAK', 
        'NB.CA': 'NB',
        'NHF': 'NXDT',
        'GCEA': 'PKST', 
        'QIPT.CA': 'QIPT', 
        'ROLL': 'RBC', 
        'NRZ': 'RITM',
        'SQFL': 'SKYX', 
        'UA': 'UAA', 
        'UONE': 'UONEK', 
        'VMD.CA': 'VMD',
        'LPI': 'VTLE', 
        'WETF': 'WT', 
        'WLTW': 'WTW', 
        'ZIMVV': 'ZIMV', 
    }
    match = re.search(r'\(([^)]+)\)\s*$', company_str)
    if match:
        extracted_ticker = match.group(1).strip()
        return adjustments_dict.get(extracted_ticker, extracted_ticker)
    else:
        return None
    
# Define a function to find the most recent PDF file within a given directory.
def find_most_recent_pdf(ticker_directory):
    
    # Check if the directory exists, return an empty string if it doesn't.
    if not os.path.exists(ticker_directory):
        return ""
    # List all PDF files in the directory.
    pdf_files = [os.path.join(ticker_directory, f) for f in os.listdir(ticker_directory) if f.lower().endswith('.pdf')]
    # If there are no PDF files, return None.
    if not pdf_files:
        return None
    # Find the most recent PDF file based on the last modification time and return its path.
    most_recent_pdf = max(pdf_files, key=os.path.getmtime)
    return most_recent_pdf

#%% Primary Data Scrape

def scrape_data(year):
        
    transcripts = []
    transcript_df = pd.DataFrame()
    directory_path = os.path.join(base_directory, r"Data\Raw Factset PDF")

    for ticker in ticker_list: 
        print(f"Currently Extracting: {ticker}")
        short_ticker = ticker.split('-')[0]
        if short_ticker == 'CON':
            short_ticker = 'CON-DE'
        file_path = os.path.join(directory_path, short_ticker)
        #print(file_path)
        
        # Find Most Recent PDF in Folder
        full_file_path = find_most_recent_pdf(file_path)
        
        if full_file_path == "": 
            continue

        #Try to Find and Read PDF File
        try: 
            reader = PdfReader(full_file_path)
            number_of_pages = len(reader.pages)
            #print("Number of Pages: ", number_of_pages)
        except: 
            #print(full_file_path + ": File Not Found")
            continue

        #Convert PDF reader to current_report dictionary {key = page, value = text} 
        current_report = {}
        for count, ele in enumerate(np.arange(0, number_of_pages)): 
            page = reader.pages[int(ele)]
            current_report[count] = page.extract_text(0)

        #Each Transcript starts with Corp. Part. Find each companies transcript page numbers
        search_val = "CORPORATE PARTICIPANTS"
        segments = [key for key, val in current_report.items() if search_val in val]
        segments.append(number_of_pages)

        #Create Company Level Transcript Dictionary
        company_level_report_mgmt = {}
        company_level_report_qa = {}
        company_level_date = {}
        company_level_event_type = {}
        
        prev_value = segments[0]
        num_segments = len(segments)
        num_pages = segments[-1]
        print(f"Company {ticker} has {num_segments} events with {num_pages} pages of text")
        
        #Loop through the events in pdf (segments list)
        for count, ele in enumerate(segments[1:]): 
            pages = np.arange(prev_value, ele)
            company_text = ""
            for page in pages: 
                company_text += current_report[page]
        
            corrected_transcript_pattern = re.compile(r"Corrected\s+Transcript", re.IGNORECASE)
            company_name = str(company_text.split('\n')[0])
            event_type =  re.sub(corrected_transcript_pattern, "", company_text.split('\n')[1]).strip()
            earnings_date = company_text.split('\n')[2].strip()
        
            # Clean and separate text
            cleaned_text = clean_text(company_text)
            management_discussion = cleaned_text[cleaned_text.find('MANAGEMENT DISCUSSION SECTION'):cleaned_text.find('QUESTION AND ANSWER SECTION')]
            q_and_a = cleaned_text[cleaned_text.find('QUESTION AND ANSWER SECTION'):cleaned_text.find('THE INFORMATION')]
        
            # Adjusted to use tuple (company_name, event_type) as key
            company_key = (company_name, event_type)
            company_level_report_mgmt[company_key] = management_discussion
            company_level_report_qa[company_key] = q_and_a
            company_level_date[company_key] = earnings_date
            company_level_event_type[company_key] = event_type
        
            prev_value = ele

        # Transform the dictionaries into DataFrames
        def dict_to_df(dict, column_name):
            rows = []
            for (company, event_type), value in dict.items():
                row = {'Company': company, 'Event Type': event_type, column_name: value}
                rows.append(row)
            return pd.DataFrame(rows)
        
        # Transform each dictionary
        company_level_report_mgmt_df = dict_to_df(company_level_report_mgmt, 'Transcript - Mgmt')
        company_level_report_qa_df = dict_to_df(company_level_report_qa, 'Transcript - QA')
        company_level_dates_df = dict_to_df(company_level_date, 'Date')
        
        #Make Sure Company Names are Strings
        if not company_level_report_mgmt_df.empty: 
            company_level_report_mgmt_df['Company'] = company_level_report_mgmt_df['Company'].astype(str)
        if not company_level_report_qa_df.empty: 
            company_level_report_qa_df['Company'] = company_level_report_qa_df['Company'].astype(str)
        if not company_level_dates_df.empty: 
            company_level_dates_df['Company'] = company_level_dates_df['Company'].astype(str)
        
        company_level_report_df = company_level_report_mgmt_df
        if not company_level_report_mgmt_df.empty and not company_level_report_qa_df.empty and not company_level_dates_df.empty:
        #Merge Features into into a single df 
            company_level_report_df = pd.merge(company_level_report_df, company_level_report_qa_df, on=['Company', 'Event Type'], how='left')
            company_level_report_df = pd.merge(company_level_report_df, company_level_dates_df, on=['Company', 'Event Type'], how='left')

            #Append company level df to a list for each loop (pdf date)
            transcripts.append(company_level_report_df)
        
        if transcripts:
            #Create and return aggregate df across pdfs
            transcript_df = pd.concat(transcripts, ignore_index=True)
            transcript_df['Ticker'] = transcript_df['Company'].apply(extract_ticker)
            transcript_df['Company Name'] = transcript_df['Company'].str.replace(r'\s*\([^)]*\)\s*$', '', regex=True)
           
            # Insert 'Ticker' and 'Company Name' at the beginning of the dataframe
            ticker_column = transcript_df.pop('Ticker')
            company_name_column = transcript_df.pop('Company Name')
            transcript_df.insert(0, 'Company Name', company_name_column)
            transcript_df.insert(0, 'Ticker', ticker_column)
            transcript_df = transcript_df.drop('Company', axis=1)
    return transcript_df

#Run Data Scraping Function
transcripts = scrape_data(year)

#%% Split Transcripts, Excel cell character count limit: 32767

print("Cleaning Transcripts")

def split_text(text, limit=32767):
    
    #Splits the text if it exceeds the specified limit.
    #Returns the text within the limit and the remaining text.
    
    # Check if the text length exceeds the limit
    if len(text) > limit:
        return text[:limit], text[limit:]
    else:
        return text, None

def clean_transcript(text, company_name, ticker):
    # Ensure company_name and ticker are strings to handle None values safely
    company_name = str(company_name) if company_name else ""
    ticker = str(ticker) if ticker else ""

    # Escape special characters in company name and ticker for regex use
    company_name_escaped = re.escape(company_name)
    ticker_escaped = re.escape(ticker)

    # Build a regex pattern to match company name and ticker, considering optional spaces
    # Include the parentheses around the ticker
    pattern = r'({}|\(\s*{}\s*\))'.format(company_name_escaped, ticker_escaped)
    
    # Remove the patterns from the text
    cleaned_text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove the trailing phrases and everything after them
    # Combine both patterns using the regex "or" (|) operator
    disclaimer_pattern = r'(You may now disconnect\. Disclaimer .*|This concludes today\'s conference call.*|Disclaimer: The information herein.*|The information herein is based on sources.*)'
    cleaned_text = re.sub(disclaimer_pattern, '', cleaned_text, flags=re.IGNORECASE | re.DOTALL)
    
    # Optional: Clean up any resulting double spaces and strip leading/trailing spaces
    cleaned_text = re.sub(r'\s{2,}', ' ', cleaned_text).strip()
    
    return cleaned_text

# Initialize new columns for split results
transcripts['Transcript - Mgmt p2'] = None
transcripts['Transcript - QA p2'] = None

for index, row in transcripts.iterrows():
    # Clean transcripts
    cleaned_mgmt = clean_transcript(row['Transcript - Mgmt'], row['Company Name'], row['Ticker'])
    cleaned_qa = clean_transcript(row['Transcript - QA'], row['Company Name'], row['Ticker'])
    
    # Split cleaned transcripts if they exceed the character limit
    split_mgmt, split_mgmt_p2 = split_text(cleaned_mgmt)
    split_qa, split_qa_p2 = split_text(cleaned_qa)
    
    # Update the DataFrame with the cleaned and split results
    transcripts.at[index, 'Transcript - Mgmt'] = split_mgmt
    transcripts.at[index, 'Transcript - Mgmt p2'] = split_mgmt_p2
    transcripts.at[index, 'Transcript - QA'] = split_qa
    transcripts.at[index, 'Transcript - QA p2'] = split_qa_p2

# Note: This method directly modifies the 'Transcript - Mgmt' and 'Transcript - QA' columns.
# If you need to retain the original columns, consider creating new columns for the cleaned data.

#%% Export Data 

print("Exporting To Excel")

transcripts.to_excel(export_file_path, index=False)