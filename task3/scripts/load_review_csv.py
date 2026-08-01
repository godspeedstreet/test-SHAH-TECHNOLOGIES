#!/usr/bin/env python3
"""
Отдельный скрипт загрузки review.csv с валидацией и отчётом.
Не загружает в основную таблицу companies — пишет в staging-таблицу для анализа.
"""

import csv
import psycopg2
from psycopg2.extras import execute_values, Json
import os
import sys
from pathlib import Path
from collections import Counter
import json

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'outreach'),
    'user': os.getenv('DB_USER', 'outreach'),
    'password': os.getenv('DB_PASSWORD', 'outreach')
}

CSV_PATH = Path(__file__).parent.parent / 'data_pack' / 'review.csv'

def clean_rating(val):
    if val is None or val == '' or val.upper() == 'N/A':
        return None, 'empty_or_na'
    val = val.strip().replace(',', '.').strip('"')
    try:
        f = float(val)
        if f < 0 or f > 5:
            return None, f'out_of_range_{f}'
        return f, 'ok'
    except ValueError:
        return None, f'not_a_number_{val}'

def clean_reviews(val):
    if val is None or val == '':
        return 0, 'empty'
    val = val.strip().lower()
    if val == 'много':
        return 1000, 'mnog'
    try:
        f = float(val)
        if f < 0:
            return 0, f'negative_{f}'
        if f != int(f):
            return int(round(f)), f'fractional_{f}'
        return int(f), 'ok'
    except ValueError:
        return 0, f'not_a_number_{val}'

def clean_site(val):
    if not val or val.strip() in ('', 'нет сайта', 'null'):
        return None, 'empty'
    val = val.strip()
    if val == 'https://,':
        return None, 'broken_trailing_comma'
    if val.startswith('htp://'):
        val = 'http' + val[3:]
        return val, 'fixed_htp'
    if not (val.startswith('http://') or val.startswith('https://')):
        if val.startswith('www.'):
            val = 'https://' + val
            return val, 'added_https'
        return None, f'no_protocol_{val}'
    return val, 'ok'

def clean_phone(val):
    if not val or val.strip() in ('', 'null'):
        return None, 'empty'
    val = val.strip()
    if 'abc' in val.lower():
        return None, 'contains_letters'
    if val == '+7':
        return None, 'incomplete'
    return val, 'ok'

def clean_city(val):
    if not val or val.strip() == '':
        return None, 'empty'
    val = val.strip()
    # Fix mojibake
    fixes = {
        'РњРѕСЃРєРІР°': 'Москва',
        'РЎР°РЅРєС‚-РџРµС‚РµСЂР±СѓСЂРі': 'Санкт-Петербург',
        'Санкат-Петербург': 'Санкт-Петербург',
        'Moscow': 'Москва',
        'москва': 'Москва',
    }
    if val in fixes:
        return fixes[val], f'fixed_{val}'
    return val, 'ok'

