# MOOSE LOON AI MENTOR PLATFORM
## MASTER ARCHITECTURE SPECIFICATION
## SOURCE OF TRUTH

Version: 1.0

This document is the highest-priority architectural specification for the repository.

All implementation decisions must follow this document.

If code conflicts with this document:

THIS DOCUMENT WINS.

---

# MISSION

Build a production-grade AI Mentor Platform focused on:

- AI Literacy
- Artificial Intelligence
- Prompt Engineering
- APIs
- Workflow Automation
- n8n
- AI Agents
- Career Development
- Portfolio Building
- Agentic AI

The platform should function as an intelligent mentor rather than a generic chatbot.

The mentor should teach, coach, review, guide, and recommend.

---

# PRODUCT VISION

The product is:

"An AI Mentor for AI & Automation Education."

The platform should feel like:

- Personal tutor
- Career coach
- Technical mentor
- Project advisor

The platform is NOT:

- A generic chatbot
- A social network
- A roleplay application
- A character simulator

---

# PRIMARY USER

Target users:

- Students
- Career changers
- Developers
- Automation engineers
- Data analysts
- AI enthusiasts

Skill levels:

- Beginner
- Intermediate

Advanced users are supported but are not the primary audience.

---

# NON-NEGOTIABLE PRINCIPLES

The system must:

- Teach
- Explain
- Guide
- Mentor

The system must not:

- Guess randomly
- Hallucinate unnecessarily
- Overcomplicate explanations
- Assume prior knowledge

Every response should optimize for learning.

---

# ARCHITECTURE DECISIONS

These decisions are fixed.

Do not change them unless instructed by a human.

---

## FRONTEND

Framework:

Streamlit

Reason:

- Fast development
- Simple deployment
- Excellent for MVPs
- Educational interface

No React.

No Vue.

No Angular.

---

## BACKEND

Framework:

FastAPI

Reason:

- Modern Python stack
- Async support
- API-first architecture

---

## DATABASE

Database:

MySQL

Reason:

- Existing organizational preference
- Familiar ecosystem
- Reliable

Do not replace with PostgreSQL unless instructed.

---

## VECTOR DATABASE

Vector Store:

ChromaDB

Reason:

- Lightweight
- Local-first
- Excellent for MVP

---

## ORM

SQLAlchemy

Required.

---

## AUTHENTICATION

JWT Authentication

Required.

Must support:

- Registration
- Login
- Session validation

---

## LLM PROVIDER

Default Model:

OpenAI GPT-5 class model

The model layer must be abstracted.

Never hardcode a specific provider.

Implement:

/services/llm/

Allow future replacement with:

- OpenAI
- Anthropic
- Google
- Local Models

without major code changes.

---

# MODEL STRATEGY

The platform is NOT training its own foundation model.

Do not build model training pipelines.

Do not attempt to create an LLM.

The platform uses:

- Prompt engineering
- Retrieval Augmented Generation (RAG)
- Memory
- Curriculum retrieval

to create value.

---

# CORE FEATURES

Version 1 must include:

1. Mentor Chat
2. User Accounts
3. Conversation History
4. Curriculum Knowledge Base
5. Learning Recommendations
6. Assignment Generation
7. Project Guidance
8. Progress Tracking

---

# KNOWLEDGE SYSTEM

The AI must prioritize curriculum knowledge.

Curriculum knowledge is authoritative.

General model knowledge is secondary.

When curriculum content exists:

Use curriculum content first.

---

# RAG ARCHITECTURE

Required.

Pipeline:

User Question
    ↓
Retriever
    ↓
Relevant Curriculum Content
    ↓
Prompt Builder
    ↓
LLM
    ↓
Response

No direct unrestricted prompting.

All educational responses should leverage retrieval.

---

# MEMORY SYSTEM

Required.

The platform must remember:

- User goals
- Completed modules
- Learning path
- Projects
- Skill level

Memory must persist in database.

Memory must survive application restarts.

---

# LEARNING PATH ENGINE

Required.

Users should receive:

- Next lesson recommendations
- Next project recommendations
- Next skill recommendations

Recommendations must be generated dynamically.

---

# ASSIGNMENT ENGINE

Required.

Users can request:

- Exercises
- Quizzes
- Mini projects

Assignments should match:

- Current module
- User skill level

---

# PROJECT COACH

Required.

The mentor must help users:

- Plan projects
- Structure projects
- Debug projects
- Improve projects

The mentor should behave like a senior technical mentor.

---

# PORTFOLIO REVIEWER

Required.

Users can submit:

- GitHub repositories
- Project descriptions
- Portfolio content

The mentor should provide:

- Strengths
- Weaknesses
- Improvements

---

# CAREER COACH

Required.

Users should be able to ask:

- What should I learn next?
- What jobs fit my skills?
- What projects should I build?

The mentor should generate actionable roadmaps.

---

# USER EXPERIENCE RULES

The platform should feel:

- Professional
- Educational
- Supportive
- Structured

Avoid:

- Excessive emojis
- Internet slang
- Gimmicks

---

# PROJECT STRUCTURE

muslune-ai-mentor/

├── app.py

├── backend/
│
├── frontend/
│
├── database/
│
├── services/
│
├── knowledge/
│
├── rag/
│
├── memory/
│
├── models/
│
├── auth/
│
├── curriculum/
│
├── prompts/
│
├── tests/
│
└── docs/

---

# CODE QUALITY RULES

Every module must have:

- Single responsibility
- Clear naming
- Type hints
- Docstrings

Avoid:

- Massive files
- Business logic in UI
- Duplicated logic

---

# TESTING

Every service must be testable.

Implement:

- Unit tests
- Integration tests

Testing is mandatory.

---

# SECURITY

Never expose:

- API keys
- Database passwords
- Secrets

Use environment variables.

Required:

.env

Never commit secrets.

---

# OBSERVABILITY

Implement logging.

Required logs:

- Authentication events
- Chat requests
- Retrieval events
- Errors

Logging should be centralized.

---

# DEPLOYMENT TARGET

Primary target:

Ubuntu Server

Deployment stack:

Nginx
+
FastAPI
+
Streamlit
+
MySQL

The system must be deployable on a single VPS.

---

# PERFORMANCE REQUIREMENTS

The platform should support:

- 100+ concurrent learners

Architecture should be scalable.

Avoid premature optimization.

---

# SUCCESS CRITERIA

The project is successful if:

1. A learner can register.
2. A learner can chat with the mentor.
3. The mentor uses curriculum knowledge.
4. Progress is remembered.
5. Assignments can be generated.
6. Projects can be recommended.
7. Learning paths can be generated.
8. The application can be deployed on Ubuntu.

---

# FINAL PRINCIPLE

Every implementation decision must answer:

"Does this improve the learner's ability to learn AI and Automation?"

If the answer is no:

Reject the feature.

Keep the platform focused on mentorship, learning, career growth, and practical project execution.