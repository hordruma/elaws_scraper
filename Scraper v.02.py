# %%
# Standard libraries
from datetime import datetime
import json
import os
import string
import time

# Third-party libraries
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager



# %%
#Constant for requests headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# %%
# Global Classes
SECTION_CLASSES = ['section', 'section-e']
HEADNOTE_CLASSES = ['headnote', 'headnote-e']
AMENDMENTS_HEADING_CLASS = 'amendments-heading'


# %%
#Function to contain base URLs
def get_url_dict():
    '''
    ##List of main URLs for different datasets, returns a dictionary of urls for different configurations:
    all_source_law - all "Source Law" including priv. statutes, total 13.75K (as of Dec 7, 2023)
    all_law - Current and Repealed Laws & regs, total 5088 (as of Dec 7 2023)
    current_all_law - current laws & regs, total 3023 (as of Dec 7 2023)
    repealed_all_law - repealed laws & regs, total 2065 (as of Dec 7 2023)
    current_statutes - current laws, total 816 (as of Dec 7 2023)
    current_regs - current regs, total 2207 (as of Dec 7 2023)
    repealed_statutes - repealed laws, total 408 (as of Dec 7 2023)
    repealed_regs - repealed regs, total 1657 (as of Dec 7 2023)

    '''
    # ELaws URL Constants
    url_dict = {
        "all_source_law": "https://www.ontario.ca/laws?search=&filterstate%5B%5D=current&filteroption=source&filteryear=&source_type%5B%5D=public&source_type%5B%5D=private&source_type%5B%5D=regulation&pit_date=&filtertype=Regulation&sort=&sort_letter=&browse=on",
        "all_law": "https://www.ontario.ca/laws?search=&filteroption=current&filterstate%5B0%5D=current&filterstate%5B1%5D=rrs&filteryear=&source_type%5B0%5D=public&source_type%5B1%5D=regulation&pit_date=&filtertype=Statute%2CRegulation&sort=&sort_letter=&browse=on&from=",
        "current_all_law": "https://www.ontario.ca/laws?search=&filteroption=current&filterstate%5B%5D=current&filteryear=&source_type%5B%5D=public&source_type%5B%5D=regulation&pit_date=&filtertype=Statute%2CRegulation&sort=&sort_letter=&browse=on",
        "repealed_all_law": "https://www.ontario.ca/laws?search=&filteroption=current&filterstate%5B%5D=rrs&filteryear=&source_type%5B%5D=public&source_type%5B%5D=regulation&pit_date=&filtertype=Statute%2CRegulation&sort=&sort_letter=&browse=on",
        "current_statutes": "https://www.ontario.ca/laws?search=&filteroption=current&filterstate%5B%5D=current&filteryear=&source_type%5B%5D=public&source_type%5B%5D=regulation&pit_date=&filtertype=Statute%2CRegulation&sort=&sort_letter=&browse=on",
        "current_regs": "https://www.ontario.ca/laws?search=&filteroption=current&filterstate%5B%5D=rrs&filteryear=&source_type%5B%5D=public&source_type%5B%5D=regulation&pit_date=&filtertype=Statute%2CRegulation&sort=&sort_letter=&browse=on",
        "repealed_statutes": "https://www.ontario.ca/laws?search=&filteroption=current&filterstate%5B%5D=current&filteryear=&source_type%5B%5D=public&source_type%5B%5D=regulation&pit_date=&filtertype=Statute%2CRegulation&sort=&sort_letter=&browse=on",
        "repealed_regs": "https://www.ontario.ca/laws?search=&filteroption=current&filterstate%5B%5D=rrs&filteryear=&source_type%5B%5D=public&source_type%5B%5D=regulation&pit_date=&filtertype=Statute%2CRegulation&sort=&sort_letter=&browse=on",
        # ... other URLs
    }
    return url_dict


# %%
#Select URL for relevant dataset
def get_main_base_url(key="all_law"):
    '''
    #Gets the url for a particular scraper batch, options include:
    all_source_law - all "Source Law" including priv. statutes, total 13.75K (as of Dec 7, 2023)
    all_law - Current and Repealed Laws & regs, total 5088 (as of Dec 7 2023)
    current_all_law - current laws & regs, total 3023 (as of Dec 7 2023)
    repealed_all_law - repealed laws & regs, total 2065 (as of Dec 7 2023)
    current_statutes - current laws, total 816 (as of Dec 7 2023)
    current_regs - current regs, total 2207 (as of Dec 7 2023)
    repealed_statutes - repealed laws, total 408 (as of Dec 7 2023)
    repealed_regs - repealed regs, total 1657 (as of Dec 7 2023)

    ## Example usage
    #print(main_base_url("current_all_law"))  # Should return the URL for 'current_all_law'
    '''
    url_dict = get_url_dict()
    main_base_url = url_dict.get(key, "Key not found")
    return main_base_url

# %%
#Function to start Selenium driver, get URL, and wait
'''
#Initializes FireFox webdriver and gets the current URL, waits 10s so all elements are loaded.
args = url, wait_time (default 10s)
'''
def start_driver_and_wait(url, wait_time=8):
    driver = webdriver.Chrome()
    driver.get(url)

    # Wait for a fixed period
    time.sleep(wait_time)

    return driver


# %%
#Function to fetch and parse page html using BS
def fetch_and_parse(driver):
    """
    Parses the current page content of a WebDriver into a BeautifulSoup object.

    Args:
        driver (webdriver): Selenium WebDriver with the loaded page.

    Returns:
        BeautifulSoup: Parsed HTML content of the page.

    ###Example USG:
    #driver = start_driver_and_wait(url)
    #soup = fetch_and_parse(driver)
    """
    soup = BeautifulSoup(driver.page_source, "lxml")
    return soup

# %%
#Define function to get list of laws and regs, 5086 Available as of 2023-11-20; default: (0, 6000, 50)
def scrape_ontario_laws(main_base_url, start_page=0, end_page=6000, step=50):
    """
    Scrapes a specified range of pages from the Ontario laws website for legislation and regulation information.

    The function iterates over pages in the specified range, extracting data such as hyperlinks, citations,
    classes (act or regulation), parent legislation names, currency status, and currency dates. The extracted 
    data is then compiled into a DataFrame.

    Parameters:
    main_base_url (str): The base URL of the Ontario laws website to scrape.
    start_page (int, optional): The starting page number for scraping. Default is 0.
    end_page (int, optional): The ending page number for scraping. Default is 6000.
    step (int, optional): The step size for iterating through the pages. Default is 50.

    Returns:
    pd.DataFrame: A DataFrame containing the scraped data, with columns for hyperlinks ('ahref'), citations,
    class ('regulation' or 'act'), parent legislation, currency status, currency date, and the date scraped.

    Example:
    # Example usage
    main_base_url = "https://www.ontario.ca/laws?..."
    laws_and_regs = scrape_ontario_laws(main_base_url, start_page=0, end_page=6000, step=50)
    print(laws_and_regs.shape)

    # Save the DataFrame to a CSV file
    csv_filename = 'laws_and_regs.csv'
    laws_and_regs.to_csv(csv_filename, index=False)
    print(f"Data saved to {csv_filename}")
    """
    # Create lists to store the extracted data
    ahref_list = []
    citation_list = []
    class_list = []
    parent_legislation_list = []
    currency_list = []
    currency_date_list = []

    #Scrape legislation and regulations - 
        # Scrape legislation and regulations
    for page_number in range(start_page, end_page, step):
        URL = main_base_url + str(page_number)
        response = requests.get(URL, headers=HEADERS)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "lxml")
        #Print the page URL for verification:
            print("Scraping page:", URL)

            # Find all the table rows (tr)
        rows = soup.find_all('tr')
        print("Number of rows in page:", len(rows))

        # Iterate through each row
        for row in rows:
            # Find the td within the row
            td = row.find('td')

            if td:
                # Extract the information from the td
                a_tag = td.find('a')
                ahref = a_tag['href'] if a_tag else None
                citation = a_tag.get_text(strip=True) if a_tag else None

                div_reg_act = td.find('div', class_='reg-act')
                parent_legislation = div_reg_act.find('b').get_text() if div_reg_act else "None"

                span_label = td.find('span', class_='label')
                currency = span_label.get_text(strip=True) if span_label else None

                # Find the span with class 'time' or 'no-date'
                span_time = td.find('span', class_='time')
                if span_time:
                    currency_date = span_time.get_text(strip=True)
                else:
                    span_no_date = td.find('span', class_='no-date')
                    if span_no_date:
                        currency_date = span_no_date.get_text(strip=True)
                    else:
                        currency_date = "None"

                # Append the extracted data to the respective lists
                ahref_list.append(ahref)
                citation_list.append(citation)
                class_list.append("regulation" if div_reg_act else "act")
                parent_legislation_list.append(parent_legislation)
                currency_list.append(currency)
                currency_date_list.append(currency_date)

        # else:
            #  print(f"Failed to retrieve page {URL}")

    # Create a DataFrame from the extracted data
    data = {
        'ahref': ahref_list,
        'citation': citation_list,
        'class': class_list,
        'parent_legislation': parent_legislation_list,
        'currency': currency_list,
        'currency_date': currency_date_list
    }

    laws_and_regs = pd.DataFrame(data)

    #Add Date Scraped Column
    today = datetime.today()
    laws_and_regs['date_scraped'] = today

    # Drop duplicate rows if any
    laws_and_regs = laws_and_regs.drop_duplicates(keep='first')

    return laws_and_regs

# %%
#Create a function to sanitize filenames
def sanitize_filename(name, max_length=168):
    if isinstance(name, pd.Series):
        name = name.iloc[0] if not name.empty else "default_name"
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    sanitized_name = ''.join(c for c in name if c in valid_chars)
    return sanitized_name[:max_length]

