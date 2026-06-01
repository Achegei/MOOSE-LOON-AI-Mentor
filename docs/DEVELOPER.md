# Developer Guide

This guide explains how to develop, test, and extend the MOOSE LOON AI Mentor Platform.

The highest-priority source of truth is `agents.md`. If implementation details conflict with that file, `agents.md` wins.

## Local Development

Recommended setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Update `.env`:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password_here
MYSQL_DATABASE=moose_loon_ai
SECRET_KEY=replace_with_a_strong_secret
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-5
CHROMA_DB_PATH=./data/chroma_db
```

Start services:

```bash
uvicorn backend.main:app --reload
streamlit run frontend/app.py
```

Run checks:

```bash
python -m compileall -q .
python -m pytest -q
```

## System Responsibilities

### Frontend

Location: `frontend/app.py`

The Streamlit frontend is the learner workspace. It should show product-level concepts such as mentor, learning path, practice, projects, portfolio review, progress, and account.

Do not show developer-only details to learners:

- Backend URLs
- Environment names
- Raw API error payloads
- Database or vector-store language
- Setup instructions
- Internal route names

### Backend

Location: `backend/`

The FastAPI backend owns authenticated mentor workflows:

- `backend/chat.py`: mentor chat with curriculum retrieval
- `backend/mentor_features.py`: learning path, assignments, projects, portfolio review, progress, and session validation
- `backend/main.py`: app creation, middleware, startup, and router registration

### Auth

Location: `auth/`

JWT authentication supports:

- Registration
- Login
- Refresh token rotation
- Logout
- Session validation
- Access token blacklist checks

Frontend code should store tokens only in Streamlit session state.

### Database

Location: `database/`

SQLAlchemy models include:

- `User`
- `Conversation`
- `Message`
- `LearningModule`
- `UserProgress`
- `UserMemory`
- `Assignment`
- `Project`
- Token tables

The production database target is MySQL.

### Memory

Location: `memory/service.py`

Learner memory persists:

- Goals
- Learning path
- Active module
- Current projects
- Skill level
- Notes

Use the memory service instead of reading and writing memory fields directly from route handlers when adding new features.

### LLM Layer

Location: `services/llm/`

The LLM provider is abstracted behind `BaseLLMService`.

Current implementations:

- `OpenAIService`
- `StubLLMService`

Do not hardcode provider-specific calls into route handlers. Add future providers behind the same base interface.

### RAG

Locations:

- `services/rag/chroma_service.py`
- `rag/ingest.py`
- `knowledge/`

RAG flow:

```text
User question
-> curriculum retriever
-> relevant curriculum snippets
-> LLM prompt context
-> mentor response
```

`ChromaService` uses ChromaDB when available. It also includes a local markdown fallback so development remains usable when the vector store is empty or unavailable.

Starter curriculum lives in `knowledge/*.md`. After editing curriculum, run:

```bash
python -m rag.ingest
```

## API Overview

Auth:

- `POST /auth/register`
- `POST /auth/token`
- `POST /auth/refresh`
- `POST /auth/logout`
- `POST /auth/logout_all`

Mentor:

- `POST /chat/`
- `GET /learning-path`
- `POST /memory/goals`
- `POST /assignments/generate`
- `POST /projects/recommend`
- `POST /portfolio-review`
- `GET /progress/summary`
- `POST /progress/update`
- `GET /settings/session`

Health:

- `GET /`
- `GET /health`

Billing and developer APIs:

- `GET /billing/tiers`
- `GET /billing/subscription`
- `POST /billing/subscription`
- `GET /developer/api-keys`
- `POST /developer/api-keys`
- `DELETE /developer/api-keys/{key_id}`
- `POST /v1/mentor/chat`

## Monetization

Tier definitions live in `services/billing.py`.

Current tiers:

- Free: learner exploration, 1 trial API key and 50 API calls per month
- Builder: 2 API keys, 1,000 API calls per month
- Pro: 10 API keys, 10,000 API calls per month
- Team: 50 API keys, 50,000 API calls per month

The current implementation lets an authenticated user select a tier directly. This is useful for MVP demos and local testing, but production billing should replace direct tier updates with a payment provider flow:

1. Frontend starts checkout for a selected tier.
2. Payment provider handles payment.
3. Backend receives a signed webhook.
4. Backend updates `UserSubscription` only after verifying the webhook.
5. API key limits are enforced from the verified subscription tier.

Do not trust frontend tier changes in production.

## Developer API Keys

API key logic lives in `services/api_keys.py`.

Keys are generated once and stored only as SHA-256 hashes. The frontend shows the plain key only immediately after creation.

Users manage keys in the Streamlit Developers page. External systems authenticate with:

```text
X-API-Key: mlm_your_key_here
```

The first integration endpoint is:

```text
POST /v1/mentor/chat
```

Request:

```json
{
  "prompt": "Explain prompt engineering to a beginner.",
  "learner_context": "The learner is new to APIs and n8n."
}
```

Response:

```json
{
  "reply": "Mentor response...",
  "usage": {
    "monthly_limit": 1000,
    "requests_this_month": 12
  }
}
```

Usage limits are stored on each `DeveloperApiKey` row. For production billing, add a scheduled monthly reset or usage-period table.

## Adding A New Mentor Feature

1. Confirm the feature supports AI and automation learning.
2. Add any persistent data to `database/models.py`.
3. Add service logic in the proper package, not the Streamlit UI.
4. Add an authenticated FastAPI route.
5. Use curriculum retrieval for educational responses.
6. Use the LLM abstraction only through `services/llm/`.
7. Add focused tests in `tests/`.
8. Add learner-facing UI in `frontend/app.py` without exposing implementation details.

## Testing Expectations

Use focused tests for:

- Auth token behavior
- Conversation ownership
- RAG context building
- Memory persistence
- Assignment/project generation flow
- Secret hygiene
- Frontend-safe helper behavior when practical

Current baseline:

```bash
python -m pytest -q
```

## Deployment Notes

Primary deployment target:

```text
Ubuntu Server
Nginx
FastAPI
Streamlit
MySQL
ChromaDB local persistence
```

Recommended production practices:

- Run FastAPI and Streamlit as separate systemd services.
- Put Nginx in front of both services.
- Use a strong `SECRET_KEY`.
- Store `.env` outside source control.
- Back up MySQL.
- Back up `data/chroma_db` if using local vector persistence.
- Rotate API keys immediately if exposed.

## Product Quality Rules

Keep learner-facing language:

- Professional
- Supportive
- Structured
- Beginner-friendly
- Career-aware

Avoid:

- Internet slang
- Excessive emojis
- Raw infrastructure details
- Placeholder copy
- Generic chatbot behavior

The mentor should teach, coach, review, guide, and recommend.
