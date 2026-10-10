# CodeMind AI — Implementation Plan

## Confirmed Configuration

| Setting | Value |
|---------|-------|
| LLM Provider | OpenAI (GPT-4o-mini default, GPT-4o optional) |
| Embedding Model | text-embedding-3-small (OpenAI) |
| MongoDB | MongoDB Atlas free tier (connection string via env var) |
| Vector Store | ChromaDB embedded |

---

## Workspace Assessment

The workspace is an empty directory. No existing frontend, backend, configuration,
environment templates, tests, Docker files, or Git history were found. This is a
green-field project. Every file will be created from scratch.

---

## Top-Level Overview

CodeMind AI is an AI-powered codebase understanding platform. Developers upload a
ZIP archive of a repository. The backend extracts and indexes the files safely,
runs static analysis to detect languages and relationships, generates semantic
embeddings, and stores everything in MongoDB. The frontend lets developers ask
natural-language questions about the codebase, explore its architecture, request
contextual debugging help, and use an interactive learning mode. Every AI answer is
grounded in retrieved source-code chunks with file and line references.

**Scope for this plan:** the full application from project scaffold to a working
MVP with automated tests, followed by a phased path to every listed feature.

**Architectural approach:** modular monolith. One backend service, one frontend
application, one database, one vector store. Add services only when a clear
scalability need emerges.

**Non-goals for MVP:** GitHub integration, autonomous code modification, advanced
multi-agent pipelines, additional language parsers beyond Python and JavaScript/
TypeScript.

---

## Proposed Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (React + Vite)                │
│  Dashboard · Upload · File Explorer · Chat · Viz · Learn │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS / REST + SSE
┌───────────────────────▼─────────────────────────────────┐
│                  FastAPI Backend                          │
│  ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌───────────┐ │
│  │ Projects │ │ Ingest   │ │ Analysis  │ │ AI / RAG  │ │
│  │ router   │ │ router   │ │ router    │ │ router    │ │
│  └──────────┘ └──────────┘ └───────────┘ └───────────┘ │
│  ┌──────────────────────────────────────────────────┐   │
│  │             Background Worker (asyncio tasks)    │   │
│  │  ZIP safety · extraction · AST · embeddings      │   │
│  └──────────────────────────────────────────────────┘   │
└──────────┬────────────────────┬────────────────────────-┘
           │                    │
  ┌────────▼──────┐    ┌────────▼──────────┐
  │   MongoDB     │    │  Vector Store      │
  │ (projects,    │    │  (Chroma or        │
  │  files, meta) │    │   pgvector — TBD)  │
  └───────────────┘    └───────────────────┘
                                │
                       ┌────────▼──────────┐
                       │  LLM API          │
                       │  (configurable:   │
                       │  OpenAI, Anthropic│
                       │  local Ollama)    │
                       └───────────────────┘