# %%
#Function to Scrape Versions to csv
def scrape_versions_to_csv(url, driver, identifier, output_directory):
    """
    Scrapes version information from a url/law and saves it as a CSV file.

    This function navigates to a given URL using a Selenium WebDriver, extracts version data from a specified HTML structure,
    and saves the data to a CSV file in a specified directory.

    Parameters:
    url (str): Webpage URL to scrape.
    driver (webdriver object): Selenium WebDriver for web navigation.
    identifier (str): Identifier for naming the output file.
    output_directory (str): Directory path for saving the CSV file.
    
    # Example usage
    scrape_versions_to_csv("https://www.ontario.ca/laws/statute/90l11", 'test', 'c:/XX')

    """
    try:
        try:
            link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr.more-versions.hide a")))
            link.click()
        except:
            print("More Versions link not found. Proceeding with the current page source.")

        #Make soup
        soup = fetch_and_parse(driver)

        # Find the 'div' tag with the class "versions"
        versions = soup.find('div', id="versions")
        if not versions:
            print("Versions Tag not found.")
            return

        # Find the table and get rows
        versions_table = versions.find('table', class_='act-reg-list noStripes')
        if not versions_table:
            print("Table not found in the HTML.")
            return

        version_rows = versions_table.findAll('tr')
        if not version_rows:
            print("No rows found in the table.")
            return

        # Initialize lists to store the data
        hrefs, valid_froms, valid_tos = [], [], []

        # Process each row
        for row in version_rows:
                td_cells = row.find_all('td')
                if len(td_cells) >= 2:
                    a_tag = td_cells[1].find('a')
                    if a_tag:
                        span_tags = td_cells[1].find_all('span', class_='time')
                        href = a_tag['href']
                        valid_from = span_tags[0].get_text().strip() if span_tags else 'N/A'
                        valid_to = span_tags[1].get_text().strip() if len(span_tags) > 1 else 'current'
                        hrefs.append(href)
                        valid_froms.append(valid_from)
                        valid_tos.append(valid_to)

        # Create DataFrame and save to CSV
        versions_data = pd.DataFrame({
            'a_href': hrefs,
            'valid_from': valid_froms,
            'valid_to': valid_tos
        })

        # Normalize Full-URL
        current_url = url
        relative_path = current_url.replace('https://www.ontario.ca', '')

        # Replace the first value in 'a_href' column
        versions_data.loc[0, 'a_href'] = relative_path

        # Ensure output_directory exists
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Process identifier to ensure it is a valid filename
        valid_filename = sanitize_filename(identifier)
        csv_filename = f"{valid_filename}.csv"
        

        # Saving the file
        file_path = os.path.join(output_directory, csv_filename)
        try:
            versions_data.to_csv(file_path, index=False)
            print(f"Data saved to {csv_filename}")
        except Exception as e:
            print(f"Failed to save {csv_filename}: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")

# %%
#Function to extract revoked regs:
def extract_revoked_regs_data(soup, url):
    """
    Extracts data about revoked regulations from a BeautifulSoup object.

    Args:
        soup (BeautifulSoup): BeautifulSoup object of the page.
        url (str): The URL of the web page being processed, used for logging and tracking purposes.

    Returns:
        dict: Dictionary with data of revoked regulations.
    # Example usage
    #url = "https://www.ontario.ca/laws/statute/90p10"
    #revoked_regs_data = extract_revoked_regs_data(url)

    # Print first few JSON objects for demonstration
    #for json_obj in revoked_regs_data[:5]:
    #    print(json_obj)

        
    """
    # Initialize Revoked Regs DF
    revoked_regs_data = pd.DataFrame()

    # Find the 'div' tag with the class "versions"
    revoked_regs = soup.find('div', id="revoked_regulations")

    if revoked_regs is not None:
    #print("Revoked Regulations (RR) Tag found for " + url + "!")

        # Find the table
        revoked_regs_table = revoked_regs.find('table', class_='act-reg-list noStripes')

        if revoked_regs_table:
            revoked_regs_rows = revoked_regs_table.findAll('tr')
            if revoked_regs_rows:
            # print("Rows found!")
                # Process the rows
                citations, titles, hrefs = [], [], []
                
                for row in revoked_regs_rows:
                    td_cells = row.find_all('td')
                if len(td_cells) >= 2:
                        a_tag = td_cells[1].find('a')
                        if a_tag:
                            citations.append(td_cells[0].get_text().strip())
                            titles.append(a_tag.get_text().strip())
                            hrefs.append(a_tag['href'])

                # Create DataFrame
                revoked_regs_data = pd.DataFrame({
                    'revoked_reg_a_href': hrefs,
                    'revoked_reg_citation': citations,
                    'revoked_reg_title': titles
                })
            else:
                print("No Revoked Regs (RR) rows found in the table.")
                pass
        else:
            print("RR Table not found in the HTML.")
            pass
    else:
        print("Revoked Regulations (RR) not found for " + url + ".")
        pass

        # Convert DataFrame to JSON object
        revoked_regs_dict = revoked_regs_data.to_dict(orient='records')

        return revoked_regs_dict

# %%
# Function to extract current regs
def extract_current_regs_data(soup, url):
    """
    Extracts data about current regulations from a BeautifulSoup object.

    Args:
        soup (BeautifulSoup): BeautifulSoup object of the page.
        url (str): The URL of the web page being processed, used for logging and tracking purposes.

    Returns:
        dict: Dictionary with data of current regulations.

    #Example Usage
    #url = "https://www.ontario.ca/laws/statute/23s01"
    #current_regulations_data = extract_current_regs_data(url)

    # Print first few JSON objects for demonstration
    #for json_obj in current_regulations_data[:5]:
    #   print(json_obj)
    """
    # Initialize DataFrame
    regulations_data = pd.DataFrame()

    # Find the 'div' tag with the class "versions"
    regulations = soup.find('div', id="regulations")

    if regulations is not None:
        # Find the table
        regulations_table = regulations.find('table', class_='act-reg-list noStripes')

        if regulations_table:
            regulations_rows = regulations_table.findAll('tr')

            if regulations_rows:
                # Initialize lists to store the data
                citations, titles, hrefs = [], [], []

                # Iterate over each row in the table
                for row in regulations_rows:
                    td_cells = row.find_all('td')
                    if len(td_cells) >= 2:
                        a_tag = td_cells[1].find('a')
                        if a_tag:
                            citations.append(td_cells[0].get_text().strip())
                            titles.append(a_tag.get_text().strip())
                            hrefs.append(a_tag['href'])

                # Create DataFrame
                regulations_data = pd.DataFrame({
                    'a_href': hrefs,
                    'Citation': citations,
                    'title': titles
                })
            else:
                print("No CR rows found in the table.")
                pass
        else:
            print("CR Table not found in the HTML.")
            pass
    else:
        print("Current Regulations (CR) tag not found for " + url + ".")
        pass

    # Convert DataFrame to JSON object
    current_regs_dict = regulations_data.to_dict(orient='records')

    return current_regs_dict

# %%
#Function to get Act Info
def parse_act_info(soup, url):
    """
    Parses act information from the given BeautifulSoup object.

    Args:
        soup (BeautifulSoup): BeautifulSoup object containing the act page content.
	url (Str): url to fill in url field

    Returns:
        dict: Extracted act information.

    # Example usage
    #url = "https://www.ontario.ca/laws/statute/90p10"
    #act_metadata_json_objects = parse_act_info(url)

    # Print first few JSON objects for demonstration
    #for json_obj in act_metadata_json_objects[:5]:
    #    print(json_obj)
    """
    # Get Short Title
    current_li = soup.find('li', class_='current')
    full_title = current_li.get_text() if current_li else 'Not Found'

    # Get citation
    act_name = soup.find('p', class_='shorttitle')
    act_name_text = act_name.get_text() if act_name else 'Not Found'
    citation_raw = full_title.replace(act_name_text, "") if full_title and act_name_text else ''
    citation = citation_raw.lstrip(', ') if citation_raw else 'Not Found'

    # Add Date Scraped Column
    today = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

    # Create dictionary of scraped data
    act_info = {
        "full_title": full_title,
        "act_name_text": act_name_text,
        "citation": citation,
        "url": url,
        "date_scraped": today
    }

    return act_info

# %%
#Function to get Regs Info
def parse_reg_info(soup, url):
    """
    Parses regulation information from the given BeautifulSoup object.

    Args:
        soup (BeautifulSoup): BeautifulSoup object containing the regulation page content.
	url (Str): url to fill in url field

    Returns:
        dict: Extracted regulation information.

    # Example usage
    #url = "https://www.ontario.ca/laws/regulation/100034"
    #reg_metadata_json_objects = scrape_reg_info(url)


    # Print first few JSON objects for demonstration
    #for json_obj in reg_metadata_json_objects[:5]:
    #    print(json_obj)
    """
    # Get Short Title
    current_li = soup.find('li', class_='current')
    full_title = current_li.get_text() if current_li else 'Not Found'

    # Get Act Promulgated Under
    act_under = soup.find('p', class_='shorttitle-e')
    act_under_text = act_under.get_text() if act_under else 'Not Found'

    # Get Reg name
    reg_name = soup.find('p', class_='regtitle-e')
    reg_name_text = reg_name.get_text() if reg_name else 'Not Found'

    # Derive Citation
    citation_raw = full_title.replace(reg_name_text, "") if full_title and reg_name_text else ''
    citation = citation_raw.lstrip(': ') if citation_raw else 'Not Found'

    # Add Date Scraped Column
    today = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

    # Create dictionary of scraped data
    reg_info = {
        "full_title": full_title,
        "reg_name_text": reg_name_text,
        "citation": citation,
        "act_under": act_under_text,
        "url": url,
        "date_scraped": today
    }

    return reg_info

