# Puppet Engine Python Migration Plan - Final Approved Version
*Revision2- July 17, 225 Executive Summary

This document outlines the migration of the Puppet Engine from JavaScript/Node.js to Python, incorporating comprehensive peer review feedback and industry best practices for production-ready migrations.

### Key Improvements from v1opic | Key Upgrade |
|-------|-------------|
| **Safety Net First** | Phase 0ession suite added; Node behavior frozen before porting |
| **Strangler-Fig Cut-over** | Python services shadow Node API via Redis bus; endpoint-by-endpoint switchover |
| **Realistic Resourcing** | Timeline in person-weeks with20r |
| **Production Readiness** | Vault secrets, OpenTelemetry, Prometheus metrics, GitHub Actions, Devcontainer |
| **Memory Evolution** | Optional vector store (Mongo Atlas Vector, PgVector, Chroma) for semantic recall |
| **Modern Twitter/X API** | `twitterx` for async v2 endpoints with paid-tier provisioning |

## Component Mapping (Node → Python)

| Concern | Node Package | Python Replacement |
|---------|--------------|-------------------|
| Web Server | `express` | `fastapi` + `uvicorn` |
| Scheduler | `node-cron` | `APScheduler` |
| Twitter API | `twitter-api-v2witterx` or custom OAuth2 client |
| OpenAI SDK | `openai` (JS) | `openai` (Py) |
| MongoDB | `mongodb` | `motor` (async) |
| Solana RPC | `@solana/web3.js` | `solana-py` |
| HTTP Client | `axios` | `httpx` |
| Logging | `winston` | `loguru` (+ JSON sink) |

## Phase Roadmap & Gates

| Phase | Duration | Exit Criteria |
|-------|----------|---------------|
| **0. Baseline Capture** |1eek | Jest/Cypress tests green on Node API; GitHub Actions badge green |
| **1. Scaffolding & Dev-Env** | 1 week | Poetry project, Devcontainer, Dockerfile, lint & unit test job pass |
| **2. Core Domain Models** |1 week | Pydantic v2/settings; adapter keeps Node tests green |
| **3. Memory + LLM Layer** | 2 weeks | Async Motor store, optional vector plugin, provider interface & fake driver |
| **4. Event Engine & Scheduler** | 1 week | Replay test proves deterministic parity with Node event history |
| **5. API Parity** | 1 week | FastAPI reproduces all baseline endpoints; contract tests pass |
| **6. Twitter/X Adapter** | 1 week | Staging account posts & streaming listener verified; rate-limit back-off works |
| **7. Solana Sub-module** | 1 week | Testnet wallet ops + Jupiter trade mock succeed E2**8servability & Hardening** |1ek | OpenTelemetry traces, Prom metrics, Vault secret injection, Snyk scan clean |
| **9. Cut-over & Hyper-care** | 1 week | Blue-green deploy, canary traffic switch, rollback script tested |

**Total:10 weeks (8 weeks + 20% contingency)**

## Target Project Structure

```
puppet-engine-py/
├── src/
│   ├── core/          # pydantic models, settings, exceptions
│   ├── agents/        # orchestration logic & personality packs
│   ├── memory/        # mongo/vector adapters
│   ├── llm/           # provider drivers
│   ├── twitter/       # X API client + stream
│   ├── events/        # scheduler & event bus
│   ├── api/           # FastAPI routes & DI wiring
│   ├── solana/        # on-chain helpers
│   └── main.py
├── ops/               # Docker, kube, helm, terraform, vault policies
├── tests/             # pytest + pytest-asyncio
├── .devcontainer/     # VS Code / Codespaces parity
└── pyproject.toml
```

## Tech Stack Highlights

- **Python3.12** (manylinux base)
- **FastAPI 0111/ Uvicorn 0.30* (async workers)
- **Motor 3.4Mongo Atlas Vector Search)
- **PgVector / Chroma** (optional swap-in)
- **APScheduler30.10(cron & in-mem job store)
- **OpenTelemetry10.25** exporter → OTLP → Grafana Tempo
- **Prometheus-FastAPI-Instrumentator 7.0 Grafana Loki dashboards
- **HashiCorp Vault** (Kubernetes auth) for secrets; `.env` only in dev
- **GitHub Actions**: lint → type-check → test → image build → push → Snyk scan

## Migration & Deployment Workflow

