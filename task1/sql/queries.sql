-- Query 1: Топ-5 категорий по числу компаний
SELECT 
    category,
    COUNT(*) as company_count
FROM companies
GROUP BY category
ORDER BY company_count DESC
LIMIT 5;

-- Query 2: Средний рейтинг по городам среди компаний с 10+ отзывами
SELECT 
    city,
    ROUND(AVG(rating)::numeric, 2) as avg_rating,
    COUNT(*) as company_count
FROM companies
WHERE reviews_count >= 10 
  AND rating IS NOT NULL
GROUP BY city
ORDER BY avg_rating DESC;

-- Query 3: Доля компаний с сайтом по категориям
SELECT 
    category,
    COUNT(*) as total_companies,
    COUNT(site) as companies_with_site,
    ROUND(COUNT(site)::numeric / COUNT(*) * 100, 2) as site_percentage
FROM companies
GROUP BY category
ORDER BY site_percentage DESC;