```

---

## Recommended Directory Structure

```
codemind-ai/
├── .env.example                  # Key names only, no values
├── .gitignore
├── README.md
├── docker-compose.yml            # Added when application is stable
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   ├── components.json           # shadcn/ui config
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── router.tsx
│       ├── api/                  # Typed API client functions
│       │   ├── projects.ts
│       │   ├── ingest.ts
│       │   ├── analysis.ts
│       │   └── ai.ts
│       ├── components/
│       │   ├── ui/               # shadcn/ui primitives
│       │   ├── layout/           # Shell, Sidebar, TopBar
│       │   ├── projects/         # ProjectCard, ProjectForm
│       │   ├── explorer/         # FileTree, FileViewer, LanguageBadge
│       │   ├── chat/             # ChatPanel, MessageBubble, SourceRef
│       │   ├── viz/              # ArchGraph (React Flow)
│       │   ├── debug/            # ErrorInput, DebugPanel
│       │   └── learn/            # LearnPanel, QuizCard
│       ├── pages/
│       │   ├── HomePage.tsx
│       │   ├── ProjectPage.tsx
│       │   ├── ExplorerPage.tsx
│       │   ├── ChatPage.tsx
│       │   ├── VizPage.tsx
│       │   ├── DebugPage.tsx
│       │   └── LearnPage.tsx
│       ├── store/                # Zustand or React Context state
│       ├── hooks/                # Custom React hooks
│       ├── types/                # Shared TypeScript interfaces
│       └── utils/                # Formatting, syntax highlighting
│
├── backend/
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── pytest.ini
│   ├── main.py                   # FastAPI app entry point
│   ├── config.py                 # Settings loaded from env vars
│   ├── database.py               # MongoDB connection
│   ├── routers/
│   │   ├── projects.py
│   │   ├── ingest.py
│   │   ├── analysis.py
│   │   └── ai.py
│   ├── services/
│   │   ├── ingest_service.py     # ZIP handling, path safety
│   │   ├── analysis_service.py   # Language detection, AST, Tree-sitter
│   │   ├── index_service.py      # Chunking, embedding, vector store
│   │   └── ai_service.py         # LLM calls, RAG, prompt assembly
│   ├── models/
│   │   ├── project.py            # Pydantic + MongoDB models
│   │   ├── file_record.py
│   │   ├── analysis_result.py
│   │   └── chat_message.py
│   ├── workers/
│   │   └── ingestion_worker.py   # Background ingestion task
│   └── tests/
│       ├── test_ingest.py
│       ├── test_analysis.py
│       ├── test_ai.py
│       └── test_projects.py
│
└── scripts/
    ├── seed_test_project.py      # Dev helper — loads a sample ZIP
    └── reset_db.py               # Dev helper — wipes MongoDB
