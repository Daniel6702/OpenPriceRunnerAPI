from dataclasses import dataclass, asdict, field
import json
import os
import requests
from typing import Optional, Dict, Any, List

@dataclass
class FilterKey:
    key: str = None
    optionId: str = None
    count: int = None
    optionValue: str = None
    optionImage: str = None

    def __str__(self) -> str:
        return f"FilterKey(key={self.key}, optionId={self.optionId}, count={self.count}, optionValue={self.optionValue})"
    
    def from_dict(self, data: dict):
        if not data: return None
        self.key = data.get("key")
        self.optionId = data.get("optionId")
        self.count = data.get("count")
        self.optionValue = data.get("optionValue")
        self.optionImage = data.get("optionImage")
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Filter:
    name: str = None
    id: str = None
    subcategory: 'SubCategory' = None

    def __str__(self) -> str:
        return f"Filter(id={self.id}, name={self.name})"

    def from_dict(self, data: dict, subcategory: 'SubCategory' = None):
        if not data: return None
        self.name = data.get("name")
        self.id = data.get("id")
        self.subcategory = subcategory
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def get_data(self):
        try:
            url = f"https://www.pricerunner.dk/dk/api/search-compare-gateway/public/search/category/facets/DK/{self.subcategory.id.replace('cl', '')}/{self.id}?"
            return requests.get(url).json()
        except Exception as e:
            print(f"Error: Failed to retrieve data for {self.name}. Exception: {e}")
            return None
    
    def get_keys(self):
        data = self.get_data()
        facet = data.get("facet", {})
        counts = facet.get("counts", [])
        rankedCounts = facet.get("rankedCounts", [])
        countGroups = facet.get("countGroups", [])
        return counts + rankedCounts + countGroups
    
    def get_info(self):
        data = self.get_data()
        facet = data.get("facet", {})
        facet.pop("counts", None)
        facet.pop("rankedCounts", None)
        facet.pop("countGroups", None)
        return facet

@dataclass
class CategoryData:
    id: str = None
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def __str__(self) -> str:
        return f"(id={self.id}, name={self.name})"
    
    def __post_init__(self):
        self.update_name()

    def update_name(self):
        pass

class Category(CategoryData):
    '''A Category will convert to a SubCategory if the ID starts with 'cl'.'''

    def __new__(cls, *args, **kwargs):
        id_ = kwargs.get('id') or (args[0] if args else None)
        
        if id_ and id_.startswith('cl'):
            return super(Category, SubCategory).__new__(SubCategory)
        else:
            return super().__new__(cls)

    def update_name(self):
        if not self.name:
            self.name = self.get_data().get("name")

    def from_dict(self, data: dict):
        if not data: return None
        self.id = data.get("id")
        self.name = data.get("name")
        return self

    def get_url(self):
        data = self.get_data()
        base_url = 'https://www.pricerunner.dk'
        path = data.get('path')
        return base_url + path
    
    def get_data(self) -> Dict[str, Any]:
        try:
            url = f"https://www.pricerunner.dk/dk/api/search-compare-gateway/public/navigation/menu/DK/hierarchy/{self.id}"
            return requests.get(url).json()
        except Exception as e:
            print(f"Error: Failed to retrieve data for {self.name}. Exception: {e}")
            return None
        
    def get_subcategories(self) -> List['Category']:
        try:
            url = f"https://www.pricerunner.dk/dk/api/search-compare-gateway/public/navigation/menu/DK/hierarchy/{self.id}"
            subcats_data = requests.get(url).json().get('categories', [])
            subcategories = [Category(id=subcat["id"], name=subcat["name"]) for subcat in subcats_data]
            return subcategories

        except Exception as e:
            print(f"Error: Failed to retrieve subcategories for {self.name}. Exception: {e}")
            return None
    
    def get_keywords(self) -> Dict[str, Any]:
        try:
            url = f"https://www.pricerunner.dk/dk/api/search-compare-gateway/public/keyword/tree/DK/{self.id}"
            return requests.get(url).json()
        except Exception as e:
            print(f"Error: Failed to retrieve keywords for {self.name}. Exception: {e}")
            return None
    
    def get_popular_products(self) -> Dict[str, Any]:
        try:
            url = f"https://www.pricerunner.dk/dk/api/search-compare-gateway/public/popularproducts/v2/DK/{self.id}"
            return requests.get(url).json()
        except Exception as e:
            print(f"Error: Failed to retrieve popular products for {self.name}. Exception: {e}")
            return None
    
    def get_breadcrumbs(self) -> Dict[str, Any]:
        try: 
            url = f"https://www.pricerunner.dk/dk/api/search-compare-gateway/public/navigation/breadcrumbs/DK/{self.id}"
            return requests.get(url).json()
        except Exception as e:
            print(f"Error: Failed to retrieve navigation data for {self.name}. Exception: {e}")
            return None
        