# %%
# Function to remove trailing '.0'
def remove_trailing_zero(number):
    """
    Removes the trailing '.0' from a number represented as a string.

    Args:
    number (float or str): The number from which to remove the trailing '.0'.

    Returns:
    str: The number as a string without the trailing '.0', if present.
    """
    number_str = str(number)
    if number_str.endswith('.0'):
        return number_str[:-1]  # Remove last two characters ('.0')
    return number_str

# %%
#Function to Process sections
def process_section(section):
    """
    Processes a given section of a legal document and returns the extracted content.

    Args: 
        section (bs4.element.Tag): The section element to process.

    Returns:
        dict: A dictionary containing the section's id, headnote, content, and raw HTML.
    """
    #Initialize Data, current headnote
    a_tag = section.find('a')
    b_tag = section.find('b')

    if a_tag is not None:
        id_value = a_tag.get('name')
    elif b_tag is not None:
        id_value = b_tag.text.strip()
    else:
        id_value = None

    # Capture the headnote for the current section
    headnote_tag = section.find_previous('p', class_='headnote') or\
                     section.find_previous('p', class_='headnote-e') or\
                     section.find_previous('h3', class_='heading1')
    current_headnote = headnote_tag.text if headnote_tag else None

    content = [section.text]
    raw_html = [str(section)]

    for sibling in section.find_next_siblings():
        #print(f"Section: {current_headnote}, Sibling tag: {sibling.name}, class: {sibling.get('class', [])}")

        # Directly check if we've hit the start of a new section
        if sibling.name == 'p' and 'headnote' in sibling.get('class', []) or 'headnote-e' in sibling.get('class', []):
            # Look ahead to the next sibling
            next_elem = sibling.find_next_sibling()
            # Check if the next sibling is a section
            if next_elem:
                if ((next_elem.name == 'p' and 'section' in next_elem.get('class', [])) or \
                    (next_elem.name == 'p' and 'section-e' in next_elem.get('class', [])) or \
                 #   (next_elem.name == 'p' and 'headnote' in next_elem.get('class', [])) or \ # experimental
                 #   (next_elem.name == 'p' and 'headnote-e' in next_elem.get('class', [])) or \ #experimental
                 #   (next_elem.name == 'h2' and 'partnum' in next_elem.get('class', [])) or \ #experimental 
                 #   (next_elem.name == 'h2' and 'partnum-e' in next_elem.get('class', [])) or \ #experimental
                    (next_elem.name == 'h3' and 'heading1' in next_elem.get('class', []))):
                    break

            # Skip if it's an amendments section
            if sibling.name == 'p' and 'amendments-heading' in sibling.get('class', []):
                continue
        
        sibling_text = sibling.text.replace('\xa0', ' ').strip()
        raw_html.append(str(sibling))
        content.append(sibling_text)

    # Return a dictionary for the current section
    return {
        'id': id_value,
        'section': current_headnote,
        'content': ' '.join(content),
        'raw_html': ' '.join(raw_html)
    }

# %%
#Function to get LAW from a traditional TOC-bearing page
def scrape_TOC_law(url):
    """
    Extracts and organizes legal information from a table of contents (TOC) on a given webpage.

    This function processes a webpage containing legal documents, such as regulations or statutes, 
    represented by a traditional TOC structure. It scrapes and organizes the legal content 
    into a structured format.

    Parameters:
    soup (BeautifulSoup): A BeautifulSoup object of the webpage, which is used for parsing HTML content.
    url (str): The URL of the webpage to be scraped. This is used to retrieve tables with Pandas.

    Returns:
    list[dict]: A list of dictionaries where each dictionary contains detailed information about a section 
                or part of the legal document. The keys in the dictionary include 'ahref_id', 'TOCid', 
                'section', 'part_id', 'part_type', 'content', and 'raw_html', providing a comprehensive
                overview of each section's content and metadata.

    The function performs several steps:
    1. Extracts tables and relevant links from the TOC.
    2. Initializes and populates a DataFrame with the TOC information.
    3. Adjusts TOC identifiers and retrieves corresponding content sections.
    4. Merges TOC information with actual content, organizing it into a structured format.
    5. Converts the organized data into a dictionary format suitable for JSON serialization.

    Example usage:
    ```
    from bs4 import BeautifulSoup
    import requests

    url = 'https://www.ontario.ca/laws/statute/90i03'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    legal_data = scrape_TOC_law(soup, url)
    ```
    """
    #Create object page
    webpage = requests.get(url)
    soup = BeautifulSoup(webpage.content, "lxml")
    
    # Obtain info from TOC
    tables = soup.find_all('table')
    for table in tables:
        if 'MsoNormalTable' in table.get('class', ''):
            table1 = table
            break
    tocspans = table1.findAll('span')

    # Initialize variables to store the previous part's TOCid and section
    previous_part_tocid = None
    previous_part_section = None  # Initialize previous_part_section

    # Create a dictionary to store PARTS ahref pointers
    parts_ahref_pointers = {}
    for span in tocspans:
        span_text = span.text
        ahref = span.find('a', href=True)
        if ahref:
            parts_ahref_pointers[span_text] = ahref['href']

    # Create dataframe to hold legislation info
    leginfo = pd.DataFrame(columns=['ahref_id', 'TOCid', 'section'])

    # Get Tables with Pandas
    dfs = pd.read_html(url)

    # Check for the presence of specific a href links
    revoked_regulations_exists = bool(soup.find('a', href="#revoked_regulations"))
    current_regulations_exists = bool(soup.find('a', href="#regulations"))

    # Determine the TOC index based on the existence of specific links
    if revoked_regulations_exists and current_regulations_exists:
        TOC = dfs[3]  # Set to table at index 3
    elif current_regulations_exists or revoked_regulations_exists:
        TOC = dfs[2]  # Set to table at index 2
    else:
        TOC = dfs[1]  # Set to table at index 1

    # Populate TOCid & section Title
    leginfo['TOCid'] = TOC[0]
    leginfo['section'] = TOC[1]

    # Remove any trailing zeroes from tocid
    leginfo['TOCid'] = leginfo['TOCid'].apply(remove_trailing_zero)

    # Iterate through the 'leginfo' DataFrame and update ahref_id
    for index, row in leginfo.iterrows():
        TOCid = row['TOCid'] or row['TOCid-e']
        ahref = soup.find('a', string=TOCid, href=True)
        if ahref:
            leginfo.at[index, 'ahref_id'] = ahref['href']

    # Update the 'leginfo' DataFrame with parts and part pointers
    next_ahref_pointer = 0
    for index, row in leginfo.iterrows():
        ahref_id = row['ahref_id']
        if pd.isna(ahref_id) and next_ahref_pointer < len(parts_ahref_pointers):
            new_ahref_id = list(parts_ahref_pointers.values())[next_ahref_pointer]
            TOCid = list(parts_ahref_pointers.keys())[next_ahref_pointer]
            leginfo.at[index, 'ahref_id'] = new_ahref_id
            leginfo.at[index, 'TOCid'] = TOCid
            next_ahref_pointer += 1

    # Update part_id and part_type in leginfo DataFrame
    previous_part_tocid = None
    for index, row in leginfo.iterrows():
        TOCid = str(row['TOCid'])
        if TOCid.startswith("PART"):
            previous_part_tocid = TOCid
            previous_part_section = row['section']
        else:
            leginfo.at[index, 'part_id'] = previous_part_tocid
            leginfo.at[index, 'part_type'] = previous_part_section

    full_data = []

    # Your list of section classes
    section_classes = ['section', 'section-e']

    # Create a CSS selector string to select paragraphs with any of the classes
    selector = ', '.join(f'p.{cls}' for cls in section_classes)

    # Assuming 'soup' is your BeautifulSoup object
    for section in soup.select('p.section') or soup.select('p.section-e'):
        section_data = process_section(section)
        full_data.append(section_data)

    content_df = pd.DataFrame(full_data)
    content_df['ahref_id'] = "#" + content_df['id']
    content_df = content_df.drop(columns=['id'], axis=1)
    content_df = content_df[['ahref_id', 'section', 'content', 'raw_html']]


    # Merge leginfo with section content
    leg_full = leginfo.merge(content_df, how="left", on=['ahref_id'])



    # Return the merged data
    #return leg_full
    # Convert DataFrame to dictionary for JSON use
    return leg_full.to_dict(orient='records')

