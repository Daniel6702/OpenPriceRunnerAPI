from dataclasses import dataclass, field
from typing import List, Optional, Any


@dataclass
class Price:
    amount: str
    currency: str

    @classmethod
    def from_dict(cls, data: dict) -> 'Price':
        return cls(**data)


@dataclass
class Image:
    id: Optional[str]
    url: Optional[str]
    path: str
    description: str

    @classmethod
    def from_dict(cls, data: dict) -> 'Image':
        return cls(**data)


@dataclass
class Rank:
    rank: int
    trend: str

    @classmethod
    def from_dict(cls, data: dict) -> 'Rank':
        return cls(**data)


@dataclass
class Brand:
    id: str
    name: str
    image: Optional[Any]  # Assuming image can be of any type or another structured type

    @classmethod
    def from_dict(cls, data: dict) -> 'Brand':
        return cls(**data)


@dataclass
class Rating:
    numberOfRatings: int
    averageRating: str
    count: int
    average: str

    @classmethod
    def from_dict(cls, data: dict) -> 'Rating':
        return cls(**data)


@dataclass
class Ribbon:
    type: str
    value: str
    description: Optional[Any]

    @classmethod
    def from_dict(cls, data: dict) -> 'Ribbon':
        return cls(**data)


@dataclass
class Merchant:
    id: str
    name: str
    image: Optional[Image]
    clickable: Optional[bool] = None  # Only present in previewMerchants

    @classmethod
    def from_dict(cls, data: dict) -> 'Merchant':
        image_data = data.get('image')
        image = Image.from_dict(image_data) if image_data else None
        return cls(
            id=data['id'],
            name=data['name'],
            image=image,
            clickable=data.get('clickable')
        )


@dataclass
class CheapestOffer:
    id: str
    price: Price
    url: str
    merchant: Merchant
    pricePerUnit: Optional[Any]

    @classmethod
    def from_dict(cls, data: dict) -> 'CheapestOffer':
        price = Price.from_dict(data['price'])
        merchant = Merchant.from_dict(data['merchant'])
        return cls(
            id=data['id'],
            price=price,
            url=data['url'],
            merchant=merchant,
            pricePerUnit=data.get('pricePerUnit')
        )


@dataclass
class PreviewMerchants:
    count: int
    merchants: List[Merchant]

    @classmethod
    def from_dict(cls, data: dict) -> 'PreviewMerchants':
        merchants = [Merchant.from_dict(m) for m in data.get('merchants', [])]
        return cls(
            count=data['count'],
            merchants=merchants
        )


@dataclass
class Product:
    id: str
    name: str
    description: str
    url: str
    lowestPrice: Price
    image: Image
    filterHits: List[Any]
    rank: Rank
    brand: Brand
    rating: Rating
    priceDrop: Optional[Any]
    ribbon: Ribbon
    productGroup: Optional[Any]
    cheapestOffer: CheapestOffer
    classification: str
    previewMerchants: PreviewMerchants
    installmentPrice: Optional[Any]

    @classmethod
    def from_dict(cls, data: dict) -> 'Product':
        lowest_price = Price.from_dict(data['lowestPrice'])
        image = Image.from_dict(data['image'])
        rank = Rank.from_dict(data['rank'])
        brand = Brand.from_dict(data['brand'])
        rating = Rating.from_dict(data['rating'])
        ribbon = Ribbon.from_dict(data['ribbon'])
        cheapest_offer = CheapestOffer.from_dict(data['cheapestOffer'])
        preview_merchants = PreviewMerchants.from_dict(data['previewMerchants'])
        
        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            url=data['url'],
            lowestPrice=lowest_price,
            image=image,
            filterHits=data.get('filterHits', []),
            rank=rank,
            brand=brand,
            rating=rating,
            priceDrop=data.get('priceDrop'),
            ribbon=ribbon,
            productGroup=data.get('productGroup'),
            cheapestOffer=cheapest_offer,
            classification=data['classification'],
            previewMerchants=preview_merchants,
            installmentPrice=data.get('installmentPrice')
        )


@dataclass
class ProductsData:
    products: List[Product]

    @classmethod
    def from_dict(cls, data: dict) -> 'ProductsData':
        products = [Product.from_dict(prod) for prod in data.get('products', [])]
        return cls(products=products)
