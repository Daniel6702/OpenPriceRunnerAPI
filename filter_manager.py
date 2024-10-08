# filter_manager.py

import requests
from typing import Dict, Optional, List
import json
import os

FILTER_OPTIONS_BASE_URL = "https://www.pricerunner.dk/dk/api/search-compare-gateway/public/search/category/facets/DK/{category_id}/{filter_id}?"


class FilterOption:
    def __init__(self, key: str, option_id: str, value: str):
        self.key = key
        self.option_id = option_id
        self.value = value

    def __repr__(self):
        return f"FilterOption(key={self.key}, option_id={self.option_id}, value={self.value})"


class Filter:
    def __init__(self, category_id: str, filter_id: str, name: str,
                 options: List[Dict[str, str]] = None,
                 is_subcategory: bool = False,
                 subcategory_filter: Optional[Dict[str, str]] = None):
        self.category_id = category_id
        self.filter_id = filter_id  # Stored without 'af_' prefix
        self.name = name
        self.type = "OPTIONS"  # "OPTIONS", "RANGE", or "INTERVAL"
        self.options: List[FilterOption] = []
        self.minimum = None  # For range filters
        self.maximum = None  # For range filters
        self.subcategory_filter = subcategory_filter  # Dict with 'filter_id' and 'option_id'

        if is_subcategory and options is not None:
            # Initialize options from the provided list without fetching
            self.options = [
                FilterOption(
                    key=opt['id'],
                    option_id=opt['id'],
                    value=opt['name']
                )
                for opt in options
            ]
        else:
            # Construct the URL using the filter ID as is
            self.base_url = FILTER_OPTIONS_BASE_URL.format(category_id=self.category_id, filter_id=self.filter_id)
            self.fetch_options()

    def fetch_options(self):
        try:
            params = {}
            if self.subcategory_filter:
                params[f"af_{self.subcategory_filter['filter_id']}"] = self.subcategory_filter['option_id']
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            facet = data.get("facet", {})
            self.type = facet.get("type", "OPTIONS")
            if self.type == "OPTIONS":
                counts = facet.get("counts", [])
                self.options = [
                    FilterOption(
                        key=str(option.get("key")),
                        option_id=str(option.get("optionId")),
                        value=option.get("optionValue")
                    )
                    for option in counts
                ]
            elif self.type == "RANGE":
                self.minimum = facet.get("minimum")
                self.maximum = facet.get("maximum")
            elif self.type == "INTERVAL":
                interval_counts = facet.get("intervalCounts", [])
                self.options = [
                    FilterOption(
                        key=option.get("interval"),  # The interval string, e.g., "4_"
                        option_id=option.get("interval"),  # Use the interval as the option_id
                        value=option.get("optionValue")  # e.g., "4"
                    )
                    for option in interval_counts
                ]
            else:
                print(f"Unknown filter type '{self.type}' for filter '{self.name}'.")
        except requests.RequestException as e:
            print(f"Error fetching filter options from {self.base_url}: {e}")

    def get_option_id(self, option_value: str) -> Optional[str]:
        for option in self.options:
            if option.value.lower() == option_value.lower():
                return option.option_id
        return None

    def is_interval_filter(self) -> bool:
        return self.type == "INTERVAL"

    def is_range_filter(self) -> bool:
        return self.type == "RANGE"

    def is_options_filter(self) -> bool:
        return self.type == "OPTIONS"


class FilterManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.categories: Dict[str, Dict] = {}
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file {self.config_path} not found.")
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.categories = json.load(f)

    def get_category_id(self, category_name: str) -> Optional[str]:
        category = self.categories.get(category_name)
        return category.get("id") if category else None

    def get_subcategory_info(self, category_name: str, subcategory_name: str) -> Optional[Dict]:
        category = self.categories.get(category_name)
        if not category:
            raise ValueError(f"Category '{category_name}' not found in configuration.")
        subcategories = category.get("subcategories", [])
        for subcat in subcategories:
            if subcat["name"].lower() == subcategory_name.lower():
                return subcat
        return None

    def get_filters(self, category_name: str, subcategory_name: Optional[str] = None) -> List[Filter]:
        category = self.categories.get(category_name)
        if not category:
            raise ValueError(f"Category '{category_name}' not found in configuration.")

        category_id = category.get("id")
        filters = []

        # Get subcategory ID if subcategory name is provided
        subcategory_id = None
        subcategory_filters = []
        if subcategory_name:
            subcategory_info = self.get_subcategory_info(category_name, subcategory_name)
            if not subcategory_info:
                raise ValueError(f"Subcategory '{subcategory_name}' not found in category '{category_name}'.")
            subcategory_id = subcategory_info.get("id")
            subcategory_filters = subcategory_info.get("filters", [])

        # Process regular filters (applicable to all subcategories)
        for filter_info in category.get("filters", []):
            filter_id = filter_info.get("id")
            filter_name = filter_info.get("name")
            is_subcategory = filter_name.lower() == "subcategory"

            if is_subcategory:
                if category.get("subcategories"):
                    filter_obj = Filter(
                        category_id=category_id,
                        filter_id=filter_id,
                        name=filter_name,
                        options=category.get("subcategories"),
                        is_subcategory=True
                    )
                    filters.append(filter_obj)
                else:
                    print(f"No subcategories defined for category '{category_name}'.")
            else:
                filter_obj = Filter(
                    category_id=category_id,
                    filter_id=filter_id,
                    name=filter_name
                )
                filters.append(filter_obj)

        # Process filters specific to the selected subcategory
        for filter_info in subcategory_filters:
            filter_id = filter_info.get("id")
            filter_name = filter_info.get("name")
            filter_obj = Filter(
                category_id=category_id,
                filter_id=filter_id,
                name=filter_name,
                subcategory_filter={
                    "filter_id": category.get("filters")[5]["id"],  # Assuming the "Subcategory" filter is at index 5
                    "option_id": subcategory_id
                }
            )
            filters.append(filter_obj)

        return filters

    def get_filter_object(self, category_name: str, filter_name: str, subcategory_name: Optional[str] = None) -> Optional[Filter]:
        filters = self.get_filters(category_name, subcategory_name)
        for filter_obj in filters:
            if filter_obj.name.lower() == filter_name.lower():
                return filter_obj
        return None

    def get_filter_option_id(self, category_name: str, filter_name: str, option_value: str, subcategory_name: Optional[str] = None) -> Optional[str]:
        filter_obj = self.get_filter_object(category_name, filter_name, subcategory_name)
        if filter_obj:
            option_id = filter_obj.get_option_id(option_value)
            if option_id:
                return option_id
        print(f"Option '{option_value}' not found in filter '{filter_name}'.")
        return None

    def get_filter_key(self, category_name: str, filter_name: str, subcategory_name: Optional[str] = None) -> Optional[str]:
        filter_obj = self.get_filter_object(category_name, filter_name, subcategory_name)
        if filter_obj:
            filter_id = filter_obj.filter_id
            # Add 'af_' prefix to the filter_id when building the product URL
            return f"af_{filter_id}"
        print(f"Filter '{filter_name}' not found for category '{category_name}'.")
        return None

    def is_range_filter(self, category_name: str, filter_name: str, subcategory_name: Optional[str] = None) -> bool:
        filter_obj = self.get_filter_object(category_name, filter_name, subcategory_name)
        return filter_obj.is_range_filter() if filter_obj else False

    def is_interval_filter(self, category_name: str, filter_name: str, subcategory_name: Optional[str] = None) -> bool:
        filter_obj = self.get_filter_object(category_name, filter_name, subcategory_name)
        return filter_obj.is_interval_filter() if filter_obj else False

    def list_available_filters(self, category_name: str, subcategory_name: Optional[str] = None):
        filters = self.get_filters(category_name, subcategory_name)
        for filter_obj in filters:
            print(f"Filter: {filter_obj.name}")
            if filter_obj.type == "OPTIONS" or filter_obj.type == "INTERVAL":
                for option in filter_obj.options:
                    print(f"  - {option.value} (ID: {option.option_id})")
            elif filter_obj.type == "RANGE":
                print(f"  - Range Filter from {filter_obj.minimum} to {filter_obj.maximum}")
            
            print()
