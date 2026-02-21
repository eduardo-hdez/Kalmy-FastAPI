from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.controllers import item_controller
from app.database import get_db
from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse

router = APIRouter(prefix="/items", tags=["items"])

@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item_data: ItemCreate, db: Session = Depends(get_db)):
    """Create a new item"""
    return item_controller.create_item(item_data, db)

@router.get("/", response_model=list[ItemResponse])
def get_items(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Get all items"""
    return item_controller.get_all_items(db, skip=skip, limit=limit)

@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: str, db: Session = Depends(get_db)):
    """Get a single item by ID"""
    item = item_controller.get_item_by_id(item_id, db)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} was not found"
        )

    return item

@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: str, item_data: ItemUpdate, db: Session = Depends(get_db)):
    """Update an existing item by ID"""
    item = item_controller.update_item(item_id, item_data, db)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} was not found"
        )

    return item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: str, db: Session = Depends(get_db)):
    """Delete an item by ID"""
    item = item_controller.delete_item(item_id, db)
    
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} was not found"
        )