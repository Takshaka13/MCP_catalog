import os
from datetime import datetime, UTC
import requests
from supabase import create_client

# Supabase configuration
SUPABASE_URL = "https://haumvquzezekwkhqsqnc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhhdW12cXV6ZXpla3draHFzcW5jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NzI4ODgzMiwiZXhwIjoyMDYyODY0ODMyfQ.MeCXNDTBP1uBh-GDZhfQIct9wuv5PKdVj9TRzwT_1zw"

print("Initializing Supabase client...")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_exchange_rates() -> dict:
    """Fetch exchange rates from the API."""
    print("Fetching exchange rates...")
    response = requests.get("https://open.er-api.com/v6/latest/USD")
    response.raise_for_status()
    data = response.json()
    
    if not data or "rates" not in data:
        raise ValueError("Invalid API response format")
    
    # Filter only the currencies we want
    target_currencies = ["EUR", "THB", "RUB"]
    return {curr: rate for curr, rate in data["rates"].items() 
            if curr in target_currencies}

def update_fx_rates(rates: dict) -> list:
    """Update FX rates in database."""
    updates = []
    
    for quote, rate in rates.items():
        print(f"Updating {quote} rate: {rate}")
        try:
            data = {
                "base": "USD",
                "quote": quote,
                "rate": float(rate),
                "fetched_at": datetime.now(UTC).isoformat()
            }
            
            # Try to insert first
            print(f"Attempting to update {quote}...")
            result = supabase.table("fx_rates").insert(data).execute()
            print(f"Insert result for {quote}:", result)
            
            if hasattr(result, "data"):
                updates.append(quote)
                print(f"Successfully inserted {quote}")
            elif hasattr(result, "error"):
                # If insert fails due to conflict, try update
                print(f"Insert failed for {quote}, trying update...")
                result = supabase.table("fx_rates")\
                    .update({"rate": float(rate), "fetched_at": datetime.now(UTC).isoformat()})\
                    .eq("base", "USD")\
                    .eq("quote", quote)\
                    .execute()
                print(f"Update result for {quote}:", result)
                
                if hasattr(result, "data"):
                    updates.append(quote)
                    print(f"Successfully updated {quote}")
                else:
                    print(f"Failed to update {quote}")
            
        except Exception as e:
            print(f"Error updating {quote}: {str(e)}")
            print(f"Error type: {type(e)}")
            if hasattr(e, "__dict__"):
                print(f"Error attributes: {e.__dict__}")
    
    return updates

def main():
    try:
        # Test database connection
        print("Testing database connection...")
        test = supabase.table("fx_rates").select("*").limit(1).execute()
        print("Database connection test result:", test)
        
        # Fetch and update rates
        rates = fetch_exchange_rates()
        print(f"Fetched rates: {rates}")
        
        updated_currencies = update_fx_rates(rates)
        
        print(f"\nSummary:")
        print(f"Updated rates for: {', '.join(updated_currencies)}")
        print(f"Total updates: {len(updated_currencies)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e)}")
        if hasattr(e, "__dict__"):
            print(f"Error attributes: {e.__dict__}")
        raise

if __name__ == "__main__":
    main() 