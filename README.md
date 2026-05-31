# MOOSE LOON AI MENTOR PLATFORM

An AI Mentor for AI & Automation Education.

## Product Vision

A production-grade intelligent mentor platform that functions as a personal tutor, career coach, technical mentor, and project advisor for students, career changers, and developers.

## Core Features (v1)

- ✅ Mentor Chat
- ✅ User Accounts & Authentication
- ✅ Conversation History
- ✅ Curriculum Knowledge Base
- ✅ Learning Recommendations
- ✅ Assignment Generation
- ✅ Project Guidance
- ✅ Progress Tracking

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Streamlit |
| **Backend** | FastAPI |
| **Database** | MySQL + SQLAlchemy |
| **Vector Store** | ChromaDB |
| **LLM** | OpenAI (abstracted) |
| **Auth** | JWT |

## Project Structure

```
.
├── app.py                 # Main entry point
├── backend/               # FastAPI application
├── frontend/              # Streamlit UI
├── database/              # Database models & migrations
├── services/              # Business logic services
│   └── llm/              # LLM abstraction layer
├── knowledge/             # Curriculum content
├── rag/                   # Retrieval Augmented Generation
├── memory/                # User memory system
├── models/                # Data models
├── auth/                  # Authentication & JWT
├── curriculum/            # Learning modules
├── prompts/               # Prompt templates
├── tests/                 # Unit & integration tests
└── docs/                  # Documentation
```

## Quick Start

### 1. Setup Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your database and API credentials
# Set your OpenAI key in .env as OPENAI_API_KEY and never commit the real key.
```

### 3. Initialize Database

```bash
# Run migrations (when implemented)
alembic upgrade head
```

### 4. Start Backend

```bash
uvicorn backend.main:app --reload
```

### 5. Start Frontend

```bash
streamlit run frontend/app.py
```

## Architecture Decisions

- **No Model Training**: Uses prompt engineering, RAG, and memory for value
- **Curriculum-First**: Curriculum knowledge is authoritative
- **RAG Pipeline**: All educational responses leverage retrieval
- **Session Persistence**: Memory survives application restarts
- **Scalable Design**: Supports 100+ concurrent learners

## Development Guidelines

- Every module has single responsibility
- Type hints required
- Docstrings mandatory
- Unit & integration tests required
- Security-first: No hardcoded secrets
- Centralized logging

## Success Criteria

1. ✅ User registration
2. ✅ Chat with mentor using curriculum knowledge
3. ✅ Progress tracking & persistence
4. ✅ Assignment generation
5. ✅ Project recommendations
6. ✅ Learning path generation
7. ✅ Ubuntu deployment ready

## Contributing

When implementing:
- Follow the architecture specification in `agents.md`
- This document is the source of truth
- Code conflicts with spec? The spec wins

## License

TBD

---

**Mission**: Build the ultimate AI & Automation mentor platform for learners worldwide.
# MOOSE-LOON-AI-Mentor
