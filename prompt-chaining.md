# CodeMind AI — MVP Prompt Chaining Guide

**Stack:** React + Vite + TypeScript + Tailwind + shadcn/ui | FastAPI + Python 3.11 | MongoDB Atlas | ChromaDB embedded | OpenAI GPT-4o-mini

**Rule:** Complete one prompt fully, verify it works, then move to the next. Never skip ahead.

---

## PROMPT 1 — Full Project Scaffold

> **Paste this into Agent mode as-is.**

```
You are building CodeMind AI from scratch. The workspace is empty.

## Task: Create the complete project scaffold with the correct tech stack installed and configured. Do NOT implement any features yet.

### Root layout
Create this structure:
codemind-ai/
  .gitignore
  .env.example
  README.md
  frontend/
  backend/

### .gitignore
Must include: .env, __pycache__, *.pyc, node_modules, dist, .chroma, *.egg-info, .venv, venv

### .env.example (key names only, no values)
MONGODB_URI=
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
SANDBOX_BASE_PATH=/tmp/codemind
VECTOR_STORE_PATH=./data/chroma
CORS_ORIGINS=http://localhost:5173
MAX_ZIP_SIZE_MB=50
MAX_FILES_PER_PROJECT=5000
MAX_FILE_SIZE_KB=500
VITE_API_BASE_URL=http://localhost:8000

### Frontend scaffold (inside frontend/)
- Vite + React + TypeScript
- Tailwind CSS v3
- shadcn/ui (init with default style, slate base color, CSS variables)
- lucide-react
- react-router-dom v6
- react-flow-renderer (or @xyflow/react)
- axios
- Vitest + @testing-library/react for tests

package.json scripts must include: dev, build, test, lint

### Backend scaffold (inside backend/)
Create these files with correct content:

requirements.txt must include:
fastapi>=0.111
uvicorn[standard]>=0.29
motor>=3.4
pydantic>=2.7
pydantic-settings>=2.3
python-dotenv>=1.0
httpx>=0.27
openai>=1.30
chromadb>=0.5
tiktoken>=0.7
python-multipart>=0.0.9
pytest>=8.2
pytest-asyncio>=0.23
mongomock>=4.1
tree-sitter>=0.22
tree-sitter-python>=0.21
tree-sitter-javascript>=0.21

Create backend/config.py:
- Use pydantic BaseSettings
- Load all vars from .env
- Fail fast with a clear error if MONGODB_URI or OPENAI_API_KEY is missing

Create backend/database.py:
- Motor AsyncIOMotorClient
- get_database() async function returning the db instance
- Connection string from config

Create backend/main.py:
- FastAPI app with CORSMiddleware (origins from config)
- GET /api/health returns {"status": "ok", "version": "0.1.0"}
- Include all routers (stub routers for now)
- Startup event: verify DB connection, print clear error if it fails

Create backend/routers/__init__.py (empty)
Create stub routers: backend/routers/projects.py, ingest.py, analysis.py, ai.py
Each stub router has an APIRouter and one placeholder GET / route returning {"status": "stub"}

Create backend/models/__init__.py (empty)
Create backend/services/__init__.py (empty)
Create backend/workers/__init__.py (empty)
Create backend/tests/__init__.py (empty)

### Frontend entry files
frontend/src/main.tsx — mounts App with BrowserRouter
frontend/src/App.tsx — single route "/" rendering <div>CodeMind AI — scaffold ready</div>
frontend/src/router.tsx — React Router routes placeholder

### Acceptance criteria
- cd backend && pip install -r requirements.txt && uvicorn main:app --reload starts with no errors
- GET http://localhost:8000/api/health returns {"status":"ok","version":"0.1.0"}
- cd frontend && npm install && npm run dev starts with no errors on port 5173
- npm run build completes with no TypeScript errors
- Browser shows "CodeMind AI — scaffold ready"
```

---

## PROMPT 2 — Project CRUD + Dashboard UI

> **Only run after Prompt 1 is fully working.**

