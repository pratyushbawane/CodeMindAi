# CodeMind AI

An AI-powered codebase understanding platform. Upload a ZIP of any repository and ask natural-language questions grounded in the actual source code.

## Prerequisites

- Node.js 18+
- Python 3.11+
- MongoDB Atlas URI (or local MongoDB)
- OpenAI API key

## Backend setup

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt

cp ../.env.example .env
# Edit .env and fill in MONGODB_URI and OPENAI_API_KEY

uvicorn main:app --reload
# Runs on http://localhost:8000
```

## Frontend setup

```bash
cd frontend
npm install

# Create frontend/.env from root .env.example — only VITE_ vars are needed
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

npm run dev
# Runs on http://localhost:5173
```

## Run tests

```bash
# Backend
cd backend
pytest --tb=short -q

# Frontend
cd frontend
npm run test
```

## Health check

```
GET http://localhost:8000/api/health
→ {"status":"ok","version":"0.1.0"}
```