def analyze_csv():
    print(f"Reading {CSV_PATH}...")
    rows = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('id') or row['id'].strip() == '':
                continue
            rows.append(row)
    
    print(f"Total data rows: {len(rows)}")
    
    # Stats
    stats = {
        'rating': Counter(),
        'reviews': Counter(),
        'site': Counter(),
        'phone': Counter(),
        'city': Counter(),
    }
    anomalies = []
    duplicates = Counter()
    
    for row in rows:
        cid = row['id'].strip()
        duplicates[cid] += 1
        
        _, r_status = clean_rating(row.get('rating'))
        stats['rating'][r_status] += 1
        if r_status != 'ok':
            anomalies.append(f"{cid}: rating={row.get('rating')} -> {r_status}")
        
        _, rv_status = clean_reviews(row.get('reviews_count'))
        stats['reviews'][rv_status] += 1
        if rv_status != 'ok':
            anomalies.append(f"{cid}: reviews={row.get('reviews_count')} -> {rv_status}")
        
        _, s_status = clean_site(row.get('site'))
        stats['site'][s_status] += 1
        if s_status != 'ok':
            anomalies.append(f"{cid}: site={row.get('site')} -> {s_status}")
        
        _, p_status = clean_phone(row.get('phone'))
        stats['phone'][p_status] += 1
        if p_status != 'ok':
            anomalies.append(f"{cid}: phone={row.get('phone')} -> {p_status}")
        
        _, c_status = clean_city(row.get('city'))
        stats['city'][c_status] += 1
        if c_status != 'ok':
            anomalies.append(f"{cid}: city={row.get('city')} -> {c_status}")
    
    # Duplicate IDs
    dup_ids = {k: v for k, v in duplicates.items() if v > 1}
    
    # Print report
    print("\n=== VALIDATION REPORT ===")
    print(f"\nTotal rows: {len(rows)}")
    print(f"Unique IDs: {len(duplicates)}")
    print(f"Duplicate IDs: {len(dup_ids)}")
    for k, v in sorted(dup_ids.items()):
        print(f"  {k}: {v} times")
    
    for field, counter in stats.items():
        print(f"\n{field.upper()}:")
        for status, count in counter.most_common():
            print(f"  {status}: {count}")
    
    print(f"\nANOMALIES FOUND: {len(anomalies)}")
    for a in anomalies[:50]:
        print(f"  {a}")
    if len(anomalies) > 50:
        print(f"  ... and {len(anomalies) - 50} more")
    
    return rows, anomalies, stats, dup_ids

def create_staging_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS companies_csv_staging (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(500),
                category VARCHAR(200),
                city VARCHAR(200),
                address VARCHAR(500),
                rating NUMERIC(3,1),
                reviews_count INTEGER,
                site VARCHAR(500),
                phone VARCHAR(100),
                raw_rating VARCHAR(50),
                raw_reviews VARCHAR(50),
                raw_site VARCHAR(500),
                raw_phone VARCHAR(100),
                raw_city VARCHAR(200),
                validation_flags JSONB,
                loaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    print("Staging table ready")

def load_to_staging(conn, rows):
    data = []
    for row in rows:
        cid = row['id'].strip()
        
        rating, r_status = clean_rating(row.get('rating'))
        reviews, rv_status = clean_reviews(row.get('reviews_count'))
        site, s_status = clean_site(row.get('site'))
        phone, p_status = clean_phone(row.get('phone'))
        city, c_status = clean_city(row.get('city'))
        
        flags = {
            'rating': r_status,
            'reviews': rv_status,
            'site': s_status,
            'phone': p_status,
            'city': c_status,
        }
        
        data.append((
            cid,
            row.get('name', '').strip(),
            row.get('category', '').strip(),
            city,
            row.get('address', '').strip() if row.get('address') else None,
            rating,
            reviews,
            site,
            phone,
            row.get('rating', '').strip(),
            row.get('reviews_count', '').strip(),
            row.get('site', '').strip(),
            row.get('phone', '').strip(),
            row.get('city', '').strip(),
            Json(flags)
        ))
    
    with conn.cursor() as cur:
        execute_values(cur, """
            INSERT INTO companies_csv_staging 
            (id, name, category, city, address, rating, reviews_count, site, phone,
             raw_rating, raw_reviews, raw_site, raw_phone, raw_city, validation_flags)
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
                raw_rating = EXCLUDED.raw_rating,
                raw_reviews = EXCLUDED.raw_reviews,
                raw_site = EXCLUDED.raw_site,
                raw_phone = EXCLUDED.raw_phone,
                raw_city = EXCLUDED.raw_city,
                validation_flags = EXCLUDED.validation_flags,
                loaded_at = CURRENT_TIMESTAMP
        """, data, page_size=100)
        conn.commit()
    print(f"Loaded {len(data)} rows to staging")

def main():
    print("=" * 60)
    print("REVIEW.CSV LOADER WITH VALIDATION")
    print("=" * 60)
    
    rows, anomalies, stats, dup_ids = analyze_csv()
    
    print("\nConnecting to DB...")
    conn = psycopg2.connect(**DB_CONFIG)
    
    create_staging_table(conn)
    load_to_staging(conn, rows)
    
    conn.close()
    print("\nDone. Check ANOMALIES.md for details.")
    print("Staging table: companies_csv_staging")

if __name__ == '__main__':
    main()