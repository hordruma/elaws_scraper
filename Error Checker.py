# %%
#Perform Imports
import os
import json
import pandas as pd

# %%
#Set db_folder and laws_and_regs constants
db_folder = r'db'
laws_and_regs_f = 'laws_and_regs.csv'
laws_and_regs =  pd.read_csv(laws_and_regs_f)

# %%
#Function to check for failed acts (empty content; empty revoked regs)
def check_jsons_act_content(json_folder):
    # Define the column names
    columns = ['citation', 'url']
    data = []

    for file in os.listdir(json_folder):
        if file.endswith(".json"):
            try:
                with open(os.path.join(json_folder, file), 'r', encoding='utf-8') as f:
                    json_data = json.load(f)

                    # Using get method with default values
                    revoked_regs = json_data.get('revoked_regs', None)
                    versions = json_data.get('versions', [])
                    content = json_data.get('content', None)

                    # Check if 'act_info' is present
                    if 'act_info' in json_data:
                        # Conditions for including the data
                        include_data = (content is None) or (revoked_regs is None and len(versions) < 3)

                        if include_data:
                            data.append({
                                'citation': json_data['act_info']['full_title'],
                                'url': json_data['act_info']['url']
                })
            except Exception as e:
                print(f"Error processing {file}: {e}")

        #print(f"Processing {file}")

    return pd.DataFrame(data, columns=columns)

# %%
#Function to check for failed regs, empty content
def check_jsons_reg_content(json_folder):
    data = []

    for file in os.listdir(json_folder):
        if file.endswith(".json"):
            with open(os.path.join(json_folder, file), 'r', encoding='utf-8') as f:
                json_data = json.load(f)

                # Check if 'reg_info' is present and 'content' is empty
                if 'reg_info' in json_data and not json_data.get('content'):
                    data.append({
                        'citation': json_data['reg_info']['full_title'],
                        'url': json_data['reg_info']['url']
                    })

    return pd.DataFrame(data)

# Example usage
df_regs = check_jsons_reg_content(r'C:\Users\horat\Codingz\Elaws Scraping Scripts\Python Pit\dbtest')
df_regs

# %%
# Function to make df of all JSON files to check for missed items
def get_missed_items(json_folder, laws_and_regs):
    """
    Reads JSON files from a specified folder, extracts specific information from each file, 
    and then merges this data with a predefined DataFrame 'laws_and_regs' to identify 
    items present in 'laws_and_regs' but not in the JSON files.

    Each JSON file is expected to contain either 'act_info' or 'reg_info' from which 
    a citation and a URL are extracted. The function normalizes URLs in 'laws_and_regs' 
    by appending a base URL to the 'ahref' field and then performs an outer merge based 
    on these URLs to find any missed items.

    Parameters:
    json_folder (str): The file path to the folder containing the JSON files.
    laws_and_regs: The laws_and_regs file containing list to be scraped

    Returns:
    pandas.DataFrame: A DataFrame of missed items, which are present in 'laws_and_regs' 
    but not in the JSON files. The returned DataFrame excludes the columns 'type', 
    'citation_x', 'url', and 'full_url'.

    Example Usage:
    missed_items = get_missed_items(r'C:\\Path\\To\\Json\\Folder', laws_and_regs_df)
    print(all_jsons)
    """
    data = []

    for file in os.listdir(json_folder):
        if file.endswith(".json"):
            with open(os.path.join(json_folder, file), 'r', encoding='utf-8') as f:
                json_data = json.load(f)

                # Check if 'act_info' or 'reg_info' is present and extract relevant data
                if 'act_info' in json_data:
                    citation = json_data['act_info'].get('full_title', 'No Title')
                    url = json_data['act_info'].get('url', 'No URL')
                    data.append({'type': 'Act', 'citation': citation, 'url': url})
                elif 'reg_info' in json_data:
                    citation = json_data['reg_info'].get('full_title', 'No Title')
                    url = json_data['reg_info'].get('url', 'No URL')
                    data.append({'type': 'Regulation', 'citation': citation, 'url': url})

    #DF Data
    all_jsons = pd.DataFrame(data)

    # Normalize the 'ahref' in laws_and_regs to full URLs by prepending the base URL
    base_url = 'https://www.ontario.ca'
    laws_and_regs['url'] = base_url + laws_and_regs['ahref'].astype(str)

    # Merge on 'ahref' from df_regs and 'url' from laws_and_regs
    all_df = all_jsons.merge(laws_and_regs, how='outer', on="url", indicator=True)
    missed_items = all_df[all_df['_merge'] == 'right_only'].copy()

    #Rename Citation column
    missed_items.loc[:, 'citation'] = missed_items['citation_y']

    #Drop Excess columns
    missed_items = missed_items.drop(['type', 'citation_x', 'url', '_merge', 'citation_y'], axis=1)

    #Reorder columns
    missed_items = missed_items[['ahref', 
                                'citation', 
                                'class', 
                                'parent_legislation', 
                                'currency', 
                                'currency_date',
                                'date_scraped']]

    return missed_items


