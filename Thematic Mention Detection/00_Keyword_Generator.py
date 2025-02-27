# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 12:49:45 2025

@author: Steven.Fandozzi
"""

import openai  # OpenAI API for keyword generation
import pandas as pd  # Pandas for exporting results to Excel
import os  # OS module for handling file paths

# Replace this with your OpenAI API key
openai.api_key = "YOUR_OPENAI_API_KEY"

# Define the path where the generated Excel files will be saved
SAVE_PATH = "C:/Users/YourUsername/Documents/KeywordExports/"  # Change this to your desired path

# Ensure the directory exists, create it if it doesn’t
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

def generate_thematic_keywords(theme, num_keywords=None):
    """
    Generates a list of descriptive keywords related to a given theme using OpenAI's API.

    Parameters:
        theme (str): The theme for which keywords should be generated.
        num_keywords (int or None): Number of keywords to generate. If None, OpenAI determines the length.

    Returns:
        List of keywords.
    """

    # Define the system's role for better control over responses
    system_content = """
    You are an expert in thematic analysis, keyword generation, and trend identification. 
    Your task is to generate detailed, highly descriptive, and contextually relevant keywords for a given theme. 
    Consider various dimensions such as industry-specific terminology, emerging trends, 
    technological advancements, market impact, and subtopics related to the theme.
    """

    # Constructing a dynamic prompt for OpenAI to generate high-quality keywords
    prompt = f"""
    I am conducting research on the theme: '{theme}'. 
    Generate a comprehensive list of keywords that are:
    - Descriptive and contextually relevant
    - Spanning various subtopics and perspectives
    - Inclusive of both technical and general terms
    - Suitable for market analysis, SEO, or trend tracking
    
    {f"Provide at least {num_keywords} keywords." if num_keywords else "Generate as many relevant keywords as possible."}
    
    Each keyword should be written on a new line.
    """

    try:
        # Making a request to OpenAI's GPT-4 model
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Using the latest GPT model for accuracy
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800  # Increased token limit to allow more keywords
        )

        # Extracting the generated text from the API response
        keywords = response['choices'][0]['message']['content']

        # Splitting the response into a list, assuming each keyword is on a new line
        keyword_list = keywords.split("\n")

        # Cleaning up any empty or whitespace-only keywords
        cleaned_keywords = [kw.strip() for kw in keyword_list if kw.strip()]

        return cleaned_keywords

    except Exception as e:
        print(f"Error occurred: {e}")
        return []

def export_to_excel(theme, keywords):
    """
    Saves the generated keywords to an Excel file at a specified path.

    Parameters:
        theme (str): The theme used for keyword generation.
        keywords (list): List of generated keywords.
    """

    # Create a Pandas DataFrame from the keyword list
    df = pd.DataFrame(keywords, columns=["Keywords"])

    # Define the filename dynamically based on the theme
    filename = f"{theme.replace(' ', '_')}_keywords.xlsx"
    filepath = os.path.join(SAVE_PATH, filename)

    # Export the DataFrame to an Excel file
    df.to_excel(filepath, index=False)

    print(f"\n✅ Keywords successfully saved to {filepath}!")

if __name__ == "__main__":
    # Prompting user for theme input
    theme_input = input("Enter a theme: ")

    # Asking user if they want to specify the number of keywords
    num_keywords_input = input("Enter the number of keywords (or press Enter for automatic generation): ").strip()

    # Convert input to integer if provided, otherwise use None
    num_keywords = int(num_keywords_input) if num_keywords_input.isdigit() else None

    # Generating keywords based on the user's input
    keywords = generate_thematic_keywords(theme_input, num_keywords)

    # Displaying the generated keywords in the console
    print("\nGenerated Keywords:")
    for i, kw in enumerate(keywords, 1):
        print(f"{i}. {kw}")

    # Exporting the keywords to the specified save path
    export_to_excel(theme_input, keywords)

