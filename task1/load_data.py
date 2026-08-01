import json
import csv
import psycopg2
from psycopg2.extras import execute_values
import os
import sys
from pathlib import Path

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'outreach',
    'user': 'outreach',
    'password': 'outreach'
}

DATA_DIR = Path(__file__).parent.parent / 'data_pack'

def clean_rating(value):
    """Clean rating value - handle strings like '4,5' or 'N/A'"""
    if value is None or value == '' or value == 'N/A' or value == 'null':
        return None
    if isinstance(value, str):
        value = value.replace(',', '.').strip()
        if value == '':
            return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def clean_reviews_count(value):
    """Clean reviews_count - handle strings, negatives, 'много'"""
    if value is None or value == '' or value == 'N/A':
        return 0
    if isinstance(value, str):
        value = value.strip()
        if value.lower() in ('много', 'много отзывов'):
            return 1000
        if value == '':
            return 0
    try:
        val = int(float(value))
        return max(0, val)  # No negative reviews
    except (ValueError, TypeError):
        return 0

def clean_site(value):
    """Clean site URL"""
    if value is None or value == '' or value == 'нет сайта' or value == 'null':
        return None
    value = value.strip()
    if value.startswith('http://') or value.startswith('https://'):
        return value
    if value.startswith('www.'):
        return 'https://' + value
    return None

def clean_phone(value):
    """Clean phone number"""
    if value is None or value == '' or value == 'null':
        return None
    return value.strip()

def load_json_files():
    """Load all JSON page files"""
    companies = []
    for page_num in range(1, 21):
        file_path = DATA_DIR / f'page_{page_num:03d}.json'
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data.get('items', []):
                    companies.append({
                        'id': item.get('id'),
                        'name': item.get('name', '').strip(),
                        'category': item.get('category', '').strip(),
                        'city': item.get('city', '').strip(),
                        'address': item.get('address', '').strip() if item.get('address') else None,
                        'rating': clean_rating(item.get('rating')),
                        'reviews_count': clean_reviews_count(item.get('reviews_count')),
                        'site': clean_site(item.get('site')),
                        'phone': clean_phone(item.get('phone')),
                        'source': 'json'
                    })
    return companies

def load_csv_file():
    """Load review.csv"""
    companies = []
    file_path = DATA_DIR / 'review.csv'
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get('id') or row.get('id', '').strip() == '':
                    continue
                companies.append({
                    'id': row.get('id', '').strip(),
                    'name': row.get('name', '').strip(),
                    'category': row.get('category', '').strip(),
                    'city': row.get('city', '').strip(),
                    'address': row.get('address', '').strip() if row.get('address') else None,
                    'rating': clean_rating(row.get('rating')),
                    'reviews_count': clean_reviews_count(row.get('reviews_count')),
                    'site': clean_site(row.get('site')),
                    'phone': clean_phone(row.get('phone')),
                    'source': 'csv'
                })
    return companies

def deduplicate_companies(companies):
    """Deduplicate by ID, preferring JSON data over CSV"""
    seen = {}
    for c in companies:
        cid = c['id']
        if cid not in seen:
            seen[cid] = c
        elif c['source'] == 'json' and seen[cid]['source'] == 'csv':
            # Prefer JSON data
            seen[cid] = c
    return list(seen.values())

def insert_companies(companies):
    """Insert companies into PostgreSQL with upsert"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    query = """
        INSERT INTO companies (id, name, category, city, address, rating, reviews_count, site, phone, source)
        VALUES %s
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            category = EXCLUDED.category,
            city = EXCLUDED.city,
            address = EXCLUDED.address,
            rating = EXCLUDED.rating,
            reviews_count = EXCLUDED.reviews_count,
            site = EXCLUDED.site,
            phone = EXCLUDED.phone,
            source = EXCLUDED.source,
            updated_at = CURRENT_TIMESTAMP
    """
    
    data = [
        (c['id'], c['name'], c['category'], c['city'], c['address'],
         c['rating'], c['reviews_count'], c['site'], c['phone'], c['source'])
        for c in companies
    ]
    
    execute_values(cursor, query, data, page_size=100)
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Inserted/updated {len(companies)} companies")

def main():
    print("Loading JSON files...")
    json_companies = load_json_files()
    print(f"Loaded {len(json_companies)} companies from JSON")
    
    print("Loading CSV file...")
    csv_companies = load_csv_file()
    print(f"Loaded {len(csv_companies)} companies from CSV")
    
    all_companies = json_companies + csv_companies
    print(f"Total before deduplication: {len(all_companies)}")
    
    unique_companies = deduplicate_companies(all_companies)
    print(f"After deduplication: {len(unique_companies)}")
    
    print("Inserting into database...")
    insert_companies(unique_companies)
    print("Done!")

if __name__ == '__main__':
    main()