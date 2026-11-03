# Helpdesk AI

A full-stack internal helpdesk for a small company. Employees raise tickets and read a knowledge base. Agents handle tickets and maintain the knowledge base. An AI assistant answers questions from published articles, and a LangGraph workflow drafts ticket replies that an agent must approve. The assistant also accepts voice input through a local Whisper model.

## Features / Core Modules

**1. Helpdesk core**
- Employee, agent and superior-agent roles, with JWT login.
- Tickets with categories, priorities, comments (public and internal) and an enforced status lifecycle.
- A knowledge base of articles (draft or published) that agents write and employees read.
- User management: only the superior agent (the seeded agent) can change roles or activate and deactivate users.
- Business rules live in a service layer, so the API and the AI follow the same rules.

**2. RAG assistant (LangChain)**
- Chat sessions with stored history.
- Searches published articles by meaning (Gemini embeddings, pgvector, cosine similarity) and answers with cited sources.
- A tool that looks up the logged-in user's own tickets. The model cannot choose whose tickets it reads.
- Unpublishing or deleting an article removes it from search.

**3. AI triage workflow (LangGraph)**
- An agent starts a triage run on a ticket.
- The graph classifies the ticket and searches the knowledge base in parallel, then routes by the result.
- If the articles answer the ticket, it drafts a reply and pauses. The agent approves, edits or rejects it. Only then is a public comment posted.
- If not, the ticket is handed off with a summary and a suggested priority.
- The paused state is stored in PostgreSQL (checkpointer), so it survives a server restart.

**4. Voice input**
- A mic button in the assistant's chat. Speech is transcribed locally by faster-whisper (Whisper `small`, CPU, English only).
- The transcript goes into the input box. The user edits it and presses Send, just like typed text.
- Audio is processed in memory and never stored.

**5. React frontend**
- Pages for login and registration, tickets, articles, the assistant, categories, users and the triage panel. Plain CSS, no UI library.

## Tech Stack

| Area | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic |
| Database | Neon PostgreSQL, pgvector |
| Auth | JWT (PyJWT), argon2 password hashing |
| AI | LangChain, LangGraph (Postgres checkpointer), Google Gemini (chat and embeddings) |
| Speech-to-text | faster-whisper (Whisper `small`) |
| Frontend | React, Vite, React Router, plain CSS |

## Project Structure

```
helpdesk/
├── backend/
│   ├── app/
│   │   ├── main.py        # app, routers, error handler, startup (checkpointer, speech model)
│   │   ├── core/          # settings, exceptions, security
│   │   ├── db/            # async engine and session
│   │   ├── models/        # SQLAlchemy tables
│   │   ├── schemas/       # request and response shapes
│   │   ├── repositories/  # database queries
│   │   ├── services/      # business rules and permissions
│   │   ├── ai/            # embeddings, chat model, prompts, tools, speech, triage graph
│   │   └── api/           # dependencies and v1 routes
│   ├── scripts/           # seed and helper scripts
│   ├── alembic/           # database migrations
│   ├── .env.example
│   └── requirements.txt
├── frontend/              # React app (src/pages, src/components, src/api.js)
├── README.md
└── .gitignore
```

Request flow: route → service → repository → model. Routes contain no business rules, and repositories know nothing about users. The AI tools and graph nodes call the same services as the API.

## Setup & Installation

**Requirements:** Python 3.12 (3.11 or later is required), a current Node.js LTS, a Neon project, and a Google Gemini API key. The commands below are for Windows PowerShell.

**1. Backend** (run everything from `backend/`)
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env              # then fill in the values
```
Fill in `.env`:

| Variable | Meaning |
|---|---|
| `DATABASE_URL` | Neon **direct** connection, used by Alembic |
| `DATABASE_URL_POOLED` | Neon **pooled** connection (host contains `-pooler`), used by the app |
| `SECRET_KEY` | generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | token lifetime (default 30) |
| `SEED_AGENT_EMAIL`, `SEED_AGENT_PASSWORD` | the first agent (the superior agent). You choose the password |
| `GEMINI_API_KEY` | Google Gemini key |
| `CHAT_MODEL`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSIONS` | `gemini-3.5-flash-lite`, `gemini-embedding-001`, `768` |

