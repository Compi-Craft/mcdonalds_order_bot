from typing import List, Optional, Union, Dict, Literal
from pydantic import BaseModel


class IngredientChange(BaseModel):
    excluded: List[str] = []
    extra: List[str] = []


class BaseItem(BaseModel):
    type: str
    name: str
    quantity: int = 1
    ingredients: Optional[IngredientChange] = None


class ComboItem(BaseModel):
    type: Literal["combo"]
    name: str
    quantity: int = 1
    burger: str
    fries: str = "French Fries"
    drink: Optional[str] = None
    ingredients: Optional[Dict[str, IngredientChange]] = None

    class Config:
        extra = "forbid"


class VirtualItem(BaseModel):
    type: str  # e.g., "drink", "dessert"


class Order(BaseModel):
    items: List[Union[BaseItem, ComboItem]]
    virtual_items: List[VirtualItem] = []


class OrderWrapper(BaseModel):
    order: Order