# %%
#Function to get LAW from a left-head-bearing page
def scrape_lefthead_law(url):
    """
    Extracts and organizes legal information from a webpage with a left-head-bearing layout.

    This function is designed to scrape and structure legal content from webpages where the table of contents (TOC) 
    and legal sections are formatted with a left-head-bearing layout. It parses the webpage content and structures it 
    into a readable and usable format.

    Parameters:
    soup (BeautifulSoup): A BeautifulSoup object for parsing HTML content of the webpage.
    url (str): The URL of the webpage to be scraped. This is used to retrieve tables using Pandas.

    Returns:
    list[dict]: A list of dictionaries where each dictionary contains information about a legal section or part.
                The keys in the dictionary include 'ahref_id', 'TOCid', 'section1', 'section2', 'part_id', and 
                corresponding section content and raw HTML.

    The function performs several steps:
    1. Extracts the TOC and identifies relevant links and parts pointers.
    2. Initializes and populates a DataFrame with TOC and section information.
    3. Associates each TOC entry with its corresponding section content.
    4. Processes and collects content of each section based on predefined classes.
    5. Merges the TOC information with the section content.
    6. Converts the final structured data into a dictionary format suitable for JSON serialization.

    Example usage:
    ```
    from bs4 import BeautifulSoup
    import requests

    url = 'http://example.com/legal-doc'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    legal_data = scrape_lefthead_law(soup, url)
    ```

    Note:
    This function is specifically tailored for webpages with a certain structure and may not work 
    correctly with pages of different formats.
    """
    #Create object page
    webpage = requests.get(url)
    soup = BeautifulSoup(webpage.content, "lxml")
    
    # Process TOC spans and parts ahref pointers
    table1 = soup.find('table', class_='MsoNormalTable') or soup.find('table', class_='MsoNormalTable-e')
    tocspans = table1.findAll('span')
    parts_ahref_pointers = {}
    for span in tocspans:
        span_text = span.text
        ahref = span.find('a', href=True)
        if ahref:
            parts_ahref_pointers[span_text] = ahref['href']

    # Create leginfo DataFrame
    leginfo = pd.DataFrame(columns=['ahref_id', 'TOCid', 'section'])
    dfs = pd.read_html(url)
    TOC = dfs[1]
    leginfo['TOCid'] = TOC[0]
    leginfo['section1'] = TOC[1]
    leginfo['section2'] = TOC[2]

    # Update leginfo DataFrame with ahref ids
    for index, row in leginfo.iterrows():
        TOCid = row['section1']
        ahref = soup.find('a', string=TOCid, href=True) or soup.find('a', string=f"{TOCid}-e", href=True)
        if ahref:
            leginfo.at[index, 'ahref_id'] = ahref['href']

    # Update leginfo DataFrame with parts and part pointers
    next_ahref_pointer = 0
    for index, row in leginfo.iterrows():
        ahref_id = row['ahref_id']
        if pd.isna(ahref_id) and next_ahref_pointer < len(parts_ahref_pointers):
            new_ahref_id = list(parts_ahref_pointers.values())[next_ahref_pointer]
            TOCid = list(parts_ahref_pointers.keys())[next_ahref_pointer]
            leginfo.at[index, 'ahref_id'] = new_ahref_id
            leginfo.at[index, 'TOCid'] = TOCid
            next_ahref_pointer += 1

    leginfo = leginfo.fillna('None')

    # Update part_id and part_type in leginfo DataFrame
    previous_part_tocid = None
    for index, row in leginfo.iterrows():
        TOCid = row['TOCid']
        if TOCid.startswith("PART"):
            previous_part_tocid = TOCid
            previous_part_section = row['section']
        else:
            leginfo.at[index, 'part_id'] = previous_part_tocid

    # Process sections and definitions
    data = []

    # Your list of section classes
    section_classes = ['section', 'section-e']

    # Create a CSS selector string to select paragraphs with any of the classes
    selector = ', '.join(f'p.{cls}' for cls in section_classes)

    # Assuming 'soup' is your BeautifulSoup object
    for section in soup.select(selector):
        section_data = process_section(section)
        data.append(section_data)

    content_df = pd.DataFrame(data)


    # Merge leginfo with section content
    leg_full = leginfo.merge(content_df, how="outer", on=['ahref_id'])

    # Convert DataFrame to dictionary for JSON use
    return leg_full.to_dict(orient='records')

# %%
#Function to get LAW from a TOCless page
def scrape_noTOC_law(url):
    """
    Extracts and organizes legal information from a webpage that lacks a traditional table of contents (TOC).

    This function is tailored to handle webpages where legal documents are presented without a clear TOC. It 
    scrapes the webpage content, particularly focusing on sections and definitions, and organizes it into 
    a structured format.

    Parameters:
    url (str): The URL of the webpage to be scraped.

    Returns:
    list[dict]: A list of dictionaries, where each dictionary contains information about a section or definition
                from the legal document. The structure of each dictionary includes keys like 'ahref_id', 'TOCid', 
                'section', and the content of each section.

    The function works through these steps:
    1. Initializes a DataFrame to hold legislation information.
    2. Finds and processes all paragraphs classified as 'section' or 'definition'.
    3. Creates a CSS selector to identify the relevant paragraphs.
    4. Processes each identified section and collects its data.
    5. Converts the collected data into a dictionary format suitable for JSON serialization.

    Example usage:
    ```
    from bs4 import BeautifulSoup
    import requests

    url = "https://www.ontario.ca/laws/statute/23s01"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    legal_data = scrape_noTOC_law(soup, url)
    ```

    Note:
    This function is specifically designed for webpages that do not have a TOC, and it relies on the presence 
    of specific HTML classes ('section', 'section-e', 'definition', 'definition-e') to identify relevant content.
    """
    
    #Create object page
    webpage = requests.get(url)
    soup = BeautifulSoup(webpage.content, "lxml")
        
    # Create dataframe to hold legislation info
    leginfo = pd.DataFrame(columns=['ahref_id', 'TOCid', 'section'])

    # Obtain sections and definitions
    definitions = soup.findAll('p', class_='definition') or soup.findAll('p', class_='definition-e')
    sections = soup.findAll('p', class_='section') or soup.findAll('p', class_='section-e')
    all_elements = soup.findAll('p')

    data = []

    # Your list of section classes
    section_classes = ['section', 'section-e']

    # Create a CSS selector string to select paragraphs with any of the classes
    selector = ', '.join(f'p.{cls}' for cls in section_classes)

    # Assuming 'soup' is your BeautifulSoup object
    for section in soup.select(selector):
        section_data = process_section(section)
        data.append(section_data)

    content_df = pd.DataFrame(data)

    # Convert DataFrame to dictionary for JSON use
    return content_df.to_dict(orient='records')

# %%
#Function to get REGS from a traditional TOC-bearing page
def scrape_TOC_reg(url):
    """
    Extracts and organizes regulation information from a webpage with a traditional table of contents (TOC).

    This function is designed to scrape and structure regulatory content from webpages where the content is 
    organized using a traditional table of contents (TOC). It extracts sections, parts, and their corresponding 
    content and organizes it into a structured format.

    Parameters:
    url (str): The URL of the webpage to be scraped.

    Returns:
    list[dict]: A list of dictionaries, where each dictionary contains information about a section, part, or 
                definition from the regulatory document. The structure of each dictionary includes keys like 
                'ahref_id', 'TOCid', 'part_id', 'part_type', 'section', 'content', and 'raw_html'.

    The function performs several steps:
    1. Extracts information from the table of contents (TOC), including links and their descriptions.
    2. Initializes and populates a DataFrame with TOC information.
    3. Associates each TOC entry with its corresponding content section.
    4. Processes and collects content of each section based on predefined classes.
    5. Merges the TOC information with the section content.
    6. Reorganizes and renames DataFrame columns for consistency.
    7. Converts the final structured data into a dictionary format suitable for JSON serialization.

    Example usage:
    ```
    from bs4 import BeautifulSoup
    import requests

    url = 'https://www.ontario.ca/laws/regulation/070407'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    regulatory_data = scrape_TOC_reg(soup, url)
    ```

    Note:
    This function assumes a specific format of the webpage with a table of contents (TOC) and specific HTML classes 
    ('section', 'section-e', 'definition', 'definition-e') for identifying relevant content.
    """
    #Create object page
    webpage = requests.get(url)
    soup = BeautifulSoup(webpage.content, "lxml")
    
    #Obtain info from TOC
    table1 = soup.find('table', class_ = 'MsoNormalTable') or soup.find('table', class_ = 'MsoNormalTable-e')
    tocspans = table1.findAll('span')

    # Create an empty dictionary to store PARTS ahref pointers
    parts_ahref_pointers = {}

    for span in tocspans:
        # Extract the span text and the ahref attribute
        span_text = span.text
        ahref = span.find('a', href=True)

        if ahref:
            parts_ahref_pointers[span_text] = ahref['href']

    #Create dataframe to hold leginfoislation
    leginfo = pd.DataFrame(columns = ['ahref_id',
                                'TOCid',
                                'section'])

    #Get Tables w Pandas
    dfs = pd.read_html(url)
    TOC = dfs[1]

    #Populate TOCid & section Title
    leginfo['TOCid'] = TOC[0]
    leginfo['section1'] = TOC[1]
    if 2 < len(TOC.columns):
        leginfo['section2'] = TOC[2]
    else:
        pass

    # Iterate through the 'leginfo' DataFrame and fetch the corresponding <a> elements
    for index, row in leginfo.iterrows():
        TOCid = row['TOCid']

        # Find the <a> (ahref) element that matches the 'TOCid' in the DataFrame
        ahref = soup.find('a', string=TOCid, href=True)

        if ahref:
            # Extract the 'href' attribute and assign it to 'ahref_id' column
            leginfo.at[index, 'ahref_id'] = ahref['href']
        else:
            # Handle the case where no <a> (ahref) element is found for the 'TOCid'
            #print(f"No ahref found for TOCid: {TOCid}")
            pass


    # Update the 'leginfo' DataFrame with parts and part pointers
    next_ahref_pointer = 0  # Initialize the counter for sequential ahref pointers

    for index, row in leginfo.iterrows():
        ahref_id = row['ahref_id']

        # Check if 'ahref_id' is NaN
        if pd.isna(ahref_id):
            if next_ahref_pointer < len(parts_ahref_pointers):
                # Get the next 'ahref' pointer and 'TOCid' from the dictionary
                new_ahref_id = list(parts_ahref_pointers.values())[next_ahref_pointer]
                TOCid = list(parts_ahref_pointers.keys())[next_ahref_pointer]

                # Assign the 'ahref' pointer and 'TOCid' to the respective columns
                leginfo.at[index, 'ahref_id'] = new_ahref_id
                leginfo.at[index, 'TOCid'] = TOCid

                next_ahref_pointer += 1

    leginfo = leginfo.fillna('None')

    # Initialize variables to store the previous part's TOCid and section
    previous_part_tocid = None
    previous_part_section = None

    # Iterate through the DataFrame and update part_id and part_type
    for index, row in leginfo.iterrows():
        TOCid = row['TOCid']
        section = row['section1']

        if TOCid.startswith("PART"):
            # For Parts, update the previous_part_tocid and previous_part_section
            previous_part_tocid = TOCid
            previous_part_section = section
        else:
            # For sections, set part_id to the previous part's TOCid
            leginfo.at[index, 'part_id'] = previous_part_tocid
            # Set part_type to the previous part's section
            leginfo.at[index, 'part_type'] = previous_part_section

    #Obtain secs and defs
    definitions = soup.findAll('p', class_ = 'definition-e') or soup.findAll('p', class_ = 'definition')
    sections = soup.findAll('p', class_ = 'section-e') or soup.findAll('p', class_ = 'section')
    all = soup.findAll('p')

    full_data = []

    # Assuming 'soup' is your BeautifulSoup object
    for section in soup.select('p.section') or soup.select('p.section-e'):
        section_data = process_section(section)
        full_data.append(section_data)

    content_df = pd.DataFrame(full_data)
    content_df['ahref_id'] = "#" + content_df['id']
    content_df = content_df.drop(columns=['id'], axis=1)
    content_df = content_df[['ahref_id', 'section', 'content', 'raw_html']]

    # Merge leginfo with section content
    leg_full = leginfo.merge(content_df, how="left", on=['ahref_id'])

    # Optionally, you can rename section_y back to section
    leg_full = leg_full.rename(columns={'section_y': 'section'})
    
    #Rename section 1 to section
    leg_full['section'] = leg_full['section1']
    leg_full = leg_full.drop(['section1'], axis = 1)

    #Drop section 2 if Matching section
    if 'section2' in leg_full.columns:
        if (leg_full['section2'] == leg_full['section']).any():
            leg_full = leg_full.drop(['section2'], axis=1)

    #Reorder
    leg_full = leg_full[['ahref_id', 'TOCid', 'part_id', 'part_type', 'section', 'content', 'raw_html']]

    # Convert DataFrame to dictionary for JSON use
    return leg_full.to_dict(orient='records')