```
CodeMind AI — implement Project CRUD backend and Dashboard frontend.

### Backend

backend/models/project.py — Pydantic models:
- ProjectStatus enum: created | ingesting | indexed | error
- ProjectCreate: name (str, 3-50 chars), description (str, optional, max 200 chars)
- ProjectDocument: id, name, description, status, created_at, updated_at, languages[], frameworks[], file_count, total_lines, error_message

backend/routers/projects.py — replace stub with real routes:
- POST   /api/projects        — create project, insert into MongoDB projects collection
- GET    /api/projects        — list all projects, sorted by created_at desc
- GET    /api/projects/{id}   — get single project, 404 if not found
- DELETE /api/projects/{id}   — delete project doc, return 204

All routes use async Motor. Validate ObjectId format (return 422 if invalid).

backend/tests/test_projects.py:
- Use pytest + httpx AsyncClient + mongomock
- Test: create project, list returns it, get by id, delete removes it, get after delete is 404
- Run pytest backend/tests/test_projects.py and confirm all pass before finishing

### Frontend

frontend/src/api/projects.ts — typed axios functions:
  createProject(data), listProjects(), getProject(id), deleteProject(id)

frontend/src/types/project.ts — TypeScript interfaces matching backend models

frontend/src/pages/HomePage.tsx:
- List projects as cards
- "New Project" button opens a modal form (name + description)
- Each card shows name, status chip (color-coded), created date, delete button with confirm
- Loading skeleton while fetching
- Empty state illustration when no projects exist

Use shadcn/ui Card, Button, Dialog, Input, Badge, Skeleton components.

### Acceptance criteria
- Create a project from the UI, it persists on page reload
- Delete removes it from the list
- All test_projects.py tests pass (show the pytest output)
```

---

## PROMPT 3 — ZIP Ingestion with Security

> **Only run after Prompt 2 is fully working.**

```
CodeMind AI — implement secure ZIP ingestion.

### Security rules (MUST enforce all of these)
1. Reject if Content-Type is not application/zip or application/octet-stream
2. Reject if decompressed size > MAX_ZIP_SIZE_MB (read from config)
3. Reject if file count > MAX_FILES_PER_PROJECT (read from config)
4. Reject any ZIP entry whose resolved path escapes the sandbox directory
5. Reject any entry that is a symlink
6. Reject entries with extensions: .exe .sh .bat .cmd .ps1 .msi .dll .so .dylib
7. Never execute any extracted file
8. Extract only to SANDBOX_BASE_PATH/{project_id}/

### backend/services/ingest_service.py
Functions:
- validate_zip(file_bytes: bytes, project_id: str) -> None  # raises HTTPException on violation
- extract_zip(file_bytes: bytes, project_id: str) -> Path   # returns sandbox path
Both functions are synchronous (called from async context via run_in_executor).

### backend/workers/ingestion_worker.py
- async run_ingestion(project_id: str, file_bytes: bytes) -> None
- Updates project status to "ingesting" at start
- Calls validate_zip then extract_zip
- On success: updates status to "indexed" (file analysis added in Prompt 4)
- On any error: updates project status to "error", stores error_message in DB

### backend/routers/ingest.py — replace stub:
- POST /api/projects/{id}/ingest
  - Accept multipart file upload (UploadFile)
  - Read file bytes, validate project exists
  - Launch run_ingestion as asyncio background task
  - Return {"status": "queued", "project_id": id} immediately
- GET /api/projects/{id}/ingest/status
  - Return current project status and error_message from MongoDB

### backend/tests/test_ingest.py
Create three test ZIP fixtures programmatically inside the test file:
- make_safe_zip() — a valid ZIP with two .py files
- make_traversal_zip() — a ZIP with entry path "../../etc/passwd"
- make_zip_bomb() — a ZIP where decompressed size exceeds the limit

Tests:
- Safe ZIP passes validation
- Traversal ZIP raises 400
- Zip bomb raises 400
- Dangerous extension (.sh) raises 400
- Symlink entry raises 400

Run pytest backend/tests/test_ingest.py and confirm all pass before finishing.

### Frontend
frontend/src/components/projects/UploadZip.tsx:
- Drag-and-drop or click-to-select, .zip files only
- Shows upload progress bar
- Polls /ingest/status every 2 seconds until status is "indexed" or "error"
- Shows success or error state

Add Upload button to ProjectPage that opens UploadZip component.
Create frontend/src/pages/ProjectPage.tsx with project name, status, and upload section.
Add route /projects/:id to router.

### Acceptance criteria
- Upload a real .zip — status transitions from queued → ingesting → indexed
- All security rejection tests pass (show pytest output)
- Status polling works in the UI
```

---

## PROMPT 4 — File Explorer + Language Detection

> **Only run after Prompt 3 is fully working.**

