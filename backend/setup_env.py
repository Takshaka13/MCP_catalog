#!/usr/bin/env python3
import os
import argparse

def setup_environment():
    """Set up environment variables for the application."""
    parser = argparse.ArgumentParser(description='Setup environment variables for WB Analytics')
    parser.add_argument('--supabase-url', required=True, help='Supabase URL')
    parser.add_argument('--supabase-key', required=True, help='Supabase service role key')
    parser.add_argument('--google-creds', required=True, help='Path to Google credentials JSON file')
    
    args = parser.parse_args()
    
    # Create credentials directory if it doesn't exist
    os.makedirs('credentials', exist_ok=True)
    
    # Update .env file
    with open('.env', 'w') as f:
        f.write(f"# Supabase Configuration\n")
        f.write(f"SUPABASE_URL={args.supabase_url}\n")
        f.write(f"SUPABASE_SERVICE_ROLE_KEY={args.supabase_key}\n\n")
        f.write(f"# Google Drive Configuration\n")
        f.write(f"GOOGLE_APPLICATION_CREDENTIALS={args.google_creds}\n")
    
    print("Environment variables have been set up successfully.")
    print("Make sure your Google credentials JSON file is in the specified location.")

if __name__ == "__main__":
    setup_environment() 