# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 10:56:06 2024

@author: Steven.Fandozzi
"""

# Background: This is the begining of the Transcript Workflow, Extracting Transcript PDFs from Factset.
# How To: Set the Start and End Dates to the Start of Current Year to Current Day Below. Open Factset and 
#         go to Document Search then Filings. Click Chronological, then Sources/Call Transcripts.
#         Minimize Search (Top) and Document Panel (Right). 
# Input:  Start/End Dates (No leading 0s), Additional/Tickers.xlsx
# Output: Data/Raw FactsetPDF/Ticker PDF Files

#Import Libraries
import numpy as np
import pandas as pd
import os
import pyautogui #Python Graphic User Interface (GUI) Library
import shutil
import time

# Define Start and End Date For Scrape (1Yr Recommended)
start_date = "10/1/2022"
end_date = "12/6/2024"

# Set Base directory path
base_directory = r'S:\Strategy Research\Transcripts\Additional'
directory_path = os.path.join(base_directory, "Tickers.xlsx")

#%% Testing (Adjustments)

#PyAuto GUI - Print Current Position, Move Cursor to Specific Pixel Location
#print(pyautogui.position())
#pix = pyautogui.pixel(1158, 139)

#%% Import Tickers

#Import Data
ticker_list = pd.read_excel(directory_path)
ticker_list = ticker_list.iloc[:, 0].tolist()

#%% Set Ticker

def set_ticker(ticker): 
    #Move to Search bar and double click
    pyautogui.click(x=101, y=223, clicks=3, duration=.1)
    
    #Remove current Value
    pyautogui.press('delete')
    
    modified_ticker = ticker.replace("/", ".")
    
    #Write Document Search
    pyautogui.write(modified_ticker, interval=.05)
    
    time.sleep(2)
    
    #Click on Ticker Value
    pyautogui.click(x=118, y=315, interval=.025)

    time.sleep(3)
    
    #Click on Select All
    #pyautogui.click(x=66, y=379, interval=.01)
    pyautogui.click(x=66, y=400, interval=.01)

#%% Download File

def download(): 

    #Click on Tool Bar
    pyautogui.click(x=1775, y=220, interval=.15)
    
    time.sleep(.5)

    #Check if Download Menu is Open
    pix = pyautogui.pixel(1158, 139)
    if pix != (50, 50, 50):
        return
    
    #Click on Save all Docs to One File
    pyautogui.click(x=524, y=357, interval=.3)
    
    #Click on Set path
    pyautogui.click(x=578, y=523, clicks=3, interval=.1)
    
    #Write File Path - COMPANY FOLDERS
    pyautogui.write(directory_path, interval=.01)
    
    #Don't Open after Download
    pyautogui.click(x=529, y=576, duration=.5)
    
    time.sleep(.5)
    """
    #Check if Open After Download is Clicked
    pix = pyautogui.pixel(565, 515)
    if pix != (225, 225, 225): 
        pyautogui.click(x=1389, y=130, duration=.25)
        return """
    
    #Click Download
    pyautogui.click(x=1264, y=1080, duration=.25)

#%% Run Function For Each Ticker

base_directory = r'S:\Strategy Research\Transcripts\Data\Raw Factset PDF'

time.sleep(2.5)


### Set Date ###

#Click custom cal
pyautogui.click(x=977, y=227, duration = .25)

#Click custom
pyautogui.click(x=1030, y=643, duration = .25)

#Move To Start
pyautogui.click(x=279, y=190, duration = .01)

#Select Current Start
pyautogui.click(x=279, y=190, clicks=3, duration = .25)

#Delete Current Start
pyautogui.press('delete')

#Set Current Start
pyautogui.write(start_date, interval=0.1)

#Select Current End
pyautogui.click(x=302, y=587, clicks=3, duration = .25)

#Delete Current End
pyautogui.press('delete')

#Set Current Start
pyautogui.write(end_date, interval=0.1)

#Click Enter
pyautogui.click(x=732, y=1026, clicks=1, duration=.25)

### Download Each Ticker ####

for ticker in ticker_list: 
    short_ticker = ticker.split('-')[0]
    if short_ticker == 'CON': 
        short_ticker = 'CON-DE'
    directory_path = os.path.join(base_directory, short_ticker)
    set_ticker(ticker)
    time.sleep(1)
    download()
    time.sleep(.25)
