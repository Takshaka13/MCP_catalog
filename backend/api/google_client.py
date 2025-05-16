import os
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
from typing import List, Optional

class GoogleDriveClient:
    """Client for interacting with Google Drive and Google Sheets"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    def __init__(self, credentials_path: Optional[str] = None):
        """Initialize Google Drive client with service account credentials"""
        if credentials_path is None:
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            
        if not credentials_path:
            raise ValueError("Google credentials path not provided")
            
        credentials = Credentials.from_service_account_file(
            credentials_path,
            scopes=self.SCOPES
        )
        self.client = gspread.authorize(credentials)

    def get_sheet_as_df(self, spreadsheet_id: str, sheet_name: str = None) -> pd.DataFrame:
        """
        Read a Google Sheet and return it as a pandas DataFrame
        
        Args:
            spreadsheet_id: The ID of the spreadsheet (from the URL)
            sheet_name: Optional name of the specific sheet to read. If None, reads the first sheet.
            
        Returns:
            pandas.DataFrame containing the sheet data
        """
        try:
            # Open the spreadsheet
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            
            # Get the specified worksheet or the first one
            if sheet_name:
                worksheet = spreadsheet.worksheet(sheet_name)
            else:
                worksheet = spreadsheet.get_worksheet(0)
            
            # Get all values
            data = worksheet.get_all_records()
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            return df
            
        except Exception as e:
            raise Exception(f"Error reading Google Sheet: {str(e)}")

    def list_spreadsheets(self) -> List[dict]:
        """
        List all accessible spreadsheets
        
        Returns:
            List of dictionaries containing spreadsheet info (id, name, url)
        """
        try:
            spreadsheet_list = self.client.list_spreadsheet_files()
            return [
                {
                    'id': sheet['id'],
                    'name': sheet['name'],
                    'url': f"https://docs.google.com/spreadsheets/d/{sheet['id']}"
                }
                for sheet in spreadsheet_list
            ]
        except Exception as e:
            raise Exception(f"Error listing spreadsheets: {str(e)}")

    def get_sheet_metadata(self, spreadsheet_id: str) -> dict:
        """
        Get metadata about a specific spreadsheet
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            
        Returns:
            Dictionary containing spreadsheet metadata
        """
        try:
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            return {
                'id': spreadsheet_id,
                'name': spreadsheet.title,
                'sheets': [sheet.title for sheet in spreadsheet.worksheets()],
                'url': f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
            }
        except Exception as e:
            raise Exception(f"Error getting spreadsheet metadata: {str(e)}") 