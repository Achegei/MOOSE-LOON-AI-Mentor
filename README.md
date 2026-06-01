# MOOSE LOON AI Mentor

MOOSE LOON is a curriculum-first AI mentor platform for learners building practical skills in AI, prompt engineering, APIs, workflow automation, n8n, AI agents, portfolio development, and career growth.

The product is designed to feel like a structured mentor workspace: part tutor, part technical coach, part project advisor, and part career guide.

## Product Positioning

MOOSE LOON is not a generic chatbot. It is an AI and automation education platform that helps learners:

- Ask curriculum-grounded questions
- Build personalized learning paths
- Generate exercises, quizzes, and mini projects
- Plan portfolio projects
- Review portfolio work
- Track learning progress
- Maintain persistent learner memory

## Core Capabilities

| Capability | Description |
| --- | --- |
| Mentor Chat | Curriculum-backed coaching for AI and automation questions |
| Learning Path | Dynamic next-step recommendations based on goals and skill level |
| Practice | Exercises, quizzes, and mini projects generated for the learner |
| Project Coach | Portfolio project planning and milestone guidance |
| Portfolio Review | Feedback on project clarity, technical proof, and improvements |
| Progress Tracking | Persistent module progress, assignments, projects, and learner memory |
| Accounts | JWT registration, login, session validation, and logout |
| Knowledge Base | ChromaDB retrieval with local curriculum markdown fallback |
| Monetization | SaaS tiers for learners, builders, pros, and teams |
| Developer API | API keys for external systems that need mentor responses |

## Architecture

| Layer | Technology |
| --- | --- |
| Frontend | Streamlit |
| Backend | FastAPI |
| Database | MySQL + SQLAlchemy |
| Vector Store | ChromaDB |
| LLM Layer | Abstracted provider interface |
| Default LLM Provider | OpenAI GPT-5 class model |
| Authentication | JWT |

The architecture follows [agents.md](agents.md), which is the repository source of truth.

## Project Structure

```text
.
├── app.py
├── backend/
├── frontend/
├── database/
├── services/
│   ├── llm/
│   └── rag/
├── knowledge/
├── rag/
├── memory/
├── models/
├── auth/
├── curriculum/
├── prompts/
├── tests/
└── docs/
```

## Quick Start

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create environment configuration:

```bash
cp .env.example .env
```

Edit `.env` with MySQL credentials, a strong `SECRET_KEY`, and your LLM API key.

Ingest starter curriculum:

```bash
python -m rag.ingest
```

Start the backend:

```bash
uvicorn backend.main:app --reload
```

Start the frontend:

```bash
streamlit run frontend/app.py
```

## Development

Run tests:

```bash
python -m pytest -q
```

Run a syntax/import check:

```bash
python -m compileall -q .
```

See [docs/DEVELOPER.md](docs/DEVELOPER.md) for developer documentation, architecture notes, API responsibilities, RAG behavior, and extension guidance.

## SaaS Tiers

The platform includes a tier model that can be connected to a payment provider:

| Tier | Audience | API Access |
| --- | --- | --- |
| Free | Learners exploring AI and automation mentorship | 1 trial API key, 50 calls/month |
| Builder | Learners building portfolio projects | 2 API keys, 1,000 calls/month |
| Pro | Career changers and automation builders | 10 API keys, 10,000 calls/month |
| Team | Cohorts and training programs | 50 API keys, 50,000 calls/month |

The current implementation stores the selected tier locally. In production, replace direct tier selection with checkout sessions and verified billing webhooks.

## Developer API

Paid tiers can create developer API keys from the Streamlit Developers page.

External systems can call:

```text
POST /v1/mentor/chat
X-API-Key: mlm_your_key_here
```

Example request:

```json
{
  "prompt": "Explain prompt engineering to a beginner.",
  "learner_context": "The learner is new to APIs and n8n."
}
```

## Security Notes

- Never commit `.env`.
- Never place real API keys in `.env.example`.
- Rotate any key that has ever been pasted into source control or shared logs.
- Use environment variables for all secrets.

## Product Principle

Every feature should improve the learner's ability to learn AI and automation. If it does not support mentorship, learning, career growth, or practical project execution, it does not belong in the product.