# %%
#Function to get REGS from a TOCless page
def scrape_noTOC_reg(url):
    """
    Extracts regulatory information from a webpage without a traditional table of contents (TOC).

    Parameters:
    url (str): The URL of the webpage to be scraped.

    Returns:
    list[dict]: A list of dictionaries containing information about regulatory sections and definitions 
                from the webpage.

    The function extracts content from sections and definitions on the webpage and structures it into a 
    dictionary format suitable for JSON use.

    Example usage:
    ```
    url = 'https://www.ontario.ca/laws/regulation/230267'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    regulatory_data = scrape_noTOC_reg(soup, url)
    ```
    """
    # Create object page
    webpage = requests.get(url)
    soup = BeautifulSoup(webpage.content, "lxml")

    # Create dataframe to hold legislation info
    leginfo = pd.DataFrame(columns=['ahref_id', 'TOCid', 'Section'])

    # Obtain sections and definitions
    definitions = soup.findAll('p', class_='definition-e')
    sections = soup.findAll('p', class_='section-e')
    all_elements = soup.findAll('p')

    data = []

    current_headnote = None  # Variable to store the current headnote

    for section in soup.select('p.section-e'):
        a_tag = section.find('a')
        b_tag = section.find('b')

        if a_tag is not None:
            id_value = a_tag.get('name')
        elif b_tag is not None:
            id_value = b_tag.text.strip()
        else:
            id_value = None

        # Capture the headnote for the current section
        headnote_tag = section.find_previous('p', class_='headnote-e') or\
                        section.find_previous('p', class_='headnote') or \
                        section.find_previous('p', class_='heading1') or \
                        section.find_previous('p', class_='heading1-e')
        if headnote_tag:
            current_headnote = headnote_tag.text

        content = [section.text]
        raw_html = [str(section)]
        
        for sibling in section.find_next_siblings():
            # Break the loop if the next section or a headnote is encountered
            if sibling.name == 'p' and ('section-e' in sibling.get('class', []) or 'headnote-e' in sibling.get('class', [])) or \
                                        ('section' in sibling.get('class', []) or 'headnote' in sibling.get('class', [])):
                break

            sibling_text = sibling.text.replace('\xa0', ' ').strip()

            raw_html.append(str(sibling))

            if sibling.name == 'p' or sibling.name == 's':
                content.append(sibling_text)
            else:
                content.append(sibling_text)

        data.append({'id': id_value, 'section': current_headnote, 'content': ' '.join(content), 'raw_html': ' '.join(raw_html)})

    content_df = pd.DataFrame(data)

    # Convert DataFrame to dictionary for JSON use
    return content_df.to_dict(orient='records') 


# %%
#Function to get REGS from a left-head page
def scrape_regs_lefthead(url):
    """
    Extracts regulations from a webpage with a left-head table of contents (TOC).

    Parameters:
    url (str): The URL of the webpage to be scraped.

    Returns:
    list[dict]: A list of dictionaries containing structured regulatory information, including sections,
                parts, and content from the webpage.

    The function extracts content from sections, parts, and definitions on the webpage and structures it 
    into a dictionary format suitable for JSON use.

    Example usage:
    ```
    url = 'https://www.ontario.ca/laws/regulation/900664'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    regulatory_data = scrape_regs_lefthead(soup, url)
    ```
    """
    # Fetch and parse the webpage
    webpage = requests.get(url)
    soup = BeautifulSoup(webpage.content, "lxml")

    # Extracting TOC and parts pointers
    parts_ahref_pointers = {}
    table1 = soup.find('table', class_='MsoNormalTable')
    tocspans = table1.findAll('span')
    for span in tocspans:
        span_text = span.text
        ahref = span.find('a', href=True)
        if ahref:
            parts_ahref_pointers[span_text] = ahref['href']

    # Create dataframe to hold legislation information
    leginfo = pd.DataFrame(columns=['ahref_id', 'TOCid', 'Section'])

    # Extract tables with Pandas and populate the DataFrame
    dfs = pd.read_html(url)
    TOC = dfs[1]
    leginfo['TOCid'] = TOC[0]
    leginfo['Section1'] = TOC[1]
    leginfo['Section2'] = TOC[2]

    # Iterate through the 'leginfo' DataFrame and fetch the corresponding <a> elements
    for index, row in leginfo.iterrows():
        TOCid = row['Section1']

        # Find the <a> (ahref) element that matches the 'TOCid' in the DataFrame
        ahref = soup.find('a', string=TOCid, href=True)

        if ahref:
            # Extract the 'href' attribute and assign it to 'ahref_id' column
            leginfo.at[index, 'ahref_id'] = ahref['href']
        else:
            # Handle the case where no <a> (ahref) element is found for the 'TOCid'
            # print(f"No ahref found for TOCid: {TOCid}")
            pass


    # Update the 'leginfo' DataFrame with parts and part pointers
    next_ahref_pointer = 0  # Initialize the counter for sequential ahref pointers

    for index, row in leginfo.iterrows():
        ahref_id = row['ahref_id']

        # Check if 'ahref_id' is NaN
        if pd.isna(ahref_id):
            if next_ahref_pointer < len(parts_ahref_pointers):
                # Get the next 'ahref' pointer and 'TOCid' from the dictionary
                new_ahref_id = list(parts_ahref_pointers.values())[next_ahref_pointer]
                TOCid = list(parts_ahref_pointers.keys())[next_ahref_pointer]

                # Assign the 'ahref' pointer and 'TOCid' to the respective columns
                leginfo.at[index, 'ahref_id'] = new_ahref_id
                leginfo.at[index, 'TOCid'] = TOCid

                next_ahref_pointer += 1

    #Fill NaNs
    leginfo = leginfo.fillna('None')

    # Initialize variables to store the previous part's TOCid and Section
    previous_part_tocid = None
    previous_part_section = None

    # Iterate through the DataFrame and update part_id and part_type
    for index, row in leginfo.iterrows():
        TOCid = row['TOCid']
        section = row['Section']

        if TOCid.startswith("PART"):
            # For Parts, update the previous_part_tocid and previous_part_section
            previous_part_tocid = TOCid
            previous_part_section = section
        else:
            # For Sections, set part_id to the previous part's TOCid
            leginfo.at[index, 'part_id'] = previous_part_tocid
            # Set part_type to the previous part's section
            leginfo.at[index, 'part_type'] = previous_part_section

    #Obtain secs and defs
    definitions = soup.findAll('p', class_ = 'definition-e')
    sections = soup.findAll('p', class_ = 'section-e') or soup.findAll('p', class_ = 'section')
    all = soup.findAll('p')


    data = []

    current_headnote = None  # Variable to store the current headnote

    for section in soup.select('p.section-e') or soup.select('p.section'):
        a_tag = section.find('a')
        b_tag = section.find('b')

        if a_tag is not None:
            id_value = a_tag.get('name')
        elif b_tag is not None:
            id_value = b_tag.text.strip()
        else:
            id_value = None

        # Capture the headnote for the current section
        headnote_tag = section.find_previous('p', class_='headnote-e') or section.find_previous('p', class_='headnote') or section.find_previous('p', class_='heading1')
        if headnote_tag:
            current_headnote = headnote_tag.text

        content = [section.text]
        raw_html = [str(section)]
        
        for sibling in section.find_next_siblings():
            # Break the loop if the next section or a headnote is encountered
            if sibling.name == 'p' and ('section-e' in sibling.get('class', []) or 'headnote-e' in sibling.get('class', [])):
                break

            sibling_text = sibling.text.replace('\xa0', ' ').strip()

            raw_html.append(str(sibling))

            if sibling.name == 'p' or sibling.name == 's':
                content.append(sibling_text)
            else:
                content.append(sibling_text)

        data.append({'id': id_value, 'Section': current_headnote, 'content': ' '.join(content), 'raw_html': ' '.join(raw_html)})

    #Make df
    content_df = pd.DataFrame(data)


    #Rename a name column to match leginfo df,
    content_df['ahref_id'] = ("#" + content_df['id'])


    #Drop old a name and Section
    content_df = content_df.drop(['id'], axis=1)

    #Drop Section
    content_df = content_df.drop(['Section'], axis=1)

    #Reorder
    content_df = content_df[['ahref_id', 'content', 'raw_html']]


    #Merge leginfo with section content
    leg_full = leginfo.merge(content_df, how="outer", on=['ahref_id'])
   

    # Convert the final DataFrame to JSON
    lefthead_reg_dict = leg_full.to_dict(orient='records')

    return lefthead_reg_dict

