# CodeMind AI

CodeMind AI is an AI-powered codebase understanding platform that helps users explore, analyze, and query repositories using natural language. It is designed for developers who want to upload a project, inspect code structure, and ask questions about architecture, logic, and implementation details without manually reading every file.

## Features

- Upload or ingest a repository for analysis
- Parse project structure and source files
- Query code using natural-language prompts
- Analyze code quality, patterns, and dependencies
- Support backend APIs and a modern frontend dashboard
- Built around FastAPI, React, and AI retrieval/search tools

## Tech Stack

- Backend: Python, FastAPI
- Frontend: React, TypeScript, Vite, Tailwind CSS
- Database: MongoDB via Motor
- AI/Vector Layer: OpenAI + ChromaDB
- Code Parsing: tree-sitter
- Testing: Pytest, Vitest

## Project Structure

```text
CodeMindAi/
├── backend/
│   ├── models/
│   ├── routers/
│   ├── services/
│   ├── tests/
│   ├── workers/
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── pytest.ini
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── vite.config.ts
│   ├── vitest.config.ts
│   └── ...
├── .env.example
├── .gitignore
├── README.md
├── codemind-ai-plan.md
├── prompt-chaining.md
└── ...
```

## Prerequisites

Before running the project, make sure you have:

- Python 3.11+
- Node.js 18+
- npm
- MongoDB instance or MongoDB Atlas connection string
- OpenAI API key

## Environment Setup

Create a root environment file from the sample file:

```bash
copy .env.example .env
```

Then update the values in `.env` with your local setup, such as:

```env
MONGODB_URI=mongodb://localhost:27017/codemind
OPENAI_API_KEY=your_openai_key_here
CORS_ORIGINS=http://localhost:5173
```

## Backend Setup

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

The backend will run at:

```text
http://localhost:8000
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will run at:

```text
http://localhost:5173
```

## API Health Check

```bash
curl http://localhost:8000/api/health
```

Expected response:

```json
{"status":"ok","version":"0.1.0"}
```

## Running Tests

### Backend

```bash
cd backend
pytest --tb=short -q
```

### Frontend

```bash
cd frontend
npm run test
```

## Typical Workflow

1. Start the backend server.
2. Start the frontend application.
3. Upload or ingest a repository.
4. Ask natural-language questions about the codebase.
5. Review AI-powered insights and analysis results.

## Notes

- Keep secrets in `.env` and never commit them to Git.
- The project uses a local or cloud MongoDB database for persistent metadata.
- The root `.gitignore` is configured to exclude environment files, Python cache, and frontend build artifacts.

## License

This project is currently for development and internal use unless otherwise specified by the repository owner.
