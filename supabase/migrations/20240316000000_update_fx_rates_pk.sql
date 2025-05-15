-- Drop existing primary key constraint if it exists
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM pg_constraint 
        WHERE conname = 'fx_rates_pkey'
    ) THEN
        ALTER TABLE public.fx_rates DROP CONSTRAINT fx_rates_pkey;
    END IF;
END $$;

-- Add new primary key that includes fetched_at
ALTER TABLE public.fx_rates 
    ADD PRIMARY KEY (base, quote, fetched_at);

-- Add index for efficient querying of latest rates if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE indexname = 'idx_fx_rates_latest'
    ) THEN
        CREATE INDEX idx_fx_rates_latest ON public.fx_rates (base, quote, fetched_at DESC);
    END IF;
END $$;

-- Add table comment
COMMENT ON TABLE public.fx_rates IS 'Historical foreign exchange rates with timestamps'; 