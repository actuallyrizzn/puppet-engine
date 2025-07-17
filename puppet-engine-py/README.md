# Puppet Engine Python Migration

This is the Python migration of the Puppet Engine, an autonomous AI agent framework for Twitter/X.

## Project Structure

```
puppet-engine-py/
├── src/
│   └── puppet_engine/
│       ├── core/          # pydantic models, settings, exceptions
│       ├── agents/        # orchestration logic & personality packs
│       ├── memory/        # mongo/vector adapters
│       ├── llm/           # provider drivers
│       ├── twitter/       # X API client + stream
│       ├── events/        # scheduler & event bus
│       ├── api/           # FastAPI routes & DI wiring
│       ├── solana/        # on-chain helpers
│       └── main.py
├── tests/                 # pytest + pytest-asyncio
├── ops/                   # Docker, kube, helm, terraform
└── pyproject.toml
```

## Migration Phases

1. **Phase 0: Baseline Capture** - Regression test suite
2. **Phase 1: Scaffolding & Dev-Env** - Poetry project setup
3ase 2: Core Domain Models** - Pydantic models
4. **Phase 3: Memory + LLM Layer** - Async Motor store
5. **Phase4: Event Engine & Scheduler** - APScheduler6hase5PI Parity** - FastAPI endpoints
7. **Phase 6: Twitter/X Adapter** - Modern API client8 **Phase 7: Solana Integration** - Blockchain helpers
9. **Phase 8 Observability** - OpenTelemetry, Prometheus
10*Phase 9: Cut-over** - Blue-green deployment

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Start development server
poetry run puppet-engine
```

## Status

Currently in Phase 0: Baseline Capture 