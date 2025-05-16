#!/usr/bin/env python3
import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client
from google.oauth2.service_account import Credentials
import gspread
from googleapiclient.discovery import build
from datetime import datetime

def main():
    # Your Google email address to share files with
    YOUR_EMAIL = input("Enter your Google email address to share the files with: ")
    
    if not YOUR_EMAIL or '@' not in YOUR_EMAIL:
        print("❌ ERROR: Invalid email address")
        return False
    
    # Load environment variables
    load_dotenv()
    
    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ ERROR: Supabase credentials not found in environment variables.")
        return False
    
    print(f"Connecting to Supabase at {supabase_url}...")
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Fetch data from catalog table
    print("Fetching catalog data from Supabase...")
    response = supabase.table("catalog").select("*").execute()
    
    if hasattr(response, 'error') and response.error:
        print(f"❌ ERROR: Failed to fetch data: {response.error}")
        return False
    
    data = response.data
    print(f"✅ Successfully fetched {len(data)} catalog entries.")
    
    if len(data) == 0:
        print("No data found in the catalog table. Let's add some sample data for testing...")
        
        # Create sample data
        sample_data = [
            {
                "developer": "Example Developer",
                "project_name": "Sample Project",
                "room_type": "1-Bedroom",
                "room_nymber": "A101",
                "block": "A",
                "sq_m": "45",
                "price_baht": 2500000,
                "stock_qty": 5
            },
            {
                "developer": "Example Developer",
                "project_name": "Sample Project",
                "room_type": "2-Bedroom",
                "room_nymber": "B202",
                "block": "B",
                "sq_m": "65",
                "price_baht": 3500000,
                "stock_qty": 3
            }
        ]
        
        # Insert sample data
        print("Inserting sample data...")
        insert_response = supabase.table("catalog").insert(sample_data).execute()
        
        if hasattr(insert_response, 'error') and insert_response.error:
            print(f"❌ ERROR: Failed to insert sample data: {insert_response.error}")
        else:
            print(f"✅ Successfully inserted {len(sample_data)} sample records.")
            data = sample_data
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
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
    
    # Create a timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sheet_name = f"Property_Catalog_{timestamp}"
    
    # Create new spreadsheet
    print(f"Creating new spreadsheet: {sheet_name}...")
    try:
        # Search for the folder
        query = f"name = '{target_folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
        folder_results = drive_service.files().list(q=query, spaces='drive').execute()
        
        folder_id = None
        
        if not folder_results.get('files', []):
            print(f"Folder '{target_folder_name}' not found. Creating it...")
            
            # Create the folder
            folder_metadata = {
                'name': target_folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
            folder_id = folder.get('id')
            
            print(f"✅ Created folder: {target_folder_name} (ID: {folder_id})")
            
            # Share the folder with the user
            print(f"Sharing folder with {YOUR_EMAIL}...")
            permission = {
                'type': 'user',
                'role': 'writer',
                'emailAddress': YOUR_EMAIL
            }
            drive_service.permissions().create(
                fileId=folder_id,
                body=permission,
                fields='id',
                sendNotificationEmail=True
            ).execute()
            print(f"✅ Folder shared with {YOUR_EMAIL}")
        else:
            folder_id = folder_results['files'][0]['id']
            print(f"Found folder: {target_folder_name} (ID: {folder_id})")
        
        # Create the spreadsheet
        spreadsheet = sheets_client.create(sheet_name)
        
        # Share the spreadsheet with the user immediately after creation
        print(f"Sharing spreadsheet with {YOUR_EMAIL}...")
        file_id = spreadsheet.id
        permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': YOUR_EMAIL
        }
        drive_service.permissions().create(
            fileId=file_id,
            body=permission,
            fields='id',
            sendNotificationEmail=True
        ).execute()
        print(f"✅ Spreadsheet shared with {YOUR_EMAIL}")
        
        if folder_id:
            # Move the spreadsheet to the folder
            drive_service.files().update(
                fileId=file_id,
                addParents=folder_id,
                removeParents='root'
            ).execute()
            
            print(f"Moved spreadsheet to '{target_folder_name}' folder.")
        
        # Get the first worksheet
        worksheet = spreadsheet.get_worksheet(0)
        
        # Reorder columns for better display in Google Sheets
        columns_order = [
            'developer', 'project_name', 'room_type', 'room_nymber', 
            'block', 'sq_m', 'price_baht', 'stock_qty', 'updated_at', 'id'
        ]
        
        # Ensure all columns exist
        for col in columns_order[:]:  # Create a copy to iterate safely
            if col not in df.columns:
                print(f"Warning: Column '{col}' not found in data. Skipping.")
                columns_order.remove(col)
        
        # Reorder columns that do exist
        df = df[columns_order]
        
        # Convert DataFrame to list of lists for Google Sheets
        data_to_write = [df.columns.tolist()] + df.values.tolist()
        
        # Update the sheet
        worksheet.update(data_to_write)
        
        print(f"✅ SUCCESS: Catalog data pushed to Google Sheets.")
        print(f"Spreadsheet URL: {spreadsheet.url}")
        print(f"You should receive an email notification that gives you access.")
        print(f"The file has been shared with your email: {YOUR_EMAIL}")
        
        return True
    
    except Exception as e:
        print(f"❌ ERROR: Failed to push data to Google Drive: {str(e)}")
        return False

if __name__ == "__main__":
    main() 