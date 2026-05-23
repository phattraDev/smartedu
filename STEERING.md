# Project Steering

## Purpose

This project is a school communication system that connects staff, parents, and a Telegram bot.

The system should make it easy for school staff to publish homework, holidays, and announcements, and for parents to retrieve the information through Telegram without needing dashboard access.

## Product Shape

The project has three main surfaces:

- `backend/`: FastAPI application, database models, authentication, REST API, file uploads, Telegram broadcast delivery, and static dashboard hosting.
- `bot/`: Telegram bot built with `python-telegram-bot`. Parents use it to register their class, select language, read homework, view holidays, and receive announcements.
- `dashboard/`: Static HTML, CSS, and JavaScript dashboard for school staff.

The backend is the system of record. The dashboard and bot should call backend APIs rather than duplicating business logic.

## Core Users

- Admins manage classes, holidays, broadcasts, and homework.
- Teachers submit and delete homework, and view holidays.
- Parents use Telegram only. They register their child's class and retrieve class-specific information.

## Architecture Principles

- Keep the backend as the source of truth for classes, homework, holidays, subscribers, and broadcast logs.
- Keep the dashboard thin. It should handle UI state and API calls, not own domain rules.
- Keep the bot thin. It should format messages and manage Telegram conversations, but rely on backend endpoints for persistent state.
- Prefer explicit API endpoints over implicit coupling between components.
- Preserve local development simplicity: SQLite fallback, `.env` configuration, and simple batch scripts are intentional.
- Production deployment should use PostgreSQL, HTTPS, explicit CORS origins, and secure environment variables.

## Backend Guidelines

- API routes live in `backend/main.py`.
- Database models live in `backend/models.py`.
- Pydantic request and response contracts live in `backend/schemas.py`.
- Authentication helpers live in `backend/auth.py`.
- Database setup and session handling live in `backend/database.py`.

When changing backend behavior:

- Update schemas when response or request shapes change.
- Keep public bot endpoints unauthenticated only when parents/bot genuinely need them.
- Keep dashboard mutation endpoints authenticated.
- Use SQLAlchemy relationships and queries rather than ad hoc database access.
- Avoid logging secrets, passwords, tokens, or uploaded file contents.
- Preserve compatibility with both SQLite and PostgreSQL unless deliberately changing deployment assumptions.

## Bot Guidelines

- Bot behavior lives in `bot/bot.py`.
- Translated strings live in `bot/translations.py`.
- The bot should call backend APIs through the helper functions in `bot/bot.py`.
- The bot supports English (`en`) and Khmer (`km`); do not hardcode user-facing bot text outside translations unless it is a deliberate bilingual language-selection prompt.
- Be careful with Telegram Markdown escaping when adding dynamic text.
- Do not store long-term state only in `context.user_data`; persist user preferences to the backend.

## Dashboard Guidelines

- The dashboard is intentionally static: `dashboard/index.html`, `dashboard/style.css`, and `dashboard/app.js`.
- API base selection is handled in `dashboard/app.js`.
- Keep UI interactions straightforward and staff-focused.
- Avoid introducing a frontend build step unless the project explicitly moves to a framework.
- If adding new backend routes, wire the dashboard through `apiFetch()` so auth handling remains consistent.

## Data Model

Current persistent entities:

- `Class`: school class or grade, identified by a short code.
- `Homework`: assignment for a class, optionally with one uploaded file.
- `Holiday`: school holiday or closure.
- `Subscriber`: Telegram parent/user registration, language, active status, and class code.
- `BroadcastLog`: history of admin broadcasts and delivery counts.

Keep class codes normalized to uppercase.

## Configuration

Important environment variables:

- `TELEGRAM_BOT_TOKEN`
- `API_BASE_URL`
- `API_SECRET_KEY`
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `DATABASE_URL`
- `SCHOOL_NAME`
- `RUN_BOT`
- `UPLOAD_DIR`

Local development should work with a root `.env` file. Render deployment is described in `render.yaml`.

## Security Expectations

Before production use, address these areas:

- Remove plaintext credential logging.
- Remove password/debug prints from auth and login flows.
- Replace permissive CORS with explicit dashboard origins.
- Use a strong `API_SECRET_KEY`.
- Avoid default admin credentials.
- Consider hashed admin passwords or a proper users table.
- Review public file download behavior for access expectations.

## Known Risks

- `backend/main.py` currently contains duplicate `run_bot()` definitions.
- Authentication is simple and environment-backed.
- The dashboard stores JWTs in `localStorage`.
- File uploads are stored on disk and depend on persistent storage in production.
- Telegram Markdown formatting can break if dynamic content contains unescaped Markdown characters.
- Static dashboard code builds some HTML with template strings; avoid inserting untrusted rich content without escaping.

## Local Runbook

Start the backend:

```powershell
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Start the bot:

```powershell
cd bot
pip install -r requirements.txt
python bot.py
```

Open the dashboard:

- `http://localhost:8000/` when served by FastAPI.
- Or open `dashboard/index.html` directly, which points API calls at `http://localhost:8000`.

## Change Discipline

- Keep changes scoped to the component being modified.
- Do not rewrite the static dashboard into a framework without a clear project decision.
- Do not change API response shapes casually; the bot and dashboard both consume them.
- Do not remove Khmer/English translation support.
- Do not commit real `.env` secrets.
- Add tests or manual verification notes for API behavior changes.