# %%
#Function to get versions
def scrape_versions(driver, url):
    """
    Extracts version information from a law or reg.

    Args:
    driver: WebDriver object for web page control.
    soup (BeautifulSoup): Parsed HTML content of the webpage.
    url (str): URL of the webpage.

    Returns:
    list[dict]: List of version data (href, valid_from, valid_to) in dictionaries.

    This function loads more versions if available, extracts version data from a table,
    and returns it in a structured dictionary format for JSON use.

    Example:
    ```
    driver = webdriver.Chrome()
    url = 'https://www.ontario.ca/laws/regulation/210679'
    soup = BeautifulSoup(driver.page_source, 'lxml')
    version_data = scrape_versions(driver, url)
    ```
    """
    #Create object page
    webpage = requests.get(url)
    soup = BeautifulSoup(webpage.content, "lxml")
    
    try:
        # Check for the presence of the 'More Versions' link
        try:
            link = driver.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr.more-versions.hide a")))
            link.click()
        except:
            pass  # Suppressing print statements

        # Find the 'div' tag with the class "versions"
        versions = soup.find('div', id="versions")

        # Find the table
        versions_table = soup.find('table', class_='act-reg-list noStripes')

        # Get versions rows
        version_rows = versions_table.findAll('tr') if versions_table else []

        # Initialize lists to store the data
        hrefs = []
        valid_froms = []
        valid_tos = []

        # Iterate over each row in the table
        for row in version_rows:
            td_cells = row.find_all('td')
            if len(td_cells) >= 2:
                a_tag = td_cells[1].find('a')
                if a_tag:
                    span_tags = td_cells[1].find_all('span', class_='time')

                    # Extract the href attribute
                    href = a_tag['href']

                    # Extract valid_from and valid_to
                    valid_from = span_tags[0].get_text().strip() if span_tags else 'N/A'
                    valid_to = span_tags[1].get_text().strip() if len(span_tags) > 1 else 'current'

                    # Append the data to the lists
                    hrefs.append(href)
                    valid_froms.append(valid_from)
                    valid_tos.append(valid_to)

        # Create a DataFrame
        versions_data = pd.DataFrame({
            'a_href': hrefs,
            'valid_from': valid_froms,
            'valid_to': valid_tos
        })

        # Convert DataFrame to dictionary for JSON use
        return versions_data.to_dict(orient='records')

    except Exception as e:
        print(f"Error occurred: {e}")

# %%
#Copyright Blurb Function
def create_copyright_entry():
    """
    Creates a copyright entry dictionary.

    Returns:
    dict: Copyright entry with the year and copyright holder.

    This function generates a dictionary containing copyright information.

    Example:
    ```
    copyright_info = create_copyright_entry()
    ```
    """
    return {"Copyright": "© King's Printer for Ontario, 2023."}

# %%
#Function to combine law data into dict
def combine_law_data(driver, soup, url, content):
    """
    Retrieves various pieces of law data from a given URL.

    Args:
    url (str): The URL from which to scrape the law data.
    content (dict/json): A dictionary/list of objects containing the content of the act

    Returns:
    dict: A dictionary containing combined law data.
    
    Example Usage:
    '''
        #url = 'https://www.ontario.ca/laws/statute/97o25a'
        #content = scrape_TOC_law(soup, url)

        #combined_data_df = combine_law_data(soup, url, content )

        #print(combined_data_df)
    '''
    """

    # Get Act Info
    act_info_json = parse_act_info(soup, url)

    #Get Current Regs, if available
    try:
        # Get Current Regs
        current_regs_json = extract_current_regs_data(soup, url)
    except (NoSuchElementException, TimeoutException) as e:
        # Handle exceptions (log them, pass, or take other actions)
        print(f"Current Regs not found for: {e}")
        # Decide what

    #Get Revoked Regs, if available
    try:
        # Attempt to extract revoked regulations
        revoked_regs_json = extract_revoked_regs_data(soup, url)
    except (NoSuchElementException, TimeoutException) as e:
        # Handle exceptions (log them, pass, or take other actions)
        print(f"Revoked Regs not found for: {e}")

    # Get Versions
    versions_json = scrape_versions(driver, url)

    #Get (C)
    copyright = create_copyright_entry()

    # Combine all the data into a single dictionary
    combined_data = {
        "act_info": act_info_json,
        "copyright": copyright,
        "versions": versions_json
    }

    # Try to add current_regs if it exists
    try:
        combined_data["current_regs"] = current_regs_json
    except NameError:
        pass

    # Try to add revoked_regs if it exists
    try:
        combined_data["revoked_regs"] = revoked_regs_json
    except NameError:
        pass

    # Add content at the end
    combined_data["content"] = content

    return combined_data

# %%
#Function to Save Law Data to JSON
def save_law_data(combined_data, act_info_json, valid_from, valid_to, db_folder="db"):
    """
    Saves the combined law data to a JSON file.

    Args:
    combined_data (dict): The combined law data to be saved.
    act_info_json (dict): JSON data containing act information.
    valid_from (str): The start date of the act's validity.
    valid_to (str): The end date of the act's validity.
    db_folder (str, optional): The directory to save the file. Defaults to "db".

    
    # Example usage
    '''
        #combined_data = scrape_TOC_law('https://www.ontario.ca/laws/statute/21b02')
        #act_info_json = scrape_act_info('https://www.ontario.ca/laws/statute/21b02')
        #copyright = create_copyright_entry()
        #save_law_data(combined_data, act_info_json, "zzz", "yyy")
    '''
    """

    # Extract information from the act_info_json
    act_full_title = act_info_json.get('full_title', "")
    act_name_text = act_info_json.get('act_name_text', "")
    citation = act_info_json.get('citation', "")
    act_url = act_info_json.get('url', "")
    date_scraped = act_info_json.get('date_scraped', "")

    # Ensure that the necessary data is available
    if act_full_title and date_scraped:
        # Generate file name using sanitized strings
        sanitized_title = sanitize_filename(act_full_title)
        sanitized_valid_from = sanitize_filename(valid_from)
        sanitized_valid_to = sanitize_filename(valid_to)
        sanitized_date_scraped = sanitize_filename(date_scraped)

        file_name = f"{sanitized_title} + {sanitized_valid_from} - {sanitized_valid_to} + {sanitized_date_scraped}.json"

        # Define the file path for the file
        file_path = os.path.join(db_folder, file_name)

        # Create db folder if it doesn't exist
        os.makedirs(db_folder, exist_ok=True)

        # Write the combined data to a file
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(combined_data, file, indent=4, ensure_ascii=False)

        print(f"Combined JSON data for version saved in {file_path}")
    else:
        # Fallback filename if combined_data is empty
        file_name = "default_filename.json"
        file_path = os.path.join(db_folder, file_name)

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(combined_data, file, indent=4, ensure_ascii=False)

        print(f"Default JSON data saved in {file_path}")

    # Return the last file path for further use, or modify as needed
    return file_path


# %%
#Function to Save Versions Data
def save_version_data(version_row, combined_data, db_folder):
    """
    Saves version data to a JSON file.

    Args:
    version_row (dict): The version information containing 'a_href', 'valid_from', and 'valid_to'.
    combined_data (dict): The data to be saved.
    db_folder (str): The folder path where the data will be saved.

    This function saves the provided data to a JSON file with a filename based on the version information.

    The JSON file is saved in the specified 'db_folder' directory. If the directory doesn't exist, it will be created.

    Example:
    ```
    version_info = {
        'a_href': 'https://www.ontario.ca/laws/statute/97o25a',
        'valid_from': '2023-01-01',
        'valid_to': 'current'
    }
    data_to_save = {'key1': 'value1', 'key2': 'value2'}
    db_folder_path = '/path/to/database/folder'

    save_version_data(version_info, data_to_save, db_folder_path)
    ```
    """
    # Extract version identifier from the 'a_href' column
    version_identifier = version_row['a_href'].split('/')[-1]  # This gets the 'vXX' part
    valid_from = sanitize_filename(version_row['valid_from'])
    valid_to = sanitize_filename(version_row['valid_to'] if version_row['valid_to'] != 'current' else 'current')

    # Create the filename
    file_name = f"{version_identifier}_{valid_from}_to_{valid_to}.json"

    # Check if the db folder exists, and if not, create it
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)

    # Define the file path
    file_path = os.path.join(db_folder, file_name)

    # Write the combined data to a file
    with open(file_path, 'w') as file:
        json.dump(combined_data, file, indent=4)

    print(f"Data for version {version_identifier} saved in {file_path}")

# %%
#Law Tri-Split Scraping Function
def scrape_law_page(driver, soup, url, valid_from, valid_to):
    """
    Scrape law content from a web page and save it.

    Args:
    driver (Selenium webdriver): To load dynamic elements on page
    soup (BeautifulSoup): The BeautifulSoup object containing the parsed HTML.
    url (str): The URL of the law page.
    valid_from (str): The valid from date for the law.
    valid_to (str): The valid to date for the law.

    This function scrapes law content from a web page and saves it in the appropriate format based on the structure of the law page.

    - If the page has no table of contents (TOCless), it uses 'scrape_noTOC_law'.
    - If the page has a left-side TOC, it uses 'scrape_lefthead_law'.
    - If the page has a regular TOC, it uses 'scrape_TOC_law'.
    - If the page has an unexpected structure, it handles it accordingly.

    The scraped data is combined into a dictionary and saved as a JSON file with a filename based on the law's metadata.

    Example:
    ```
     # Make a GET request to the law page and create a BeautifulSoup object
    url = 'https://www.ontario.ca/laws/statute/90e09'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Define valid_from and valid_to dates
    valid_from_date = '2023-01-01'
    valid_to_date = 'current'

    # Scrape and save law data
    scrape_law_page(soup, url, valid_from_date, valid_to_date)
    ```
    """
