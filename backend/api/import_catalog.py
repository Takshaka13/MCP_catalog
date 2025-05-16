from fastapi import APIRouter, UploadFile, HTTPException
from supabase import create_client, Client
import pandas as pd
import os
from dotenv import load_dotenv
from io import StringIO
from typing import Dict, Any

# Load environment variables
load_dotenv()

# Initialize router
router = APIRouter()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL", ""),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
)

@router.post("/import")
async def import_catalog(file: UploadFile) -> Dict[str, Any]:
    """
    Import catalog data from CSV file.
    Expected columns: developer, project_name, room_type, room_nymber, block, sq_m, price_baht, stock_qty
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    try:
        # Read CSV content
        contents = await file.read()
        csv_string = contents.decode()
        df = pd.read_csv(StringIO(csv_string))

        # Validate required columns
        required_columns = [
            'developer', 'project_name', 'room_type', 'room_nymber',
            'block', 'sq_m', 'price_baht', 'stock_qty'
        ]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )

        # Data type validation and conversion
        try:
            df['price_baht'] = pd.to_numeric(df['price_baht'])
            df['stock_qty'] = pd.to_numeric(df['stock_qty'], downcast='integer')
            df['sq_m'] = df['sq_m'].astype(str)  # Ensure sq_m is string as per schema
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Data type validation failed: {str(e)}"
            )

        # Convert DataFrame to list of dictionaries for insertion
        records = df.to_dict('records')
        
        # Bulk upsert to Supabase
        result = supabase.table('catalog').upsert(records).execute()

        return {
            "success": True,
            "inserted": len(records),
            "message": f"Successfully processed {len(records)} records"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 