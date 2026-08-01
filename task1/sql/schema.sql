-- Database schema for company data
-- Run this after PostgreSQL is up

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    category VARCHAR(200) NOT NULL,
    city VARCHAR(200) NOT NULL,
    address VARCHAR(500),
    rating NUMERIC(3,1),
    reviews_count INTEGER DEFAULT 0,
    site VARCHAR(500),
    phone VARCHAR(100),
    source VARCHAR(50) NOT NULL DEFAULT 'json',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_companies_category ON companies(category);
CREATE INDEX IF NOT EXISTS idx_companies_city ON companies(city);
CREATE INDEX IF NOT EXISTS idx_companies_rating ON companies(rating);
CREATE INDEX IF NOT EXISTS idx_companies_reviews_count ON companies(reviews_count);
CREATE INDEX IF NOT EXISTS idx_companies_site ON companies(site) WHERE site IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_companies_category_city ON companies(category, city);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_companies_updated_at ON companies;
CREATE TRIGGER update_companies_updated_at
    BEFORE UPDATE ON companies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- View for companies with website
CREATE OR REPLACE VIEW companies_with_site AS
SELECT * FROM companies WHERE site IS NOT NULL AND site != '' AND site != 'нет сайта';