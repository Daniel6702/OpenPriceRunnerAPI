# api_client.py

import requests
from urllib.parse import urlencode
from typing import Dict, Any, Optional
from old.filter_manager import FilterManager


class APIClient:
    BASE_SEARCH_URL = "https://www.pricerunner.dk/dk/api/search-compare-gateway/public/search/category/v3/DK"

    def __init__(self, category_name: str, config_path: str = "config.json"):
        self.category_name = category_name
        self.filter_manager = FilterManager(config_path=config_path)
        self.category_id = self.filter_manager.get_category_id(category_name)
        if not self.category_id:
            raise ValueError(f"Category '{category_name}' not found.")
        self.subcategory_name: Optional[str] = None

    def build_url(self, selected_filters: Dict[str, Any] = {}, parameters: Dict[str, Any] = {}) -> str:
        """
        Construct the API URL with the selected filters and additional parameters.
        """
        # Initialize parameters with any provided in the parameters dict
        params = parameters.copy()

        # Check if subcategory is selected
        self.subcategory_name = selected_filters.get("Subcategory")

        # Validate and get filter key-value pairs
        for filter_name, option_value in selected_filters.items():
            filter_key = self.filter_manager.get_filter_key(self.category_name, filter_name, self.subcategory_name)
            if not filter_key:
                print(f"Filter key for '{filter_name}' not found. Skipping this filter.")
                continue

            if self.filter_manager.is_range_filter(self.category_name, filter_name, self.subcategory_name):
                # Handle range filters
                if isinstance(option_value, dict) and "min" in option_value and "max" in option_value:
                    try:
                        min_val = int(option_value["min"])
                        max_val = int(option_value["max"])
                        params[filter_key] = f"{min_val}_{max_val}"
                    except ValueError:
                        print(f"Invalid range values for filter '{filter_name}'. 'min' and 'max' must be integers.")
                else:
                    print(f"Invalid range value for filter '{filter_name}'. Expected a dictionary with 'min' and 'max'.")
            elif self.filter_manager.is_interval_filter(self.category_name, filter_name, self.subcategory_name):
                # Handle interval filters
                option_id = self.filter_manager.get_filter_option_id(self.category_name, filter_name, option_value, self.subcategory_name)
                if option_id:
                    params[filter_key] = option_id  # For interval filters, option_id is the interval string
                else:
                    print(f"Option '{option_value}' for filter '{filter_name}' not found. Skipping this filter.")
            else:
                # Handle options filters
                option_id = self.filter_manager.get_filter_option_id(
                    self.category_name, filter_name, option_value, self.subcategory_name
                )
                if option_id:
                    params[filter_key] = option_id
                else:
                    print(f"Option '{option_value}' for filter '{filter_name}' not found. Skipping this filter.")

        # Encode parameters
        query_string = urlencode(params)
        url = f"{self.BASE_SEARCH_URL}/{self.category_id}?{query_string}"
        return url

    def fetch_products(self, selected_filters: Dict[str, Any] = {}, parameters: Dict[str, Any] = {}) -> Optional[Dict[str, Any]]:
        """
        Fetch products from the API based on selected filters and additional parameters.
        """
        url = self.build_url(selected_filters=selected_filters, parameters=parameters)
        print(f"Fetching URL: {url}")  # Optional: For debugging
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.RequestException as e:
            print(f"Error fetching data from API: {e}")
            return None

    def display_products(self, data: Dict[str, Any]):
        """
        Display fetched products in a readable format.
        """
        products = data.get("products", [])
        if not products:
            print("No products found with the selected filters.")
            return
        for product in products:
            product_id = product.get("id", "N/A")
            name = product.get("name", "N/A")
            price = product.get("lowestPrice", {}).get("amount", "N/A")
            currency = product.get("lowestPrice", {}).get("currency", "")
            print(f"ID: {product_id}, Name: {name}, Price: {price} {currency}")