```
CodeMind AI — implement file indexing, language detection, and the file explorer.

### backend/services/analysis_service.py
Functions:
- detect_language(file_path: str) -> str
  Map extensions: .py→Python, .ts/.tsx→TypeScript, .js/.jsx→JavaScript,
  .java→Java, .go→Go, .rs→Rust, .md→Markdown, .json→JSON, .yaml/.yml→YAML, else→Unknown
- is_binary(file_bytes: bytes) -> bool
  Check first 512 bytes for null bytes
- walk_project_files(sandbox_path: Path, project_id: str) -> list[FileRecord]
  Walk directory, skip: node_modules, .git, __pycache__, dist, build, .next
  Skip files > MAX_FILE_SIZE_KB
  Skip binary files
  Return list of FileRecord dicts

### backend/models/file_record.py
FileRecord Pydantic model: project_id, path (relative, str), language, size_bytes, line_count, is_binary, indexed_at

### Extend backend/workers/ingestion_worker.py
After successful extraction:
- Call walk_project_files
- Insert all FileRecord docs into file_records collection
- Update project languages[] and file_count in projects collection

### backend/routers/analysis.py — replace stub:
- GET /api/projects/{id}/files
  Return list of file records for project, sorted by path
- GET /api/projects/{id}/files/{file_path:path}
  SECURITY: resolve file_path relative to sandbox, verify result is inside sandbox
  Return 403 if path escapes sandbox
  Return {"path": str, "language": str, "content": str, "line_count": int}
  Never serve binary files (return 400)

### backend/tests/test_analysis.py
- Language detection returns correct language for each extension
- Binary detection identifies binary files
- File list returns expected files after ingestion
- Path traversal in file viewer returns 403
Run pytest backend/tests/test_analysis.py and confirm all pass.

### Frontend
frontend/src/components/explorer/FileTree.tsx
- Recursive tree from file records API
- Folders collapsible, files clickable
- LanguageBadge next to each file

frontend/src/components/explorer/FileViewer.tsx
- Fetch file content from API on click
- Syntax-highlighted read-only view (use highlight.js or prism via a simple wrapper)
- Show line numbers
- Never allow editing

frontend/src/components/explorer/LanguageBadge.tsx
- Color-coded pill for each language

frontend/src/pages/ExplorerPage.tsx
- Left panel: FileTree
- Right panel: FileViewer
- Route: /projects/:id/explorer

### Acceptance criteria
- Upload a ZIP, navigate to explorer, see file tree
- Click a file, see syntax-highlighted content
- Language badges are correct
- Path traversal in file viewer API returns 403 (show pytest output)
```

---

## PROMPT 5 — RAG Chat with Source References (Core MVP Feature)

> **Only run after Prompt 4 is fully working. This is the most important prompt.**

