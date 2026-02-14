from pydantic import BaseModel, Field

# Create item validation
class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    available: bool = True

# Response validation for GET, POST and PUT methods
class ItemResponse(BaseModel):
    id: str
    name: str
    description: str
    price: float
    available: bool