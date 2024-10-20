from dataclasses import dataclass, asdict, field, fields
import json
import os
import requests
from typing import Optional, Dict, Any, List, Union
from api_client.base_layer import *
import re

BASE_URL = "https://www.pricerunner.dk"

@dataclass
class Review:
    id: str
    date: str 
    lang: str
    country: str
    source: str
    domain: str
    score: int
    scoreMax: int
    title: str
    extract: str
    author: str
    product: str
    type: str
    logo: str
    logoWidth: int
    logoHeight: int
    icon: str
    iconWidth: int
    iconHeight: int
    votesUp: int
    votesDown: int
    feedbackUrl: str
    link: str
    pros: Optional[str] = None
    cons: Optional[str] = None

    def __str__(self):
        return f"Review(id={self.id}, date={self.date}, txt={self.extract})"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)
    

@dataclass
class Product:
    pass

@dataclass
class Merchant:
    pass


@dataclass
class Keyword:
    name: str = None
    url: str = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Keyword':
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
class ProductService:
    def __init__(self, id: str):
        self.id = id
        self.subcategory_id = self.get_product_category()

    def get_product_rank(self) -> Dict[str, Any]:
        return get_product_rank(self.id)

    def get_product_category(self) -> str:
        url = self.get_product_rank().get("url")
        return re.findall(r'cl/(\d+)/', url)[0]

    def get_product_details(self) -> Dict[str, Any]:
        return get_product_details(self.subcategory_id, self.id)
    
    def get_name(self) -> str:
        return self.get_product_details().get("product").get("name")
    
    def get_lowest_price(self) -> Dict[str, Any]:
        return self.get_product_details().get("minPriceInStock").get("amount")
    
    def get_keywords(self) -> List[Keyword]:
        return [Keyword(**keyword) for keyword in get_product_keywords(self.subcategory_id, self.id)]
    
    def get_price_history(self, merchant: Merchant = None, selected_interval: str = 'THREE_MONTHS') -> Dict[str, Any]:
        merchant_id = merchant.id if merchant else ''
        return get_price_history(self.id, selected_interval, merchant_id)
    
    def get_rewiews(self, count: int = 4) -> List[Review]:
        return [Review(**review) for review in get_product_reviews(self.id, count)]

    
class Searcher:
    def get_seo_text(self, item: Union['Keyword', 'SubCategory']) -> str:
        if isinstance(item, Keyword):
            id = item.name.replace(" ", "-").lower()
            return get_seo_text(id)
        elif isinstance(item, SubCategory):
            return get_seo_text(item.id)
        else:
            raise TypeError("Unsupported type provided to get_seo_text")

    def search_categories(self, search_query: str, size: int = 10, additional_params: str = "&suggestionsActive=true&suggestionClicked=false&suggestionReverted=false") -> List['Category']:
        data = search(search_query, size, additional_params)
        category_data = data.get("categories", [])  
        categories = [Category(id=category.get("id")) for category in category_data]
        return categories
    
    def search_products(self, search_query: str, size: int = 10, additional_params: str = "&suggestionsActive=true&suggestionClicked=false&suggestionReverted=false") -> List[Product]:
        data = search(search_query, size, additional_params)
        products_data = data.get("products", [])
        products = [Product(**product) for product in products_data]
        return products

    def suggest_categories(self, query: str) -> List['SubCategory']:
        def get_distinct_numbers(text) -> set:
            pattern = r'cl/(\d+)/'
            matches = re.findall(pattern, text)
            distinct_numbers = set(map(int, matches))
            return distinct_numbers
        data = suggest(query)
        suggestions_txt  = str(data.get("suggestions", []))
        distinct_numbers = get_distinct_numbers(suggestions_txt)
        return [SubCategory(id=f"cl{num}") for num in distinct_numbers]

    def suggest_products(self, query: str) -> List[Product]:
        data = suggest(query)
        products = data.get("products", [])
        return [Product(**product) for product in products]


class Category:
    def __init__(self, id: str):
        self.validate_id(id)
        self.id = id

    def validate_id(self, id: str):
        if not id.startswith('t'):
            raise ValueError("Category ID must start with 't'.")
        
    def get_category_info(self) -> Dict[str, Any]:
        return get_category_data(self.id).pop("categories", None)
    
    def get_name(self) -> str:
        return self.get_category_info().get("name")
    
    def get_path(self) -> str:
        return BASE_URL + self.get_category_info().get("path")
    
    def get_keywords(self):
        return get_keywords(self.id)
    
    def get_popular_products(self):
        return get_popular_products(self.id)
    
    def get_breadcrumbs(self):
        return get_breadcrumbs(self.id)
    
    def get_children_ids(self) -> List[str]:
        return [subcat["id"] for subcat in get_category_data(self.id).get('categories', [])]
    
    def get_all_children(self) -> List[Union['Category', 'SubCategory']]:
        """Returns a list of all child categories and subcategories."""
        ids = self.get_children_ids()
        children = []
        for id in ids:
            if id.startswith('cl'):
                children.append(SubCategory(id))
            elif id.startswith('t'):
                children.append(Category(id))
        return children

    def get_children_categories(self) -> List['Category']:
        """Returns a list of child categories."""
        return [child for child in self.get_all_children() if isinstance(child, Category)]

    def get_children_subcategories(self) -> List['SubCategory']:
        """Returns a list of child subcategories."""
        return [child for child in self.get_all_children() if isinstance(child, SubCategory)]


