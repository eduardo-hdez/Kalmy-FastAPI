from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class ItemBase(BaseModel):
    name: str = Field(..., max_length=128)
    description: Optional[str] = Field(None, max_length=256)
    price: float = Field(..., gt=0)
    available: bool = True

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=128)
    description: Optional[str] = Field(None, max_length=256)
    price: Optional[float] = Field(None, gt=0)
    available: Optional[bool] = None

class ItemResponse(ItemBase):
    id: str

    model_config = ConfigDict(from_attributes=True)