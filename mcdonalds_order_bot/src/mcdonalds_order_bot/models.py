from typing import List, Optional, Union, Dict, Literal
from pydantic import BaseModel, Field


class IngredientChange(BaseModel):
    excluded: List[str] = Field(default_factory=list)
    extra: List[str] = Field(default_factory=list)


def default_ingredients() -> Dict[Literal['burgers', 'drinks', 'fries'], IngredientChange]:
    return {
        'burgers': IngredientChange(),
        'drinks': IngredientChange(),
        'fries': IngredientChange()
    }

class SizeProperty(BaseModel):
    size: Literal['small', 'medium', 'large']


class BaseItem(BaseModel):
    type: Literal['burgers', 'drinks', 'fries', 'desserts', 'sauces']
    name: str
    quantity: int = 1
    size: Optional[Literal['small', 'medium', 'large']] = None
    ingredients: IngredientChange = Field(default_factory=IngredientChange)
    combo_suggested: bool = False

class ComboItem(BaseModel):
    type: Literal["combos"]
    name: str
    quantity: int = 1
    fries: str = "French Fries"
    drink: Optional[str] = None
    size: Literal['small', 'medium', 'large'] = 'medium'
    ingredients: Dict[Literal['burgers', 'drinks', 'fries'], IngredientChange] = Field(default_factory=default_ingredients)
    sauce: Optional[str] = None
    sauce_suggested: bool = False

    class Config:
        extra = "forbid"


class VirtualItem(BaseModel):
    type: str  # e.g., "drink", "dessert"


class Order(BaseModel):
    items: List[Union[BaseItem, ComboItem]]
    virtual_items: List[VirtualItem] = Field(default_factory=list)
    finish_order: bool = False
