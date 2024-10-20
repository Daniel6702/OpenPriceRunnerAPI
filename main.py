from api_client.base_layer import *

subCategory = SubCategory(id='cl40')

products = subCategory.get_products(query='af_BRAND=509&size=1')
print(json.dumps(products, indent=4))