Both Neon URLs use the asyncpg format: `postgresql+asyncpg://USER:PASSWORD@HOST/DB?ssl=require`.

```powershell
alembic upgrade head
python -m scripts.seed_agent        # creates the first agent from .env
uvicorn app.main:app --reload
```
- `alembic upgrade head` also enables the `vector` extension.
- The LangGraph checkpoint tables are created automatically when the app starts.
- **The first start downloads the Whisper `small` model, so it needs internet.**
- `requirements.txt` pins `av<19`, because PyAV 19 breaks faster-whisper 1.2.1.

**2. Frontend** (a second terminal, from `frontend/`)
```powershell
npm install
npm run dev
```
Open http://localhost:5173. The dev server forwards `/api` to the backend on port 8000, so no CORS setup is needed.

## Usage / API Documentation

- **Swagger UI:** http://127.0.0.1:8000/docs. All routes are under `/api/v1`.
- **Seeded agent:** the email and password you set in `SEED_AGENT_EMAIL` and `SEED_AGENT_PASSWORD`. The repository ships no default password.
- **Log in:** the login form field is called `username`, and it takes the **email**. In Swagger, click **Authorize** and enter the email and password.
- **Employees:** anyone can register at `POST /auth/register` (or on the Register page). Registration only creates employees.

**Suggested test flow in Swagger**
1. As the agent: `POST /categories`, then `POST /articles`, then `PATCH /articles/{id}/status` with `published`.
2. As an employee: `GET /articles`, then `POST /tickets`.
3. As an employee: `POST /chat/sessions`, then `POST /chat/sessions/{id}/messages` with a question about the article. The answer includes `sources`.
4. As the agent: `POST /tickets/{id}/triage-runs`, then `POST /triage-runs/{id}/decision` with `{"action": "edit", "text": "..."}`. The employee sees the reply in `GET /tickets/{id}/comments`.
5. As the superior agent: `PATCH /users/{id}/role` and `PATCH /users/{id}/active`.

| Group | Endpoints |
|---|---|
| Auth and users | `/auth/register`, `/auth/login`, `/users/me`, `/users` |
| Categories | `/categories` |
| Tickets and comments | `/tickets`, `/tickets/{id}/status`, `/tickets/{id}/assignee`, `/tickets/{id}/comments` |
| Articles | `/articles`, `/articles/{id}/status` |
| Assistant | `/chat/sessions`, `/chat/sessions/{id}/messages` |
| Voice | `/speech/transcribe` |
| Triage | `/tickets/{id}/triage-runs`, `/triage-runs/{id}`, `/triage-runs/{id}/decision` |

## Scripts

Run from `backend/` as `python -m scripts.<name>`.

| Script | Purpose |
|---|---|
| `seed_agent` | Creates the first agent (the superior agent) from `.env` |
| `reindex_articles` | Indexes published articles that were created before indexing existed |
| `try_day8 "question"` | Tests article search from the command line |
| `try_day12` | Runs the triage graph without the API (`start` and `resume` modes) |
| `try_stt <audio file>` | Tests the Whisper model on an audio file |

On Windows, scripts that use the triage checkpointer set the selector event-loop policy, because async `psycopg` does not work on the default Windows event loop.

## Known Limitations & Future Roadmap

**Known limitations**
- The Gemini free tier has quotas, and free-tier data may be used by Google, so use test data only.
- The access token lasts 30 minutes and there are no refresh tokens. After that, the user logs in again.
- An agent who chats with the assistant sees all tickets through the ticket tool.
- Answer sources list every article the search returned, not only the ones the model used.
- Voice input transcribes on the server's CPU, so it takes a few seconds per recording. English only.
- Lists use Previous / Next pagination (the API returns no totals).
- Known race conditions, rare and accepted: two agents starting a triage run on one ticket at the same instant, and two registrations with the same email at the same instant.
- A server crash during a triage run leaves it marked `running`.
- CORS is not enabled. The frontend relies on the Vite dev proxy, so hosting it on a different address needs CORS or a reverse proxy.
- No automated tests, Docker setup or request logging yet.

**Roadmap**
- BM25 hybrid search (keyword plus vector).
- Streaming voice input.
- Tests for the service rules, a Dockerfile and request logging.
- Refresh tokens.
- A database constraint for "one active triage run per ticket".



