from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class ProductionDates(BaseModel):
    """Model for production milestone dates"""
    fabric: Optional[str] = None
    cutting: Optional[str] = None
    sewing: Optional[str] = None
    finishing: Optional[str] = None
    packing: Optional[str] = None
    shipping: Optional[str] = None
    delivery: Optional[str] = None
    
    # Additional flexible fields for other milestones
    other_milestones: Optional[Dict[str, str]] = Field(default_factory=dict)

    class Config:
        populate_by_name = True


class ProductionItemBase(BaseModel):
    """Base model for production items"""
    order_number: Optional[str] = None
    style: Optional[str] = None
    fabric: Optional[str] = None
    color: Optional[str] = None
    quantity: Optional[int] = None
    status: Optional[str] = "pending"
    dates: Optional[ProductionDates] = Field(default_factory=ProductionDates)
    source_file: Optional[str] = None
    
    # Additional flexible fields for varying Excel structures
    additional_data: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class ProductionItemCreate(ProductionItemBase):
    """Model for creating production items"""
    pass


class ProductionItem(ProductionItemBase):
    """Model for production items with database fields"""
    id: Optional[str] = Field(alias="_id", default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class ProductionItemInDB(ProductionItem):
    """Model for production items as stored in database"""
    pass


class FileUploadResponse(BaseModel):
    """Response model for file upload"""
    message: str
    filename: str
    items_processed: int
    items_stored: int
    status: str
    errors: Optional[List[str]] = None


class ProductionItemsResponse(BaseModel):
    """Response model for listing production items"""
    items: List[ProductionItem]
    total: int
    skip: int
    limit: int
