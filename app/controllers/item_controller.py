import uuid
from pymongo import ReturnDocument
from app.database import items_collection
from app.schemas.item import ItemCreate, ItemUpdate

async def create_item(item_data: ItemCreate):
    # Generate unique ID and prepare document
    item_id = str(uuid.uuid4())
    item_dict = item_data.model_dump()
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
    # Retrieve item by UUID
    item = await items_collection.find_one({"id": item_id})

    # Remove MongoDB ID from item
    if item:
        item.pop("_id", None)

    return item

async def update_item(item_id: str, item_data: ItemUpdate):
    item_dict = item_data.model_dump(exclude_unset=True) # Exclude not sent fields

    # If no fields to update, just return the item
    if not item_dict:
        return await get_item_by_id(item_id)
    
    # Update item in MongoDB
    updated_item = await items_collection.find_one_and_update(
        {"id": item_id},
        {"$set": item_dict},
        return_document=ReturnDocument.AFTER
    )

    # Remove MongoDB ID from item
    if updated_item:
        updated_item.pop("_id", None)

    return updated_item

async def delete_item(item_id: str):
    # Delete item by ID
    deleted_item = await items_collection.find_one_and_delete({"id": item_id})

    # Remove MongoDB ID from item
    if deleted_item:
        deleted_item.pop("_id", None)

    return deleted_item