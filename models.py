from dataclasses import dataclass
@dataclass
class Product:
    product_id: str
    name: str
    price: float
    category: str
    stock: int
@dataclass
class OrderItem:
    product_id: str
    quantity: int
@dataclass
class Order:
    order_id: str
    customer: str
    items: list[OrderItem]
    payment_status: str