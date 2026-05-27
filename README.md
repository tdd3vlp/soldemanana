# 🇪🇸 Habla Bot — Telegram-бот для изучения испанского языка

MVP-версия бота для практики испанского языка (испанский Испании) для русскоязычных пользователей.

## 🚀 Возможности

### Реализовано в MVP:
- ✅ **Onboarding**: выбор уровня (A0-C1), цели изучения, режима исправлений
- ✅ **Свободный разговор**: диалог с ботом на испанском, автоисправление ошибок с объяснением на русском
- ✅ **Исправление фразы**: детальный анализ одиночной фразы
- ✅ **Ситуации в Испании**: ролевые игры (ресторан, аптека, мэрия, врач, и т.д.)
- ✅ **Грамматика**: объяснение тем + упражнения (Ser/Estar, времена, subjuntivo, и др.)
- ✅ **Лимиты сообщений**: Free (10/день), Basic (50/день), Pro (безлимит)
- ✅ **Настройки**: смена уровня, цели, интенсивности исправлений
- ✅ **Админ-команды**: статистика пользователей

### В планах (не реализовано):
- ⏳ Платежи (Telegram Stars / Stripe)
- ⏳ Голосовые сообщения через Whisper API (для Pro подписчиков)
- ⏳ Личный словарь с экспортом (платная функция)
- ⏳ Детальная статистика прогресса

## 📦 Стек технологий

- **Python 3.11+**
- **aiogram 3.x** — Telegram Bot API
- **OpenAI API (GPT-4o)** — языковая модель для диалогов и исправлений
- **PostgreSQL 16** — хранение пользователей, сообщений, ошибок
- **SQLAlchemy 2.x + Alembic** — ORM и миграции
- **Redis** — FSM states, rate limiting, кэш
- **FastAPI** — API для webhook (опционально)
- **Docker Compose** — запуск всей инфраструктуры

## 🛠️ Установка и запуск

### Требования:
- Docker и Docker Compose
- OpenAI API ключ (https://platform.openai.com)
- Telegram Bot Token (через @BotFather)

### 1. Клонирование репозитория

```bash
cd /path/to/habla_bot
```

### 2. Настройка окружения

Скопируй `.env.example` в `.env`:

```bash
cp .env.example .env
```

Отредактируй `.env`:

```env
BOT_TOKEN=your_telegram_bot_token
ADMIN_IDS=123456789

OPENAI_API_KEY=sk-...your_openai_key
OPENAI_MODEL=gpt-4o

DATABASE_URL=postgresql+asyncpg://habla:habla_password@postgres:5432/habla_db
REDIS_URL=redis://redis:6379/0
```

### 3. Запуск через Docker Compose

```bash
docker-compose up -d
```

Это запустит:
- PostgreSQL (порт 5432)
- Redis (порт 6379)
- Бот (в фоне)

### 4. Применение миграций базы данных

После запуска контейнеров:

```bash
docker-compose exec bot alembic upgrade head
```

Если команда не сработала, выполни миграции вручную:

```bash
docker-compose exec bot python -c "
from alembic.config import Config
from alembic import command
alembic_cfg = Config('alembic.ini')
command.upgrade(alembic_cfg, 'head')
"
```

### 5. Проверка логов

```bash
docker-compose logs -f bot
```

### 6. Остановка

```bash
docker-compose down
```

## 🧪 Локальная разработка (без Docker)

### 1. Установка зависимостей через Poetry

```bash
poetry install
```

### 2. Запуск PostgreSQL и Redis локально

```bash
# PostgreSQL
docker run -d -p 5432:5432 -e POSTGRES_USER=habla -e POSTGRES_PASSWORD=habla_password -e POSTGRES_DB=habla_db postgres:16-alpine

# Redis
docker run -d -p 6379:6379 redis:7-alpine
```

### 3. Применение миграций

```bash
poetry run alembic upgrade head
```

### 4. Запуск бота

```bash
poetry run python -m app.main
```

## 📚 Структура проекта

```
habla_bot/
├── app/
│   ├── main.py                 # Точка входа
│   ├── config.py               # Конфигурация (pydantic-settings)
│   ├── core/
│   │   ├── models/             # SQLAlchemy модели
│   │   ├── schemas/            # Pydantic схемы
│   │   ├── enums.py            # Enum классы
│   │   └── constants.py        # Константы
│   ├── infrastructure/
│   │   ├── database/           # Работа с БД
│   │   ├── redis/              # Redis клиент
│   │   ├── llm/                # OpenAI клиент + промпты
│   │   └── voice/              # Заготовка для голосовых
│   ├── services/               # Бизнес-логика
│   ├── bot/
│   │   ├── handlers/           # Обработчики команд
│   │   ├── keyboards/          # Клавиатуры
│   │   ├── middlewares/        # Middleware
│   │   ├── filters/            # Фильтры
│   │   ├── states.py           # FSM состояния
│   │   └── dispatcher.py       # Настройка dispatcher
│   └── api/                    # FastAPI (опционально)
├── alembic/                    # Миграции БД
├── docker/                     # Dockerfiles
├── docker-compose.yml
├── pyproject.toml
├── .env.example
└── README.md
```

## 🎯 Использование бота

### Команды:
- `/start` — начать работу / пройти онбординг
- `/admin` — админ-панель (только для ADMIN_IDS)

### Режимы работы:
1. **🗣️ Свободный разговор** — пиши на испанском, бот отвечает и исправляет
2. **✏️ Исправить фразу** — отправь фразу для детального разбора
3. **🎭 Ситуации в Испании** — ролевая игра (выбери сцену)
4. **📚 Грамматика** — выбери тему и делай упражнения
5. **⚙️ Настройки** — измени уровень, цель, режим исправлений

### Настройки интенсивности исправлений:
- **Исправлять всё** — каждая ошибка, даже мелкая
- **Только важные** — грамматические и смысловые ошибки (по умолчанию)
- **Не исправлять** — режим обычного разговора

## 🔧 Разработка

### Создание новой миграции

```bash
poetry run alembic revision --autogenerate -m "description"
```

### Применение миграций

```bash
poetry run alembic upgrade head
```

### Откат миграций

```bash
poetry run alembic downgrade -1
```

### Линтинг

```bash
poetry run ruff check app/
```

### Форматирование

```bash
poetry run ruff format app/
```

## 🐛 Troubleshooting

### Бот не запускается
1. Проверь `.env` — все ли переменные заполнены
2. Проверь логи: `docker-compose logs bot`
3. Проверь, что PostgreSQL и Redis запущены: `docker-compose ps`

### Ошибка миграций
```bash
# Сброс БД (осторожно, удалит все данные!)
docker-compose down -v
docker-compose up -d
docker-compose exec bot alembic upgrade head
```

### OpenAI API ошибки
- Проверь ключ API
- Проверь баланс на https://platform.openai.com
- Убедись что выбрана модель `gpt-4o` или `gpt-4o-mini`

## 📝 TODO для продакшн-версии

- [ ] Реализовать платежи (Telegram Stars)
- [ ] Добавить голосовые сообщения (Whisper API)
- [ ] Реализовать личный словарь с сохранением слов
- [ ] Добавить экспорт диалогов и словаря
- [ ] Webhook режим вместо polling
- [ ] Мониторинг (Prometheus + Grafana)
- [ ] CI/CD pipeline
- [ ] Тесты (unit + integration)
- [ ] Backup БД

## 📄 Лицензия

MIT

---

**Made with ❤️ for Spanish learners**
