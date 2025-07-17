# Puppet Engine Python Migration Plan v20
*Revised based on peer review feedback - addressing gaps in timeline, testing strategy, and technical decisions*

## Executive Summary

This document outlines the migration of the Puppet Engine from JavaScript/Node.js to Python, incorporating peer review feedback to ensure a robust, testable, and production-ready migration strategy.

## Key Changes from v1.0

- **Added Phase 0eline test capture before any migration
- **Strangler Fig Pattern**: Gradual migration instead of big-bang rewrite
- **Realistic Timeline**:9es with 20% buffer and proper resourcing
- **Enhanced Observability**: OpenTelemetry, Prometheus metrics, structured logging
- **Security Focus**: Proper secrets management and security scanning
- **CI/CD Pipeline**: Complete development and deployment automation

## Migration Strategy: Strangler Fig Pattern

Instead of a complete rewrite, we'll use the **strangler fig pattern**:
1. **Phase 0**: Capture baseline behavior with comprehensive tests
2hases 1-8 Python components alongside existing Node.js system
3. **Phase 9**: Gradual cutover with canary deployments and rollback capability

This minimizes downtime risk and allows for incremental validation.

## Revised Phase Plan

| Phase | Duration | Purpose & Exit Criteria | Person-Weeks |
|-------|----------|-------------------------|--------------|
| **0. Baseline Capture** | 1 week | Comprehensive test suite of current Node.js behavior | 1 |
| **1. Scaffolding & Dev-Env** | 1 week | Poetry project, devcontainer, CI skeleton | 1 |
| **2. Core Domain Models** |1 | Pydantic models & settings validation |1 |
| **3. Memory & LLM Layer** | 2 weeks | Async MongoDB, provider interface, OpenAI integration | 2 |
| **4. Event Engine & Scheduler** | 1 week | Event system parity with determinism tests | 1 |
| **5. API (FastAPI) Parity** | 1 week | REST endpoint migration with baseline tests | 1|
| **6. Twitter/X Adapter** | 1 week | Live posting with rate limit handling |1
| **7. Solana Sub-module** | 1 week | Wallet ops + Jupiter integration |1**8servability & Hardening** | 1 week | Monitoring, security, performance optimization | 1 |
| **9. Cut-over & Hypercare** | 1 week | Canary deployment, blue-green switch | 1 |

**Total Duration:10 weeks (8 weeks + 20% buffer)**
**Total Effort: 10person-weeks**

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

### Project Structure
```
puppet-engine-python/
├── pyproject.toml          # Poetry configuration
├── .devcontainer/          # VS Code dev container
├── docker-compose.yml      # Local development
├── .github/workflows/      # CI/CD pipelines
├── src/
│   ├── __init__.py
│   ├── core/              # Domain models
│   ├── adapters/          # Strangler fig adapters
│   ├── memory/            # Memory management
│   ├── llm/               # LLM providers
│   ├── twitter/           # Twitter integration
│   ├── events/            # Event engine
│   ├── api/               # FastAPI server
│   ├── solana/            # Blockchain integration
│   ├── utils/             # Utilities
│   └── main.py            # Entry point
├── tests/
│   ├── baseline/          # Phase 0 tests
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
└── config/
    ├── agents/            # Agent configurations
    └── settings.py        # Pydantic settings
```

### Dependencies (pyproject.toml)
```toml
[tool.poetry]
name = "puppet-engineversion = "010description = "Autonomous AI agent framework
authors = ["Your Name <your.email@example.com>]

[tool.poetry.dependencies]
python =^3.12
fastapi = ^0.111
uvicorn = {extras = ["standard], version =^0.30}
pydantic =^2.7
pydantic-settings = ^22motor = ^30.4
httpx = "^00.27
openai = ^1.30
twitterx =^0.3          # Modern Twitter/X client
solana = "^00.3
apscheduler = "^3.10
loguru =^07python-dotenv =^1.0prometheus-fastapi-instrumentator = "^7
opentelemetry-api = "^10.25
opentelemetry-sdk = ^10.25redis = ^50
celery = ^50.3
pytest = ^70.4
pytest-asyncio = "^00.21
pytest-mock = ^30.12
black = "^2311
isort = ^512ypy = ^10.7
flake8 = "^6.1[tool.poetry.group.dev.dependencies]
pre-commit = ^30.5### CI/CD Pipeline (.github/workflows/ci.yml)
```yaml
name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '30.12   - name: Install Poetry
        run: |
          curl -sSL https://install.python-poetry.org | python3 -
      - name: Install dependencies
        run: poetry install
      - name: Run linting
        run: |
          poetry run black --check .
          poetry run isort --check-only .
          poetry run flake8 .
          poetry run mypy src/
      - name: Run tests
        run: poetry run pytest tests/
      - name: Run baseline tests
        run: poetry run pytest tests/baseline/
