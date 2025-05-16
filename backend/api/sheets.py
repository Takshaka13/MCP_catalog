from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from .google_client import GoogleDriveClient
import os

router = APIRouter()
google_client = GoogleDriveClient()

@router.get("/sheets/health", response_model=Dict[str, Any])
async def check_connection():
    """Check Google Drive connection and credentials"""
    try:
        # Try to list spreadsheets as a connection test
        spreadsheets = google_client.list_spreadsheets()
        return {
            "status": "healthy",
            "message": "Successfully connected to Google Drive",
            "spreadsheets_count": len(spreadsheets)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "unhealthy",
                "message": f"Failed to connect to Google Drive: {str(e)}"
            }
        )

@router.get("/sheets", response_model=List[Dict[str, str]])
async def list_sheets():
    """List all available Google Sheets"""
    try:
        return google_client.list_spreadsheets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sheets/{spreadsheet_id}")
async def get_sheet_data(
    spreadsheet_id: str,
    sheet_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get data from a specific Google Sheet
    
    Args:
        spreadsheet_id: ID of the spreadsheet
        sheet_name: Optional name of the specific sheet to read
    """
    try:
        # First get metadata
        metadata = google_client.get_sheet_metadata(spreadsheet_id)
        
        # Then get the data
        df = google_client.get_sheet_as_df(spreadsheet_id, sheet_name)
        
        return {
            "metadata": metadata,
            "rows": len(df),
            "columns": list(df.columns),
            "data": df.to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 