### 1. Shadow Releases
Python event loop subscribes to Redis topics published by Node engine. Endpoints are mirrored; traffic percentage toggled via LaunchDarkly feature flags.

### 2Sync
Mongo replica set used by both runtimes; new vector collections are additive and read-only until final cut.

### 3. Blue-Green Switch
Kubernetes `puppet-node` and `puppet-py` deployments behind Istio virtual-service. Canary at 5% for 24 then full flip if error-budget < 0.1.

### 4. Rollback
Helm chart keeps last three releases; `helm rollback` + feature-flag off instantly restores Node path.

## Success Metrics

| Category | KPI | Target |
|----------|-----|--------|
| Data | Data loss incidents | **0** |
| Reliability | 95entile API latency | ≤ existing Node p95 |
| Coverage | Critical path test coverage | ≥ 90% |
| Post-migration churn | Hotfix count (303|
| Dev velocity | Avg. PR cycle time | 20% ↓ vs. Node baseline |

## Dependencies (pyproject.toml)

```toml
[tool.poetry.dependencies]
python =^3.12
fastapi = ^0.111
uvicorn = {extras = ["standard], version =^0.30}
pydantic = ^27motor = ^30.4
httpx = "^00.27
openai = ^1.30twitterx = ^03
solana = "^00.3
apscheduler = "^3.10
loguru =^07python-dotenv =^1.0prometheus-fastapi-instrumentator = "^7
opentelemetry-api = ^10.25edis =^5.0
protobuf =^50.27[tool.poetry.group.dev.dependencies]
pytest = ^70.4
pytest-asyncio = "^00.21
pytest-mock = ^30.12
black = "^2311
isort = ^512ypy = ^10.7
flake8 =^6.1
pre-commit = "^3.5
```

## Phase 0: Baseline Capture (Week 1)

### Objectives
- **Regression Test Suite**: Comprehensive tests covering all current functionality
- **Behavioral Contract**: Documented expected behavior for each component
- **Performance Baseline**: Current system performance metrics

### Deliverables
```javascript
// tests/baseline/integration.test.js
describe('Puppet Engine Baseline Tests', () => {
  test('Agent Management', async () => {
    // Test agent loading, personality, memory
  });
  
  test('Twitter Integration', async () => {
    // Test posting, streaming, rate limits
  });
  
  test(LLM Integration', async () => {
    // Test OpenAI, Grok providers
  });
  
  test(Memory Management', async () => {
    // Test MongoDB operations, file fallback
  });
  
  test('Event Engine', async () => {
    // Test scheduling, event processing
  });
  
  test('API Endpoints', async () =>[object Object]  // Test all REST endpoints
  });
  
  test('Solana Integration', async () => {
    // Test wallet operations, trading
  });
});
```

### Success Criteria
- ✅ All baseline tests pass consistently
- ✅ GitHub Actions CI pipeline green
- ✅ Performance metrics documented
- ✅ Behavioral contract signed off

## Phase 1: Scaffolding & Dev-Environment (Week 2)

### Project Setup
```bash
# Create new repository
mkdir puppet-engine-py
cd puppet-engine-py

# Initialize Poetry project
poetry init --name puppet-engine --description "Autonomous AI agent framework" --author "Your Name <your.email@example.com>"

# Add dependencies
poetry add fastapi uvicorn pydantic motor httpx openai twitterx solana apscheduler loguru python-dotenv prometheus-fastapi-instrumentator opentelemetry-api redis protobuf

# Add dev dependencies
poetry add --group dev pytest pytest-asyncio pytest-mock black isort mypy flake8re-commit
```

### DevContainer Configuration
```json
// .devcontainer/devcontainer.json[object Object]name": "Puppet Engine Python,
  e": mcr.microsoft.com/devcontainers/python:312,
 features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {},
    "ghcr.io/devcontainers/features/git:1":[object Object]
 customizations:[object Object]vscode": {
    extensions: [       ms-python.python",
      ms-python.black-formatter",
      ms-python.isort",
     ms-python.mypy-type-checker"
      ]
    }
  },
  postCreateCommand:poetry install,
 forwardPorts: [8000]
}
```

## Phase 2: Core Domain Models (Week 3)

### Pydantic Models
```python
# src/core/models.py
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class MemoryType(str, Enum):
    CORE = core"
    EVENT =event"
    INTERACTION =interaction"
    GENERAL = "general"

class Personality(BaseModel):
    traits: List[str] = Field(default_factory=list, max_items=20)
    values: List[str] = Field(default_factory=list, max_items=10)
    speaking_style: str = Field(max_length=50   interests: List[str] = Field(default_factory=list, max_items=15)
    
    @validator('traits', 'values', 'interests')
    def validate_list_items(cls, v):
        return [item.strip() for item in v if item.strip()]

class Agent(BaseModel):
    id: str = Field(regex=r'^[a-z0-9+$) name: str = Field(min_length=1, max_length=100)
    description: str = Field(max_length=1000)
    personality: Personality = Field(default_factory=Personality)
    custom_system_prompt: Optional[str] = Field(max_length=500   rotating_system_prompts: List[str] = Field(default_factory=list)
    behavior: Dict[str, Any] = Field(default_factory=dict)
    current_mood: Dict[str, float] = Field(default_factory=dict)
    last_post_time: Optional[datetime] = None
```

### Settings Management
```python
# src/core/settings.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application
    app_name: str = "Puppet Engine"
    debug: bool = False
    log_level: str =INFO   
    # Database
    mongodb_uri: str = "mongodb://localhost:27017puppet-engine"
    redis_url: str = redis://localhost:6379"
    
    # Twitter/X API
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_token_secret: Optional[str] = None
    twitter_bearer_token: Optional[str] = None
    
    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str =gpt-4-preview"
    
    # Solana
    solana_rpc_url: str =https://api.mainnet-beta.solana.com"
    solana_private_key: Optional[str] = None
    
    # Security
    secret_manager: str = "env"  # env, vault, aws-secrets-manager
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

## Phase 3: Memory + LLM Layer (Weeks 4-5)

### Memory Management with Vector Search
```python
# src/memory/vector_store.py
from typing import List, Dict, Any, Optional
import motor.motor_asyncio
from pymongo import ASCENDING
import numpy as np

class VectorMemoryStore:
    def __init__(self, mongodb_uri: str):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_uri)
        self.db = self.client.puppet_engine
        self.memories = self.db.agent_memories
        self.vectors = self.db.memory_vectors
        
    async def create_indexes(self):
       eate MongoDB Atlas Vector Search indexes"""
        await self.memories.create_index([("agent_id", ASCENDING)])
        await self.memories.create_index([("type", ASCENDING)])
        await self.memories.create_index([("timestamp, -1)])
        
        # Vector search index (requires MongoDB Atlas)
        await self.vectors.create_index([
            ("vector",vectorSearch),           ("agent_id", ASCENDING)
        ])
    
    async def search_memories(self, agent_id: str, query: str, 
                            limit: int = 10-> List[MemoryItem]:
        tic search through memories"""
        # MongoDB Atlas Vector Search implementation
        pipeline =          {"$match": {"agent_id": agent_id}},
            {"$search":[object Object]
        text                 query                   patht"
                }
            }},
          [object Object]$limitimit},
           [object Object]$sort: {ore: -1}}       ]
        
        cursor = self.memories.aggregate(pipeline)
        memories = await cursor.to_list(length=limit)
        return [MemoryItem(**memory) for memory in memories]
