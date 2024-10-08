from api_client import APIClient

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

from api_client import APIClient

def main():
    api_client = APIClient(category_name="COOLER", config_path="config.json")

    print("Available Filters and Options:")
    api_client.filter_manager.list_available_filters("COOLER", subcategory_name="AirCooler")


if __name__ == "__main__":
    main()
