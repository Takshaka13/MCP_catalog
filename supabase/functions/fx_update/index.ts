// supabase/functions/fx_update/index.ts
// Follow this pattern to schedule Edge Functions:
// https://supabase.com/docs/guides/functions/schedule-functions

// Schedule function to run at 05:00 UTC every day
// cron: 0 5 * * *

import { serve } from "https://deno.land/std/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

serve(async (req) => {
  try {
    // Check if the request is a scheduled invocation
    const authHeader = req.headers.get('Authorization');
    if (!authHeader) {
      return new Response(JSON.stringify({
        error: 'No authorization header'
      }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const supabase = createClient(
      Deno.env.get("SUPABASE_URL") ?? "",
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "",  // Using service role key for admin access
      {
        auth: {
          autoRefreshToken: false,
          persistSession: false
        }
      }
    );

    // Check if environment variables are set
    if (!Deno.env.get("SUPABASE_URL") || !Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")) {
      throw new Error("Missing Supabase environment variables");
    }

    // Get current date in YYYY-MM-DD format (UTC)
    const today = new Date().toISOString().split('T')[0];
    
    // Check if we already have rates for today
    const { data: existingRates } = await supabase
      .from("fx_rates")
      .select("fetched_at")
      .gte("fetched_at", `${today}T00:00:00Z`)
      .lt("fetched_at", `${today}T23:59:59Z`)
      .limit(1);

    if (existingRates && existingRates.length > 0) {
      console.log("Rates for today already exist, skipping update");
      return new Response(
        JSON.stringify({
          success: true,
          message: "Rates for today already exist",
          skipped: true,
          date: today
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        },
      );
    }

    console.log("Fetching exchange rates...");
    const res = await fetch(
      "https://open.er-api.com/v6/latest/USD"
    );

    if (!res.ok) {
      throw new Error(`API request failed with status ${res.status}`);
    }

    const data = await res.json();
    console.log("API Response:", JSON.stringify(data, null, 2));
    
    if (!data || !data.rates) {
      console.error("Received data:", data);
      throw new Error("Invalid API response format");
    }

    // Filter only the currencies we want
    const targetCurrencies = ["EUR", "THB", "RUB"];
    const rates = Object.fromEntries(
      Object.entries(data.rates).filter(([currency]) => targetCurrencies.includes(currency))
    );

    console.log("Processing rates:", rates);
    const updates = [];
    const timestamp = new Date().toISOString();

    // Insert new rows for each currency pair
    for (const [quote, rate] of Object.entries(rates)) {
      console.log(`Inserting new rate for ${quote}:`, rate);
      const insert = await supabase
        .from("fx_rates")
        .insert({
          base: "USD",
          quote,
          rate: Number(rate),
          fetched_at: timestamp,
        });
      
      if (insert.error) {
        console.error(`Error inserting ${quote}: ${insert.error.message}`);
      } else {
        updates.push(quote);
      }
    }

    return new Response(
      JSON.stringify({
        success: true,
        message: `Inserted new rates for: ${updates.join(", ")}`,
        count: updates.length,
        timestamp,
        scheduled: true
      }),
      {
        status: 200,
        headers: { "Content-Type": "application/json" },
      },
    );

  } catch (error) {
    console.error("Error:", error.message);
    return new Response(
      JSON.stringify({
        success: false,
        error: error.message,
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      },
    );
  }
});
