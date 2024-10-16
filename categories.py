
from dataclasses import dataclass, asdict
import json
import os
from colorama import init, Fore, Style
import requests
from typing import Optional, Dict, Any, List
from models import *

def load_categories(json_file):
    """Load categories from a JSON file with error handling."""
    if not os.path.exists(json_file):
        print(f"{Fore.RED}Error: The file '{json_file}' does not exist.{Style.RESET_ALL}")
        return None

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"{Fore.RED}Error: The file '{json_file}' contains invalid JSON.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: An unexpected error occurred while reading '{json_file}'. Exception: {e}{Style.RESET_ALL}")
    return None

def find_category(categories, key, value):
    """Find categories matching a key-value pair."""
    matches = [cat for cat in categories if str(cat.get(key, "")).lower() == str(value).lower()]
    
    if not matches:
        print(f"{Fore.RED}Error: No category found with {key} '{value}'.{Style.RESET_ALL}")
        return None
    if len(matches) > 1:
        print(f"{Fore.YELLOW}Warning: Multiple categories found with {key} '{value}'. Using the first match.{Style.RESET_ALL}")
    
    return matches[0]

def get_id_from_name(name, json_file="output.json"):
    """Get category ID based on the category name."""
    categories = load_categories(json_file)
    if not categories:
        return None

    category = find_category(categories, "name", name)
    if category:
        category_id = category.get("id")
        if not category_id:
            print(f"{Fore.RED}Error: The category '{name}' does not have a valid ID.{Style.RESET_ALL}")
            return None
        return category_id
    return None

def get_name_from_id(category_id, json_file="output.json"):
    """Get category name based on the category ID."""
    categories = load_categories(json_file)
    if not categories:
        return None

    category = find_category(categories, "id", category_id)
    if category:
        category_name = category.get("name")
        if not category_name:
            print(f"{Fore.RED}Error: The category with ID '{category_id}' does not have a valid name.{Style.RESET_ALL}")
            return None
        return category_name
    return None

def fetch_data(url, headers, timeout=10):
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"{Fore.RED}Error: Failed to retrieve or parse data from URL '{url}'. Exception: {e}.{Style.RESET_ALL}")
        return None

def get_category_data(category_id: str = None, name: str = None, empty_category: Category = None, json_file: str="output.json") -> Optional[Category]:
    if category_id:
        name = get_name_from_id(category_id, json_file)
    elif name:
        category_id = get_id_from_name(name, json_file)
    elif empty_category:
        category_id = empty_category.id
        name = empty_category.name
    else:
        print(f"{Fore.RED}Error: No category identifier provided.{Style.RESET_ALL}")
        return None
    
    endpoints = [
        "keyword/tree/DK/{id}",
        "popularproducts/v2/DK/{id}",
        "navigation/menu/DK/hierarchy/{id}",
        "navigation/breadcrumbs/DK/{id}"
    ]
    
    base_url = "https://www.pricerunner.dk/dk/api/search-compare-gateway/public/"
    headers = {'User-Agent': 'CategoryManager/1.0 (contact@yourdomain.com)'}

    data = [
        json_data
        for endpoint in endpoints
        if (json_data := fetch_data(f"{base_url}{endpoint.format(id=category_id)}", headers)) is not None and
        print(f"{Fore.GREEN}Success: Retrieved data for category ID '{category_id}'.{Style.RESET_ALL}") is None
    ]

    path = data[2].get("path")
 
    return Category(
        id=category_id,
        name=name,
        path=path,
        image=Image().from_dict(data[2].get("image", {})),
        subcategories=[Subcategory().from_dict(subcat, Category(id=category_id, name=name, path=path)) for subcat in data[2].get("categories", [])],
        keywords=[Keyword().from_dict(keyword) for keyword in data[0].get("keywords")],
        popular_products=[Product().from_dict(prod) for prod in data[1].get("productsCards", [])],
        parent_category=Category().from_dict(data[3].get("paths", {})[0])
    )