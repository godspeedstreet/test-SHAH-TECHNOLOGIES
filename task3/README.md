
# Задание 3 — Данные с сюрпризом

Загрузка «свежей выгрузки» `review.csv` (205 записей) в staging-таблицу PostgreSQL **с валидацией**, плюс отчёт по аномалиям в данных.

## Файлы

| Файл | Назначение |
|------|-----------|
| `scripts/load_review_csv.py` | Скрипт: читает CSV, валидирует поля, грузит в staging-таблицу с флагами проблем |
| `ANOMALIES.md` | Подробный список всех 111 найденных аномалий (что именно, как обнаружено) |
| `REVIEW_REPORT.md` | Краткий итоговый отчёт по данным |

## Требования

- PostgreSQL из задачи 1 (контейнер `outreach-postgres`, БД `outreach`)
- Python 3 + `psycopg2-binary`

## Запуск

### 1. Подними базу

В папке `task1/`:
```bash
cd task1
docker-compose up -d
```

### 2. Установи зависимости Python

```bash
pip install psycopg2-binary
```

### 3. Запусти скрипт

Из корня проекта (где лежит `data_pack/`):
```bash
python scripts/load_review_csv.py
```

Скрипт:
1. Читает `data_pack/review.csv`
2. Валидирует каждое поле (рейтинг, отзывы, сайт, телефон, город)
3. Выводит консольный отчёт по статусам валидации
4. Создаёт таблицу `companies_csv_staging` (если нет)
5. Загружает 205 записей с JSON-флагом `validation_flags` по каждой проблеме

> ⚠️ Данные попадают **только в staging** (`companies_csv_staging`), основная таблица `companies` **не изменяется** — это сделано намеренно, чтобы не затирать «хорошие» данные JSON грязным CSV.

## Как смотреть аномалии в БД

```powershell
docker exec -i outreach-postgres psql -U outreach -d outreach -c "SELECT validation_flags->>'rating' as rating_status, COUNT(*) FROM companies_csv_staging GROUP BY 1 ORDER BY 2 DESC;"
```

Все записи с проблемами по полю `rating`:
```powershell
docker exec -i outreach-postgres psql -U outreach -d outreach -c "SELECT id, raw_rating, validation_flags FROM companies_csv_staging WHERE validation_flags->>'rating' != 'ok';"
```

## Что найдено (кратко)

- **181 / 202** записей полностью валидны
- **21** проблемный рейтинг: 19 пустых/`N/A`, 1 отрицательный (`-3`), 1 зашкаливающий (`7.2`)
- **3** проблемы с отзывами: `-10`, `45.5` (дробное), `много`
- **5** битовых городов (mojibake, `Moscow`, `москва`, опечатка «Санкат-Петербург»)
- **3** дубликата ID внутри CSV (c_001049, c_001050, c_001075)
- **Смещение колонок** у 4 записей (пустой `rating` сдвигает данные влево)
- Подробности — в `ANOMALIES.md`


