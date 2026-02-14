import uuid
from app.database import items_collection
from app.schemas.item import ItemCreate, ItemResponse

async def create_item(item_data: ItemCreate):
    # Generate unique ID and prepare document
    item_id = str(uuid.uuid4())
    item_dict = item_data.dict()
    item_dict["id"] = item_id

    # Insert into MongoDB
    await items_collection.insert_one(item_dict)

    return item_dict

async def get_all_items():
    # Retrieve all items with limit of 100
    items = await items_collection.find().to_list(100)
     
    # Remove MongoDB ID from each item
    for item in items:
        item.pop("_id", None)
    
    return items

async def get_item_by_id(item_id: str):
    # Retrieve item by id
    item = await items_collection.find_one({"id": item_id})

    # Remove MongoDB ID from item
    if item:
        item.pop("_id", None)

    return item