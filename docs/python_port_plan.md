Perfect. Here's your **full swarm-ready project plan**, structured with:

* ✅ Actionable task blocks
* 🚫 Negative prompts to *ward off derailments*
* 🔁 Interfaces + shared protocols to avoid merge hell
* 🧱 Foundation stack assumptions baked in

---

# 🐜 Puppet Engine Port: Swarm Project Plan (Codename: *Marionette*)

> Port legacy Puppet Engine (NodeJS) to a fully async, Python-native architecture using FastAPI, `asyncio`, and SQLite. Preserve behavior/state fidelity. Modernize structure for Letta compatibility.

---

## 🏗️ System Stack

| Component     | Stack                                  |
| ------------- | -------------------------------------- |
| Web API       | `FastAPI`, `pydantic`, `uvicorn`       |
| Async Tasks   | `asyncio`, custom queues               |
| Memory Layer  | `SQLite` + `SQLiteWriteQueue` buffer   |
| LLM Support   | `openai`, (later) `grok` custom client |
| Twitter       | `tweepy`                               |
| Solana        | `solana-py`                            |
| Scheduling    | `apscheduler`                          |
| Auth (future) | `python-jose`, JWT                     |
| Testing       | `pytest`, `httpx`, `pytest-asyncio`    |

---

## 🧩 Directory Layout

```plaintext
marionette/
├── api/               # FastAPI routes + models
├── agents/            # Agent manager, mood model, prompt logic
├── memory/            # SQLite + buffered write queue
├── llm/               # OpenAI + Grok clients
├── events/            # Event engine
├── twitter/           # Tweet + reply logic
├── solana/            # Wallet + tx handling
├── config/            # Pydantic-driven settings
├── tests/             # Pytest suite
└── main.py            # App entrypoint
```

---

## 🧠 Agent + Memory Data Model (Key Types)

* `Agent`
* `Personality`
* `StyleGuide`
* `MemoryItem`
* `Relationship`
* `Event`

All `@dataclass` or `pydantic.BaseModel` for strict typing and validation.

---

## ✅ Task Blocks

### **1. Base Project Scaffolding (Lead: Architect)** ✅

* [x] Repo layout + `pyproject.toml`
* [x] Shared `types/` module for base data classes
* [x] Dependency lock + `venv`/`poetry` setup

---

### **2. FastAPI Core API ( A)** ✅

* [x] Implement `GET /status`
* [x] Build out `/agents/` endpoints (list, get, create, post, reply, etc.)
* [x] `POST /agents/:id/memories` connected to queue

🚫 **Don't**: Implement front-end rendering, template engines, or docs UI. Pure JSON API only.

---

### **3. SQLite Memory Layer ( B)** ✅

* [x] Create SQLite schema for memories, agents, relationships
* [x] Implement `SQLiteWriteQueue` (from prior)
* [x] Add basic DAO layer with `enqueue()` wrapper
* [x] Validate memory persistence and query performance

🚫 **Don't**: Add ORM (like SQLAlchemy). Keep tight low-level control with raw SQL or `aiosqlite`.

---

### **4. Agent Runtime Core ( C)** ✅

* [x] Implement `Agent` class with VAD mood tracking
* [x] Add behavior profile handling (posting frequency, interaction logic)
* [x] Hook into memory system
* [x] Stub system prompt generator

🚫 **Don't**: Implement complex scheduling or prompt chaining yet. Focus on scaffold + interface fidelity.

---

### **5. Event Engine ( D)** ✅

* [x] Port `Event` type
* [x] `POST /events` and `GET /events`
* [x] Create internal event router for agents

🚫 **Don't**: Add complex scheduling logic. Trigger all events immediately for now.

---

### **6. Twitter Adapter (E)** ✅

* [x] Basic tweet/post/send reply client using `tweepy`
* [x] Rate limit handler
* [x] Credential rotation interface

🚫 **Don't**: Implement scraping fallback or full thread tracking in this pass.

---

### **7. LLM Adapter ( F)** ✅

* [x] Implement OpenAI call wrapper
* [x] Add retry logic with `tenacity`
* [x] Hook to agent prompt formatter

🚫 **Don't**: Add Grok yet. Don't hardcode API keys into the repo.

---

### **8. Solana Integration ( G)** ✅

* [x] Wallet connect test with `solana-py`
* [x] Stub token transfer
* [x] Simulate Jupiter swap (mock if needed)

🚫 **Don't**: Implement real trading or contract interaction in early phases.

---

## 🧪 Testing Protocols ✅

* [x] Write `pytest` tests for every route
* [x] Use `pytest-asyncio` for async support
* [x] Include rate limit test cases
* [x] Add memory insert + retrieval tests

🚫 **Don't**: Skip tests even for MVP logic. Break it down into async test blocks.

---

## 🛑 Negative Prompt Safeguards

| Trigger Behavior                    | Redirect To                                                      |
| ----------------------------------- | ---------------------------------------------------------------- |
| "Let's just use SQLAlchemy"         | No. Raw SQL + `aiosqlite` + queue buffer is mandatory.           |
| "Can I add a front-end UI?"         | No UI work. This is backend API infrastructure only.             |
| "Can I try Redis/Postgres instead?" | SQLite is required. The point is offline-friendly minimal infra. |
| "What if we just skip Twitter?"     | Implement at least one outbound action per agent.                |
