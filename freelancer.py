# Write a program to scratch the freelancer.com website and get the following information:


# WebDriver settings
# selenium 4.2.0 version

# Import regular expression
import re
import time

# Import selenium
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

# Path to the chromedriver
# Chromedriver 108.0.5359.22
# https://chromedriver.chromium.org/downloads
#### Notice the chromedriver version and google chrome version ###
PATH = "chromedriver"

# Set the options
options = Options()
options.add_argument("--disable-notifications")
options.add_argument("--disable-infobars")
options.add_argument("--mute-audio")
options.add_argument("--disable-extensions")
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-default-apps")
options.add_argument("--disable-translate")
options.add_argument("--disable-sync")
options.add_argument("--disable-background-networking")
options.add_argument("--disable-background-timer-throttling")
options.add_argument("--disable-client-side-phishing-detection")
options.add_argument("--disable-component-update")
options.add_argument("--disable-domain-reliability")
options.add_argument("--disable-hang-monitor")
options.add_argument("--disable-ipc-flooding-protection")

# full screen
options.add_argument("--start-maximized")
# Set the driver
driver = webdriver.Chrome(PATH, options=options)
# Import beautifulsoup
from bs4 import BeautifulSoup
# import tqdm
from tqdm import tqdm
import openpyxl
import warnings

# page source: https://www.freelancer.com/job/
driver.get("https://www.freelancer.com/job/")
soup = BeautifulSoup(driver.page_source, "html.parser")
elements = soup.select('.PageJob-category-link[title]')

# Create a new excel file
df1 = pd.DataFrame(columns=['Title', 'Number'])

writer = pd.ExcelWriter('freelancer.xlsx', engine='openpyxl')
cnt = 0
# write in tqdm
for element in tqdm(elements):
    # Job title
    title = element['title']
    # title[0:-5] to remove the " Jobs" at the end of the title
    title = title[0:-5]
    
    # Number of jobs
    element = str(element)
    number = re.search(r"\((\d+)\)", element)
    if number:
        # Extract the number from the match object and save it to the excel file
        number = int(number.group(1))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=FutureWarning)
            new_row = pd.DataFrame({'Title': [title], 'Number': [number]})
            df1 = pd.concat([df1, new_row], ignore_index=True)
    else:
        # If the number was not found, save title to the excel file
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=FutureWarning)
            new_row = pd.DataFrame({'Title': [title], 'Number': [np.nan]})
            df1 = pd.concat([df1, new_row], ignore_index=True)       
    
df1.to_excel(writer, sheet_name="Job Categories", index=False)

search_element = "python"
driver.get("https://www.freelancer.com/job-search/" + search_element + "/")
wait = WebDriverWait(driver, 10)
radio_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(., 'All open jobs')]")))
# Scroll the radio button into view and click it
driver.execute_script("arguments[0].scrollIntoView();", radio_button)
# Click the radio button
radio_button.click()

# Find the checkbox element and click it
checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(., 'Fixed Price Projects')]")))
checkbox.click()

# Find the element and get the text
# element = driver.find_element_by_id('total-results')
# result_text = element.text
cnt = 0

time.sleep(1)

cnt = 0

# Create df2
df2 = pd.DataFrame(columns=['Project', 'Days', 'Avg Price ($)', 'Budget', 'Bid', 'URL', 'Paragraph'])

def get_project():
    global df2
    # Iterate through the job listings
    for i, job_listing in enumerate(job_listings):
        try:
            # Find the title element
            # title_element = job_listing.find_elements(By.CSS_SELECTOR, '.JobSearchCard-primary-heading-link')
            # Get the html from the job_listing
            # html = job_listing.get_attribute('innerHTML')
            project_element = job_listing.find_element(By.CSS_SELECTOR, 'a.JobSearchCard-primary-heading-link')
            project = project_element.text
            
            days_element = job_listing.find_element(By.CSS_SELECTOR, 'span.JobSearchCard-primary-heading-days')
            days = days_element.text
            
            avg_price_element = job_listing.find_element(By.CSS_SELECTOR, 'div.JobSearchCard-secondary-price')
            # remove (Avg Bid) from the text
            avg_price = avg_price_element.text[0:-9]
            avg_price = avg_price.replace("$", "")
            # Convert string to int and add dollar sign
            avg_price = int(avg_price)
            
            bid_element = job_listing.find_element(By.CSS_SELECTOR, 'div.JobSearchCard-secondary-entry')
            bid = bid_element.text
            # Remove the " bids" at the end of the text
            bid = int(bid[0:-5])
            
            element = job_listing.find_element(By.CSS_SELECTOR, 'a.JobSearchCard-primary-heading-link')
            url = element.get_attribute('href')
            
            # Open a new tab, switch to it, and go to the url
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(url) 
               
            try:
                # wait for the QTextEdit element to be visible
                # find the paragraph element using its class name
                parent_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "PageProjectViewLogout-detail")))
                # if the element not found, it will throw an exception
                paragraph_element = parent_element.find_elements(By.TAG_NAME, "p")
            except TimeoutException:
                print("Job not found")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
            # Extract the text from each p element
            text_list = []
            for p_element in paragraph_element:
                text = p_element.text
                text_list.append(text)
            combined_text = "\n".join(text_list)
        
            budget_element = driver.find_element(By.XPATH, "//p[@class='PageProjectViewLogout-header-byLine']")
            budget = budget_element.text
            budget = budget[7:]
            
            # Save the data to the excel file
            # project, days, avg_price, budget, bid, url, paragraph, 
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=FutureWarning)
                
                # Add the data to the dataframe
                new_row = pd.DataFrame({'Project': project, 'Days': days, 'Avg Price ($)': avg_price, 'Budget': budget, 'Bid': bid, 'URL': url, 'Paragraph': combined_text}, index=[0])
                df2 = pd.concat([df2, new_row], ignore_index=True)
                
            # Save the data to the excel file
            df2.to_excel(writer, sheet_name="Job Listings", index=False)
            # Close the tab
            driver.close()
            
            # Switch back to the first tab
            driver.switch_to.window(driver.window_handles[0])
            
            if i == len(job_listings) - 1:
                print("Last element")
        except:
            continue
        

page = 1

while True:
    flag = False
    # Scroll down to the button
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # Wait for the job listings to be present
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.JobSearchCard-item'))
    )
    # Find all the job listings
    job_listings = driver.find_elements(By.CSS_SELECTOR, '.JobSearchCard-item')
    get_project()
    try: 
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#last-entry'))
        )
        
        last_entry_element = driver.find_element(By.CSS_SELECTOR, '#last-entry')
        last_entry = last_entry_element.text
    except:
        pass
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#total-results-bottom'))
        )
        total_results_bottom_element = driver.find_element(By.CSS_SELECTOR, '#total-results-bottom')
        total_results_bottom = total_results_bottom_element.text
    except:
        pass
    if last_entry != total_results_bottom:
        flag = True
        page = page + 1
        
    if flag == True:
        print(flag)
        xpath = f"//li[@data-link='{page}']/a"
        element = driver.find_element(By.XPATH, xpath)
        element.click()
        time.sleep(2)
        continue
    break

writer.save()
driver.close()
driver.quit()