import uuid
from sqlalchemy.orm import Session
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate

def create_item(item_data: ItemCreate, db: Session):
    item = Item(id=str(uuid.uuid4()), **item_data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def get_all_items(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Item).offset(skip).limit(limit).all()

def get_item_by_id(item_id: str, db: Session):
    return db.query(Item).filter(Item.id == item_id).first()

def update_item(item_id: str, item_data: ItemUpdate, db: Session):
    item = get_item_by_id(item_id, db)

    if not item:
        return None

    for key, value in item_data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item

def delete_item(item_id: str, db: Session):
    item = get_item_by_id(item_id, db)

    if not item:
        return None
        
    db.delete(item)
    db.commit()
    return item
