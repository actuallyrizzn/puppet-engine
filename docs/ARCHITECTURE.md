# Puppet Engine Architecture

## Overview

Puppet Engine follows a modular, event-driven architecture designed for scalability, maintainability, and extensibility. The system is built around autonomous AI agents that can interact with social media platforms and blockchain networks.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Puppet Engine                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Agents    │  │ Event Engine│  │   Memory    │        │
│  │  Manager    │  │             │  │   Store     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │     LLM     │  │   Twitter   │  │   Solana    │        │
│  │  Providers  │  │    Client   │  │   Trading   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │     API     │  │  Observ-    │  │   Utils     │        │
│  │   Server    │  │  ability    │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Agent Manager (`src/agents/`)

The Agent Manager orchestrates the lifecycle and interactions of all AI agents in the system.

#### Key Responsibilities:
- **Agent Lifecycle Management**: Creation, initialization, and shutdown of agents
- **Behavior Orchestration**: Coordinating posting, trading, and interaction behaviors
- **State Management**: Maintaining agent states and personality consistency
- **Event Handling**: Processing external events and triggers

#### Key Classes:
- `AgentManager`: Main orchestrator for all agents
- `Agent`: Individual agent implementation
- `AgentConfig`: Configuration management for agents

```python
class AgentManager:
    def __init__(self, config: Dict[str, Any]):
        self.agents: Dict[str, Agent] = {}
        self.memory_store = config['memory_store']
        self.llm_provider = config['default_llm_provider']
        self.event_engine = config['event_engine']
    
    async def start_agents(self):
        """Initialize and start all configured agents"""
        
    async def stop_agents(self):
        """Gracefully shutdown all agents"""
```

### 2. Event Engine (`src/events/`)

The Event Engine handles scheduled and triggered events that influence agent behavior.

#### Key Responsibilities:
- **Scheduled Events**: Regular posting, trading, and maintenance events
- **Triggered Events**: Response to external stimuli (mentions, market changes)
- **Event Routing**: Directing events to appropriate agents
- **Event History**: Maintaining event logs for analysis

#### Key Classes:
- `EventEngine`: Main event processing engine
- `Event`: Event data structure
- `EventScheduler`: Scheduling and timing management

```python
class EventEngine:
    def __init__(self):
        self.scheduled_events: List[Event] = []
        self.event_handlers: Dict[str, Callable] = {}
        self.running = False
    
    async def start(self):
        """Start the event processing loop"""
        
    async def schedule_event(self, event: Event):
        """Schedule a new event"""
```

### 3. Memory Store (`src/memory/`)

The Memory Store provides persistent storage with vector search capabilities for agent memories and knowledge.

#### Key Responsibilities:
- **Persistent Storage**: Long-term memory retention
- **Vector Search**: Semantic similarity search for relevant memories
- **Memory Management**: CRUD operations for agent memories
- **Knowledge Base**: Storing agent knowledge and relationships

#### Key Classes:
- `MemoryStore`: Abstract base class for memory operations
- `SQLiteStore`: SQLite-based memory implementation
- `VectorStore`: Vector search capabilities

```python
class MemoryStore(ABC):
    @abstractmethod
    async def add_memory(self, agent_id: str, memory: Memory) -> str:
        """Add a new memory entry"""
        
    @abstractmethod
    async def search_memories(self, agent_id: str, query: str, limit: int = 10) -> List[Memory]:
        """Search memories by semantic similarity"""
```

### 4. LLM Providers (`src/llm/`)

The LLM Providers module provides an abstract interface for multiple AI language model providers.

#### Key Responsibilities:
- **Content Generation**: Creating tweets, responses, and other content
- **Provider Abstraction**: Unified interface for different LLM services
- **Prompt Management**: Handling system prompts and context
- **Response Processing**: Parsing and validating LLM responses

#### Key Classes:
- `LLMProvider`: Abstract base class for LLM providers
- `OpenAIProvider`: OpenAI API integration
- `GrokProvider`: Grok API integration
- `FakeProvider`: Testing and development provider