```

## Phase 2: Core Domain Models (Week 3)

### Pydantic Models with Validation
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

class StyleGuide(BaseModel):
    voice: str = Field(max_length=200 tone: str = Field(max_length=200  formatting: Dict[str, Any] = Field(default_factory=dict)
    topics_to_avoid: List[str] = Field(default_factory=list)
    
    @validator('topics_to_avoid')
    def validate_topics(cls, v):
        return [topic.strip() for topic in v if topic.strip()]

class MemoryItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4)
    content: str = Field(min_length=1, max_length=10000)
    type: MemoryType = MemoryType.GENERAL
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    importance: float = Field(ge=0.0, le=1, default=0.5
    emotional_valence: float = Field(ge=-1.0, le=1, default=0.0)
    associations: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Agent(BaseModel):
    id: str = Field(regex=r'^[a-z0-9+$) name: str = Field(min_length=1, max_length=100)
    description: str = Field(max_length=1000)
    personality: Personality = Field(default_factory=Personality)
    style_guide: StyleGuide = Field(default_factory=StyleGuide)
    custom_system_prompt: Optional[str] = Field(max_length=500   rotating_system_prompts: List[str] = Field(default_factory=list)
    behavior: Dict[str, Any] = Field(default_factory=dict)
    current_mood: Dict[str, float] = Field(default_factory=dict)
    last_post_time: Optional[datetime] = None
    
    @validator(rotating_system_prompts')
    def validate_prompts(cls, v):
        return [prompt.strip() for prompt in v if prompt.strip()]
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
    openai_model: str = "gpt-4rbo-preview   
    # Grok
    grok_api_key: Optional[str] = None
    grok_api_endpoint: str =https://api.grok.x.com/v1chat/completions"
    grok_model: str =grok-1
    
    # Solana
    solana_rpc_url: str =https://api.mainnet-beta.solana.com"
    solana_private_key: Optional[str] = None
    
    # Security
    secret_manager: str = "env"  # env, vault, aws-secrets-manager
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

## Phase 3: Memory & LLM Layer (Weeks 4-5)

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
    
    async def add_memory(self, agent_id: str, memory: MemoryItem, 
                        embedding: Optional[List[float]] = None):
        mory with optional vector embedding        memory_doc = memory.dict()
        memory_doc['agent_id'] = agent_id
        
        await self.memories.insert_one(memory_doc)
        
        if embedding:
            vector_doc =[object Object]
               agent_id': agent_id,
          memory_id': memory.id,
       vector': embedding,
          timestamp': memory.timestamp
            }
            await self.vectors.insert_one(vector_doc)
    
    async def search_memories(self, agent_id: str, query: str, 
                            limit: int = 10-> List[MemoryItem]:
        tic search through memories      # This would use MongoDB Atlas Vector Search
        # For now, fallback to text search
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
    
    async def _handle_rate_limit(self, retry_after: int):
    ndle rate limiting with exponential backoff
        import asyncio
        await asyncio.sleep(retry_after)
    
    async def _retry_with_backoff(self, func, max_retries: int = 3:
       etry function with exponential backoff"""
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
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

class Event(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    target_agent_ids: List[str] = Field(default_factory=list)
    priority: EventPriority = EventPriority.NORMAL
    scheduled_time: Optional[datetime] = None

class EventEngine:
    def __init__(self):
        self.event_queue: List[Event] = []
        self.event_listeners: Dict[str, List[Callable]] =[object Object]    self.scheduled_events: List[Event] = ]
        self.is_processing = false        self.event_history: List[Event] = []
        
    async def start(self):
        e event processing loop"self.is_processing = True
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
                await asyncio.sleep(00.1    
    async def _check_scheduled_events(self):
  heck for scheduled events that are due"""
        while self.is_processing:
            now = datetime.utcnow()
            due_events = []
            
            for event in self.scheduled_events:
                if event.scheduled_time and event.scheduled_time <= now:
                    due_events.append(event)
            
            for event in due_events:
                self.scheduled_events.remove(event)
                self.queue_event(event)
            
            await asyncio.sleep(1)
    
    def queue_event(self, event: Event):
      event to priority queue""       heapq.heappush(self.event_queue, event)
    
    def schedule_event(self, event: Event, delay_seconds: int):
    Schedule an event for future execution"   event.scheduled_time = datetime.utcnow() + timedelta(seconds=delay_seconds)
        self.scheduled_events.append(event)
        self.scheduled_events.sort(key=lambda x: x.scheduled_time)
    
    async def _dispatch_event(self, event: Event):
       Dispatch event to all registered listeners"""
        listeners = self.event_listeners.get(event.type, [])
        all_listeners = self.event_listeners.get(*)
        
        all_handlers = listeners + all_listeners
        
        # Execute handlers concurrently
        tasks = [handler(event) for handler in all_handlers]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
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
        url = f"{self.node_url}{path}      
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
import uvicorn

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
    
    def _setup_middleware(self):
      FastAPI middleware""      self.app.add_middleware(
            CORSMiddleware,
            allow_origins=*
            allow_credentials=True,
            allow_methods=*
            allow_headers=["*"],
        )
    
    def _setup_observability(self):
        "tup monitoring and metrics"""
        Instrumentator().instrument(self.app).expose(self.app)
    
    def _setup_routes(self):
  up API routes with strangler fig pattern""        
        @self.app.get("/api/status")
        async def get_status():
       Get system status"""
            return[object Object]
               status": "online,
               version": "2.0.0,
                migration_phase": "strangler_fig"
            }
        
        @self.app.get("/api/agents")
        async def get_agents():
           all agents - route to Node.js during migration"""
            return await self.node_adapter.forward_request("GET, agents")
        
        @self.app.post("/api/agents/{agent_id}/post")
        async def create_agent_post(agent_id: str, options: Dict[str, Any] = None):
         Create agent post - route to Node.js during migration"""
            return await self.node_adapter.forward_request(
       POST, 
                f"/api/agents/{agent_id}/post,           options or[object Object]           )
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
    
    async def _get_oauth_token(self) -> str:
      et OAuth2.0ken for API v2""        auth_url = "https://api.twitter.com/2/oauth2     
        data = {
         grant_type": "client_credentials",
           client_id": self.api_key,
          client_secret: self.api_secret
        }
        
        response = await self.client.post(auth_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        return token_data["access_token"]
    
    async def _handle_rate_limit(self, response: httpx.Response):
    ndle rate limiting"""
        if response.status_code == 429:
            reset_time = int(response.headers.get("x-rate-limit-reset, 0))
            wait_time = max(0, reset_time - datetime.utcnow().timestamp())
            
            if wait_time > 0             await asyncio.sleep(wait_time)
            
            return True
        return False
    
    async def post_tweet(self, text: str, 
                        reply_to: Optional[str] = None) -> Dict[str, Any]:
     Post a tweet using Twitter API v2      url = "https://api.twitter.com/2/tweets     
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
            raise Exception(fTwitter API error: {e}")
    
    async def get_mentions(self, user_id: str, 
                          since_id: Optional[str] = None) -> List[Dict[str, Any]]:
     Get mentions using Twitter API v2     url = f"https://api.twitter.com/2ers/{user_id}/mentions   
        params = [object Object]      max_results": 10           tweet.fields": created_at,author_id,conversation_id"
        }
        
        if since_id:
            params["since_id"] = since_id
        
        headers =[object Object]Authorization": fBearer {self.bearer_token}"}
        
        try:
            response = await self.client.get(url, params=params, headers=headers)
            
            if await self._handle_rate_limit(response):
                response = await self.client.get(url, params=params, headers=headers)
            
            response.raise_for_status()
            return response.json().get("data",          
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
    
    async def transfer_sol(self, to_address: str, amount_sol: float) -> str:
     Transfer SOLwith comprehensive error handling"""
        try:
            to_pubkey = PublicKey(to_address)
            amount_lamports = int(amount_sol * 1_000_000_0      
            # Get recent blockhash
            blockhash_response = await self.client.get_latest_blockhash()
            blockhash = blockhash_response.value.blockhash
            
            transaction = Transaction()
            transaction.add(
                transfer(
                    TransferParams(
                        from_pubkey=self.keypair.public_key,
                        to_pubkey=to_pubkey,
                        lamports=amount_lamports
                    )
                )
            )
            transaction.recent_blockhash = blockhash
            
            # Sign and send transaction
            response = await self.client.send_transaction(
                transaction,
                self.keypair
            )
            
            # Wait for confirmation
            await self.client.confirm_transaction(response.value)
            
            return response.value
            
        except Exception as e:
            raise Exception(f"Transfer failed: {e})

#src/solana/trading.py
import httpx
from typing import Dict, Any, List
import asyncio

class JupiterTrader:
er API integration for Solana token trading"   
    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url
        self.jupiter_api = https://quote-api.jup.ag/v6"
        self.client = httpx.AsyncClient()
    
    async def get_quote(self, input_mint: str, output_mint: str, 
                       amount: int, slippage: float =1) -> Dict[str, Any]:
    Gettrading quote from Jupiter"
        url = f{self.jupiter_api}/quote   
        params = {
            inputMint": input_mint,
       outputMint": output_mint,
        amount": str(amount),
            slippageBps:int(slippage * 100)
        }
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Jupiter quote error: {e}")
    
    async def execute_swap(self, quote_response: Dict[str, Any], 
                          wallet: SolanaWallet) -> str:
     e swap transaction"""
        # Get swap transaction
        swap_url = f{self.jupiter_api}/swap     
        swap_data = {
          quoteResponse": quote_response,
          userPublicKey": str(wallet.keypair.public_key),
          wrapUnwrapSOL: True       }
        
        try:
            response = await self.client.post(swap_url, json=swap_data)
            response.raise_for_status()
            
            swap_result = response.json()
            
            # Sign and send transaction
            transaction_data = swap_result["swapTransaction"]
            transaction = Transaction.deserialize(transaction_data)
            
            signed_transaction = await wallet.client.send_transaction(
                transaction,
                wallet.keypair
            )
            
            return signed_transaction.value
            
        except Exception as e:
            raise Exception(f"Swap execution error: {e})
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

class MetricsCollector:Prometheus metrics collection"   
    def __init__(self):
        from prometheus_client import Counter, Histogram, Gauge
        
        # Counters
        self.tweets_posted = Counter('tweets_posted_total', 'Total tweets posted)
        self.llm_requests = Counter('llm_requests_total', 'Total LLM requests')
        self.memory_operations = Counter(memory_operations_total', 'Total memory operations')
        
        # Histograms
        self.tweet_generation_time = Histogram(tweet_generation_seconds',Tweet generation time)
        self.llm_response_time = Histogram('llm_response_seconds', LLM response time')
        
        # Gauges
        self.active_agents = Gauge(active_agents',Number of active agents')
        self.memory_usage = Gauge('memory_usage_bytes', 'Memory usage in bytes')

def setup_observability(app: FastAPI, service_name: str):
    """Setup comprehensive observability""   # Setup tracing
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
    
    # Setup metrics
    metrics = MetricsCollector()
    
    return logger, metrics
```

