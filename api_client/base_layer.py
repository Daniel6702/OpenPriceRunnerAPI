import json
import os
import requests
from typing import Optional, Dict, Any, List

''' Additional features to be added if useful:
https://www.pricerunner.dk/dk/api/search-compare-gateway/public/content/da-DK/home/home-DK ###
https://www.pricerunner.dk/dk/api/search-compare-gateway/public/template/home/DK
https://www.pricerunner.dk/dk/api/search-compare-gateway/public/navigation/menu/DK/items
https://www.pricerunner.dk/dk/api/search-compare-gateway/public/template/treepage/DK?url=https%3A%2F%2Fwww.pricerunner.dk%2Ft%2F1493%2FLegetoej-Hobby
https://www.pricerunner.dk/dk/api/search-compare-gateway/public/search/deals/products/v3/DK?ids=PRICE_DROP,PRICE,CATEGORY,MERCHANT_DEAL,BRAND&af_PRICE_DROP=-90_-10&size=10
https://www.pricerunner.dk/dk/api/search-compare-gateway/public/cms?contentType=treePageExtraContent&id=t1493&language=da
https://www.pricerunner.dk/dk/api/search-compare-gateway/public/productinfo/DK?productIds=3205665051,3200338672&withShipping=false
https://www.pricerunner.dk/dk/api/search-compare-gateway/public/search/board/DK/507/?size=4
https://www.pricerunner.dk/dk/api/search-compare-gateway/public/keyword/category/DK/40?af_BRAND=509
https://www.pricerunner.dk/dk/api/search-compare-gateway/public/search/category/initial/DK/40?device=desktop&af_BRAND=509
https://www.pricerunner.dk/dk/api/search-compare-gateway/public/search/category/filters/DK/40?showAll=true&af_BRAND=509

https://www.pricerunner.dk/dk/api/search-compare-gateway/public/productlistings/rank/DK/3205665051
https://www.pricerunner.dk/dk/api/search-compare-gateway/public/keyword/product/DK/40-3205665051
https://www.pricerunner.dk/dk/api/search-compare-gateway/public/productlistings/pl/initial/40-3205665051/DK
https://www.pricerunner.dk/dk/api/search-compare-gateway/public/product-detail/v0/offers/DK/3205665051?af_ORIGIN=NATIONAL&af_ITEM_CONDITION=NEW,UNKNOWN&sortByPreset=PRICE
https://www.pricerunner.dk/dk/api/search-compare-gateway/public/reviews/products/overview/DK/3205665051?count=3
https://www.pricerunner.dk/dk/api/search-compare-gateway/public/pricehistory/product/3205665051/DK/DAY?merchantId=&selectedInterval=THREE_MONTHS&filter=NATIONAL

'''

BASE_API_URL = 'https://www.pricerunner.dk/dk/api/search-compare-gateway/public'

def fetch_json(url: str) -> Optional[Dict[str, Any]]:
    try:
        response = requests.get(url)
        response.raise_for_status()  
        return response.json()
    except requests.RequestException as e:
        print(f"Exception: {e}")
        return None
    
# --- Product Detail ---
def get_product_details(subcategory_id: str, product_id: str) -> Optional[Dict[str, Any]]:
    '''simple subcategory id'''
    return fetch_json(f"{BASE_API_URL}/productlistings/pl/initial/{subcategory_id}-{product_id}/DK")

def get_product_rank(product_id: str) -> Optional[Dict[str, Any]]:
    return fetch_json(f"{BASE_API_URL}/productlistings/rank/DK/{product_id}")

def get_product_keywords(subcategory_id: str, product_id: str) -> Optional[Dict[str, Any]]:
    return fetch_json(f"{BASE_API_URL}/keyword/product/DK/{subcategory_id}-{product_id}")

def get_product_offers(product_id: str, additional_params: str = '?af_ORIGIN=NATIONAL&af_ITEM_CONDITION=NEW,UNKNOWN&sortByPreset=PRICE') -> Optional[Dict[str, Any]]:
    return fetch_json(f"{BASE_API_URL}/product-detail/v0/offers/DK/{product_id}{additional_params}")