```

---

## Frontend Pages and Component Plan

### Pages

| Page | Route | Purpose |
|------|-------|---------|
| HomePage | `/` | Project dashboard — list, create, delete projects |
| ProjectPage | `/projects/:id` | Project overview, analysis status, nav hub |
| ExplorerPage | `/projects/:id/explorer` | File tree, language badges, safe file viewer |
| ChatPage | `/projects/:id/chat` | Natural-language Q&A with source references |
| VizPage | `/projects/:id/viz` | React Flow architecture graph |
| DebugPage | `/projects/:id/debug` | Paste error, get grounded explanation |
| LearnPage | `/projects/:id/learn` | Guided explanations and project-specific quizzes |

### Key Components

**Layout**
- `Shell` — outer wrapper with sidebar and top bar
- `Sidebar` — project-aware navigation links
- `TopBar` — project name, status indicator

**Projects**
- `ProjectCard` — name, language badges, status chip, created date
- `ProjectForm` — create/rename form, ZIP upload dropzone

**Explorer**
- `FileTree` — recursive tree from analysis metadata; no raw filesystem access
- `FileViewer` — syntax-highlighted read-only view; content fetched from backend by path
- `LanguageBadge` — color-coded language label

**Chat**
- `ChatPanel` — message history, streaming input
- `MessageBubble` — user/AI distinction, markdown rendering
- `SourceRef` — collapsible chip showing filename, line range, and snippet

**Viz**
- `ArchGraph` — React Flow canvas; nodes are modules/files, edges are imports/calls

**Debug**
- `ErrorInput` — textarea for pasting stack traces or error messages
- `DebugPanel` — AI explanation with file/line references highlighted

**Learn**
- `LearnPanel` — AI-generated explanation of selected module or concept
- `QuizCard` — multiple-choice or fill-in question generated from repo content

---

## Backend Module and API Endpoint Plan

### Config (`config.py`)
Reads all secrets and settings from environment variables using Pydantic `BaseSettings`.
No default values for secrets. Fails fast at startup if required variables are missing.

### Database (`database.py`)
Motor (async MongoDB driver) client. One function returns the database instance.
Connection string read from env var `MONGODB_URI`.

### Routers

#### `POST /api/projects` — Create project
Body: `{ name, description }`
Response: project document with `id`, `status: "created"`

#### `GET /api/projects` — List projects
Response: array of project summaries

#### `GET /api/projects/{id}` — Get project detail
Response: full project document with analysis status

#### `DELETE /api/projects/{id}` — Delete project
Removes project, all file records, embeddings, and uploaded archive.

#### `POST /api/projects/{id}/ingest` — Upload ZIP
Multipart form with ZIP file.
Triggers background ingestion worker.
Response: `{ job_id, status: "queued" }`

#### `GET /api/projects/{id}/ingest/status` — Poll ingestion status
Response: `{ status, progress_pct, current_file, error }`

#### `GET /api/projects/{id}/files` — List project files
Response: file records (path, language, size, line_count)

#### `GET /api/projects/{id}/files/{file_path:path}` — Get file content
Returns file content lines and metadata. Path is validated against project root.
Never serves files outside the project sandbox.

#### `GET /api/projects/{id}/analysis` — Get analysis summary
Response: language breakdown, top-level structure, detected frameworks

#### `GET /api/projects/{id}/graph` — Get architecture graph data
Response: `{ nodes, edges }` for React Flow

#### `POST /api/projects/{id}/chat` — Ask a question
Body: `{ question, conversation_id? }`
Response (streaming SSE): token stream, then final message with source refs

#### `GET /api/projects/{id}/chat/{conversation_id}` — Get conversation history

#### `POST /api/projects/{id}/debug` — Debug an error
Body: `{ error_text, language? }`
Response: explanation with file/line references

#### `POST /api/projects/{id}/learn` — Get concept explanation
Body: `{ topic, file_path? }`
Response: explanation, related files

#### `POST /api/projects/{id}/learn/quiz` — Generate quiz
Body: `{ topic, file_path? }`
Response: `{ questions: [ { text, options, answer_index, explanation } ] }`

---

## MongoDB Data Model

### Collection: `projects`
```json
{
  "_id": "ObjectId",
  "name": "string",
  "description": "string",
  "status": "created | ingesting | indexed | error",
  "created_at": "datetime",
  "updated_at": "datetime",
  "archive_path": "string (internal sandbox path)",
  "languages": ["string"],
  "frameworks": ["string"],
  "file_count": "int",
  "total_lines": "int",
  "error_message": "string | null"
}
```

### Collection: `file_records`
```json
{
  "_id": "ObjectId",
  "project_id": "ObjectId (ref projects)",
  "path": "string (relative, sanitized)",
  "language": "string",
  "size_bytes": "int",
  "line_count": "int",
  "content_hash": "string",
  "is_binary": "bool",
  "indexed_at": "datetime"
}
```

### Collection: `analysis_results`
```json
{
  "_id": "ObjectId",
  "project_id": "ObjectId",
  "graph_nodes": [{ "id": "string", "label": "string", "type": "string" }],
  "graph_edges": [{ "source": "string", "target": "string", "type": "string" }],
  "language_breakdown": { "Python": 42, "TypeScript": 18 },
  "detected_frameworks": ["FastAPI", "React"],
  "top_level_summary": "string",
  "generated_at": "datetime"
}
```

### Collection: `conversations`
```json
{
  "_id": "ObjectId",
  "project_id": "ObjectId",
  "created_at": "datetime",
  "messages": [
    {
      "role": "user | assistant",
      "content": "string",
      "source_refs": [
        { "file": "string", "start_line": "int", "end_line": "int", "snippet": "string" }
      ],
      "timestamp": "datetime"
    }
  ]
}
```

---

## Repository Ingestion and File-Processing Workflow

```
Upload ZIP
    │
    ▼
[Safety Gate]
  • Reject if not a valid ZIP
  • Reject if > configurable size limit (default 50 MB)
  • Scan all entry paths for traversal attacks (../, absolute paths, symlinks)
  • Reject entries with suspicious extensions (.exe, .sh, .bat, .cmd, .ps1, etc.)
  • Limit total number of files (default 5000)
    │
    ▼
