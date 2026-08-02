
# Задание 2 — Мини-фича с доказательством работы

Веб-страница поверх базы из задачи 1: таблица компаний с **поиском по названию**, **фильтром по городу** и **пагинацией**. Данные тянутся серверно через Route Handler (`/api/companies`), секреты — только через `.env.local`, в репозитории — `.env.example`.

## Требования

- Node.js 18+ (проверка: `node --version`)
- PostgreSQL из задачи 1 (контейнер `outreach-postgres`, БД `outreach`) с загруженными данными (~1190 компаний)

## Установка и запуск

### 1. Подними базу (если ещё не запущена)

В папке `task1/`:
```bash
cd task1
docker-compose up -d
```

Убедись, что данные загружены (задача 1):
```bash
docker exec -i outreach-postgres psql -U outreach -d outreach -c "SELECT COUNT(*) FROM companies;"
```
Должно вернуть `1190`.

### 2. Установи зависимости

```bash
cd web
npm install
```

### 3. Создай .env.local

```bash
copy .env.example .env.local
```

### 4. Запусти dev-сервер

```bash
npm run dev
```

### 5. Открой в браузере

| URL | Что это |
|-----|---------|
| http://localhost:3000 | Главная страница со ссылкой |
| http://localhost:3000/companies | Таблица компаний (основная) |


## Возможности страницы /companies

- **Поиск** — по названию, регистронезависимо (`ILIKE`), с debounce 300 мс
- **Фильтр** — по городу (dropdown из `SELECT DISTINCT city`)
- **Пагинация** — по 50 записей, кнопки «Назад»/«Вперёд»
- **Счётчик** — «Найдено: N компаний»
- **Ссылки на сайты** — кликабельные, открываются в новой вкладке
- **Обработка NULL** — пустые рейтинги/сайты/телефоны отображаются как «—»

## Как это устроено

| Файл | Назначение |
|------|-----------|
| `src/app/companies/page.tsx` | Client Component — таблица, поиск, фильтр, пагинация |
| `src/app/api/companies/route.ts` | Route Handler — серверная выборка из PostgreSQL (LIMIT/OFFSET, ILIKE) |
| `src/app/api/cities/route.ts` | Route Handler — список городов |
| `src/lib/db.ts` | Пул подключений `pg` к PostgreSQL |
| `src/lib/types.ts` | TypeScript-интерфейсы |


# Как проверял

### Cкриншоты:

<img width="3107" height="1741" alt="prsc2" src="https://github.com/user-attachments/assets/56e14d6f-d963-4e58-af28-f211fe99c509" />
<img width="3101" height="1045" alt="prsc1" src="https://github.com/user-attachments/assets/1aa1fc15-78de-47a3-9285-faddb70fb63a" />
<img width="3105" height="1749" alt="prsc3" src="https://github.com/user-attachments/assets/ebdda651-94ed-4c72-82c3-265192c7fd3c" />


### Как проверял: 

При первом запуске возникла ошибка и страница не запускалась. Numeric из Postgres сериализировалась в JSON как строка "4.5", а не число. Number() решает это. После доработки страница открылась без ошибок. Из багов: не работали кнопки «Назад»/«Вперед» для перехода между страницами таблицы из-за того, что при смене страницы срабатывал эффект, который сбрасывал страницу на 1. 

После этих доработок страница работает без ошибок и крашей.


