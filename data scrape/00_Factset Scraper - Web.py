# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 12:18:52 2025

@author: Steven.Fandozzi
"""

# Import Libraries
from selenium import webdriver  # Import Selenium WebDriver
from selenium.webdriver.common.by import By  # Import the By class for locating elements
from selenium.webdriver.common.keys import Keys  # Import Keys for sending keyboard input
from selenium.webdriver.support.ui import WebDriverWait  # For explicit waits
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import time  # Import time module for adding delays
import pandas as pd # Data Storage and Manipulation
import time 
from datetime import datetime
import shutil
import os # Download Path

# Set Parameters
email = "steven.fandozzi@evercoreisi.com" # Use Factset Email 

# Define Start and End Date For Scrape (1Yr Recommended) - NO LEADING Zeros
start_date = "1/1/2022"
end_date = "4/1/2025"

# Set Base directory path
base_directory = r'S:\Strategy Research\Transcripts\Additional'
directory_path = os.path.join(base_directory, "Tickers.xlsx")

#%% Import Data

ticker_list = pd.read_excel(directory_path)
ticker_list = ticker_list.iloc[:, 0].tolist()

#%% Launch Factset Document Search

# STEP 1: Set up the WebDriver
# This initializes a new instance of the Edge browser.
driver = webdriver.Edge()

# STEP 2: Open FactSet Document Search
# The driver.get() method opens the specified webpage.
driver.get("https://my.apps.factset.com/workstation/document-search/all-documents/")
time.sleep(5)  # Pause execution for 5 seconds to allow the page to load

# STEP 3: Wait for the email input box to load and type email
try:
    # Wait until the input box is visible (up to 10 seconds)
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "input"))  # Or use By.ID / By.NAME if available
    )
    
    # Type your email into the input box
    email_input.send_keys(email)  # Replace with your actual email

    # Press Enter
    email_input.send_keys(Keys.RETURN)

    print("Email entered successfully.")
except Exception as e:
    print(f"Error: Could not find the email field. Details: {e}")
    
time.sleep(1)  # Pause execution for 1 seconds to allow the page to load

# STEP 4: Click the 'Sign in' button
try:
    sign_in_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "submitButton"))  # ID for 'Sign In' on FS login
    )
    sign_in_button.click()
    print("Clicked the sign-in button.")
except Exception as e:
    print(f"Could not click the sign-in button: {e}")

time.sleep(15)  # Pause execution for 15 seconds to allow the page to load

# STEP 5: Switch into the document search iframe
try:
    print("Switching into 'document-search' iframe...")
    WebDriverWait(driver, 20).until(
        EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[data-id='document-search']"))
    )
    print("Successfully switched into document-search iframe.")
except Exception as e:
    print(f"Error switching into iframe: {e}")
    driver.save_screenshot("iframe_switch_failed.png")

"""#%% Set Date Range"""

# STEP 1: Click the calendar icon (with tfv-icon-date inside)
try:
    print("[DEBUG] Looking for calendar button with tfv-icon-date inside...")

    button_candidates = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[role='button']"))
    )

    print(f"[DEBUG] Found {len(button_candidates)} div[role='button'] elements.")

    match = None
    for i, button in enumerate(button_candidates):
        inner_html = button.get_attribute("innerHTML")
        if "tfv-icon-date" in inner_html:
            print(f"[DEBUG] Candidate {i} contains tfv-icon-date → this is likely the calendar.")
            match = button
            break

    if match:
        print("[DEBUG] Scrolling to calendar button...")
        driver.execute_script("arguments[0].scrollIntoView(true);", match)
        time.sleep(0.5)

        try:
            match.click()
            print("[SUCCESS] Calendar icon clicked with .click().")
        except Exception as e:
            print(f"[WARNING] .click() failed: {e}, trying JavaScript click...")
            driver.execute_script("arguments[0].click();", match)
            print("[SUCCESS] Calendar icon clicked via JavaScript.")

    else:
        print("[ERROR] Could not find a calendar icon button.")
        driver.save_screenshot("calendar_icon_not_found.png")

