from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from datetime import datetime
import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Import our modules
from models import (
    ProductionItem, 
    ProductionItemCreate, 
    FileUploadResponse,
    ProductionItemsResponse
)
from database import Database
from parser import ProductionPlanParser

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://admin:pass1234@localhost:27017/production?authSource=admin")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client: Optional[AsyncIOMotorClient] = None
db = None
database: Optional[Database] = None
parser: Optional[ProductionPlanParser] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global client, db, database, parser
    try:
        # Initialize MongoDB
        client = AsyncIOMotorClient(MONGODB_URL)
        db = client.production
        await client.server_info()  # Test connection
        logger.info("Connected to MongoDB successfully")
        
        # Initialize database operations
        database = Database(db)
        logger.info("Database operations initialized")
        
        # Initialize parser
        if OPENAI_API_KEY:
            parser = ProductionPlanParser(openai_api_key=OPENAI_API_KEY)
            logger.info("AI Parser initialized successfully")
        else:
            logger.warning("OpenAI API key not found. Parser will not be available.")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")

    yield

    # Shutdown
    if client:
        client.close()
        logger.info("Disconnected from MongoDB")

# Create FastAPI app
app = FastAPI(
    title="Production Planning Parser API",
    description="API for parsing and managing production planning data",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Production Planning Parser API",
        "status": "running",
        "version": "1.0.0",
        "parser_available": parser is not None
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check MongoDB connection
        if client:
            await client.server_info()
            mongo_status = "connected"
        else:
            mongo_status = "disconnected"
    except:
        mongo_status = "error"

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "mongodb": mongo_status,
        "parser": "available" if parser else "unavailable"
    }

@app.post("/api/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and parse production planning sheet
    """
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an Excel file (.xlsx or .xls)"
        )
    
    # Check if parser is available
    if not parser:
        raise HTTPException(
            status_code=503,
            detail="Parser not available. Please configure OpenAI API key."
        )
    
    # Check if database is available
    if not database:
        raise HTTPException(
            status_code=503,
            detail="Database not available."
        )
    
    try:
        # Read file content
        file_content = await file.read()
        logger.info(f"Processing file: {file.filename}, Size: {len(file_content)} bytes")
        
        # Parse Excel file using AI
        production_items = parser.parse_excel_to_production_items(
            file_content=file_content,
            filename=file.filename
        )
        
        logger.info(f"Parsed {len(production_items)} items from {file.filename}")
        
        # Store in database
        if production_items:
            item_ids = await database.create_many_production_items(production_items)
            logger.info(f"Stored {len(item_ids)} items in database")
            
            return FileUploadResponse(
                message="File processed successfully",
                filename=file.filename,
                items_processed=len(production_items),
                items_stored=len(item_ids),
                status="completed"
            )
        else:
            return FileUploadResponse(
                message="No items found in file",
                filename=file.filename,
                items_processed=0,
                items_stored=0,
                status="completed",
                errors=["No production items could be extracted from the file"]
            )
        
    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )

@app.get("/api/production-items", response_model=ProductionItemsResponse)
async def get_production_items(
    skip: int = 0,
    limit: int = 100,
    style: Optional[str] = None,
    status: Optional[str] = None,
    order_number: Optional[str] = None
):
    """
    Get production line items with optional filtering
    """
    if not database:
        raise HTTPException(
            status_code=503,
            detail="Database not available"
        )
    
    try:
        items, total = await database.get_production_items(
            skip=skip,
            limit=limit,
            style=style,
            status=status,
            order_number=order_number
        )
        
        # Convert to Pydantic models
        production_items = [ProductionItem(**item) for item in items]
        
        return ProductionItemsResponse(
            items=production_items,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error getting production items: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving items: {str(e)}"
        )

@app.get("/api/production-items/{item_id}", response_model=ProductionItem)
async def get_production_item(item_id: str):
    """
    Get a specific production item by ID
    """
    if not database:
        raise HTTPException(
            status_code=503,
            detail="Database not available"
        )
    
    try:
        item = await database.get_production_item(item_id)
        
        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"Production item {item_id} not found"
            )
        
        return ProductionItem(**item)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting production item {item_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving item: {str(e)}"
        )

@app.delete("/api/production-items/{item_id}")
async def delete_production_item(item_id: str):
    """
    Delete a production item
    """
    if not database:
        raise HTTPException(
            status_code=503,
            detail="Database not available"
        )
    
    try:
        deleted = await database.delete_production_item(item_id)
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Production item {item_id} not found"
            )
        
        return {
            "message": f"Item {item_id} deleted successfully",
            "id": item_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting production item {item_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting item: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)