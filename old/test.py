import json
import os
from colorama import init, Fore, Style
import requests
from dataclasses import dataclass

@dataclass
class Subcategory:
    id: str
    name: str
    parent_category: 'Category'

@dataclass
class Category:
    id: str
    name: str
    subcategories: list[Subcategory] = None


def list_categories(json_file="output.json"):
    """
    Reads category data from a JSON file, prints each category's ID and Name,
    and returns the list of category dictionaries.

    Args:
        json_file (str): The path to the JSON file containing category data.

    Returns:
        list: A list of dictionaries, each representing a category.
    """
    if not os.path.exists(json_file):
        print(f"Error: The file '{json_file}' does not exist.")
        return []

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: The file '{json_file}' contains invalid JSON.")
        return []
    except Exception as e:
        print(f"Error: An unexpected error occurred while reading '{json_file}'. Exception: {e}")
        return []

    if not isinstance(data, list):
        print(f"Error: The file '{json_file}' does not contain a list of categories.")
        return []

    if not data:
        print(f"Warning: The file '{json_file}' is empty.")
        return []

    print("\n===== Category List =====\n")
    for category in data:
        cat_id = category.get("id", "N/A")
        cat_name = category.get("name", "N/A")
        print(f"ID: {cat_id}\nName: {cat_name}\n{'-'*30}")

    print("\n===== End of Category List =====\n")
    return data

def get_category(identifier: str, data_type: str="navigation", json_file: str="output.json") -> dict:
    """
    Retrieves data for a specific category based on ID or Name and the specified type.

    Args:
        identifier (str): The ID or Name of the category.
        data_type (str): The type of data to retrieve. 
                         Options: "keyword", "popularproducts", "navigation", "breadcrumbs".
                         Default is "navigation".
        json_file (str): The path to the JSON file containing category data.

    Returns:
        dict or None: The retrieved data as a dictionary if successful, else None.
    """
    allowed_types = {
        "keyword": "keyword/tree/DK/{id}",
        "popularproducts": "popularproducts/v2/DK/{id}",
        "navigation": "navigation/menu/DK/hierarchy/{id}",
        "breadcrumbs": "navigation/breadcrumbs/DK/{id}"
    }

    if data_type not in allowed_types:
        print(f"{Fore.RED}Error: Invalid data_type '{data_type}'. Allowed types are: {', '.join(allowed_types.keys())}.{Style.RESET_ALL}")
        return None

    # Load categories from JSON file
    if not os.path.exists(json_file):
        print(f"{Fore.RED}Error: The file '{json_file}' does not exist.{Style.RESET_ALL}")
        return None

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            categories = json.load(f)
    except json.JSONDecodeError:
        print(f"{Fore.RED}Error: The file '{json_file}' contains invalid JSON.{Style.RESET_ALL}")
        return None
    except Exception as e:
        print(f"{Fore.RED}Error: An unexpected error occurred while reading '{json_file}'. Exception: {e}{Style.RESET_ALL}")
        return None

    # Determine if identifier is ID or Name
    if identifier.startswith("t"):
        category_id = identifier
    else:
        # Search for the category by name (case-insensitive)
        matching_categories = [cat for cat in categories if cat.get("name", "").lower() == identifier.lower()]
        if not matching_categories:
            print(f"{Fore.RED}Error: No category found with the name '{identifier}'.{Style.RESET_ALL}")
            return None
        elif len(matching_categories) > 1:
            print(f"{Fore.YELLOW}Warning: Multiple categories found with the name '{identifier}'. Using the first match.{Style.RESET_ALL}")
        category_id = matching_categories[0].get("id")
        if not category_id:
            print(f"{Fore.RED}Error: The category '{identifier}' does not have a valid ID.{Style.RESET_ALL}")
            return None

    # Construct the URL based on data_type
    base_url = "https://www.pricerunner.dk/dk/api/search-compare-gateway/public/"
    endpoint = allowed_types[data_type].format(id=category_id)
    url = base_url + endpoint

    headers = {
        'User-Agent': 'CategoryManager/1.0 (contact@yourdomain.com)'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"{Fore.GREEN}Success: Retrieved data for category ID '{category_id}' with type '{data_type}'.{Style.RESET_ALL}")
                return data
            except json.JSONDecodeError:
                print(f"{Fore.RED}Error: Received invalid JSON from URL '{url}'.{Style.RESET_ALL}")
                return None
        elif response.status_code == 429:
            print(f"{Fore.YELLOW}Warning: Received 429 Too Many Requests.")
            return None
        elif response.status_code == 404:
            print(f"{Fore.RED}Error: URL '{url}' not found (404). Check if the category ID '{category_id}' and type '{data_type}' are correct.{Style.RESET_ALL}")
            return None
        else:
            print(f"{Fore.RED}Error: Received status code {response.status_code} from URL '{url}'.{Style.RESET_ALL}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error: Failed to retrieve data from URL '{url}'. Exception: {e}.")
        return None



def main():
    """
    Main function to execute list_categories and handle its output.
    """
    json_filename = "output.json"
    #categories = list_categories(json_filename)
    
    category_data = get_category("t9")
    if category_data:
        print(json.dumps(category_data, indent=4))

if __name__ == "__main__":
    main()
