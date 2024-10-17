### OpenPriceRunnerAPI
A reverse-engineered API wrapper for PriceRunner.dk, enabling simple and public retrieval of product prices with filtering options.

## Example Usage

```python
from base import *

for cat in get_main_categories()[:3]:
    print(cat)
```

```log
Output:
(id=t1, name=Lyd & Billede)  
(id=t2, name=Computer & Software)  
(id=t3, name=Hvidevarer)
```

```python
category = Category(id='t9')
print(category)
```

```log
Output:
(id=t9, name=Computer hardware)
```

```python
subcategories = category.get_subcategories()
for subcat in subcategories[:3]:
    print(subcat)
```

```log
Output:
(id=cl40, name=CPUs)
(id=cl37, name=Grafikkort)
(id=cl186, name=Kabinetter)
```

```python
subCategory = SubCategory(id='cl40')

filters = subCategory.get_filters()
for filter in filters[:3]:
    print(filter)
```

```log
Output:
Filter(id=PRICE, name=Pris)
Filter(id=BRAND, name=Mærke)
Filter(id=RATING, name=Vurdering)
```

```python
filter = Filter(id='BRAND', subcategory=subCategory)
filter_keys = filter.get_keys()
for key in filter_keys[:3]:
    print(key)
```

```log
Output:
{'key': '179629', 'optionId': 179629, 'count': 2, 'optionValue': 'ABB', 'optionImage': None}
{'key': '176', 'optionId': 176, 'count': 1, 'optionValue': 'Acer', 'optionImage': None}
{'key': '509', 'optionId': 509, 'count': 303, 'optionValue': 'AMD', 'optionImage': None}
```

```python
products = subCategory.get_products(query='af_BRAND=509&size=1')
print(json.dumps(products, indent=4))
```


```log
Output:
{
    "totalProductHits": 303,
    "totalCategoryOfferHits": 0,
    "clickableCategoryOfferHits": 0,
    "subCategoryLevel": null,
    "products": [
        {
            "id": "3205665051",
            "name": "AMD Ryzen 7 7800X3D 4.2GHz Socket AM5 Box",
            "description": "AMD Socket AM5",
            "url": "/pl/40-3205665051/CPUs/AMD-Ryzen-7-7800X3D-4.2GHz-Socket-AM5-Box-Sammenlign-Priser",
            "lowestPrice": {
                "amount": "3309.00",
                "currency": "DKK"
            },
            "image": {
                "id": "3009863292",
                "url": null,
                "path": "/product/3009863292/AMD-Ryzen-7-7800X3D-4.2GHz-Socket-AM5-Box.jpg",
                "description": "AMD Ryzen 7 7800X3D 4.2GHz Socket AM5 Box"
            },
            "filterHits": [],
            "rank": {
                "rank": 1,
                "trend": "NEUTRAL"
...
        ]
    },
    "buyingGuidesQuestion": null
}
```
