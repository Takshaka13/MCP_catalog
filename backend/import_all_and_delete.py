#!/usr/bin/env python3
import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from supabase import create_client, Client
from google.oauth2.service_account import Credentials
import gspread
from googleapiclient.discovery import build
from datetime import datetime

def process_worksheet(worksheet, supabase):
    """Process a single worksheet and import its data to Supabase"""
    print(f"Processing worksheet: {worksheet.title}")
    
    # Get all data from the worksheet
    data = worksheet.get_all_records()
    if not data:
        print("⚠️ Worksheet is empty or has no header row. Skipping.")
        return False
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Check required columns
    required_columns = ['developer', 'project_name', 'room_type', 'room_nymber', 'block', 
                       'sq_m', 'price_baht', 'stock_qty']
    
    # Check if all required columns are present
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"⚠️ Missing required columns: {', '.join(missing_columns)}. Skipping worksheet.")
        return False
    
    # Data validation and conversion
    print("Validating and converting data types...")
    
    # Clean up data
    try:
        # Handle price_baht - convert to numeric
        df['price_baht'] = pd.to_numeric(df['price_baht'], errors='coerce')
        invalid_prices = df[df['price_baht'].isna()].index.tolist()
        if invalid_prices:
            print(f"⚠️ Invalid price values found in {len(invalid_prices)} rows. Setting to 0.")
            df.loc[df['price_baht'].isna(), 'price_baht'] = 0
            
        # Handle stock_qty - convert to integer
        df['stock_qty'] = pd.to_numeric(df['stock_qty'], errors='coerce')
        df['stock_qty'] = df['stock_qty'].fillna(0).astype(int)
        
        # Ensure other fields are strings
        string_cols = ['developer', 'project_name', 'room_type', 'room_nymber', 'block', 'sq_m']
        for col in string_cols:
            df[col] = df[col].astype(str)
            
        # Remove completely invalid rows (where critical fields are empty)
        critical_cols = ['developer', 'project_name', 'room_type']
        
        # Filter out rows where any critical field is empty
        invalid_mask = df[critical_cols].isna().any(axis=1) | (df[critical_cols] == '').any(axis=1)
        if invalid_mask.any():
            print(f"⚠️ Removing {invalid_mask.sum()} rows with missing critical data")
            df = df[~invalid_mask]
            
        # Drop any columns that are not in our catalog schema
        extra_columns = [col for col in df.columns if col not in required_columns + ['id', 'updated_at']]
        if extra_columns:
            print(f"⚠️ Ignoring extra columns: {', '.join(extra_columns)}")
            df = df.drop(columns=extra_columns)
            
    except Exception as e:
        print(f"❌ ERROR during data validation: {str(e)}. Skipping worksheet.")
        return False
        
    # Prepare data for upsert - handle id field if present
    if 'id' in df.columns:
        # Keep only valid UUIDs
        valid_uuid_mask = df['id'].str.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', na=False)
        if (~valid_uuid_mask).any():
            print(f"⚠️ Removing invalid UUID values from {(~valid_uuid_mask).sum()} rows")
            df.loc[~valid_uuid_mask, 'id'] = np.nan
    
    # Remove updated_at if present - let Supabase handle this
    if 'updated_at' in df.columns:
        df = df.drop(columns=['updated_at'])
    
    # Convert to records for upsert
    records = df.to_dict('records')
    
    if not records:
        print("⚠️ No valid records found after validation. Skipping.")
        return False
    
    # Insert or update data in Supabase
    print(f"Upserting {len(records)} rows to Supabase catalog table...")
    try:
        result = supabase.table('catalog').upsert(records).execute()
        print(f"✅ Successfully imported {len(records)} rows to Supabase catalog table.")
        return True
    except Exception as e:
        print(f"❌ ERROR during Supabase upsert: {str(e)}")
        return False

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize Google credentials
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        print("❌ ERROR: Google credentials path not found.")
        return False
    
    print(f"Loading Google credentials from {credentials_path}...")
    credentials = Credentials.from_service_account_file(
        credentials_path,
        scopes=[
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
    )
    
    # Initialize Google Sheets and Drive clients
    sheets_client = gspread.authorize(credentials)
    drive_service = build('drive', 'v3', credentials=credentials)
    
    # Look for MCP_sandbox_app folder
    print("Searching for 'MCP_sandbox_app' folder in Google Drive...")
    target_folder_name = "MCP_sandbox_app"
    
    # Search for the folder
    query = f"name = '{target_folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
    folder_results = drive_service.files().list(q=query, spaces='drive').execute()
    
    if not folder_results.get('files', []):
        print(f"❌ ERROR: Folder '{target_folder_name}' not found.")
        return False
    
    folder_id = folder_results['files'][0]['id']
    print(f"Found folder: {target_folder_name} (ID: {folder_id})")
    
    # List all files in the folder (only Google Sheets)
    query = f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.spreadsheet'"
    file_results = drive_service.files().list(q=query, spaces='drive').execute()
    
    files = file_results.get('files', [])
    if not files:
        print(f"No Google Sheets found in folder '{target_folder_name}'.")
        return False
    
    print(f"Found {len(files)} Google Sheets in folder. Processing all files...")
    
    # Connect to Supabase
    print("Connecting to Supabase...")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ ERROR: Supabase credentials not found in environment variables.")
        return False
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Process each file
    successfully_processed_files = []
    
    for file in files:
        print(f"\n=== Processing file: {file['name']} ===")
        file_id = file['id']
        
        try:
            # Open the spreadsheet
            spreadsheet = sheets_client.open_by_key(file_id)
            worksheets = spreadsheet.worksheets()
            
            # Process all worksheets in the file
            file_success = False
            
            for worksheet in worksheets:
                print(f"\nProcessing worksheet: {worksheet.title}")
                worksheet_success = process_worksheet(worksheet, supabase)
                if worksheet_success:
                    file_success = True
            
            if file_success:
                print(f"✅ Successfully processed file: {file['name']}")
                successfully_processed_files.append(file)
            else:
                print(f"⚠️ No worksheets were successfully processed in file: {file['name']}")
                
        except Exception as e:
            print(f"❌ ERROR processing file {file['name']}: {str(e)}")
    
    # Delete successfully processed files
    if successfully_processed_files:
        print(f"\n=== Deleting {len(successfully_processed_files)} successfully processed files ===")
        
        for file in successfully_processed_files:
            try:
                drive_service.files().delete(fileId=file['id']).execute()
                print(f"✅ Deleted: {file['name']}")
            except Exception as e:
                print(f"❌ ERROR deleting file {file['name']}: {str(e)}")
                
        print(f"\n✅ Processed and deleted {len(successfully_processed_files)} files")
    else:
        print("\n⚠️ No files were successfully processed. Nothing to delete.")
    
    return True

if __name__ == "__main__":
    main() 