```python
class LLMProvider(ABC):
    @abstractmethod
    async def generate_content(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate content using the LLM"""
        
    @abstractmethod
    async def generate_tweet(self, agent: Agent, context: Dict[str, Any]) -> str:
        """Generate a tweet for a specific agent"""
```

### 5. Twitter Client (`src/twitter/`)

The Twitter Client handles all interactions with the Twitter API.

#### Key Responsibilities:
- **Posting**: Publishing tweets and threads
- **Monitoring**: Tracking mentions and interactions
- **Rate Limiting**: Managing API rate limits
- **Authentication**: Handling Twitter API credentials

#### Key Classes:
- `TwitterClient`: Main Twitter API client
- `TweetStream`: Real-time tweet monitoring
- `TwitterAdapter`: Adapter for different Twitter API versions

```python
class TwitterClient:
    def __init__(self, credentials: TwitterCredentials):
        self.api = self._initialize_api(credentials)
        self.rate_limiter = RateLimiter()
    
    async def post_tweet(self, text: str, reply_to: Optional[str] = None) -> str:
        """Post a tweet to Twitter"""
        
    async def get_mentions(self, since_id: Optional[str] = None) -> List[Tweet]:
        """Get mentions for the authenticated user"""
```

### 6. Solana Trading (`src/solana/`)

The Solana Trading module provides blockchain trading capabilities for agents.

#### Key Responsibilities:
- **Wallet Management**: Managing agent wallets and balances
- **Trading Execution**: Executing trades on Solana
- **Market Analysis**: Analyzing token trends and prices
- **Transaction History**: Tracking trading activities

#### Key Classes:
- `SolanaTrader`: Main trading interface
- `SolanaWallet`: Wallet management and operations
- `JupiterAPI`: Jupiter protocol integration for swaps

```python
class SolanaTrader:
    def __init__(self, wallet: SolanaWallet, config: TradingConfig):
        self.wallet = wallet
        self.jupiter_api = JupiterAPI()
        self.config = config
    
    async def execute_trade(self, token_in: str, token_out: str, amount: float) -> TradeResult:
        """Execute a token swap"""
        
    async def analyze_market(self) -> MarketAnalysis:
        """Analyze current market conditions"""
```

### 7. API Server (`src/api/`)

The API Server provides HTTP endpoints for monitoring and controlling the system.

#### Key Responsibilities:
- **Health Monitoring**: System health and status endpoints
- **Agent Control**: Manual agent operations
- **Memory Operations**: Memory management via API
- **Configuration**: Runtime configuration updates

#### Key Classes:
- `APIServer`: Main API server implementation
- `HealthEndpoint`: Health check endpoints
- `AgentEndpoints`: Agent management endpoints

```python
class APIServer:
    def __init__(self, agent_manager: AgentManager, memory_store: MemoryStore):
        self.agent_manager = agent_manager
        self.memory_store = memory_store
        self.app = FastAPI()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes"""
```

### 8. Observability (`src/utils/`)

The Observability module provides logging, metrics, and monitoring capabilities.

#### Key Responsibilities:
- **Logging**: Structured logging throughout the system
- **Metrics**: Performance and usage metrics
- **Monitoring**: System health monitoring
- **Debugging**: Debug information and tracing

#### Key Classes:
- `Logger`: Centralized logging system
- `Metrics`: Metrics collection and reporting
- `Tracer`: Request tracing and debugging

## Data Flow

### 1. Agent Posting Flow

```
Agent Manager → Event Engine → LLM Provider → Twitter Client → Twitter API
     ↑              ↑              ↑              ↑
Memory Store ← Content Generation ← Prompt Creation ← Context Building
```

### 2. Mention Response Flow

```
Twitter API → Twitter Client → Agent Manager → LLM Provider → Twitter Client → Twitter API
     ↑              ↑              ↑              ↑              ↑
Memory Store ← Context Building ← Memory Search ← Mention Processing ← Tweet Monitoring
```

### 3. Trading Flow

```
Event Engine → Agent Manager → Solana Trader → Jupiter API → Solana Network
     ↑              ↑              ↑              ↑
Memory Store ← Trade Recording ← Trade Execution ← Market Analysis
```

## Configuration Management

### Environment Variables

