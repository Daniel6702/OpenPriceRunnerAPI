import requests
import json
import time
import os

def fetch_data(base_url, start, end, delay=0.1, output_file="output.json"):
    """
    Fetch JSON data from URLs with parameters ranging from t{start} to t{end}.
    Handles HTTP 429 responses by waiting and retrying.

    Args:
        base_url (str): The base URL with a placeholder for the parameter.
        start (int): The starting integer for the parameter.
        end (int): The ending integer for the parameter.
        delay (float): Delay in seconds between requests to prevent server overload.
        output_file (str): The filename for the output JSON.

    Returns:
        list: A list of dictionaries containing the extracted data.
    """
    collected_data = []
    # If output file exists, load existing data to resume
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                collected_data = json.load(f)
            print(f"Info: Loaded existing data from {output_file}. Resuming from where it left off.")
        except json.JSONDecodeError:
            print(f"Warning: {output_file} exists but is not valid JSON. Starting fresh.")
        except Exception as e:
            print(f"Error: Could not read {output_file}. Exception: {e}")

    # Determine the starting point based on existing data
    existing_ids = {item["id"] for item in collected_data if "id" in item}
    current = start

    for i in range(start, end + 1):
        param = f"t{i}"
        if param in existing_ids:
            print(f"Info: Data for {param} already exists. Skipping.")
            continue  # Skip already fetched data

        url = base_url.format(param=param)
        while True:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract required fields
                    extracted = {
                        "id": data.get("id"),
                        "name": data.get("name"),
                        "path": data.get("path")
                    }

                    # Check if all fields are present
                    if all(extracted.values()):
                        collected_data.append(extracted)
                        print(f"Success: Retrieved data for {param}")
                    else:
                        print(f"Warning: Missing fields in data for {param}")

                    # Save progress after each successful retrieval
                    save_to_json(collected_data, output_file)
                    break  # Exit the retry loop and proceed to next URL

                elif response.status_code == 429:
                    print(f"Warning: Received 429 for {param}. Saving progress and waiting for 60 seconds before retrying.")
                    save_to_json(collected_data, output_file)
                    time.sleep(60)  # Wait for 60 seconds before retrying
                else:
                    print(f"Info: URL {url} returned status code {response.status_code}. Skipping.")
                    break  # Skip to next URL on other HTTP errors

            except requests.exceptions.RequestException as e:
                print(f"Error: Failed to retrieve data for {param}. Exception: {e}. Waiting for 60 seconds before retrying.")
                time.sleep(60)  # Wait before retrying on network errors

        # Optional: Delay to prevent overwhelming the server
        time.sleep(delay)

    return collected_data

def save_to_json(data, filename):
    """
    Save the collected data to a JSON file.

    Args:
        data (list): The list of dictionaries to save.
        filename (str): The filename for the output JSON.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Success: Data saved to {filename}")
    except IOError as e:
        print(f"Error: Failed to write data to {filename}. Exception: {e}")

def main():
    # Base URL with a placeholder for the parameter
    base_url = "https://www.pricerunner.dk/dk/api/search-compare-gateway/public/navigation/menu/DK/hierarchy/{param}"

    # Define the range
    start = 0
    end = 2000

    # Output filename
    output_filename = "output.json"

    # Fetch the data
    print("Starting data retrieval...")
    data = fetch_data(base_url, start, end, output_file=output_filename)

    print("Data retrieval completed.")

if __name__ == "__main__":
    main()