class SubCategory(Category):
    def get_products(self, query: str = '&size=4') -> Dict[str, Any]:
        try: 
            url = f"https://www.pricerunner.dk/dk/api/search-compare-gateway/public/search/category/v3/DK/{self.id.replace('cl', '')}?{query}"
            return requests.get(url).json()
        except Exception as e:
            print(f"Error: Failed to retrieve products for {self.name}. Exception: {e}")
            return None

    def get_filters(self) -> List[Filter]:
        try:
            url = f"https://www.pricerunner.dk/dk/api/search-compare-gateway/public/search/category/filters/DK/{self.id.replace('cl', '')}?showAll=true"
            filters = [
                Filter().from_dict(filter_data, subcategory=self) 
                for group in requests.get(url).json().get("groups", []) 
                for filter_data in group.get("filters", [])
            ]
            return filters
        except Exception as e:
            print(f"Error: Failed to retrieve filters for {self.name}. Exception: {e}")
            return None

    def get_keywords(self):
        try:
            url = f"https://www.pricerunner.dk/dk/api/search-compare-gateway/public/keyword/category/DK/{self.id.replace('cl', '')}"
            return requests.get(url).json()
        except Exception as e:
            print(f"Error: Failed to retrieve popular keywords for {self.name}. Exception: {e}")
            return None
        
    def get_seoText(self):
        try:
            url = f'https://www.pricerunner.dk/dk/api/search-compare-gateway/public/content/da-DK/seoText/{self.id.replace("cl", "CL")}'
            return requests.get(url).json()
        except Exception as e:
            print(f"Error: Failed to retrieve SEO text for {self.name}. Exception: {e}")
            return None
        
    def get_guidingcontent(self, size: int = 10):
        try:
            url = f'https://www.pricerunner.dk/dk/api/search-compare-gateway/public/search/guidingcontent/v2/DK/{self.id.replace("cl", "CL")}?size={size}'
            return requests.get(url).json()
        except Exception as e:
            print(f"Error: Failed to retrieve guiding content for {self.name}. Exception: {e}")
            return None
        
def suggest(query: str):
    try:
        url = f"https://www.pricerunner.dk/dk/api/search-compare-gateway/public/search/suggest/DK?q={query}"
        return requests.get(url).json()
    except Exception as e:
        print(f"Error: Failed to retrieve suggestions for '{query}'. Exception: {e}")
        return None

def search(search_query: str, size: int = 10, additional_params: str = "") -> Dict[str, Any]:
    try:
        url = f"https://www.pricerunner.dk/dk/api/search-compare-gateway/public/search/v5/DK?q={search_query}&suggestionsActive=true&suggestionClicked=false&suggestionReverted=false&carouselSize={size}{additional_params}"
        return requests.get(url).json()
    except Exception as e:
        print(f"Error: Failed to retrieve search results for '{search_query}'. Exception: {e}")
        return None
        
def list_products(productIds: list[str]):
    try:
        base_url = 'https://www.pricerunner.dk/dk/api/search-compare-gateway/public/listings/products/DK?productIds='
        url = base_url + ','.join(productIds)
        return requests.get(url).json()
    except Exception as e:
        print(f"Error: Failed to retrieve products. Exception: {e}")
        return None
    
def get_product_reviews(productId: str, count: int = 4):
    try:
        url = f"https://www.pricerunner.dk/dk/api/search-compare-gateway/public/reviews/products/overview/DK/{productId}?count={count}"
        return requests.get(url).json()
    except Exception as e:
        print(f"Error: Failed to retrieve reviews for product {productId}. Exception: {e}")
        return None

def get_main_categories(json_file: str = 'categories.json') -> List[Category]:
    if not os.path.exists(json_file):
        print(f"Error: The file '{json_file}' does not exist.")
        return None
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return [Category(id=category.get("id"), name=category.get("name")) for category in json.load(f)]
    except Exception as e:
        print(f"Error: Failed to read categories from {json_file}. Exception: {e}")
        return None
    
result = suggest("cpu")
print(json.dumps(result, indent=4))