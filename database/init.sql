CREATE TABLE IF NOT EXISTS website (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS asset_crawl (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    is_asset BOOLEAN DEFAULT FALSE,
    website_id INTEGER REFERENCES website (id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_website_url ON website (url);

CREATE INDEX IF NOT EXISTS idx_asset_crawl_url ON asset_crawl (url);

CREATE INDEX IF NOT EXISTS idx_asset_crawl_website_id ON asset_crawl (website_id);