def get_price_history(product_id: str, selected_interval: str = 'THREE_MONTHS', merchant_id: str = '') -> Optional[Dict[str, Any]]:
    '''Empty merchant_id for all merchants'''
    return fetch_json(f"{BASE_API_URL}/pricehistory/product/{product_id}/DK/DAY?merchantId={merchant_id}&selectedInterval={selected_interval}&filter=NATIONAL")

def get_product_reviews(product_id: str, count: int = 4) -> Optional[Dict[str, Any]]:
    return fetch_json(f"{BASE_API_URL}/reviews/products/overview/DK/{product_id}?count={count}")

# --- Search ---
def get_filter_data(subcategory_id: str, filter_id: str) -> Optional[Dict[str, Any]]:
    return fetch_json(f"{BASE_API_URL}/search/category/facets/DK/{subcategory_id}/{filter_id}?")

def get_products(subcategory_id: str, size: int = 10, filters: str = "", additional_params: str = "") -> Optional[Dict[str, Any]]:
    size_param = f"&size={size}" if size else ""
    return fetch_json(f"{BASE_API_URL}/search/category/v3/DK/{subcategory_id}?{filters}{size_param}{additional_params}")

def get_filters(subcategory_id: str) -> Optional[Dict[str, Any]]:
    return fetch_json(f"{BASE_API_URL}/search/category/filters/DK/{subcategory_id}?showAll=true")

def get_guiding_content(subcategory_id: str, size: int = 10) -> Optional[Dict[str, Any]]:
    return fetch_json(f"{BASE_API_URL}/search/guidingcontent/v2/DK/{subcategory_id}?size={size}")

def suggest(query: str) -> Optional[Dict[str, Any]]:
    return fetch_json(f"{BASE_API_URL}/search/suggest/DK?q={query}")

def search(search_query: str, size: int = 10, additional_params: str = "&suggestionsActive=true&suggestionClicked=false&suggestionReverted=false") -> Optional[Dict[str, Any]]:
    return fetch_json(f"{BASE_API_URL}/search/v5/DK?q={search_query}&carouselSize={size}{additional_params}")


# --- Navigation ---
def get_category_data(category_id: str) -> Optional[Dict[str, Any]]:
    return fetch_json(f"{BASE_API_URL}/navigation/menu/DK/hierarchy/{category_id}")

def get_breadcrumbs(category_id: str) -> Optional[Dict[str, Any]]:
    return fetch_json(f"{BASE_API_URL}/navigation/breadcrumbs/DK/{category_id}")


# --- Keyword ---
def get_keywords(category_id: str) -> Optional[Dict[str, Any]]:
    return fetch_json(f"{BASE_API_URL}/keyword/tree/DK/{category_id}")

def get_keywords_sub(subcategory_id: str) -> Optional[Dict[str, Any]]:
    return fetch_json(f"{BASE_API_URL}/keyword/category/DK/{subcategory_id}")


# --- Content ---
def get_seo_text(seo_id: str) -> Optional[Dict[str, Any]]:
    return fetch_json(f"{BASE_API_URL}/content/da-DK/seoText/{seo_id}")

def get_homepage_data() -> Optional[Dict[str, Any]]:
    return fetch_json(f"{BASE_API_URL}/content/da-DK/home/home-DK")


# --- Misc ---
def get_popular_products(category_id: str) -> Optional[Dict[str, Any]]:
    return fetch_json(f"{BASE_API_URL}/popularproducts/v2/DK/{category_id}")

def list_products(product_ids: List[str]) -> Optional[Dict[str, Any]]:
    base_url = ("{BASE_API_URL}/listings/products/DK?productIds=")
    url = base_url + ",".join(product_ids)
    return fetch_json(url)

def get_product_reviews(product_id: str, count: int = 4) -> Optional[Dict[str, Any]]:
    return fetch_json(f"{BASE_API_URL}/reviews/products/overview/DK/{product_id}?count={count}")

def get_main_categories_from_json(json_file: str = 'categories.json'):
    if not os.path.exists(json_file):
        print(f"Error: The file '{json_file}' does not exist.")
        return None
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error: Failed to read categories from {json_file}. Exception: {e}")
        return None
    
#result = suggest("cpu")
#print(json.dumps(result, indent=4))