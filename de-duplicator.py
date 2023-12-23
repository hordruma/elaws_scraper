#Perform imports
import os
import json

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

    print(f"Starting to process files in {json_folder}")
    for file in os.listdir(json_folder):
        if file.endswith(".json"):
#            file_path = os.path.join(json_folder, file)
            print(f"Processing file: {file_path}")

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
#                    print(f"Successfully read JSON data from {file}")

            except json.JSONDecodeError as e:
                print(f"JSON decode error in file {file}: {e}")
                continue  # Skip files that are not valid JSON
            except Exception as e:
                print(f"Unexpected error while reading file {file}: {e}")
                traceback.print_exc()
                continue

            # Extract full_title and url
            for key in ['act_info', 'reg_info']:
                if key in json_data:
                    full_title = json_data[key].get('full_title', '')
                    url = json_data[key].get('url', '')
                    unique_key = (full_title, url)

                    # Check if this combination has been seen before
                    if unique_key in seen_combinations:
                        try:
                            os.remove(file_path)
                            print(f"Deleted duplicate file: {file}")
                        except PermissionError as e:
                            print(f"PermissionError while deleting file {file}: {e}")
                            traceback.print_exc()
                        except Exception as e:
                            print(f"Unexpected error while deleting file {file}: {e}")
                            traceback.print_exc()
                    else:
                        seen_combinations.add(unique_key)
#                        print(f"Added new combination to seen: {unique_key}")

    print("Finished processing all files.")

def delete_oldest_duplicate_json_files(json_folder):
    import os
    import json
    from datetime import datetime

    seen_combinations = {}  # Dictionary to store unique combinations with the most recent date and file path

    print(f"Starting to process files in {json_folder}")
    for file in os.listdir(json_folder):
        if file.endswith(".json"):
            file_path = os.path.join(json_folder, file)

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)

            except json.JSONDecodeError as e:
                print(f"JSON decode error in file {file}: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error while reading file {file}: {e}")
                continue

            # Extract full_title, url, and date_scraped
            for key in ['act_info', 'reg_info']:
                if key in json_data:
                    full_title = json_data[key].get('full_title', '')
                    url = json_data[key].get('url', '')
                    date_scraped_str = json_data[key].get('date_scraped', '')
                    try:
                        date_scraped = datetime.strptime(date_scraped_str, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        print(f"Invalid date format in file {file}: {date_scraped_str}")
                        continue

                    unique_key = (full_title, url)

                    # Check if this combination has been seen before and compare dates
                    if unique_key in seen_combinations:
                        existing_file, existing_date = seen_combinations[unique_key]
                        if date_scraped > existing_date:
                            # The current file is more recent, delete the existing one
                            try:
                                os.remove(existing_file)
                                print(f"Deleted older duplicate file: {existing_file}")
                                seen_combinations[unique_key] = (file_path, date_scraped)
                            except Exception as e:
                                print(f"Error deleting file {existing_file}: {e}")
                    else:
                        seen_combinations[unique_key] = (file_path, date_scraped)

    print("Finished processing all files.")