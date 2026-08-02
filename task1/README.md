# Задание 1 - Выгрузка → Postgres

Загрузка данных компаний из JSON и CSV в PostgreSQL с дедупликацией.

## Структура проекта

```
├── docker-compose.yml          # PostgreSQL в Docker
├── sql/
│   ├── schema.sql              # Схема БД + индексы
│   └── queries.sql             # 3 аналитических запроса
├── scripts/
│   └── load_data.py            # Скрипт загрузки данных
└── data_pack/                  # Исходные данные (page_001.json...page_020.json + review.csv)
```

## Быстрый запуск

### 1. Запуск PostgreSQL
```bash
docker-compose up -d
```

### 2. Установка зависимостей Python
```bash
pip install psycopg2-binary
```

### 3. Загрузка данных
```bash
python scripts/load_data.py
```

### 4. Выполнение аналитических запросов
```bash
docker exec -i outreach-postgres psql -U outreach -d outreach -f /sql/queries.sql
```

Или через любой SQL-клиент (DBeaver, pgAdmin, DataGrip) - подключитесь к `localhost:5432`, БД `outreach`, пользователь `outreach`, пароль `outreach`.

## Что делает скрипт загрузки

1. **Читает все 20 JSON файлов** (`page_001.json` … `page_020.json`)
2. **Читает `review.csv`** (дополнительные ~200 записей)
3. **Очищает данные**:
   - Рейтинг: приводит `4,5` → `4.5`, `N/A` → `NULL`
   - Отзывы: `много` → `1000`, отрицательные → `0`
   - Сайты: убирает `нет сайта`, нормализует URL
4. **Дедуплицирует по `id`** — приоритет JSON данным
5. **Upsert в PostgreSQL** — вставляет новые, обновляет существующие

## Схема БД

Таблица `companies`:
- `id` (PK) — уникальный идентификатор
- `name` — название
- `category` — категория
- `city` — город
- `address` — адрес
- `rating` — рейтинг (numeric)
- `reviews_count` — кол-во отзывов
- `site` — сайт
- `phone` — телефон
- `source` — источник (`json` или `csv`)

**Индексы** для производительности запросов:
- `idx_companies_category`
- `idx_companies_city`
- `idx_companies_rating`
- `idx_companies_reviews_count`
- `idx_companies_site` (partial, только где site IS NOT NULL)
- `idx_companies_category_city` (composite)

## Аналитические запросы (queries.sql)

1. **Топ-5 категорий по числу компаний**
2. **Средний рейтинг по городам** (только компании с 10+ отзывами)
3. **Доля компаний с сайтом по категориям** (в %)

## Проверка результатов

```sql
-- Всего компаний
SELECT COUNT(*) FROM companies;

-- По источникам
SELECT source, COUNT(*) FROM companies GROUP BY source;

-- Пример топ-5 категорий
SELECT category, COUNT(*) as cnt FROM companies GROUP BY category ORDER BY cnt DESC LIMIT 5;
```

## Остановка

```bash
docker-compose down
# С сохранением данных:
docker-compose down -v  # удалит volume с данными
```