```

### LLM Provider Interface
```python
# src/llm/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel

class LLMResponse(BaseModel):
    content: str
    model: str
    usage: Optional[Dictstr, int]] = None
    metadata: Dict[str, Any] =[object Object]ss BaseLLMProvider(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = config.get(model, 'gpt-4')
        self.max_tokens = config.get(max_tokens', 1024  self.temperature = config.get(temperature', 0.7
        self.rate_limit_delay = config.get('rate_limit_delay, 1.0)    
    @abstractmethod
    async def generate_content(self, prompt: str, 
                             options: Dict[str, Any] = None) -> LLMResponse:
 erate content with rate limiting and error handling"""
        pass
    
    @abstractmethod
    async def generate_tweet(self, agent: Agent, 
                           prompt: str = ') -> str:
   nerate a tweet for an agent"""
        pass
```

## Phase4: Event Engine & Scheduler (Week 6)

### Async Event System
```python
# src/events/engine.py
import asyncio
from typing import Dict, List, Any, Callable, Optional
from datetime import datetime, timedelta
from enum import Enum
import heapq

class EventPriority(Enum):
    LOW =0    NORMAL = 1   HIGH = 2    CRITICAL = 3

class EventEngine:
    def __init__(self):
        self.event_queue: List[Event] = []
        self.event_listeners: Dict[str, List[Callable]] =[object Object]    self.scheduled_events: List[Event] = ]
        self.is_processing = false        self.event_history: List[Event] = []
        
    async def start(self):
    t event processing loop"self.is_processing = True
        asyncio.create_task(self._process_events())
        asyncio.create_task(self._check_scheduled_events())
    
    async def _process_events(self):
   n event processing loop"""
        while self.is_processing:
            if self.event_queue:
                event = heapq.heappop(self.event_queue)
                await self._dispatch_event(event)
                
                # Add to history
                self.event_history.append(event)
                if len(self.event_history) > 1000:
                    self.event_history = self.event_history[-500]
            else:
                await asyncio.sleep(0.1)
```

## Phase 5: API Parity (Week 7)

### FastAPI with Strangler Fig Adapter
```python
# src/adapters/node_adapter.py
import httpx
from typing import Dict, Any
from ..core.settings import Settings

class NodeAdapter: to route requests to existing Node.js API during migration"   
    def __init__(self, settings: Settings):
        self.node_url = settings.node_api_url
        self.client = httpx.AsyncClient()
    
    async def forward_request(self, method: str, path: str, 
                            data: Dict[str, Any] = None) -> Dict[str, Any]:
        Forward request to Node.js API"
        url = f"{self.node_url}{path}"
        try:
            response = await self.client.request(
                method=method,
                url=url,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(fNode.js API error: {e}")

# src/api/server.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

class APIServer:
    def __init__(self, settings: Settings):
        self.app = FastAPI(
            title=Puppet Engine API",
            description="Autonomous AI agent management API",
            version=2.0.0       )
        
        self.settings = settings
        self.node_adapter = NodeAdapter(settings)
        
        self._setup_middleware()
        self._setup_routes()
        self._setup_observability()
    
    def _setup_observability(self):
        "tup monitoring and metrics"""
        Instrumentator().instrument(self.app).expose(self.app)
```

## Phase 6: Twitter/X Adapter (Week 8)

### Modern Twitter/X Integration
```python
# src/twitter/client.py
import httpx
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime

class TwitterXClient:
   dern Twitter/X API client with OAuth 2.0d v2 endpoints"   
    def __init__(self, credentials: Dict[str, str]):
        self.api_key = credentials.get(api_key')
        self.api_secret = credentials.get('api_secret')
        self.access_token = credentials.get('access_token')
        self.bearer_token = credentials.get('bearer_token')
        
        self.client = httpx.AsyncClient()
        self.rate_limit_remaining =300
        self.rate_limit_reset = None
    
    async def post_tweet(self, text: str, 
                        reply_to: Optional[str] = None) -> Dict[str, Any]:
     Post a tweet using Twitter API v2      url = "https://api.twitter.com/2/tweets"
        data = {"text": text}
        if reply_to:
            data[reply] = {in_reply_to_tweet_id": reply_to}
        
        headers = {
            Authorization": fBearer [object Object]self.bearer_token}",
           Content-Type":application/json"
        }
        
        try:
            response = await self.client.post(url, json=data, headers=headers)
            
            if await self._handle_rate_limit(response):
                # Retry after rate limit
                response = await self.client.post(url, json=data, headers=headers)
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            raise Exception(fTwitter API error: {e})
```

## Phase 7: Solana Integration (Week 9kchain Integration with Error Handling
```python
# src/solana/wallet.py
from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from solana.publickey import PublicKey
import base58
from typing import Dict, Any, Optional
import asyncio

class SolanaWallet:
    def __init__(self, private_key: str, rpc_url: str):
        self.private_key = private_key
        self.rpc_url = rpc_url
        self.client = AsyncClient(rpc_url)
        self.keypair = self._create_keypair()
        self.retry_attempts = 3
    
    def _create_keypair(self) -> Keypair:
       reate keypair with multiple format support"""
        try:
            # Try base58
            decoded_key = base58ecode(self.private_key)
            return Keypair.from_secret_key(decoded_key)
        except Exception:
            try:
                # Try JSON array
                import json
                secret_key = bytes(json.loads(self.private_key))
                return Keypair.from_secret_key(secret_key)
            except Exception:
                # Try hex
                secret_key = bytes.fromhex(self.private_key)
                return Keypair.from_secret_key(secret_key)
    
    async def get_balance(self) -> float:
   Get wallet balance with retry logic"""
        for attempt in range(self.retry_attempts):
            try:
                response = await self.client.get_balance(self.keypair.public_key)
                return response.value / 1_000_00            except Exception as e:
                if attempt == self.retry_attempts - 1:
                    raise Exception(f"Failed to get balance: {e})             await asyncio.sleep(2 ** attempt)
```

## Phase 8servability & Hardening (Week 10)

### Comprehensive Monitoring
```python
# src/utils/observability.py
import logging
import json
from datetime import datetime
from typing import Dict, Any
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.motor import MotorInstrumentor

class StructuredLogger:
    tured JSON logging with correlation IDs"   
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        
        # Setup JSON formatter
        formatter = logging.Formatter(
            {timestamp": "%(asctime)s",level": "%(levelname)s", '
         service": "%(name)s", "message":%(message)s", '
            "correlation_id":%(correlation_id)s"}'
        )
        
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log(self, level: str, message: str, **kwargs):
 og with structured data"        extra = [object Object]     correlation_id': trace.get_current_span().get_span_context().trace_id,
            **kwargs
        }
        
        log_method = getattr(self.logger, level.lower())
        log_method(message, extra=extra)

def setup_observability(app: FastAPI, service_name: str):
    """Setup comprehensive observability"""
    # Setup tracing
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        ConsoleSpanExporter()
    )
    
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
    
    # Instrument HTTP client
    HTTPXClientInstrumentor().instrument()
    
    # Instrument MongoDB
    MotorInstrumentor().instrument()
    
    # Setup structured logging
    logger = StructuredLogger(service_name)
    
    return logger
```

## Phase 9: Cut-over & Hyper-care (Week 11)

### Canary Deployment Strategy
```python
# src/deployment/canary.py
import asyncio
from typing import Dict, Any, List
import httpx
from prometheus_client import Counter, Histogram

class CanaryDeployment:
    ""Canary deployment with traffic splitting"   
    def __init__(self):
        self.canary_traffic_percentage = 01 # Start with 10%
        self.success_threshold = 00.95# 95% success rate required
        self.error_threshold = 0.05ror rate threshold
        
        # Metrics
        self.canary_requests = Counter('canary_requests_total', 'Canary requests')
        self.canary_errors = Counter('canary_errors_total',Canary errors')
        self.canary_latency = Histogram('canary_latency_seconds,Canary latency')
    
    async def route_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
      ute request to canary or stable based on percentage     import random
        
        # Determine routing
        if random.random() < self.canary_traffic_percentage:
            return await self._route_to_canary(request_data)
        else:
            return await self._route_to_stable(request_data)
    
    async def evaluate_canary_health(self) -> Dict[str, Any]:
         canary deployment health    total_requests = self.canary_requests._value.get()
        total_errors = self.canary_errors._value.get()
        
        if total_requests == 0:
            return[object Object]healthy: True, "reason:No traffic yet"}
        
        error_rate = total_errors / total_requests
        success_rate = 1 - error_rate
        
        healthy = (
            success_rate >= self.success_threshold and
            error_rate <= self.error_threshold
        )
        
        return {
            healthy": healthy,
         success_rate": success_rate,
       error_rate": error_rate,
           total_requests": total_requests,
         total_errors": total_errors
        }
```

## Risk Mitigation

### 1. Data Loss Prevention
- **Comprehensive backups** before migration
- **Data validation** scripts for each phase
- **Rollback procedures** documented and tested
- **Gradual migration** with strangler fig pattern

### 2Service Continuity
- **Parallel deployment** strategy
- **Feature flags** for gradual rollout
- **Monitoring** and alerting setup
- **Performance benchmarking** at each phase

### 3. Testing Strategy
- **Automated testing** pipeline
- **Integration tests** for all components
- **Load testing** for performance validation
- **User acceptance** testing

## Immediate Next Steps
1Approve this final migration plan** and resource allocation2. **Create `puppet-engine-py` repository** with Poetry + Devcontainer skeleton
3. **Implement Phase 0**: regression test harness on current Node.js master
4. **Schedule design review** at end of Phase 3 to finalize memory/vector direction

**Recommendation**: Lock the baseline test suite this week so every future milestone has an objective "definition of done." Let's proceed with Phase 0 immediately.

---

*This final migration plan ensures a smooth, monitored, and reversible transition to Python while maintaining all existing functionality and improving the overall system architecture.* 