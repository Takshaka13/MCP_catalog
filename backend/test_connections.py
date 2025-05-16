#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
import argparse

def test_supabase():
    """Test Supabase connection."""
    try:
        from supabase import create_client, Client
        
        # Load environment variables
        load_dotenv()
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ ERROR: Supabase credentials not found in environment variables.")
            print("Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env file.")
            return False
        
        print(f"Connecting to Supabase at {supabase_url}...")
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Try a simple query
        response = supabase.table("catalog").select("id").limit(1).execute()
        
        print("✅ SUCCESS: Successfully connected to Supabase!")
        return True
    except Exception as e:
        print(f"❌ ERROR: Failed to connect to Supabase: {str(e)}")
        return False

def test_google_drive():
    """Test Google Drive connection."""
    try:
        from google.oauth2.service_account import Credentials
        import gspread
        
        # Load environment variables
        load_dotenv()
        
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        if not credentials_path:
            print("❌ ERROR: Google credentials path not found in environment variables.")
            print("Please set GOOGLE_APPLICATION_CREDENTIALS in .env file.")
            return False
        
        if not os.path.exists(credentials_path):
            print(f"❌ ERROR: Google credentials file not found at {credentials_path}")
            return False
        
        print(f"Loading Google credentials from {credentials_path}...")
        credentials = Credentials.from_service_account_file(
            credentials_path,
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
        )
        
        client = gspread.authorize(credentials)
        
        print("Retrieving spreadsheets...")
        spreadsheets = client.list_spreadsheet_files()
        
        print(f"✅ SUCCESS: Successfully connected to Google Drive!")
        print(f"Found {len(spreadsheets)} accessible spreadsheets.")
        return True
    except Exception as e:
        print(f"❌ ERROR: Failed to connect to Google Drive: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Test connections for WB Analytics')
    parser.add_argument('--service', choices=['supabase', 'google', 'all'], default='all',
                        help='Service to test (supabase, google, or all)')
    
    args = parser.parse_args()
    
    success = True
    
    if args.service in ['supabase', 'all']:
        print("\n=== Testing Supabase Connection ===")
        if not test_supabase():
            success = False
    
    if args.service in ['google', 'all']:
        print("\n=== Testing Google Drive Connection ===")
        if not test_google_drive():
            success = False
    
    print("\n=== Test Results ===")
    if success:
        print("✅ All tested connections are working!")
        return 0
    else:
        print("❌ Some connections failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 