except Exception as e:
    print(f"[FATAL] Could not locate or click calendar icon: {e}")
    import traceback
    traceback.print_exc()
    driver.save_screenshot("calendar_icon_click_failed.png")

time.sleep(5)  # Pause execution for 15 seconds to allow the page to load

try:
    print("[INFO] Attempting to detect all visible input-like fields across the DOM after calendar click...")
    time.sleep(2)  # Allow time for popup animation/rendering

    all_elements = driver.find_elements(By.XPATH, "//input")  # Limit to input fields only
    usable_inputs = []

    for i, el in enumerate(all_elements):
        try:
            tag = el.tag_name
            cls = el.get_attribute("class") or ""
            placeholder = el.get_attribute("placeholder") or ""
            val = el.get_attribute("value") or ""
            input_type = el.get_attribute("type") or ""
            visible = el.is_displayed()
            enabled = el.is_enabled()

            is_editable = input_type == "text"

            if visible and enabled and is_editable:
                print(f"[MATCH] Element {i}: class='{cls}', placeholder='{placeholder}', value='{val}', tag={tag}, type={input_type}")
                usable_inputs.append(el)

        except Exception as err:
            print(f"[ERROR] Could not read element {i}: {err}")
            continue

    print(f"[INFO] Found {len(usable_inputs)} editable input fields on page.")

    # We know the date fields are element 3 and 4
    if len(usable_inputs) >= 4:
        print("[INFO] Sending start_date to Element 3")
        usable_inputs[2].click()
        usable_inputs[2].send_keys(Keys.CONTROL, 'a')
        usable_inputs[2].send_keys(Keys.BACKSPACE)
        usable_inputs[2].send_keys(start_date)

        print("[INFO] Sending end_date to Element 4")
        usable_inputs[3].click()
        usable_inputs[3].send_keys(Keys.CONTROL, 'a')
        usable_inputs[3].send_keys(Keys.BACKSPACE)
        usable_inputs[3].send_keys(end_date)

        print("[SUCCESS] Dates entered into calendar popup.")
    else:
        raise Exception("Less than 4 usable input elements found.")

    print("[INFO] Scanning for OK or Apply button candidates...")
    button_candidates = driver.find_elements(By.XPATH, "//div[@role='button']")
    ok_found = False
    for btn in button_candidates:
        try:
            btn_text = btn.text.strip().lower()
            if btn.is_displayed() and (btn_text == "ok" or btn_text == "apply"):
                print(f"[INFO] Clicking '{btn_text}' button.")
                driver.execute_script("arguments[0].click();", btn)
                print("[SUCCESS] Clicked OK or Apply button.")
                ok_found = True
                break
        except Exception as err:
            print(f"[ERROR] Button interaction failed: {err}")

    if not ok_found:
        print("[WARNING] No visible OK or Apply button matched explicitly. Trying fuzzy fallback...")
        for el in button_candidates:
            try:
                if el.is_displayed() and "ok" in el.get_attribute("innerHTML").lower():
                    driver.execute_script("arguments[0].click();", el)
                    print("[SUCCESS] Fallback clicked button containing 'ok'.")
                    break
            except Exception as e:
                print(f"[ERROR] Fallback button click failed: {e}")

except Exception as e:
    print(f"[FATAL] Calendar popup interaction failed: {e}")

#%% Function That Downloads Transcripts (Given Ticker)

