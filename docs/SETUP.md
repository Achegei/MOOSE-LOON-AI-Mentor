# Development Setup Guide

## Prerequisites

- Python 3.10+
- MySQL 8.0+
- Git

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd moose-loon-ai-mentor
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your configuration:
- MySQL credentials
- OpenAI API key
- JWT secret

### 5. Initialize Database

```bash
# Create database
mysql -u root -p -e "CREATE DATABASE moose_loon_ai;"

# Run migrations (when implemented)
alembic upgrade head
```

### 6. Run Application

**Backend (Terminal 1):**
```bash
python -m uvicorn backend.main:app --reload
```

Backend will be available at: `http://localhost:8000`

**Frontend (Terminal 2):**
```bash
streamlit run frontend/app.py
```

Frontend will be available at: `http://localhost:8501`

## Testing

```bash
pytest tests/
```

## Project Structure Reference

See [README.md](../README.md) for project structure overview.

## Common Issues

### MySQL Connection Error
- Ensure MySQL is running
- Verify database credentials in `.env`
- Check MYSQL_HOST is correct (usually `localhost`)

### OpenAI API Errors
- Ensure `OPENAI_API_KEY` is set in `.env`
- Verify API key is valid in OpenAI dashboard

### Port Already in Use
- Backend (8000): `lsof -i :8000` to find process
- Frontend (8501): `lsof -i :8501` to find process

## Next Steps

- [ ] Set up database migrations with Alembic
- [ ] Implement authentication endpoints
- [ ] Build chat interface
- [ ] Create curriculum module loader
- [ ] Implement RAG pipeline
- [ ] Add logging and monitoring
