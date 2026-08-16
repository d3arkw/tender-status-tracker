# Tender Status Tracker

Backend-сервис для отслеживания статусов тендеров: создание тендера, смена статуса с валидацией переходов и полным журналом изменений.

## Стек

- Python 3.13, FastAPI, SQLAlchemy 2.0 (async), Alembic, asyncpg
- PostgreSQL, Redis (кэш)
- Docker, Docker Compose
- GitHub Actions (CI)
- uv, pytest, flake8, black

## Возможности

- Создание тендера (статус по умолчанию — черновик)
- Смена статуса: `draft → active → won | lost` с проверкой допустимых переходов
- Журнал изменений статуса: кто, когда и почему изменил
- Кэширование чтения через Redis (cache-aside, TTL 300 сек)

## Архитектура

Проект разделён на слои:

```
app/
├── api/       — HTTP-слой: роутеры и обработка ошибок
├── services/  — бизнес-логика: машина состояний, работа с БД и кэшем
├── models/    — ORM-модели (SQLAlchemy 2.0)
├── schemas/   — Pydantic-схемы валидации
├── database/  — engine, сессии
└── core/      — конфигурация, Redis-клиент
```

## Логика решения

### Машина состояний

Допустимые переходы заданы таблицей:

| Из | В |
|----|---|
| draft | active |
| active | won, lost |
| won | — |
| lost | — |

Невалидный переход возвращает `400 Bad Request`.

### Смена статуса

1. Тендер загружается из БД (иначе — `404`).
2. Проверяется допустимость перехода.
3. В одной транзакции: создаётся запись в `tender_status_history` (old_status, new_status, changed_by, reason) и обновляется статус.
4. Кэш тендера инвалидируется (Redis), чтобы следующий GET не вернул устаревшие данные.

### Чтение (cache-aside)

1. Сначала запрос в Redis.
2. Если ключа нет — чтение из PostgreSQL, результат кладётся в кэш с TTL 300 сек.

## Запуск локально

```bash
uv sync
cp .env.example .env
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

Нужны запущенные PostgreSQL и Redis (или `docker compose up db redis`).

## Запуск через Docker Compose

```bash
docker compose up --build
```

Поднимаются три контейнера:

| Сервис | Описание |
|--------|----------|
| app | FastAPI-приложение (порт 8000) |
| db | PostgreSQL 16 (порт 5433 наружу) |
| redis | Redis 7 (порт 6379) |

При старте контейнера app автоматически применяются миграции (`alembic upgrade head`).

## Эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| POST | /tenders | Создать тендер |
| GET | /tenders/{id} | Получить тендер |
| PATCH | /tenders/{id}/status | Сменить статус |
| GET | /tenders/{id}/history | История изменений |
| GET | /health | Проверка здоровья |

Пример смены статуса:

```bash
curl -X PATCH http://localhost:8000/tenders/1/status \
  -H "Content-Type: application/json" \
  -d '{"new_status": "active", "changed_by": "denis", "reason": "приступаем к работе"}'
```

## Тесты и линтеры

```bash
uv run pytest
uv run black --check app/ tests/
uv run flake8 app/ tests/
```

## CI

GitHub Actions проверяет код линтерами (flake8, black) и прогоняет тесты при каждом пуше.

## Лицензия

MIT
