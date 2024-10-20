from dataclasses import dataclass, asdict, field
import json
import os
import requests
from typing import Optional, Dict, Any, List
from api_client.base_layer import *

@dataclass
class Product:
    pass

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
    current_key: FilterKey = None

    def set_key(self, key: FilterKey):
        self.current_key = key

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
    
    def get_keys(self):
        data = get_filter_data(self.subcategory.simple_id(), self.id)
        facet = data.get("facet", {})
        counts = facet.get("counts", [])
        rankedCounts = facet.get("rankedCounts", [])
        countGroups = facet.get("countGroups", [])
        return counts + rankedCounts + countGroups
    
    def get_info(self):
        data = get_filter_data(self.subcategory.simple_id(), self.id)
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
            self.name = self.get_category_info().get("name")

    def get_url(self):
        data = get_category_data(self.id)
        base_url = 'https://www.pricerunner.dk'
        path = data.get('path')
        return base_url + path
    
    def get_subcategories(self) -> List['Category']:
        subcats_data = get_category_data(self.id).get('categories', [])
        subcategories = [Category(id=subcat["id"], name=subcat["name"]) for subcat in subcats_data]
        return subcategories
    
    def get_category_info(self) -> Dict[str, Any]:
        data = get_category_data(self.id).pop("categories", None)
        return data
    
    def get_keywords(self) -> List[str]:
        return get_keywords(self.id)
    
    def get_popular_products(self) -> List[Product]:
        return get_popular_products(self.id)
    
    def get_breadcrumbs(self) -> List[str]:
        return get_breadcrumbs(self.id)


class SubCategory(Category):
    
    def simple_id(self):
        return self.id.replace('cl','')
    
    def get_filters(self) -> List[Filter]:
        filters_data = get_filters(self.simple_id())
        filters = [Filter().from_dict(filter_data, subcategory=self) for filter_data in filters_data]
        return filters
    
    def get_keywords(self) -> List[str]:
        return get_keywords_sub(self.simple_id())
    
    def get_seo_text(self) -> str:
        return get_seo_text(self.simple_id())
    
    def get_guiding_content(self, size: int = 10) -> List[str]:
        return get_guiding_content(self.simple_id(), size)
    
    def get_products(self, size: int = 10, filters: List[Filter] = [], additional_params: str = "") -> List[Product]:
        pass
    
def get_main_categories(json_file: str = 'categories.json') -> List[Category]:
    data = get_main_categories_from_json(json_file)
    return [Category(id=category.get("id"), name=category.get("name")) for category in data]