[Extract to Isolated Sandbox]
  • Write to /tmp/codemind/projects/{project_id}/  (sandboxed)
  • Do NOT execute any file
    │
    ▼
[File Discovery]
  • Walk extracted tree
  • Skip binary files (detect via content sniffing)
  • Respect .gitignore if present (skip node_modules, .git, build dirs)
    │
    ▼
[Language Detection]
  • Extension-based mapping (primary)
  • Magic bytes for ambiguous cases
  • Framework detection via package.json, requirements.txt, go.mod, etc.
    │
    ▼
[Static Analysis]
  • Python files → Python AST (stdlib, no execution)
    - Extract module-level symbols, imports, function/class names
  • JS/TS files → Tree-sitter
    - Extract imports, exports, function declarations
  • Build import/dependency graph
    │
    ▼
[Chunking]
  • Split files into overlapping chunks (~512 tokens)
  • Chunk at logical boundaries (function/class boundaries if AST available)
  • Store chunk metadata: file, start_line, end_line, symbol_context
    │
    ▼
[Embedding]
  • Send chunks to embedding model (configurable provider)
  • Store vectors in vector store with chunk metadata
    │
    ▼
[Persist Metadata]
  • Write file_records to MongoDB
  • Write analysis_results to MongoDB
  • Update project status to "indexed"
