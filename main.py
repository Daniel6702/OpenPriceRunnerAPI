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

def main():
    # Initialize the API client for COOLER
    api_client = APIClient(category_name="CPU", config_path="config.json")

    # Optional: List available filters and their options
    print("Available Filters and Options:")
    api_client.filter_manager.list_available_filters("CPU")

    '''
    # Define selected filters
    selected_filters = {
        "Subcategory": "AirCooler",
        "Price": {"min": 100, "max": 1900},
        "Brand": "Noctua"
    }

    # Define additional parameters
    parameters = {
        "sorting": "PRICE_asc",
        "size": 12
    }

    # Fetch products with selected filters and additional parameters
    data = api_client.fetch_products(selected_filters=selected_filters, parameters=parameters)

    # Display fetched products
    if data:
        api_client.display_products(data)
    else:
        print("No data retrieved.")
    '''

if __name__ == "__main__":
    main()

