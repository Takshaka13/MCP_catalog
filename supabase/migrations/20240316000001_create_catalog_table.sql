-- Create catalog table for property listings
create table if not exists public.catalog (
  id           uuid        primary key default gen_random_uuid(),
  developer    text        not null,
  project_name text        not null,
  room_type    text        not null,
  room_nymber  text        not null,
  block        text        not null,
  sq_m         text        not null,
  price_baht   numeric     not null,
  stock_qty    int         not null,
  updated_at   timestamptz not null default now()
);

-- Add indexes for common queries
CREATE INDEX if not exists idx_catalog_project ON public.catalog(developer, project_name);
CREATE INDEX if not exists idx_catalog_updated_at ON public.catalog(updated_at DESC);

-- Add row level security (RLS)
ALTER TABLE public.catalog ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Enable read access for all users" ON public.catalog
    FOR SELECT USING (true);

-- Only allow insert/update through authenticated service role
CREATE POLICY "Enable insert for service role only" ON public.catalog
    FOR INSERT WITH CHECK (
        auth.jwt() ->> 'role' = 'service_role'
    );

CREATE POLICY "Enable update for service role only" ON public.catalog
    FOR UPDATE USING (
        auth.jwt() ->> 'role' = 'service_role'
    ) WITH CHECK (
        auth.jwt() ->> 'role' = 'service_role'
    );

-- Add helpful comments
COMMENT ON TABLE public.catalog IS 'Property catalog with listings from various developers';
COMMENT ON COLUMN public.catalog.id IS 'Unique identifier for each listing';
COMMENT ON COLUMN public.catalog.developer IS 'Property developer name';
COMMENT ON COLUMN public.catalog.project_name IS 'Name of the development project';
COMMENT ON COLUMN public.catalog.room_type IS 'Type of room/unit';
COMMENT ON COLUMN public.catalog.room_nymber IS 'Room or unit number';
COMMENT ON COLUMN public.catalog.block IS 'Building/Block identifier';
COMMENT ON COLUMN public.catalog.sq_m IS 'Area in square meters';
COMMENT ON COLUMN public.catalog.price_baht IS 'Price in Thai Baht';
COMMENT ON COLUMN public.catalog.stock_qty IS 'Number of units available';
COMMENT ON COLUMN public.catalog.updated_at IS 'Last update timestamp'; 