```

---

## Source-Code Indexing and Semantic Retrieval Design

### Chunking Strategy
- Target chunk size: 400–512 tokens (not characters — use tiktoken or equivalent)
- Overlap: 50–80 tokens to preserve context across boundaries
- Prefer splitting at function/class boundaries when AST data is available
- Store with metadata: `project_id`, `file_path`, `start_line`, `end_line`, `language`, `symbol_name`

### Vector Store Choice
Use **ChromaDB** as the default. It is embeddable (runs in-process), requires no
additional infrastructure, and is easy to swap. The `index_service.py` wraps all
vector store calls behind a thin interface. A future operator can swap to pgvector
or Qdrant by reimplementing that interface.

### Embedding Model
Configurable via env vars. Default recommendation: `text-embedding-3-small` (OpenAI)
or a local sentence-transformers model for offline use. The model is injected into
`index_service.py` through config, never hardcoded.

### Retrieval at Query Time
1. Embed the user question.
2. Query vector store for top-K similar chunks (default K=6).
3. Optionally expand with BM25 keyword search on file paths / symbol names for hybrid retrieval (Phase 3+).
4. Return chunks with metadata. Frontend displays source refs from metadata.

### Context Window Management
Never send the entire repository to the LLM. The prompt includes:
- System instruction (role + rules)
- Project summary (language, framework, file count)
- Retrieved chunks (up to ~3000 tokens of source)
- Conversation history (last N turns, budget-limited)
- User question

---

## LLM Integration and Configuration Strategy

### Provider Abstraction
`ai_service.py` defines a thin `LLMProvider` protocol with one method:
`complete(messages) -> AsyncIterator[str]`. Concrete implementations:
- `OpenAIProvider` — uses `openai` SDK
- `AnthropicProvider` — uses `anthropic` SDK
- `OllamaProvider` — uses `httpx` against local Ollama REST API

Selected at startup via `LLM_PROVIDER` env var. Fails fast if required keys are absent.

### Configuration Env Vars (LLM)
```
LLM_PROVIDER=openai          # openai | anthropic | ollama
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
ANTHROPIC_API_KEY=...
ANTHROPIC_MODEL=claude-3-haiku-20240307
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=codellama
EMBEDDING_PROVIDER=openai    # openai | sentence_transformers
EMBEDDING_MODEL=text-embedding-3-small
```

### Streaming
Chat responses use Server-Sent Events (SSE). FastAPI yields token chunks as they
arrive from the LLM. The frontend consumes the SSE stream and appends tokens to the
message bubble in real time.

---

## AI Response Grounding and Source-Reference Strategy

1. **Grounded prompting** — the system prompt instructs the LLM to cite specific
   files and line numbers from the retrieved context. It must not invent file names.

2. **Post-generation validation** — after the LLM responds, the backend checks that
   every cited file path exists in `file_records` for the project. Invalid references
   are stripped before sending to the frontend.

3. **Source ref display** — `SourceRef` components in the frontend link back to the
   ExplorerPage at the exact line range. The viewer highlights those lines.

4. **Uncertainty signaling** — the system prompt instructs the LLM: "If the context
   does not contain enough information to answer confidently, say so explicitly."
   The frontend renders a low-confidence indicator when the model flags uncertainty.

5. **No hallucinated code** — the system prompt forbids the LLM from generating
   modified code unless the user explicitly requests a code suggestion. Code
   suggestions are clearly labeled as AI-generated and unreviewed.

---

## Security Plan for Untrusted ZIP Archives and Source Code

| Threat | Mitigation |
|--------|-----------|
| ZIP path traversal (`../../etc/passwd`) | Validate every entry path. Reject absolute paths and any path containing `..`. |
| ZIP bomb (deeply nested / huge decompressed size) | Enforce decompressed size limit and file count limit before extraction. |
| Executable files | Reject dangerous extensions. Never execute extracted files. |
| Symlink attacks | Reject ZIP entries that are symlinks. |
| Malicious AST payloads | Use Python `ast.parse()` in a try/except. Never call `eval`, `exec`, or `compile`. |
| Tree-sitter memory issues | Parse files with a timeout and file-size ceiling. |
| LLM prompt injection via source code | Wrap retrieved code in explicit delimiters in the prompt. Sanitize before insertion. |
| Path traversal in file viewer API | Resolve requested path relative to project sandbox. Reject if outside sandbox. |
| Large file denial of service | Skip files over a configurable size limit (default 500 KB per file). |
| Uploaded file storage exposure | Store archives only in the server-side sandbox. Never serve the raw archive to the client. |

---

## Testing Strategy

### Backend (pytest + pytest-asyncio)
- `test_ingest.py` — ZIP validation, path traversal rejection, extraction, sandbox isolation
- `test_analysis.py` — language detection, Python AST parsing, framework detection
- `test_ai.py` — RAG prompt assembly, source reference validation, mock LLM responses
- `test_projects.py` — CRUD routes with TestClient, MongoDB mocked with mongomock

### Frontend (Vitest + React Testing Library)
- Component unit tests for `FileTree`, `MessageBubble`, `SourceRef`, `ProjectCard`
- API client tests with mock service worker (MSW)
- Integration tests for upload flow and chat flow

### Test Fixtures
- `tests/fixtures/safe_repo.zip` — a small, safe synthetic repository
- `tests/fixtures/traversal_attack.zip` — a ZIP with `../../` paths (must be rejected)
- `tests/fixtures/zip_bomb.zip` — a highly compressed file (must be rejected)

### No test passes before execution
Tests are only marked passing after actually running `pytest` and `vitest`. The plan
does not claim anything passes in advance.

---

## Environment Variable Requirements

```
# Backend — required
MONGODB_URI=                     # MongoDB connection string
LLM_PROVIDER=                    # openai | anthropic | ollama
OPENAI_API_KEY=                  # if LLM_PROVIDER=openai
ANTHROPIC_API_KEY=               # if LLM_PROVIDER=anthropic

# Backend — optional with defaults
OPENAI_MODEL=gpt-4o-mini
ANTHROPIC_MODEL=claude-3-haiku-20240307
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=codellama
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
MAX_ZIP_SIZE_MB=50
MAX_FILES_PER_PROJECT=5000
MAX_FILE_SIZE_KB=500
SANDBOX_BASE_PATH=/tmp/codemind
VECTOR_STORE_PATH=./data/chroma
CORS_ORIGINS=http://localhost:5173

