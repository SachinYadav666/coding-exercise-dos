from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import List, Optional, Dict, Any
from models import ProductionItem, ProductionItemCreate
from datetime import datetime
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class Database:
    """Database operations for production items"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.production_items
    
    async def create_production_item(self, item: ProductionItemCreate) -> str:
        """Create a new production item"""
        item_dict = item.model_dump(exclude_unset=True)
        item_dict["created_at"] = datetime.utcnow()
        item_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(item_dict)
        return str(result.inserted_id)
    
    async def create_many_production_items(self, items: List[ProductionItemCreate]) -> List[str]:
        """Create multiple production items"""
        items_dict = []
        for item in items:
            item_dict = item.model_dump(exclude_unset=True)
            item_dict["created_at"] = datetime.utcnow()
            item_dict["updated_at"] = datetime.utcnow()
            items_dict.append(item_dict)
        
        if not items_dict:
            return []
        
        result = await self.collection.insert_many(items_dict)
        return [str(id) for id in result.inserted_ids]
    
    async def get_production_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a production item by ID"""
        try:
            item = await self.collection.find_one({"_id": ObjectId(item_id)})
            if item:
                item["_id"] = str(item["_id"])
            return item
        except Exception as e:
            logger.error(f"Error getting production item: {e}")
            return None
    
    async def get_production_items(
        self,
        skip: int = 0,
        limit: int = 100,
        style: Optional[str] = None,
        status: Optional[str] = None,
        order_number: Optional[str] = None
    ) -> tuple[List[Dict[str, Any]], int]:
        """Get production items with optional filtering"""
        query = {}
        
        if style:
            query["style"] = {"$regex": style, "$options": "i"}
        if status:
            query["status"] = status
        if order_number:
            query["order_number"] = {"$regex": order_number, "$options": "i"}
        
        # Get total count
        total = await self.collection.count_documents(query)
        
        # Get items
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        items = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for item in items:
            item["_id"] = str(item["_id"])
        
        return items, total
    
    async def update_production_item(self, item_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a production item"""
        try:
            update_data["updated_at"] = datetime.utcnow()
            result = await self.collection.update_one(
                {"_id": ObjectId(item_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating production item: {e}")
            return False
    
    async def delete_production_item(self, item_id: str) -> bool:
        """Delete a production item"""
        try:
            result = await self.collection.delete_one({"_id": ObjectId(item_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting production item: {e}")
            return False
    
    async def delete_all_production_items(self) -> int:
        """Delete all production items (for testing)"""
        result = await self.collection.delete_many({})
        return result.deleted_count
