from api_client.api_client import APIClient

'''
Parameters:
sorting = 
RANK_asc
RANK_desc
PRICE_desc
PRICE_asc
PRICE_DROP

device=desktop
quickFilterSize=3
showAll=true
size=10
af_PRICE_DROP=-90_-25 #25-90% discount
af_ONLY_IN_STOCK=true
'''
#https://www.pricerunner.dk/dk/api/search-compare-gateway/public/search/guidingcontent/v2/DK/40?size=4 ##
#https://www.pricerunner.dk/dk/api/search-compare-gateway/public/search/v5/DK?q=ninja&suggestionsActive=true&suggestionClicked=false&suggestionReverted=false&carouselSize=10
#https://www.pricerunner.dk/dk/api/search-compare-gateway/public/keyword/category/DK/40
#https://www.pricerunner.dk/dk/api/search-compare-gateway/public/content/da-DK/seoText/CL40
#https://www.pricerunner.dk/dk/api/search-compare-gateway/public/search/suggest/DK?q=ninja
#https://www.pricerunner.dk/dk/api/search-compare-gateway/public/search/suggest/DK?q=i9%2012900k
#https://www.pricerunner.dk/dk/api/search-compare-gateway/public/product-detail/v0/offers/DK/3205665051?af_ORIGIN=NATIONAL&af_ITEM_CONDITION=NEW,UNKNOWN&sortByPreset=PRICE
#https://www.pricerunner.dk/dk/api/search-compare-gateway/public/listings/products/DK?productIds=3202548406,3202759256,3214876618,3208321147,3203089519,3202910404,3202910095,3202620785,3205014210,3205014211
#https://www.pricerunner.dk/dk/api/search-compare-gateway/public/reviews/products/overview/DK/3205665051?count=3

'''
Category Navigation: (Computer Hardware)
https://www.pricerunner.dk/dk/api/search-compare-gateway/public/navigation/menu/DK/hierarchy/t9
'''

from api_client.api_client import APIClient

def main():
    api_client = APIClient(category_name="COOLER", config_path="config.json")

    print("Available Filters and Options:")
    api_client.filter_manager.list_available_filters("COOLER", subcategory_name="AirCooler")


if __name__ == "__main__":
    main()