#Find Toc, Get Filename Parameters
    toc = soup.find('table', class_='MsoNormalTable')

    #Scrape Act Info/MetaData for filename parameters
    act_info_json = parse_act_info(soup, url)

#If TOCless
    if not toc:
        print("Structure Type: No Law TOC (TOCless logic) for " + str(url))
        
        # Get TOC-less Content
        noTOC_content = scrape_noTOC_law(url)

        #Combine into dict
        combined_data = combine_law_data(driver, soup, url, noTOC_content)

        #Save File
        save_law_data(combined_data, act_info_json, valid_from, valid_to)
        


#If LeftHead
    elif toc.find('p', class_='TOCheadLeft'):
        print("Structure Type: Law Left-side TOC (left-side TOC logic)")

        #Get LeftHead Law Content
        lefthead_content = scrape_lefthead_law(url)

        #Combine into dict
        combined_data = combine_law_data(driver, soup, url, lefthead_content)

        #Save File
        save_law_data(combined_data, act_info_json, valid_from, valid_to)


#If Normal
    elif toc.find('p', class_='table'):
        print("Structure Type: Regular Law TOC (regular logic)")

        #Get LeftHead Law Content
        TOC_law_content = scrape_TOC_law(url)

        #Combine into dict
        combined_data = combine_law_data(driver, soup, url, TOC_law_content )

        #Save File
        save_law_data(combined_data, act_info_json, valid_from, valid_to)

#If Unexpected
    else:
        print("Structure Type: Unknown Law" + ":" + str(url))
        # Handle any unexpected structure

# %%
#Function to combine reg data into dict
def combine_reg_data(driver, soup, url, content):
    """
    Retrieves various pieces of law data from a given URL.

    Args:
    driver (Selenium webdriver): To load dynamic elements on page
    soup (BeautifulSoup object): BS object to pass to functions
    url (str): The URL from which to scrape the law data.
    content (dict/json): A dictionary/list of objects containing the content of the act

    Returns:
    dict: A dictionary containing combined law data.
    """
    #Get Reg Info
    reg_info_json = parse_reg_info(soup, url)

    #Get Versions
    versions_json = scrape_versions(driver, url)

    #Get (C)
    copyright = create_copyright_entry()

    #Combine data into dict
    combined_data = {"reg_info": reg_info_json,
                    "copyright": copyright,
                    "versions":versions_json,
                    "content": content
                    }

    return combined_data

# %%
# Function to Save Regulation Data to JSON
def save_reg_data(combined_data, reg_info_json, valid_from, valid_to, db_folder="db"):
    """
    Saves the combined regulation data to a JSON file.

    Args:
    combined_data (dict): The combined regulation data to be saved.
    reg_info_json (dict): Dictionary with regulation information.
    valid_from (str): The start date of the regulation's validity.
    valid_to (str): The end date of the regulation's validity.
    db_folder (str, optional): The directory to save the file. Defaults to "db".

    Example:
    # Example usage
    reg_info = parse_reg_info('https://www.ontario.ca/laws/regulation/100034')
    copyright = create_copyright_entry()

    # Accessing 'valid_from' and 'valid_to' dates
    save_reg_data(copyright, reg_info, 'test1', 'test2')
    """

    # Check if the db folder exists, and if not, create it
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)

    # Generate sanitized file name components
    sanitized_valid_from = sanitize_filename(valid_from)
    sanitized_valid_to = sanitize_filename(valid_to)

    if reg_info_json:
        # Initialize file name components with placeholders or actual values
        file_name_components = {
            'title': sanitize_filename(reg_info_json.get('full_title', '')),
            'act_under': sanitize_filename(reg_info_json.get('act_under', '')),
            'date_scraped': sanitize_filename(reg_info_json.get('date_scraped', ''))
        }

        # Generate file name by concatenating components with specific separators
        file_name = (file_name_components['title'] + " + " +
 #            file_name_components['act_under'] + " + " +
             sanitized_valid_from + " - " +
             sanitized_valid_to + " + " +
             file_name_components['date_scraped']) + ".json"

        file_path = os.path.join(db_folder, file_name)

        # Write the combined data to a file
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(combined_data, file, indent=4, ensure_ascii=False)

        print(f"Combined JSON data for version saved in {file_path}")

    else:
        # Fallback filename if reg_info_json is empty
        file_name = "default_filename.json"
        file_path = os.path.join(db_folder, file_name)

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(combined_data, file, indent=4, ensure_ascii=False)

        print(f"Default JSON data saved in {file_path}")

    return file_path

# %%
#Regulations Tri-Split Scraping Function
def scrape_reg_page(driver, soup, url, valid_from, valid_to):
    """
    Scrape regulation content from a web page and save it.

    Args:
    driver (Selenium webdriver): To load dynamic elements on page
    soup (BeautifulSoup): The BeautifulSoup object containing the parsed HTML.
    url (str): The URL of the regulation page.
    valid_from (str): The valid from date for the regulation.
    valid_to (str): The valid to date for the regulation.

    This function scrapes regulation content from a web page and saves it in the appropriate format based on the structure of the regulation page.

    - If the page has no table of contents (TOCless), it uses 'scrape_noTOC_reg'.
    - If the page has a left-side TOC, it uses 'scrape_regs_lefthead'.
    - If the page has a regular TOC, it uses 'scrape_TOC_reg'.
    - If the page has an unexpected structure, it handles it accordingly.

    The scraped data is combined into a dictionary and saved as a JSON file with a filename based on the regulation's metadata.

    Example:
    ```
     # Make a GET request to the regulation page and create a BeautifulSoup object
    url = 'https://www.ontario.ca/laws/regulation/940275'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Define valid_from and valid_to dates
    valid_from_date = '2023-01-01'
    valid_to_date = 'current'

    # Scrape and save regulation data
    scrape_reg_page(soup, url, valid_from_date, valid_to_date)
    ```
    """
#Get TOC and Filename Data
    #Get TOC
    toc = soup.find('table', class_='MsoNormalTable')

    #Get Reg Info
    reg_info_json = parse_reg_info(soup, url)

#If TOCLess Reg
    if not toc:
        print("Structure Type: No Reg TOC (TOCless logic)")

        #GetTocLess Content
        noTOC_reg_content = scrape_noTOC_reg(url)

        #Combine into dict
        combined_data = combine_reg_data(driver, soup, url, noTOC_reg_content)

        #Save File
        save_reg_data(combined_data, reg_info_json, valid_from, valid_to)

#If LeftHead Reg
    elif toc.find('p', class_='TOCheadLeft-e') or toc.find('p', class_='TOCpartLeft-e'):
        print("Structure Type: Left-side Reg TOC (left-side TOC logic)")

        #Get LeftHead Content
        lefthead_regs_content = scrape_regs_lefthead(url)

        #Combine into dict
        combined_data = combine_reg_data(driver, soup, url, lefthead_regs_content)

        #Save File
        save_reg_data(combined_data, reg_info_json, valid_from, valid_to)

#If Normal
    elif toc.find('p', class_='TOCid-e'):
        print("Structure Type: Regular Reg TOC (regular logic)")

        #Get TOC-based Content
        TOC_reg_content = scrape_TOC_reg(url)

        #Combine into dict
        combined_data = combine_reg_data(driver, soup, url, TOC_reg_content)

        #Save File
        save_reg_data(combined_data, reg_info_json, valid_from, valid_to)

# If No-TOC, but with MsoNormal Table
    elif toc and not toc.find('p', class_='TOCid-e'):
        print("Structure Type: TOCless w/ Table Reg TOC")
        # Implement logic for this specific case here

        #GetTocLess Content
        noTOC_reg_content = scrape_noTOC_reg(url)

        #Combine into dict
        combined_data = combine_reg_data(driver, soup, url, noTOC_reg_content)

        #Save File
        save_reg_data(combined_data, reg_info_json, valid_from, valid_to)

#If Unknown
    else:
        print("Structure Type: Unknown Reg" + ":" + str(url))
        # Handle any unexpected structure