The system uses environment variables for configuration:

```env
# Core Configuration
DATABASE_URL=sqlite:///puppet_engine.db
LOG_LEVEL=INFO
ENABLE_METRICS=true

# API Keys
TWITTER_API_KEY=your_key
OPENAI_API_KEY=your_key
GROK_API_KEY=your_key

# Solana Configuration
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_PRIVATE_KEY_AGENT_ID=your_private_key
```

### Agent Configuration

Agents are configured via JSON files:

```json
{
  "id": "agent-id",
  "name": "Agent Name",
  "personality": { ... },
  "behavior": { ... },
  "llm_provider": "openai",
  "solana_integration": { ... }
}
```

## Error Handling

### Error Types

1. **API Errors**: Twitter, OpenAI, Solana API failures
2. **Network Errors**: Connection timeouts and network issues
3. **Configuration Errors**: Invalid configuration parameters
4. **Runtime Errors**: Unexpected system errors

### Error Handling Strategy

- **Retry Logic**: Automatic retries with exponential backoff
- **Circuit Breaker**: Prevent cascading failures
- **Graceful Degradation**: Continue operation with reduced functionality
- **Error Logging**: Comprehensive error logging and monitoring

## Performance Considerations

### Async Architecture

The entire system is built on async/await patterns for optimal performance:

- **Concurrent Operations**: Multiple agents can operate simultaneously
- **Non-blocking I/O**: All external API calls are non-blocking
- **Resource Efficiency**: Efficient use of system resources

### Caching Strategy

- **Memory Caching**: Frequently accessed memories cached in memory
- **API Caching**: API responses cached to reduce external calls
- **Configuration Caching**: Agent configurations cached for performance

### Database Optimization

- **Indexing**: Proper database indexing for fast queries
- **Connection Pooling**: Efficient database connection management
- **Query Optimization**: Optimized queries for common operations

## Security Considerations

### API Key Management

- **Environment Variables**: Sensitive keys stored in environment variables
- **Agent-Specific Keys**: Separate keys for different agents
- **Key Rotation**: Support for key rotation and updates

### Data Privacy

- **User ID Protection**: User IDs are not exposed in agent responses
- **Memory Encryption**: Sensitive memory data can be encrypted
- **Access Control**: API endpoints protected with authentication

### Trading Security

- **Transaction Limits**: Configurable limits on trading amounts
- **Safety Checks**: Multiple safety checks before trade execution
- **Audit Trail**: Complete audit trail of all trading activities

## Scalability

### Horizontal Scaling

- **Stateless Design**: Components designed for stateless operation
- **Load Balancing**: Support for multiple instances
- **Database Scaling**: Database can be scaled independently

### Vertical Scaling

- **Resource Optimization**: Efficient use of CPU and memory
- **Async Processing**: Non-blocking operations for better throughput
- **Connection Pooling**: Efficient connection management

## Monitoring and Observability

### Logging

- **Structured Logging**: JSON-formatted logs for easy parsing
- **Log Levels**: Configurable log levels for different environments
- **Log Aggregation**: Support for log aggregation systems

### Metrics

- **Performance Metrics**: Response times, throughput, error rates
- **Business Metrics**: Post frequency, engagement rates, trading volume
- **System Metrics**: CPU, memory, disk usage

### Health Checks

- **Component Health**: Individual component health monitoring
- **Dependency Health**: External service health monitoring
- **Overall Health**: System-wide health status

## Future Architecture Considerations

### Microservices Migration

The current monolithic architecture can be migrated to microservices:

- **Agent Service**: Dedicated service for agent management
- **Trading Service**: Dedicated service for trading operations
- **Memory Service**: Dedicated service for memory management
- **API Gateway**: Centralized API management

### Event Sourcing

Consider implementing event sourcing for better audit trails:

- **Event Store**: Centralized event storage
- **Event Replay**: Ability to replay events for debugging
- **Temporal Queries**: Query system state at any point in time

### CQRS Pattern

Command Query Responsibility Segregation for better performance:

- **Command Side**: Write operations (posts, trades)
- **Query Side**: Read operations (memory search, analytics)
- **Event Bus**: Communication between command and query sides 