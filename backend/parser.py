import pandas as pd
import io
import json
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
import os
from models import ProductionItemCreate, ProductionDates
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)


class ProductionPlanParser:
    """AI-based parser for production planning Excel files"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize parser with OpenAI client"""
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
    
    def read_excel_file(self, file_content: bytes, filename: str) -> pd.DataFrame:
        """Read Excel file using pandas"""
        try:
            # Try reading with openpyxl engine
            df = pd.read_excel(io.BytesIO(file_content), engine='openpyxl')
            logger.info(f"Successfully read Excel file: {filename}, Shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error reading Excel file {filename}: {e}")
            raise
    
    def dataframe_to_text(self, df: pd.DataFrame) -> str:
        """Convert DataFrame to text representation for AI parsing"""
        # Get basic info
        text_parts = [
            f"Excel Data Summary:",
            f"Total Rows: {len(df)}",
            f"Total Columns: {len(df.columns)}",
            f"\nColumn Names: {', '.join(df.columns.tolist())}",
            f"\nFirst 10 rows of data:\n"
        ]
        
        # Convert first 10 rows to string
        text_parts.append(df.head(10).to_string())
        
        return "\n".join(text_parts)
    
    def extract_production_data(self, excel_text: str) -> List[Dict[str, Any]]:
        """Use OpenAI to extract structured production data from Excel text"""
        
        system_prompt = """You are an expert at extracting production planning data from Excel sheets.
Your task is to analyze the Excel data and extract production line items.

Each production item should include:
- order_number: Order or PO number
- style: Style code or name
- fabric: Fabric type/description
- color: Color variant
- quantity: Production quantity (as integer)
- status: Production status (e.g., "pending", "in_production", "completed")
- dates: Object containing milestone dates (fabric, cutting, sewing, finishing, packing, shipping, delivery)
- Any other relevant fields in additional_data

IMPORTANT:
- Extract ALL rows that represent production orders
- If a field is not present, omit it or set to null
- Dates should be in YYYY-MM-DD format if possible
- Be flexible with column names (e.g., "Style", "Style Code", "Style No" all mean style)
- If multiple color variants exist for same style, create separate items
- Return valid JSON array of objects"""

        user_prompt = f"""Extract all production line items from this Excel data:

{excel_text}

Return a JSON array of production items. Each item should have the structure:
{{
  "order_number": "string or null",
  "style": "string or null",
  "fabric": "string or null",
  "color": "string or null",
  "quantity": number or null,
  "status": "string (pending/in_production/completed)",
  "dates": {{
    "fabric": "YYYY-MM-DD or null",
    "cutting": "YYYY-MM-DD or null",
    "sewing": "YYYY-MM-DD or null",
    "finishing": "YYYY-MM-DD or null",
    "packing": "YYYY-MM-DD or null",
    "shipping": "YYYY-MM-DD or null",
    "delivery": "YYYY-MM-DD or null"
  }},
  "additional_data": {{}}
}}

Return ONLY the JSON array, no other text."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            logger.info(f"OpenAI response received: {len(result)} characters")
            
            # Parse JSON response
            parsed_data = json.loads(result)
            
            # Handle different response formats
            if isinstance(parsed_data, dict):
                if "items" in parsed_data:
                    items = parsed_data["items"]
                elif "production_items" in parsed_data:
                    items = parsed_data["production_items"]
                else:
                    # Try to find any list in the response
                    for value in parsed_data.values():
                        if isinstance(value, list):
                            items = value
                            break
                    else:
                        items = [parsed_data]
            else:
                items = parsed_data
            
            logger.info(f"Extracted {len(items)} production items")
            return items
            
        except Exception as e:
            logger.error(f"Error extracting production data with OpenAI: {e}")
            raise
    
    def parse_excel_to_production_items(
        self, 
        file_content: bytes, 
        filename: str
    ) -> List[ProductionItemCreate]:
        """Main parsing pipeline: Excel -> AI extraction -> Pydantic models"""
        
        # Step 1: Read Excel file
        df = self.read_excel_file(file_content, filename)
        
        # Step 2: Convert to text representation
        excel_text = self.dataframe_to_text(df)
        
        # Step 3: Extract structured data using AI
        extracted_items = self.extract_production_data(excel_text)
        
        # Step 4: Convert to Pydantic models
        production_items = []
        for item_data in extracted_items:
            try:
                # Extract dates if present
                dates_data = item_data.pop("dates", {})
                if dates_data:
                    dates = ProductionDates(**dates_data)
                else:
                    dates = ProductionDates()
                
                # Create production item
                production_item = ProductionItemCreate(
                    order_number=item_data.get("order_number"),
                    style=item_data.get("style"),
                    fabric=item_data.get("fabric"),
                    color=item_data.get("color"),
                    quantity=item_data.get("quantity"),
                    status=item_data.get("status", "pending"),
                    dates=dates,
                    source_file=filename,
                    additional_data=item_data.get("additional_data", {})
                )
                
                production_items.append(production_item)
                
            except Exception as e:
                logger.warning(f"Error creating production item from data: {e}, Data: {item_data}")
                continue
        
        logger.info(f"Successfully created {len(production_items)} production items from {filename}")
        return production_items


# Convenience function for direct use
async def parse_uploaded_file(
    file_content: bytes,
    filename: str,
    openai_api_key: Optional[str] = None
) -> List[ProductionItemCreate]:
    """Parse an uploaded Excel file and return production items"""
    parser = ProductionPlanParser(openai_api_key=openai_api_key)
    return parser.parse_excel_to_production_items(file_content, filename)
