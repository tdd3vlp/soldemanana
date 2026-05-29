# AGENTS.md — Руководство для AI-агентов

Этот файл содержит инструкции для AI-агентов, работающих с проектом Sol de Mañana.

## Архитектура проекта

Проект построен по принципам **Clean Architecture**:

1. **app/core/** — бизнес-логика, модели, константы (не зависит от внешних библиотек)
2. **app/infrastructure/** — внешние сервисы (БД, Redis, LLM API)
3. **app/services/** — сервисы с бизнес-логикой (используют infrastructure и core)
4. **app/bot/** — Telegram bot handlers, keyboards, middlewares (зависит от services)
5. **app/api/** — FastAPI endpoints (опционально, для webhook)

## Правила работы с кодом

### Модели данных (SQLAlchemy)

- Все модели наследуются от `app.core.models.base.Base`
- Используем `TimestampMixin` для `created_at` и `updated_at`
- Enum поля используют `SAEnum` из SQLAlchemy
- Foreign keys всегда с `ondelete` действием (`CASCADE` или `SET NULL`)

### Промпты для LLM

- Промпты находятся в `app/infrastructure/llm/prompts.py`
- Каждый режим (conversation, correction, scenarios, grammar) имеет свой system prompt
- Промпты учитывают уровень, цель, интенсивность исправлений пользователя
- OpenAI API используется с `response_format={"type": "json_object"}` для структурированных ответов

### Handlers (aiogram)

- Каждый режим имеет свой router в `app/bot/handlers/`
- FSM states определены в `app/bot/states.py`
- Middlewares: Database → User → Throttling (в таком порядке)
- Всегда проверяем `is_onboarded` перед основным функционалом
- Всегда проверяем лимиты через `LimitService`

### Services

- Все сервисы принимают `AsyncSession` в конструкторе
- Сервисы НЕ делают commit — это обязанность middleware
- UserService — работа с пользователями и сообщениями
- ConversationService, CorrectionService, ScenarioService, GrammarService — режимы работы
- LimitService — проверка дневных лимитов

### База данных

- Используется PostgreSQL с asyncpg драйвером
- Миграции через Alembic (версии в `alembic/versions/`)
- Всегда создавай миграции после изменения моделей: `alembic revision --autogenerate -m "description"`
- Применяй миграции: `alembic upgrade head`

### Redis

- Используется для FSM storage (aiogram) и rate limiting
- RedisClient в `app/infrastructure/redis/client.py` — singleton
- Методы: `get`, `set`, `delete`, `incr`, `expire`, `ttl`

### OpenAI API

- Модель: `gpt-4o` (настраивается в `.env`)
- Max tokens: 1024 (настраивается)
- Temperature: 0.7
- История диалога: последние 8 сообщений (настраивается)
- JSON mode всегда включен для структурированных ответов

## Добавление новых функций

### Новый режим работы

1. Добавь FSM state в `app/bot/states.py`
2. Создай service в `app/services/your_service.py`
3. Создай handler в `app/bot/handlers/your_handler.py`
4. Добавь router в `app/bot/dispatcher.py` (функция `_register_handlers`)
5. Создай промпт в `app/infrastructure/llm/prompts.py`
6. Добавь кнопку в главное меню (`app/bot/keyboards/main_menu.py`)

### Новая модель БД

1. Создай модель в `app/core/models/your_model.py`
2. Импортируй в `app/core/models/__init__.py`
3. Создай миграцию: `alembic revision --autogenerate -m "add your_model"`
4. Примени: `alembic upgrade head`

### Новая грамматическая тема

1. Добавь тему в `GrammarTopic` enum (`app/core/enums.py`)
2. Добавь тему в `GRAMMAR_TOPICS` список (`app/core/constants.py`)
3. Добавь объяснение и упражнения в `build_grammar_exercise_prompt` (`app/infrastructure/llm/prompts.py`)

### Новая ситуация (scenario)

1. Добавь сценарий в `SCENARIO_LIST` (`app/core/constants.py`)
2. Добавь контекст в `build_scenario_context` (`app/infrastructure/llm/prompts.py`)

## Запуск и отладка

### Локальная разработка

```bash
poetry install
poetry run alembic upgrade head
poetry run python -m app.main
```

### Docker

```bash
docker-compose up -d
docker-compose exec bot alembic upgrade head
docker-compose logs -f bot
```

### Проверка ошибок

- Логи: `docker-compose logs -f bot`
- Проверка БД: `docker-compose exec postgres psql -U habla -d habla_db`
- Проверка Redis: `docker-compose exec redis redis-cli`

## Важные замечания для агентов

1. **НЕ изменяй структуру промптов** без понимания логики — они тщательно настроены
2. **НЕ удаляй миграции** — только добавляй новые
3. **НЕ изменяй Enum значения** без миграции БД
4. **Всегда учитывай timezone** — используй `DateTime(timezone=True)` в SQLAlchemy
5. **Голосовые сообщения** — пока заглушка, будут через OpenAI Whisper API для Pro подписчиков
6. **Платежи** — пока заглушка, планируются через Telegram Stars
7. **Словарь пользователя** — модель готова, UI будет в следующих версиях

## Контакты и поддержка

- Стек: Python 3.11+, aiogram 3.x, OpenAI API, PostgreSQL, Redis
- LLM: OpenAI GPT-4o
- Deployment: Docker Compose

**Удачи в разработке! 🚀**

# Rules for CODEX

Core Rules
Be concise.
Think before acting.
Read files before editing.
Change only what is necessary.
Prefer minimal diffs.
User instructions override this file.
***Token Efficiency
Avoid unnecessary repository exploration.
Prefer exact file paths.
Do not re-read unchanged files.
Skip files >100KB unless required.
Ignore build/generated files.
Keep responses short and technical.
***Editing Rules
Preserve existing architecture.
Preserve naming/style conventions.
Do not refactor unrelated code.
Do not introduce dependencies unless necessary.
Reuse existing utilities/components.
***Communication
No filler text.
No motivational language.
No repeated context.
Use bullets instead of long paragraphs.
Show only relevant code.
***Debugging
Identify root cause first.
Prefer smallest valid fix.
Avoid speculative changes.
State assumptions briefly.
***Safety
Never run destructive commands without confirmation.
Never overwrite user work silently.
Ask before large refactors/deletions.
***Workflow
For simple tasks:
Execute directly.
For complex tasks:
Short plan.
Execute step-by-step.
Recommend new sessions for unrelated tasks.