# %%
#Function to Check for Errors and Save rescrape_list.csv
def check_for_fails(db_folder, laws_and_regs):
    """
    Scans the database folder and compares it with the laws and regulations file to identify any missing or failed downloads.
    This function is designed to create a list of items that need to be re-scraped due to errors or omissions.

    Args:
    db_folder (str): The path to the database folder where acts and regulations are stored.
    laws_and_regs (str): The filename of the laws and regulations CSV file. Default is 'laws_and_regs.csv'.

    The function performs the following steps:
    - Reads the laws and regulations CSV file into a DataFrame.
    - Checks for errors in acts and regulations content using helper functions.
    - Identifies any items that were missed during the initial scraping.
    - Normalizes URLs in the laws_and_regs DataFrame for comparison.
    - Merges data to create a final list of items to re-scrape.
    - Saves this list as 'rescrape_list.csv' in a 'failed' subdirectory within the specified db_folder.

    Example:
    ```
    db_folder = 'path/to/db_folder'
    laws_and_regs = 'laws_and_regs.csv'
    check_for_fails(db_folder, laws_and_regs)
    ```
    """
    #Make laws_and_regs DF
    laws_and_regs = pd.read_csv('laws_and_regs.csv')

    #Compile 3 basic lists, error acts, error regs, and missed items
    df_acts = check_jsons_act_content(db_folder)
    df_regs = check_jsons_reg_content(db_folder)
    missed_items = get_missed_items(db_folder, laws_and_regs)

    # Normalize the 'ahref' in laws_and_regs to full URLs by prepending the base URL
    base_url = 'https://www.ontario.ca'
    laws_and_regs['url'] = base_url + laws_and_regs['ahref']

    # Perfom merges to get final errored rescrape_list
    acts_rescrape_list = df_acts.merge(laws_and_regs, left_on='url', right_on='url', how='left')
    regs_rescrape_list = df_regs.merge(laws_and_regs, left_on='url', right_on='url', how='left')
    raw_rescrape_list = acts_rescrape_list.merge(regs_rescrape_list, how="outer")
        
    #Rename Citation column
    raw_rescrape_list.loc[:, 'citation'] = raw_rescrape_list['citation_y']

    #Drop & Merge with missed items for final rescraping list
    raw_rescrape_list = raw_rescrape_list.drop(['citation_x', 'url', 'citation_y'], axis=1)
    full_rescrape_list = raw_rescrape_list.merge(missed_items, how="outer")

    #Reorder columns
    full_rescrape_list = full_rescrape_list[['ahref', 
                            'citation', 
                            'class', 
                            'parent_legislation', 
                            'currency', 
                            'currency_date',
                            'date_scraped']]

    # Define save path
    save_path = os.path.join('failed', 'rescrape_list.csv')

    # Check if the directory exists, and create it if it does not
    save_dir = os.path.dirname(save_path)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Save CSV
    full_rescrape_list.to_csv(save_path, index=False)

    print(f'File saved to {save_path}')

check_for_fails(db_folder, laws_and_regs)