### Security Hardening
```python
# src/utils/security.py
import hashlib
import hmac
import os
from typing import Dict, Any
import hvac  # HashiCorp Vault client

class SecretManager:
   secret management"   
    def __init__(self, backend: str = "env"):
        self.backend = backend
        self.vault_client = None
        
        if backend == "vault":
            self.vault_client = hvac.Client(
                url=os.getenv("VAULT_URL"),
                token=os.getenv("VAULT_TOKEN")
            )
    
    def get_secret(self, key: str) -> str:
        et from configured backend"      if self.backend == env            return os.getenv(key)
        elif self.backend == "vault":
            response = self.vault_client.secrets.kv.v2.read_secret_version(
                path=key
            )
            return response['data']['data']['value']
        else:
            raise ValueError(f"Unsupported secret backend: {self.backend}")
    
    def verify_webhook_signature(self, payload: bytes, signature: str, 
                                secret: str) -> bool:
        webhook signature""     expected_signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256       ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)

class RateLimiter:
  Rate limiting with Redis"   
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def is_allowed(self, key: str, limit: int, window: int) -> bool:
 heck if request is allowed"
        current = await self.redis.incr(key)
        
        if current == 1:
            await self.redis.expire(key, window)
        
        return current <= limit
```

## Phase 9: Cut-over & Hypercare (Week 11)

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
    
    async def _route_to_canary(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        oute to Python canary deployment""       self.canary_requests.inc()
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Route to Python API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    http://python-api:800api/agents/post",
                    json=request_data
                )
                response.raise_for_status()
                
                latency = asyncio.get_event_loop().time() - start_time
                self.canary_latency.observe(latency)
                
                return response.json()
                
        except Exception as e:
            self.canary_errors.inc()
            raise e
    
    async def _route_to_stable(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
       to Node.js stable deployment"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
               http://node-api:300api/agents/post,              json=request_data
            )
            response.raise_for_status()
            return response.json()
    
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
    
    def adjust_traffic_percentage(self, new_percentage: float):
      ust canary traffic percentage""       self.canary_traffic_percentage = max(0.0, min(10new_percentage))

