# %%
#Perform imports 
import os
import json

# %%
#Function to find and delete duplicated
def delete_duplicate_json_files(json_folder):
    """
    Delete duplicate JSON files in a specified folder based on unique combinations of `full_title` and `url` values found within the files.

    The function identifies duplicates by checking if the combination of `full_title` and `url` from either 'act_info' or 'reg_info' keys in each JSON file has been seen before. If a duplicate is found, it is deleted from the folder.

    Parameters:
    json_folder (str): The path to the directory containing the JSON files.

    Returns:
    None: The function returns nothing but deletes duplicate files from the specified directory and prints out the status of various operations.

    Raises:
    PermissionError: If the function fails to delete a file due to permission issues.

    Example:
    >>> json_folder = r'C:\\example_json_folder'
    >>> delete_duplicate_json_files(json_folder)
    """
    seen_combinations = set()  # Set to store unique combinations of full_title and url

    for file in os.listdir(json_folder):
        if file.endswith(".json"):
            file_path = os.path.join(json_folder, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    json_data = json.load(f)
                except json.JSONDecodeError:
                    continue  # Skip files that are not valid JSON

                # Extract full_title and url
                if 'act_info' in json_data:
                    full_title = json_data['act_info'].get('full_title', '')
                    url = json_data['act_info'].get('url', '')
                    unique_key = (full_title, url)

                    # Check if this combination has been seen before
                    if unique_key in seen_combinations:
                        # Duplicate found, delete the file
                        os.remove(file_path)
                        print(f"Deleted duplicate file: {file}")
                    else:
                        # New combination, add to the set
                        seen_combinations.add(unique_key)