def download_ticker_pdf(ticker):
    try:
        print(f"[INFO] Starting process for ticker: {ticker}")

        # Step 0: Close lingering overlays if present
        try:
            overlay = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, "dialog-overlay_mMAQ3SKE_light"))
            )
            driver.execute_script("arguments[0].remove();", overlay)
            print("[INFO] Overlay removed.")
        except:
            print("[INFO] No overlay found, continuing.")

        # Step 1: Focus on ticker input and enter ticker
        input_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='All Identifiers']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", input_field)
        time.sleep(1)
        input_field.click()
        input_field.send_keys(Keys.CONTROL, 'a')
        input_field.send_keys(Keys.BACKSPACE)
        input_field.send_keys(ticker)
        input_field.send_keys(Keys.ENTER)
        print(f"[SUCCESS] Entered ticker: {ticker}")
        time.sleep(2)  # Slow down to allow ticker load and dropdown selection (6)

        # Step 2: Click checkbox using ActionChains
        checkbox_icon = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'tg-checkbox') and contains(@class, 'tf-icon-checkbox-off-rest')]"))
        )
        container = checkbox_icon.find_element(By.XPATH, "./ancestor::div[contains(@class, 'tf-grid-standard-header') or contains(@class, 'tg-checkbox')]")
        actions = ActionChains(driver)
        actions.move_to_element(container).pause(1).click().perform()
        print("[SUCCESS] Checkbox toggled.")
        time.sleep(2)
        
        # Step 3: Click the download icon (not the final confirmation)
        print("[INFO] Looking for the main download icon...")
        download_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.icon_O53UeJ2D.download_tFstp4RZ"))
        )
        driver.execute_script("arguments[0].click();", download_button)
        print("[SUCCESS] Download button clicked.")
        time.sleep(3)
        
        # Step 4: Select second radio button (Save All Documents)
        radio_buttons = driver.find_elements(By.CSS_SELECTOR, "div.tfv-radio-sprites.icon_O53UeJ2D.radio-sprite_xMiOmUkF_light")
        if len(radio_buttons) >= 2:
            target_radio = radio_buttons[1]  # 2nd option assumed to be 'Save all documents to one file'
            driver.execute_script("arguments[0].scrollIntoView(true);", target_radio)
            time.sleep(.5)
            driver.execute_script("arguments[0].click();", target_radio)
            time.sleep(.5)

        # Step 5: Click final 'Download' confirmation button
        print("[INFO] Looking for final confirmation download button...")
        final_download = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='tfv-button-content tfv-button-content_IhligsEc' and text()='Download']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", final_download)
        time.sleep(.5)
        driver.execute_script("arguments[0].click();", final_download)
        print("[SUCCESS] Final download confirmed.")
        
        # Step 6: Wait for file to appear in Downloads folder and move it
        print("[INFO] Waiting for file to appear in Downloads folder...")
        download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        base_directory = r'S:\\Strategy Research\\Transcripts\\Data\\Raw Factset PDF'
        short_ticker = ticker.split('-')[0]
        destination_folder = os.path.join(base_directory, short_ticker)
        os.makedirs(destination_folder, exist_ok=True)

        filename = None
        timeout = 60
        start_time = time.time()

        # Monitor downloads folder for a matching PDF
        while time.time() - start_time < timeout:
            files = os.listdir(download_dir)
            pdfs = [f for f in files if f.lower().endswith(".pdf") and "smart search" in f.lower() and not f.endswith(".crdownload")]
            if pdfs:
                filename = max(pdfs, key=lambda f: os.path.getctime(os.path.join(download_dir, f)))
                break
            time.sleep(1)

        if filename:
            source_path = os.path.join(download_dir, filename)
            dest_path = os.path.join(destination_folder, filename)
            shutil.move(source_path, dest_path)
            print(f"[SUCCESS] File moved to {dest_path}")
        else:
            print("[WARNING] No matching PDF file found after waiting.")

    except Exception as e:
        print(f"[FATAL] Failed to complete download for {ticker}: {e}")

#%% Loop over tickers

for ticker in ticker_list:
    download_ticker_pdf(ticker)

#%% Close the Browser

driver.quit() # Always close the browser after completing automation.

