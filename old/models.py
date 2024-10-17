from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional, Union

@dataclass 
class Merchant:
    id: str = None
    name: str = None
    image: 'Image' = None

    def __str__(self):
        return f"Merchant(id={self.id}, name={self.name}, image={self.image})"

@dataclass
class LowestPrice:
    amount: float = None
    currency: str = None

    def from_dict(self, data: Dict[str, Any]):
        self.amount = data.get("amount")
        self.currency = data.get("currency")
        return self

    def __str__(self):
        return f"{self.amount} {self.currency}"

@dataclass
class Rating:
    average: float = None
    count: int = None

    def __str__(self):
        return f"Rating(average={self.average}, count={self.count})"

@dataclass
class Keyword:
    name: str = None
    url: str = None

    def __str__(self):
        return self.name or "No Keyword Name"

    def from_dict(self, data: Dict[str, Any]):
        self.name = data.get("name")
        self.url = data.get("url")
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Image:
    path: str = None
    description: str = None

    def from_dict(self, data: Dict[str, Any] = None):
        if not data: return None
        self.path = data.get("path")
        self.description = data.get("description")
        return self

    def __str__(self):
        return f"Image(description={self.description}, path={self.path})"

@dataclass
class Brand:
    id: str = None
    name: str = None 
    image: Image = None

    def from_dict(self, data: Dict[str, Any]):
        if not data: return None
        self.id = data.get("id")
        self.name = data.get("name")
        self.image = Image().from_dict(data.get("image")) if data.get("image") else None
        return self

    def __str__(self):
        return f"Brand(id={self.id}, name={self.name}, image={self.image})"

@dataclass
class Product:
    id: str = None
    name: str = None
    path: str = None
    category: 'Subcategory' = None
    image: Image = None
    lowest_price: LowestPrice = None
    brand: Brand = None

    def from_dict(self, data: Dict[str, Any]):
        if not data: return None
        self.id = data.get("id")
        self.name = data.get("name")
        self.path = data.get("path")
        self.category = Subcategory().from_dict(data.get("category")) if data.get("category") else None
        self.image = Image().from_dict(data.get("image")) if data.get("image") else None
        self.lowest_price = LowestPrice().from_dict(data.get("lowestPrice")) if data.get("lowestPrice") else None
        self.brand = Brand().from_dict(data.get("brand")) if data.get("brand") else None
        return self

    def __str__(self):
        return (f"Product(id={self.id}, name={self.name}, category={self.category.name}, "
                f"lowest_price={self.lowest_price})")

@dataclass
class Subcategory:
    id: Optional[str] = None
    name: Optional[str] = None
    path: Optional[str] = None
    image: Optional[Image] = None
    parent_category: Optional[Union['Category', 'Subcategory']] = None
    children: List['Subcategory'] = field(default_factory=list)

    def from_dict(self, data: Dict[str, Any], parent: Optional[Union[dict, 'Category', 'Subcategory']] = None) -> 'Subcategory':
        if not data:
            return None
        self.id = data.get("id")
        self.name = data.get("name")
        self.path = data.get("path")
        self.image = Image.from_dict(data.get("image")) if data.get("image") else None
        
        if isinstance(parent, dict):
            self.parent_category = Category.from_dict(parent)  
        else:
            self.parent_category = parent  
    
        self.children = [Subcategory().from_dict(child, parent=self) for child in data.get("children", [])]
        return self

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def __str__(self) -> str:
        return self._str_helper()

    def _str_helper(self, level: int = 0) -> str:
        indent = "    " * level
        lines = [
            f"{indent}Subcategory:",
            f"{indent}    ID: {self.id}",
            f"{indent}    Name: {self.name}",
            f"{indent}    Path: {self.path}",
            f"{indent}    Image: {self.image}",
            f"{indent}    Parent Category: {self.parent_category.name if self.parent_category else 'None'}",
            f"{indent}    Children ({len(self.children)}):"
        ]
        for child in self.children[:2]:
            lines.append(child._str_helper(level + 1))
        return "\n".join(lines)

@dataclass
class Category:
    id: Optional[str] = None
    name: Optional[str] = None
    path: Optional[str] = None
    image: Optional[Image] = None
    subcategories: List[Subcategory] = field(default_factory=list)
    parent_category: Optional['Category'] = None
    keywords: List[Keyword] = field(default_factory=list)
    popular_products: List[Product] = field(default_factory=list)

    def from_dict(self, data: Dict[str, Any] = None) -> 'Category':
        if not data:
            return None
        self.id = data.get("id")
        self.name = data.get("name")
        self.path = data.get("path") if data.get("path") else data.get("url")
        self.image = Image.from_dict(data.get("image")) if data.get("image") else None
        self.subcategories = [Subcategory().from_dict(subcat, parent=self) for subcat in data.get("subcategories", [])] if data.get("subcategories") else []
        parent_data = data.get("parent_category")
        if isinstance(parent_data, dict):
            self.parent_category = Category.from_dict(parent_data)
        else:
            self.parent_category = None
        self.keywords = [Keyword().from_dict(keyword) for keyword in data.get("keywords", [])]
        self.popular_products = [Product(**prod) for prod in data.get("popular_products", [])]
        return self

    def __str__(self) -> str:
        return self._str_helper()

    def _str_helper(self, level: int = 0) -> str:
        indent = "    " * level
        lines = [
            f"{indent}Category:",
            f"{indent}    ID: {self.id}",
            f"{indent}    Name: {self.name}",
            f"{indent}    Path: {self.path}",
            f"{indent}    Image: {self.image}",
            f"{indent}    Parent Category: {self.parent_category.name if self.parent_category else 'None'}",
            f"{indent}    Subcategories ({len(self.subcategories)}):"
        ]
        for subcat in self.subcategories[:2]:
            lines.append(subcat._str_helper(level + 1))
        if len(self.subcategories) > 2:
            lines.append(f"{indent}        ... and {len(self.subcategories) - 2} more subcategories")
        
        lines.append(f"{indent}    Keywords ({len(self.keywords)}): " + ", ".join(map(str, self.keywords[:2])) + ("..." if len(self.keywords) > 2 else ""))
        lines.append(f"{indent}    Popular Products ({len(self.popular_products)}): " + ", ".join(map(str, self.popular_products[:2])) + ("..." if len(self.popular_products) > 2 else ""))
        return "\n".join(lines)