```
CodeMind AI — implement semantic indexing and RAG-powered chat with source references.

### backend/services/index_service.py
- chunk_file(content: str, file_path: str, language: str) -> list[Chunk]
  Split into ~400 token chunks (use tiktoken cl100k_base)
  Overlap: 50 tokens
  Each Chunk has: text, file_path, start_line, end_line, language
- embed_chunks(chunks: list[Chunk], project_id: str) -> None
  Call OpenAI text-embedding-3-small API
  Store in ChromaDB collection named "project_{project_id}"
  Metadata per chunk: file_path, start_line, end_line, language
- retrieve_chunks(query: str, project_id: str, k: int = 6) -> list[Chunk]
  Embed query, query ChromaDB, return top-k chunks with metadata

### Extend ingestion_worker.py
After file records are saved:
- For each non-binary file: chunk and embed
- Update project status to "indexed" only after all embeddings are stored

### backend/services/ai_service.py
- assemble_prompt(question: str, chunks: list[Chunk], project_summary: str) -> list[dict]
  System prompt instructs LLM to:
    - Answer only from provided context
    - Cite file path and line numbers for every claim
    - Say "I don't have enough context" if context is insufficient
    - Never invent file names
  Wrap each chunk in <source file="..." lines="..."> tags
  Budget: system ~300 tokens + project summary ~200 + chunks ~2500 + history ~500 = stay under 4000 total
- stream_chat(question: str, project_id: str, history: list) -> AsyncIterator[str]
  Call retrieve_chunks
  Call assemble_prompt
  Call OpenAI chat completions with stream=True
  Yield tokens

- validate_source_refs(response: str, project_id: str) -> str
  Parse file references from response
  Check each cited file exists in file_records for this project
  Remove or mark invalid references

### backend/models/chat_message.py
ConversationDocument: id, project_id, created_at
MessageDocument: role (user|assistant), content, source_refs[], timestamp
SourceRef: file, start_line, end_line, snippet (first 80 chars of chunk)

### backend/routers/ai.py — replace stub:
- POST /api/projects/{id}/chat
  Body: {question: str, conversation_id: str | null}
  Create or load conversation from MongoDB
  Save user message
  Stream response via StreamingResponse (SSE format: data: {token}\n\n)
  After stream completes: save assistant message with validated source refs
  Return conversation_id in first SSE event

- GET /api/projects/{id}/chat/{conversation_id}
  Return full conversation history

### backend/tests/test_ai.py
Use unittest.mock to mock openai.AsyncOpenAI:
- Test assemble_prompt includes chunks correctly
- Test stream_chat calls retrieve_chunks and LLM
- Test validate_source_refs strips invalid file references
- Test validate_source_refs keeps valid file references
Run pytest backend/tests/test_ai.py and confirm all pass.

### Frontend
frontend/src/api/ai.ts — streamChat(projectId, question, conversationId) using fetch SSE

frontend/src/components/chat/ChatPanel.tsx
- Message history with user/assistant distinction
- Streaming: append tokens in real time as SSE arrives
- Input box with send button (Enter to send)

frontend/src/components/chat/MessageBubble.tsx
- Render markdown (use react-markdown)
- Show SourceRef chips below assistant messages

frontend/src/components/chat/SourceRef.tsx
- Collapsible chip: filename + line range
- Click navigates to ExplorerPage at that file

frontend/src/pages/ChatPage.tsx
- Route: /projects/:id/chat

### Acceptance criteria
- Upload a Python or JS project ZIP
- Ask "What does this project do?" — get an answer citing actual files
- Ask "Explain the main function" — get answer with file + line reference
- Source ref chip navigates to the correct file in the explorer
- Invalid file references are not shown
- All test_ai.py tests pass (show pytest output)
```

---

## PROMPT 6 — Tests, Polish, and MVP Verification

> **Only run after Prompt 5 is fully working.**

```
CodeMind AI — final MVP hardening, missing tests, and end-to-end verification.

### Complete any missing tests
Run the full test suite:
  cd backend && pytest --tb=short -q

Fix any failing tests. Do not mark tests as passing until pytest output confirms it.

### Frontend tests
Set up Vitest in frontend/.
Write tests for:
- ProjectCard renders name and status correctly
- SourceRef renders file name and line range
- FileTree renders a nested structure correctly

Run: cd frontend && npm run test

### Security audit — verify these are enforced
1. File viewer API: test that /api/projects/{id}/files/../../etc/passwd returns 403
2. ZIP traversal: confirmed in test_ingest.py
3. No .env file exists in the repo (only .env.example)
4. config.py raises on missing MONGODB_URI or OPENAI_API_KEY

### README.md
Write a concise README with:
- Project description (2 sentences)
- Prerequisites: Node 18+, Python 3.11+, MongoDB Atlas URI, OpenAI API key
- Setup steps for backend (venv, pip install, copy .env.example to .env, fill values, uvicorn)
- Setup steps for frontend (npm install, copy .env.example, npm run dev)
- How to run tests (pytest, npm run test)

### Final acceptance checklist (verify each one)
- [ ] Both servers start with no errors
- [ ] GET /api/health returns 200
- [ ] Create a project from the UI
- [ ] Upload a ZIP — status reaches "indexed"
- [ ] File explorer shows the tree and file content
- [ ] Ask a chat question — answer cites real files
- [ ] Source ref chip works
- [ ] All backend tests pass (show full pytest output)
- [ ] All frontend tests pass (show vitest output)
- [ ] No secrets in any committed file
```

---

## Chaining Rules

1. **One prompt at a time.** Do not paste Prompt 2 until Prompt 1 acceptance criteria are met.
2. **Show test output.** Every prompt that writes tests requires showing the actual pytest / vitest output before calling it done.
3. **No skipping.** If a prompt is only partially done, finish it before moving on.
4. **Security is non-negotiable.** The ZIP security checks and file viewer path validation must pass on every prompt that touches them.
5. **No secrets committed.** Before finishing any prompt, verify `.env` is in `.gitignore`.