# src/deployment/rollback.py
class RollbackManager:
    """Rollback management for failed deployments"   
    def __init__(self):
        self.deployment_history = []
        self.current_version =node-v10    
    async def trigger_rollback(self, reason: str):
Trigger immediate rollback""     rollback_data = {
      timestamp: datetime.utcnow(),
            reasoneason,
           from_version: v20,       to_version": self.current_version
        }
        
        # Update routing to 10stable
        canary = CanaryDeployment()
        canary.adjust_traffic_percentage(0.0)
        
        # Log rollback
        self.deployment_history.append(rollback_data)
        
        # Alert team
        await self._send_rollback_alert(rollback_data)
        
        return rollback_data
    
    async def _send_rollback_alert(self, rollback_data: Dict[str, Any]):
      end rollback alert to team"""
        # Implementation for Slack/Discord/email alerts
        pass
```

## Success Metrics & Monitoring

### Technical Metrics
- **Zero data loss** during migration
- **Performance parity** or improvement (latency, throughput)
- **100est coverage** for critical paths
- **Zero downtime** during cutover

### Business Metrics
- **Feature parity** maintained
- **User experience** unchanged or improved
- **Development velocity** increased
- **Maintenance overhead** reduced

### Monitoring Dashboard
```python
# src/monitoring/dashboard.py
class MigrationDashboard:
    """Real-time migration monitoring dashboard"   
    def __init__(self):
        self.metrics = [object Object]        canary_traffic_percentage": 0          success_rate": 1           error_rate": 0,
            latency_p50": 0,
            latency_p95": 0           active_agents":0           tweets_posted": 0,
            memory_operations":0        }
    
    async def update_metrics(self): dashboard metrics"""
        # Collect metrics from Prometheus
        # Update dashboard state
        pass
    
    def get_migration_status(self) -> Dict[str, Any]:
     current migration status
        return {
          phase": canary_deployment",
          progress:90           health": "healthy",
           metrics": self.metrics,
           next_milestone: l_cutover"
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

## Next Steps

1. **Approve revised migration plan** and resource assignment
2. **Stand up Phase 0regression suite** on current Node.js code
3reate Poetry-based repository** with dev-container setup
4. **Schedule design review** after Phase 3 for memory/vector search direction
5e 0tion** immediately

---

*This revised migration plan addresses peer review feedback and provides a robust, testable, and production-ready migration strategy with proper risk mitigation and monitoring.* 