# %%
#Function to Scrape Versions and return a dataframe
def scrape_versions_to_df(driver, soup, url):
    """
    Scrape versions of legislation from a web page and return them as a DataFrame.

    Args:
    driver: WebDriver: The Selenium WebDriver used for web scraping.
    soup (BeautifulSoup): The BeautifulSoup object containing the parsed HTML.
    url (str): The URL of the legislation page.

    Returns:
    pd.DataFrame: A DataFrame containing the scraped legislation versions with columns:
      - 'a_href': The URLs of legislation versions.
      - 'valid_from': The valid from date of each version.
      - 'valid_to': The valid to date of each version.

    This function scrapes versions of legislation content from a web page and returns them as a DataFrame.
    It processes the 'More Versions' link, extracts version details, and standardizes the URLs.
    The DataFrame is structured with columns for the URL of each version, its valid from date, and valid to date.

    Example:
    ```
    # Define a Selenium WebDriver and create a BeautifulSoup object
    driver = webdriver.Chrome()
    url = 'https://www.ontario.ca/laws/regulation/980134'
    response = driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'lxml')

    # Scrape legislation versions and store them in a DataFrame
    versions_df = scrape_versions_to_df(driver, soup, url)
    driver.quit()

    # Display the first few rows of the DataFrame
    print(versions_df.head())
    ```
    """
    try:
        # Check for the presence of the 'More Versions' link
        try:
            link = driver.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr.more-versions.hide a")))
            link.click()
        except:
            pass  # Suppressing print statements

        # Find the 'div' tag with the class "versions"
        versions_div = soup.find('div', id="versions")
        if not versions_div:
            print("Versions Tag not found.")
            return pd.DataFrame()

        # Find the first relevant table within the versions div
        versions_table = versions_div.find('table', class_='act-reg-list noStripes')
        if not versions_table:
            print("Versions table not found.")
            return pd.DataFrame()

        # Process each row in the first table
        hrefs, valid_froms, valid_tos = [], [], []
        for index, row in enumerate(versions_table.find_all('tr')):
            td_cells = row.find_all('td')
            if len(td_cells) >= 2:
                a_tag = td_cells[1].find('a')
                href = a_tag['href'] if a_tag else 'N/A'

                # Replace the first href with the current url
                if index == 0:
                    hrefs.append(url)
                else:
                    hrefs.append(href)

                # Check if current legislation
                current_label = td_cells[0].find('span', class_='label')
                if current_label and current_label.get_text().strip().lower() == 'current':
                    valid_from = td_cells[1].find('span', class_='time').get_text().strip()
                    valid_to = 'current'
                else:
                    # Extract valid dates
                    span_tags = td_cells[1].find_all('span', class_='time')
                    if len(span_tags) == 1:
                        valid_from = 'Repealed'
                        valid_to = span_tags[0].get_text().strip()
                    elif len(span_tags) > 1:
                        valid_from = span_tags[0].get_text().strip()
                        valid_to = span_tags[1].get_text().strip()
                    else:
                        valid_from = 'N/A'
                        valid_to = 'N/A'

                valid_froms.append(valid_from)
                valid_tos.append(valid_to)

        # Create DataFrame and return it
        versions_data = pd.DataFrame({
            'a_href': hrefs,
            'valid_from': valid_froms,
            'valid_to': valid_tos
        })

        #Set first a_href to current url
        versions_data['a_href'][0] = url

        # Standardize URLs by removing the base URL part from first entry
        base_url = "https://www.ontario.ca"
        versions_data['a_href'][0] = versions_data['a_href'][0].replace(base_url, '')

        # Return the DataFrame
        return versions_data
    
    except Exception as e:
        print(f"Error occurred: {e}")

# %%
# Function to save the current state
def save_state(index, file='last_state.txt'):
    with open(file, 'w') as f:
        f.write(str(index))

# %%
# Function to load the last saved state
def load_last_successful_state(file='last_state.txt'):
    try:
        with open(file, 'r') as f:
            return int(f.read().strip())
    except FileNotFoundError:
        return 0

# %%
#Function to Scrape Latest In Force Versions of Laws & Regs
def scrape_latest_versions(url, start_page, end_page, step):
    """
    Scrape and save the latest in-force versions of laws and regulations.

    Args:
    url (str): The base URL for scraping.
    start_page (int): The index of the page to start scraping from.
    end_page (int): The index of the page to stop scraping at.
    step (int): The step size for iterating through pages.

    This function scrapes the latest in-force versions of laws and regulations from the specified URL.
    It loads or scrapes a DataFrame containing law and regulation information, then iterates through the rows.
    For each row, it determines if it's an act or regulation, scrapes the versions, and saves the data.

    Example:
    ```
    # Define the URL and scraping parameters
    base_url = "https://www.ontario.ca"
    start_page = 0
    end_page = 10
    step = 1

    # Scrape and save the latest versions of laws and regulations
    scrape_latest_versions(base_url, start_page, end_page, step)
    ```
    """
    #Set Function Terms
    base_url = "https://www.ontario.ca"
    main_base_url = url
    laws_and_regs_file = 'laws_and_regs.csv'

    # Load or scrape the DataFrame
    try:
        laws_and_regs = pd.read_csv(laws_and_regs_file)
        print("Loaded saved laws and regulations.")
    except FileNotFoundError:
        laws_and_regs = scrape_ontario_laws(main_base_url, start_page=0, end_page=end_page, step=step)
        laws_and_regs.to_csv(laws_and_regs_file, index=False)
        print("Saved new laws and regulations.")

    # Iterate through each row, starting from start_page
    for index, row in laws_and_regs.iterrows():
        # Skip rows until the start_page index is reached
        if index < start_page:
            continue

        try:
            # Complete URL
            full_url = base_url + row['ahref']

            driver = start_driver_and_wait(full_url)
            soup = fetch_and_parse(driver)

            # Act Logic
            if row['class'] == 'act':
                print(f"Act at {full_url}")
                act_versions_df = scrape_versions_to_df(driver, soup, full_url)
                valid_from = act_versions_df['valid_from'][0]
                valid_to = act_versions_df['valid_to'][0]
                scrape_law_page(driver, soup, full_url, valid_from, valid_to)

            # Regulation Logic
            elif row['class'] == 'regulation':
                print(f"Regulation at {full_url}")
                reg_versions_df = scrape_versions_to_df(driver, soup, full_url)
                valid_from = reg_versions_df['valid_from'][0]
                valid_to = reg_versions_df['valid_to'][0]
                scrape_reg_page(driver, soup, full_url, valid_from, valid_to)
                
            # Save state after successful scraping
            save_state(index)

            # Quit the driver after processing each row
            driver.quit()

        except (AttributeError, TypeError) as e:
            print(f"Parsing error for {url}: {e}")
            continue  # Continue to the next row in case of an error

        # Break the loop if end_page is reached
        if index >= end_page:
            break

# %%
#Function for Restartable Scraping
def restartable_scrape(url, start_from=0, end_page=6000, step=50):
    last_successful_index = load_last_successful_state()
    while last_successful_index < end_page:
        try:
            scrape_latest_versions(url, last_successful_index, end_page, step)
            break  # Exit loop if scrape_latest_versions completes without errors
        except Exception as e:
            print(f"Error occurred: {e}")
            last_successful_index = load_last_successful_state()  # Reload the last successful index
            # Consider adding a delay or logic to prevent infinite loops


# %%
# Restart from the last successful state
url = get_main_base_url("all_law")
restartable_scrape(url)


# %%
'''# Draft All-Versions Scraping Script
def scrape_all_versions:(url, start_page, end_page, step):
    """Draft All-Versions Scraping Script for Ontario Laws and Regulations

    This script is designed to automate the process of scraping all versions of laws and regulations from the Ontario government's website. It focuses on systematically retrieving and storing information in a structured format, suitable for further analysis or archival purposes.

    Functions:
    - scrape_ontario_laws: Retrieves a list of laws and regulations from the main base URL.
    - scrape_versions_to_df: Extracts different versions of a particular law or regulation and stores them in a DataFrame.
    - scrape_law_page: Scrapes the content of a law from its URL and saves it in JSON format.
    - scrape_reg_page: Similar to scrape_law_page but tailored for regulations.

    Flow:
    1. Set the base URLs for the main page and the listing of all laws and regulations.
    2. Create a list of laws and regulations to be scraped by calling scrape_ontario_laws.
    3. Iterate through each law or regulation:
    - For each 'act', scrape all its versions and save the data.
    - For each 'regulation', perform a similar scraping and saving process.
    4. Handle exceptions and errors gracefully to ensure the script continues running even if some URLs fail to be scraped.

    Usage:
    This script is intended for data collection and archival purposes. It should be used in compliance with the website's terms of service, particularly regarding automated data collection.

    Note:
    This script is currently in a draft stage and may require further testing and refinement for full functionality.
    '''
'''
    # Scraping Time

    # Set Base URL
    base_url = "https://www.ontario.ca"

    #Set main_base_url for list of all laws and regs
    main_base_url = "https://www.ontario.ca/laws?search=&filteroption=current&filterstate%5B0%5D=current&filterstate%5B1%5D=rrs&filteryear=&source_type%5B0%5D=public&source_type%5B1%5D=regulation&pit_date=&filtertype=Statute%2CRegulation&sort=&sort_letter=&browse=on&from="

    # Create list of all laws and regs to be scraped
    laws_and_regs = scrape_ontario_laws(main_base_url, start_page=0, end_page=50, step=50)


    # Iterate through each row in the DataFrame, save all versions to db folder
    for index, row in laws_and_regs.iterrows():

        try:
            # Complete URL
            full_url = base_url + row['ahref']

            #Act Logic
            if row['class'] == 'act':
                # Perform actions for 'act'
                print(f"Act at {full_url}")
            
            #Scrape Versions for Each Act
                act_versions_df = scrape_versions_to_df(full_url)

                #Iterate over versions for each act, scrape, and save
                for index, row in act_versions_df.iterrows():

                    try:

                        # Set url to scrape from versions list
                        law_link = base_url + row['a_href']

                        #Print scraped page
                        print(f"Scraping {law_link}")

                        #Scrape law_link & Save JSON
                        scrape_law_page(law_link, row['valid_from'], row['valid_to'])

                    except (Exception, AttributeError, TypeError) as e:
                        print(f"Error scraping {url}: {e}")
                    continue  # Skip to the next URL in the list
                
                
            elif row['class'] == 'regulation':
                # Perform actions for 'regulation'
                print(f"Regulation at {full_url}")
                # Add more code here for regulations

                #Scrape Versions to dataframe
                reg_versions_df = scrape_versions_to_df(full_url)
            
                #Iterate over versions for each act, scrape, and save
                for index, row in reg_versions_df.iterrows():

                    try:

                        # Set url to scrape from versions list
                        reg_link = base_url + row['a_href']

                        #Print scraped page
                        print(f"Scraping {reg_link}")


                        valid_from = row['valid_from']
                        valid_to = row['valid_to']

                        #Scrape reg_link & Save JSON
                        scrape_reg_page(reg_link, valid_from, valid_to) 

                    except (Exception, AttributeError, TypeError) as e:
                        print(f"Error scraping {url}: {e}")
                    continue  # Skip to the next URL in the list

            # Optionally, handle cases that are neither 'regulation' nor 'act'
            else:
                print(f"Row {index} is neither regulation nor act")
            continue

        except (Exception, AttributeError, TypeError) as e:
            print(f"Error scraping {url}: {e}")
            continue  # Skip to the next URL in the list

            '''