@dataclass
class FilterOption:
    value: str
    data: Dict[str, Any] = field(default_factory=dict)

    def __str__(self):
        return f'FilterOption(value={self.value}, data={self.data})'
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], filter_type: str) -> 'FilterOption':
        factory_methods = {
            'RANGE': cls.from_range,
            'INTERVAL': cls.from_interval,
            'OPTIONS': cls.from_option
        }
        method = factory_methods.get(filter_type, cls.default_option)
        return method(data)

    @classmethod
    def from_range(cls, data: Dict[str, Any]) -> 'FilterOption':
        from_ = data.get('from') if data.get('from') and data.get('from') != 'null' else '_'
        to_ = data.get('to') if data.get('to') and data.get('to') != 'null' else '_'
        value = f"{from_}_{to_}"
        return cls(value=value, data=data)

    @classmethod
    def from_interval(cls, data: Dict[str, Any]) -> 'FilterOption':
        value = data.get('interval')
        return cls(value=value, data=data)

    @classmethod
    def from_option(cls, data: Dict[str, Any]) -> 'FilterOption':
        value = data.get('optionId')
        return cls(value=value, data=data)

    @classmethod
    def default_option(cls, data: Dict[str, Any]) -> 'FilterOption':
        return cls(value='', data=data)

class Filter:
    option_keys = ['counts', 'rankedCounts', 'groups', 'countGroups', 'intervalCounts']

    def __init__(self, id: str, subcategory_id: str, filter_type: str, option: Optional[FilterOption] = None):
        self.id = id
        self.categoryId = subcategory_id
        self.options = set(option)
        if filter_type == 'OPTIONS': 
            self.add_option = self._add_option
            self.select_option = self._select_option
        elif filter_type == 'RANGE': 
            self.set_range = self._set_range
            self.set_option = self._set_option
        elif filter_type == 'INTERVAL': 
            self.set_option = self._set_option
            self.select_option = self._select_option
        else:
            raise ValueError("Invalid filter type.")

        self.add_option = self._add_option if filter_type == 'OPTIONS' else None

    def _select_option(self, option_value: str):
        self.set_option(FilterOption(value=option_value))
    
    def _set_range(self, from_value: Union[str, int, float], to_value: Union[str, int, float]):
        self.set_option(FilterOption(value=f"{from_value}_{to_value}"))

    def _add_option(self, option: FilterOption):
        self.options.add(option)

    def _set_option(self, option: FilterOption):
        self.options = {option}
    
    def get_options(self) -> List[FilterOption]:
        data = get_filter_data(self.categoryId, self.id).get("facet", {})
        filter_type = data.get("type")
        options = []
        for key in self.option_keys:
            for option_data in data.get(key, []):
                option = FilterOption.from_dict(option_data, filter_type)
                options.append(option)
        return options

    def get_info(self) -> Dict[str, Any]:
        data = get_filter_data(self.categoryId, self.id).get("facet", {})
        for key in self.option_keys:
            data.pop(key, None)
        return data

    def get_query(self) -> str:
        option_values = [option.value for option in self.options]
        joined_values = '%2C'.join(option_values)
        return f'af_{self.id}={joined_values}'

class SubCategory(Category):
    def __init__(self, id: str):
        self.validate_id(id)
        super().__init__(id)

    def get_filter_ids(self) -> List[str]:
        data = get_filters(self.id)
        return [filter_data.get("id") for filter_data in data]

    def get_filters(self):
        data = get_filters(self.id)
        return [Filter(id=filter_data.get("id"), subcategory_id=self.__simple_id(), filter_type=filter_data.get("type")) for filter_data in data]

    def get_product_ids(self, filters: List[Filter] = None, size: int = 10, only_in_stuck: bool = False, sorting: str = 'RANK_desc', price_drop: str = '') -> List[str]:
        '''
        Sorting options: ['RANK_asc', 'RANK_desc', 'PRICE_desc', 'PRICE_asc', 'PRICE_DROP']
        Price drop example '-90_-25' = #25-90% discount
        '''
        filter_query = '&'.join(f.get_query() + '&' for f in filters)
        additional_params = f"&af_ONLY_IN_STOCK={only_in_stuck}&sorting={sorting}&af_PRICE_DROP={price_drop}"
        product_data = get_products(subcategory_id = self.__simple_id(), filters = filter_query, size=size, additional_params=additional_params)
        products = product_data.get("products", [])
        return [product.get("id") for product in products]

    def get_prodcuts(self, filters: List[Filter] = None, size: int = 10, only_in_stuck: bool = False, sorting: str = 'RANK_desc', price_drop: str = '') -> List[Product]:
        '''
        Sorting options: ['RANK_asc', 'RANK_desc', 'PRICE_desc', 'PRICE_asc', 'PRICE_DROP']
        Price drop example '-90_-25' = #25-90% discount
        '''
        product_ids = self.get_product_ids(filters, size, only_in_stuck, sorting, price_drop)
        return [Product(id) for id in product_ids]
    
    def validate_id(self, id: str):
        if not id.startswith('cl'):
            raise ValueError("Subcategory ID must start with 'cl'.")

    def __simple_id(self):
        return self.id.replace('cl','')
    
    def __bold_id(self):
        return self.id.upper()
        
    def get_keywords(self) -> List[str]:
        return get_keywords_sub(self.__simple_id())
    
    def get_seo_text(self) -> str:
        return get_seo_text(self.__bold_id())
    
    def get_guiding_content(self, size: int = 10) -> List[str]:
        return get_guiding_content(self.__simple_id(), size)
        

def get_main_categories(json_file: str = 'categories.json') -> List[Category]:
    data = get_main_categories_from_json(json_file)
    return [Category(id=category.get("id"), name=category.get("name")) for category in data]