# Frontend — Vite public env vars
VITE_API_BASE_URL=http://localhost:8000
```

---

## Development Phases

---

### Phase 1 — Project Scaffold and Startup [ ] pending

**Intent:** Establish the project skeleton so both frontend and backend start
correctly and developers can verify the toolchain.

**Expected Outcomes:**
- `cd frontend && npm run dev` serves the React app on port 5173 with no errors
- `cd backend && uvicorn main:app --reload` starts on port 8000 with no errors
- `GET /api/health` returns `{ "status": "ok" }`
- TypeScript compiles with no errors
- Tailwind and shadcn/ui render correctly in the browser

**Todo List:**
1. Create `codemind-ai/` root with `.gitignore`, `.env.example`, `README.md`
2. Scaffold frontend: `npm create vite@latest`, configure TypeScript, Tailwind, shadcn/ui, React Router, Lucide React, React Flow
3. Scaffold backend: create virtual env, `requirements.txt` (FastAPI, uvicorn, motor, pydantic, python-dotenv, httpx, pytest, pytest-asyncio)
4. Create `config.py` using Pydantic `BaseSettings`
5. Create `database.py` with Motor async client
6. Create `main.py` with health check route and CORS middleware
7. Create `HomePage.tsx` shell (empty project list placeholder)
8. Confirm both start without errors

**Relevant Context:** Entry points are `backend/main.py` and `frontend/src/main.tsx`

**Acceptance Criteria:**
- Both servers start without errors
- Health check returns 200
- No TypeScript compile errors
- Tailwind styles are applied

---

### Phase 2 — Project CRUD and Dashboard [ ] pending

**Intent:** Allow users to create and manage projects, giving the UI its first real
interactive surface.

**Expected Outcomes:**
- Users can create, list, and delete projects from the dashboard
- Projects persist in MongoDB across server restarts
- Project status chip shows current state

**Todo List:**
1. Implement `projects` router (`POST`, `GET`, `DELETE /api/projects`, `GET /api/projects/{id}`)
2. Define `Project` Pydantic model and MongoDB document structure
3. Implement `ProjectCard`, `ProjectForm` components
4. Connect `HomePage` to the projects API
5. Write `test_projects.py` covering all four routes
6. Run tests and confirm all pass

**Relevant Context:** `backend/routers/projects.py`, `backend/models/project.py`, `frontend/src/pages/HomePage.tsx`

**Acceptance Criteria:**
- CRUD operations work end-to-end
- Projects persist in MongoDB
- All `test_projects.py` tests pass when executed

---

### Phase 3 — ZIP Ingestion and Safety [ ] pending

**Intent:** Allow users to upload a repository ZIP. The backend must extract it
safely into a sandbox and reject all malicious inputs.

**Expected Outcomes:**
- Valid ZIPs are accepted, extracted, and project status transitions to `ingesting`
- Path traversal, ZIP bombs, and dangerous extensions are rejected with 400 errors
- No uploaded file is ever executed

**Todo List:**
1. Implement `ingest` router (`POST /api/projects/{id}/ingest`, `GET .../status`)
2. Implement `ingest_service.py`: validation, sandbox extraction, safety checks
3. Implement `ingestion_worker.py` background task (asyncio)
4. Create test fixtures: `safe_repo.zip`, `traversal_attack.zip`, `zip_bomb.zip`
5. Write `test_ingest.py` covering all safety checks and the happy path
6. Run tests and confirm all pass

**Relevant Context:** `backend/services/ingest_service.py`, `backend/workers/ingestion_worker.py`

**Acceptance Criteria:**
- All security rejection tests pass
- Safe ZIP is extracted to sandbox
- Status polling reflects progress
- All `test_ingest.py` tests pass when executed

---

### Phase 4 — File Listing, Language Detection, and Explorer [ ] pending

**Intent:** Populate `file_records` in MongoDB and expose the file tree to the
frontend. Give users safe, read-only access to repository files.

**Expected Outcomes:**
- `GET /api/projects/{id}/files` returns all indexed file records
- `GET /api/projects/{id}/files/{path}` returns sanitized file content
- `ExplorerPage` displays file tree with language badges
- Path traversal in file viewer API is rejected

**Todo List:**
1. Extend `ingestion_worker.py` to walk files, detect languages, and write `file_records`
2. Implement `analysis` router: file listing and file content endpoints
3. Implement `FileTree`, `FileViewer`, `LanguageBadge` components
4. Build `ExplorerPage`
5. Write `test_analysis.py` covering language detection and path safety
6. Run tests and confirm all pass

**Relevant Context:** `backend/services/analysis_service.py`, `frontend/src/pages/ExplorerPage.tsx`

**Acceptance Criteria:**
- File tree renders in UI after ingestion
- Syntax-highlighted file viewer works
- Path traversal attempts return 403
- All `test_analysis.py` tests pass when executed

---

### Phase 5 — Static Analysis and Project Overview [ ] pending

**Intent:** Run Python AST and Tree-sitter analysis to extract symbols, imports,
and build a basic dependency graph. Generate a plain-language project overview.

**Expected Outcomes:**
- `GET /api/projects/{id}/analysis` returns language breakdown, detected frameworks, summary
- `GET /api/projects/{id}/graph` returns node/edge data
- `ProjectPage` displays the overview and a basic graph

**Todo List:**
1. Implement Python AST symbol extraction in `analysis_service.py`
2. Integrate Tree-sitter for JS/TS import extraction
3. Build import/dependency graph from extracted relationships
4. Generate LLM-based project summary (prompt uses only file tree + language stats, not full source)
5. Implement `VizPage` with React Flow graph
6. Implement `ProjectPage` with summary panel
7. Extend `test_analysis.py` with AST and graph tests
8. Run tests and confirm all pass

**Relevant Context:** `backend/services/analysis_service.py`, `frontend/src/pages/VizPage.tsx`

**Acceptance Criteria:**
- Symbol extraction works for Python and JS/TS files
- Architecture graph renders in React Flow
- Project summary is displayed
- All new analysis tests pass when executed

---

### Phase 6 — Semantic Indexing and RAG Chat [ ] pending

**Intent:** Chunk and embed the repository. Enable the core Q&A feature with
source-code references grounded in retrieved chunks.

**Expected Outcomes:**
- After ingestion, all text files are chunked, embedded, and stored in ChromaDB
- `POST /api/projects/{id}/chat` returns a streamed AI response with source refs
- Every cited file path is validated against `file_records`
- Source refs appear as clickable chips in the frontend

**Todo List:**
1. Implement `index_service.py`: chunking, embedding, ChromaDB storage
2. Integrate embedding into `ingestion_worker.py` pipeline
3. Implement `ai_service.py`: `LLMProvider` protocol + OpenAI/Anthropic/Ollama implementations
4. Implement RAG prompt assembly with budget-aware context packing
5. Implement source ref validation post-generation
6. Implement `ai` router with SSE streaming
7. Build `ChatPage`, `ChatPanel`, `MessageBubble`, `SourceRef` components
8. Write `test_ai.py`: mock LLM, verify prompt structure, verify source ref validation
9. Run tests and confirm all pass

**Relevant Context:** `backend/services/index_service.py`, `backend/services/ai_service.py`, `frontend/src/pages/ChatPage.tsx`

**Acceptance Criteria:**
- Chat answers reference actual project files and line numbers
- Invalid file references are stripped before display
- Streaming works in the UI
- All `test_ai.py` tests pass when executed

---

### Phase 7 — Contextual Debugging [ ] pending

**Intent:** Let users paste an error message and receive a grounded explanation
that cites relevant code from their repository.

**Expected Outcomes:**
- `POST /api/projects/{id}/debug` accepts error text and returns an explanation with source refs
- `DebugPage` renders the explanation with highlighted file/line references

**Todo List:**
1. Implement debug endpoint in `ai` router
2. Build debug-specific prompt template (error + retrieved context)
3. Build `DebugPage`, `ErrorInput`, `DebugPanel` components
4. Extend `test_ai.py` with debug endpoint tests
5. Run tests and confirm all pass

**Acceptance Criteria:**
- Error explanations cite actual project files
- UI renders debug panel correctly
- All new debug tests pass when executed

---

### Phase 8 — Interactive Learning Mode [ ] pending

**Intent:** Provide guided explanations and project-specific quizzes to support
developers learning an unfamiliar codebase.

**Expected Outcomes:**
- `POST /api/projects/{id}/learn` returns a concept explanation with related files
- `POST /api/projects/{id}/learn/quiz` returns generated quiz questions
- `LearnPage` renders explanations and a working quiz UI

**Todo List:**
1. Implement learn and quiz endpoints in `ai` router
2. Build learn and quiz prompt templates
3. Build `LearnPage`, `LearnPanel`, `QuizCard` components
4. Extend `test_ai.py` with learn/quiz tests
5. Run tests and confirm all pass

**Acceptance Criteria:**
- Explanations reference actual project code
- Quiz questions have correct answer metadata
- UI renders quiz and handles answer selection
- All new learn tests pass when executed

---

### Phase 9 — Docker and Production Readiness [ ] pending

**Intent:** Containerize the application so it runs consistently in any environment.

**Expected Outcomes:**
- `docker compose up` starts MongoDB, ChromaDB, backend, and frontend
- No secrets are baked into images
- All environment variables injected at container startup

**Todo List:**
1. Write `backend/Dockerfile`
2. Write `frontend/Dockerfile`
3. Write `docker-compose.yml` with MongoDB, backend, frontend services
4. Confirm all env vars flow through compose file
5. Confirm full test suite passes inside the container
6. Add `.dockerignore` files

**Acceptance Criteria:**
- `docker compose up` starts all services cleanly
- Application is fully functional in the containerized environment
- No secrets in images or compose files

---

## Major Technical Risks and Practical Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| ZIP path traversal attack | High (if unmitigated) | Critical | Validate every entry path before extraction; enforce sandbox; tested with attack fixtures |
| LLM prompt injection via malicious source code | Medium | High | Wrap retrieved code in delimiters; sanitize before insertion |
| Context window overflow | Medium | Medium | Budget-aware context packing; enforce token limits before LLM call |
| Embedding API cost on large repos | Medium | Medium | Skip binary files; enforce file and chunk count limits; cache embeddings by content hash |
| MongoDB unavailable at startup | High (dev) | High | `config.py` validates connection at startup with a clear error message |
| LLM API key not configured | High (new dev) | High | `config.py` fails fast with a human-readable message listing missing vars |
| Tree-sitter segfault or memory issue | Low | Medium | Parse files with timeout + try/except; skip files that fail |
| ChromaDB data loss on restart | Low | Medium | Mount `VECTOR_STORE_PATH` as a persistent volume; document this clearly |
| Slow ingestion blocking HTTP request | Medium | High | Background worker + status polling; ingestion never blocks the upload response |
| Large monorepo exhausts disk space | Low | High | Enforce decompressed size limit; delete sandbox on project deletion |

---

## Assumptions

1. The developer will supply at least one LLM API key (OpenAI, Anthropic, or a
   running Ollama instance) before running Phase 6+.
2. MongoDB is either running locally or a connection string (e.g., MongoDB Atlas)
   will be provided. No authentication layer is required for MVP.
3. The developer's machine runs Node.js 18+ and Python 3.11+.
4. Files are encoded in UTF-8 or ASCII. Binary detection will skip non-text files.
5. GitHub integration is explicitly out of scope for this plan.
