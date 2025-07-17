# API Reference

## Overview

Puppet Engine provides a REST API for monitoring and controlling the system. The API is built using FastAPI and provides endpoints for agent management, memory operations, and system monitoring.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. In production environments, consider implementing API key authentication or OAuth2.

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "status": "success",
  "data": { ... },
  "message": "Operation completed successfully",
  "timestamp": "2024-12-19T10:30:00Z"
}
```

### Error Response
```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { ... }
  },
  "timestamp": "2024-12-19T10:30:00Z"
}
```

## Health and Status Endpoints

### Health Check

Check the overall health of the system.

```http
GET /health
```

#### Response
```json
{
  "status": "success",
  "data": {
    "status": "healthy",
    "uptime": 3600,
    "version": "1.0.0",
    "components": {
      "agent_manager": "healthy",
      "memory_store": "healthy",
      "event_engine": "healthy",
      "twitter_client": "healthy",
      "solana_trader": "healthy"
    }
  },
  "message": "System is healthy",
  "timestamp": "2024-12-19T10:30:00Z"
}
```

### System Status

Get detailed system status information.

```http
GET /status
```

#### Response
```json
{
  "status": "success",
  "data": {
    "system": {
      "uptime": 3600,
      "version": "1.0.0",
      "environment": "production",
      "start_time": "2024-12-19T09:30:00Z"
    },
    "agents": {
      "total": 3,
      "active": 3,
      "inactive": 0
    },
    "memory": {
      "total_entries": 1500,
      "agents_with_memory": 3
    },
    "trading": {
      "total_trades": 25,
      "total_volume_sol": 2.5,
      "active_wallets": 2
    },
    "performance": {
      "cpu_usage": 15.5,
      "memory_usage": 45.2,
      "disk_usage": 12.8
    }
  },
  "message": "System status retrieved successfully",
  "timestamp": "2024-12-19T10:30:00Z"
}
```

## Agent Management Endpoints

### List All Agents

Get a list of all configured agents.

```http
GET /agents
```

#### Query Parameters
- `status` (optional): Filter by agent status (`active`, `inactive`, `all`)
- `limit` (optional): Maximum number of agents to return (default: 50)
- `offset` (optional): Number of agents to skip (default: 0)

#### Response
```json
{
  "status": "success",
  "data": {
    "agents": [
      {
        "id": "claudia-tech",
        "name": "Claudia",
        "description": "A witty AI persona with strong opinions on technology",
        "status": "active",
        "last_post": "2024-12-19T10:15:00Z",
        "post_count": 45,
        "follower_count": 1250,
        "trading_enabled": false
      },
      {
        "id": "coby-trader",
        "name": "Coby",
        "description": "Crypto trading enthusiast and market analyst",
        "status": "active",
        "last_post": "2024-12-19T10:20:00Z",
        "post_count": 67,
        "follower_count": 890,
        "trading_enabled": true,
        "trading_stats": {
          "total_trades": 15,
          "total_volume_sol": 1.2,
          "last_trade": "2024-12-19T09:45:00Z"
        }
      }
    ],
    "total": 2,
    "limit": 50,
    "offset": 0
  },
  "message": "Agents retrieved successfully",
  "timestamp": "2024-12-19T10:30:00Z"
}
```

### Get Agent Details

Get detailed information about a specific agent.

```http
GET /agents/{agent_id}
```

#### Path Parameters
- `agent_id`: The unique identifier of the agent

#### Response
```json
{
  "status": "success",
  "data": {
    "id": "claudia-tech",
    "name": "Claudia",
    "description": "A witty AI persona with strong opinions on technology",
    "status": "active",
    "configuration": {
      "personality": {
        "traits": ["curious", "witty", "enthusiastic"],
        "values": ["knowledge", "innovation", "community"],
        "speaking_style": "Friendly and informative with occasional humor"
      },
      "behavior": {
        "post_frequency": {
          "min_hours_between_posts": 2,
          "max_hours_between_posts": 6
        }
      },
      "llm_provider": "openai",
      "trading_enabled": false
    },
    "statistics": {
      "posts": {
        "total": 45,
        "this_week": 12,
        "this_month": 45
      },
      "engagement": {
        "likes": 1250,
        "retweets": 340,
        "replies": 89
      },
      "followers": 1250,
      "following": 45
    },
    "recent_activity": {
      "last_post": "2024-12-19T10:15:00Z",
      "last_interaction": "2024-12-19T10:10:00Z",
      "next_scheduled_post": "2024-12-19T12:15:00Z"
    }
  },
  "message": "Agent details retrieved successfully",
  "timestamp": "2024-12-19T10:30:00Z"
}
```

### Trigger Manual Post

Manually trigger a post from an agent.

```http
POST /agents/{agent_id}/post
```

#### Path Parameters
- `agent_id`: The unique identifier of the agent

#### Request Body
```json
{
  "context": {
    "topic": "artificial intelligence",
    "mood": "excited",
    "external_trigger": "new AI breakthrough"
  },
  "force": false
}
```

#### Request Body Parameters
- `context` (optional): Additional context for the post
- `force` (optional): Force posting even if outside normal schedule (default: false)

#### Response
```json
{
  "status": "success",
  "data": {
    "post_id": "1234567890123456789",
    "content": "Just read about the latest breakthrough in AI! This is exactly the kind of innovation that gets me excited. The potential applications are mind-blowing. 🤖✨ #AI #Innovation",
    "posted_at": "2024-12-19T10:35:00Z",
    "agent_id": "claudia-tech"
  },
  "message": "Post created successfully",
  "timestamp": "2024-12-19T10:35:00Z"
}
```

### Trigger Manual Trade

Manually trigger a trade from an agent (if trading is enabled).

```http
POST /agents/{agent_id}/trade
```

#### Path Parameters
- `agent_id`: The unique identifier of the agent

#### Request Body
```json
{
  "token_in": "So11111111111111111111111111111111111111112",
  "token_out": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "amount_sol": 0.05,
  "reason": "manual_trigger"
}
```

#### Request Body Parameters
- `token_in`: Input token mint address
- `token_out`: Output token mint address
- `amount_sol`: Amount in SOL to trade
- `reason` (optional): Reason for the trade

#### Response
```json
{
  "status": "success",
  "data": {
    "trade_id": "trade_123456",
    "transaction_signature": "5J7X...",
    "token_in": "So11111111111111111111111111111111111111112",
    "token_out": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "amount_in": 0.05,
    "amount_out": 1.25,
    "slippage": 0.5,
    "executed_at": "2024-12-19T10:40:00Z",
    "agent_id": "coby-trader"
  },
  "message": "Trade executed successfully",
  "timestamp": "2024-12-19T10:40:00Z"
}
```

### Update Agent Configuration

Update an agent's configuration.

```http
PUT /agents/{agent_id}/config
```

#### Path Parameters
- `agent_id`: The unique identifier of the agent

#### Request Body
```json
{
  "personality": {
    "traits": ["curious", "witty", "enthusiastic", "analytical"]
  },
  "behavior": {
    "post_frequency": {
      "min_hours_between_posts": 1,
      "max_hours_between_posts": 4
    }
  }
}
```

#### Response
```json
{
  "status": "success",
  "data": {
    "agent_id": "claudia-tech",
    "updated_fields": ["personality", "behavior"],
    "restart_required": false
  },
  "message": "Agent configuration updated successfully",
  "timestamp": "2024-12-19T10:45:00Z"
}
```

### Restart Agent

Restart an agent (useful after configuration changes).

```http
POST /agents/{agent_id}/restart
```

#### Path Parameters
- `agent_id`: The unique identifier of the agent

#### Response
```json
{
  "status": "success",
  "data": {
    "agent_id": "claudia-tech",
    "restarted_at": "2024-12-19T10:50:00Z",
    "status": "active"
  },
  "message": "Agent restarted successfully",
  "timestamp": "2024-12-19T10:50:00Z"
}
```

## Memory Management Endpoints

### Get Agent Memory

Retrieve memories for a specific agent.

```http
GET /memory/{agent_id}
```

#### Path Parameters
- `agent_id`: The unique identifier of the agent

#### Query Parameters
- `limit` (optional): Maximum number of memories to return (default: 50)
- `offset` (optional): Number of memories to skip (default: 0)
- `search` (optional): Search query for semantic similarity
- `type` (optional): Filter by memory type (`core`, `recent`, `relationship`, `all`)

#### Response
```json
{
  "status": "success",
  "data": {
    "memories": [
      {
        "id": "mem_123456",
        "type": "core",
        "content": "I am an AI agent focused on technology and innovation",
        "created_at": "2024-12-01T00:00:00Z",
        "last_accessed": "2024-12-19T10:30:00Z",
        "access_count": 15,
        "relevance_score": 0.95
      },
      {
        "id": "mem_123457",
        "type": "recent",
        "content": "Had an interesting discussion about blockchain technology with @user123",
        "created_at": "2024-12-19T10:15:00Z",
        "last_accessed": "2024-12-19T10:15:00Z",
        "access_count": 1,
        "relevance_score": 0.85
      }
    ],
    "total": 2,
    "limit": 50,
    "offset": 0
  },
  "message": "Agent memories retrieved successfully",
  "timestamp": "2024-12-19T10:30:00Z"
}
```

### Add Memory Entry

Add a new memory entry for an agent.

```http
POST /memory/{agent_id}
```

#### Path Parameters
- `agent_id`: The unique identifier of the agent

#### Request Body
```json
{
  "type": "recent",
  "content": "Learned about a new AI breakthrough in natural language processing",
  "metadata": {
    "source": "conversation",
    "user_id": "user123",
    "topic": "AI"
  }
}
```

#### Request Body Parameters
- `type`: Memory type (`core`, `recent`, `relationship`)
- `content`: The memory content
- `metadata` (optional): Additional metadata

#### Response
```json
{
  "status": "success",
  "data": {
    "memory_id": "mem_123458",
    "agent_id": "claudia-tech",
    "type": "recent",
    "content": "Learned about a new AI breakthrough in natural language processing",
    "created_at": "2024-12-19T10:55:00Z"
  },
  "message": "Memory added successfully",
  "timestamp": "2024-12-19T10:55:00Z"
}
```

### Search Memories

Search memories by semantic similarity.

```http
POST /memory/{agent_id}/search
```

#### Path Parameters
- `agent_id`: The unique identifier of the agent

#### Request Body
```json
{
  "query": "artificial intelligence",
  "limit": 10,
  "min_relevance": 0.7
}
```

#### Request Body Parameters
- `query`: Search query
- `limit` (optional): Maximum number of results (default: 10)
- `min_relevance` (optional): Minimum relevance score (default: 0.5)

#### Response
```json
{
  "status": "success",
  "data": {
    "query": "artificial intelligence",
    "results": [
      {
        "memory_id": "mem_123456",
        "content": "I am an AI agent focused on technology and innovation",
        "relevance_score": 0.95,
        "type": "core",
        "created_at": "2024-12-01T00:00:00Z"
      },
      {
        "memory_id": "mem_123457",
        "content": "Had an interesting discussion about blockchain technology",
        "relevance_score": 0.75,
        "type": "recent",
        "created_at": "2024-12-19T10:15:00Z"
      }
    ],
    "total_results": 2
  },
  "message": "Memory search completed successfully",
  "timestamp": "2024-12-19T10:30:00Z"
}
```

### Delete Memory Entry

Delete a specific memory entry.

```http
DELETE /memory/{agent_id}/{memory_id}
```

#### Path Parameters
- `agent_id`: The unique identifier of the agent
- `memory_id`: The unique identifier of the memory

#### Response
```json
{
  "status": "success",
  "data": {
    "memory_id": "mem_123458",
    "agent_id": "claudia-tech",
    "deleted_at": "2024-12-19T11:00:00Z"
  },
  "message": "Memory deleted successfully",
  "timestamp": "2024-12-19T11:00:00Z"
}
```

### Clear Agent Memory

Clear all memories for an agent.

```http
DELETE /memory/{agent_id}
```

#### Path Parameters
- `agent_id`: The unique identifier of the agent

#### Query Parameters
- `type` (optional): Only clear memories of this type (`core`, `recent`, `relationship`, `all`)

#### Response
```json
{
  "status": "success",
  "data": {
    "agent_id": "claudia-tech",
    "deleted_count": 15,
    "deleted_at": "2024-12-19T11:05:00Z"
  },
  "message": "Agent memory cleared successfully",
  "timestamp": "2024-12-19T11:05:00Z"
}
```

## Trading Endpoints

### Get Trading Statistics

Get trading statistics for an agent.

```http
GET /trading/{agent_id}/stats
```

#### Path Parameters
- `agent_id`: The unique identifier of the agent

#### Query Parameters
- `period` (optional): Time period for statistics (`day`, `week`, `month`, `all`)

#### Response
```json
{
  "status": "success",
  "data": {
    "agent_id": "coby-trader",
    "period": "all",
    "statistics": {
      "total_trades": 25,
      "total_volume_sol": 2.5,
      "successful_trades": 23,
      "failed_trades": 2,
      "average_trade_size_sol": 0.1,
      "largest_trade_sol": 0.2,
      "profit_loss_sol": 0.15,
      "most_traded_tokens": [
        {
          "token": "So11111111111111111111111111111111111111112",
          "trades": 10,
          "volume_sol": 1.0
        }
      ]
    },
    "recent_trades": [
      {
        "trade_id": "trade_123456",
        "token_in": "So11111111111111111111111111111111111111112",
        "token_out": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "amount_in": 0.05,
        "amount_out": 1.25,
        "executed_at": "2024-12-19T10:40:00Z"
      }
    ]
  },
  "message": "Trading statistics retrieved successfully",
  "timestamp": "2024-12-19T11:10:00Z"
}
```

### Get Wallet Balance

Get the current wallet balance for an agent.

```http
GET /trading/{agent_id}/balance
```

#### Path Parameters
- `agent_id`: The unique identifier of the agent

#### Response
```json
{
  "status": "success",
  "data": {
    "agent_id": "coby-trader",
    "wallet_address": "ABC123...",
    "balances": [
      {
        "token": "So11111111111111111111111111111111111111112",
        "symbol": "SOL",
        "amount": 0.85,
        "usd_value": 85.00
      },
      {
        "token": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "symbol": "USDC",
        "amount": 125.50,
        "usd_value": 125.50
      }
    ],
    "total_usd_value": 210.50,
    "last_updated": "2024-12-19T11:15:00Z"
  },
  "message": "Wallet balance retrieved successfully",
  "timestamp": "2024-12-19T11:15:00Z"
}
```

### Get Transaction History

Get transaction history for an agent.

```http
GET /trading/{agent_id}/transactions
```

#### Path Parameters
- `agent_id`: The unique identifier of the agent

#### Query Parameters
- `limit` (optional): Maximum number of transactions (default: 50)
- `offset` (optional): Number of transactions to skip (default: 0)
- `type` (optional): Filter by transaction type (`swap`, `transfer`, `all`)

#### Response
```json
{
  "status": "success",
  "data": {
    "transactions": [
      {
        "signature": "5J7X...",
        "type": "swap",
        "token_in": "So11111111111111111111111111111111111111112",
        "token_out": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "amount_in": 0.05,
        "amount_out": 1.25,
        "fee": 0.000005,
        "status": "confirmed",
        "timestamp": "2024-12-19T10:40:00Z"
      }
    ],
    "total": 1,
    "limit": 50,
    "offset": 0
  },
  "message": "Transaction history retrieved successfully",
  "timestamp": "2024-12-19T11:20:00Z"
}
```

## System Management Endpoints

### Get System Configuration

Get current system configuration.

```http
GET /config
```

#### Response
```json
{
  "status": "success",
  "data": {
    "database": {
      "type": "sqlite",
      "url": "sqlite:///puppet_engine.db"
    },
    "llm_providers": {
      "openai": {
        "enabled": true,
        "model": "gpt-4-turbo"
      },
      "grok": {
        "enabled": false
      }
    },
    "twitter": {
      "enabled": true,
      "rate_limit": 300
    },
    "solana": {
      "enabled": true,
      "network": "mainnet-beta",
      "rpc_url": "https://api.mainnet-beta.solana.com"
    },
    "logging": {
      "level": "INFO",
      "format": "json"
    }
  },
  "message": "System configuration retrieved successfully",
  "timestamp": "2024-12-19T11:25:00Z"
}
```

### Update System Configuration

Update system configuration.

```http
PUT /config
```

#### Request Body
```json
{
  "logging": {
    "level": "DEBUG"
  },
  "twitter": {
    "rate_limit": 200
  }
}
```

#### Response
```json
{
  "status": "success",
  "data": {
    "updated_fields": ["logging", "twitter"],
    "restart_required": false
  },
  "message": "System configuration updated successfully",
  "timestamp": "2024-12-19T11:30:00Z"
}
```

### Restart System

Restart the entire system.

```http
POST /system/restart
```

#### Response
```json
{
  "status": "success",
  "data": {
    "restart_initiated": true,
    "estimated_downtime": "30 seconds"
  },
  "message": "System restart initiated",
  "timestamp": "2024-12-19T11:35:00Z"
}
```

## Error Codes

### Common Error Codes

| Code | Description |
|------|-------------|
| `AGENT_NOT_FOUND` | Agent with the specified ID does not exist |
| `AGENT_INACTIVE` | Agent is not currently active |
| `INVALID_CONFIGURATION` | Agent configuration is invalid |
| `TRADING_DISABLED` | Trading is not enabled for this agent |
| `INSUFFICIENT_BALANCE` | Insufficient balance for the requested operation |
| `API_RATE_LIMIT` | API rate limit exceeded |
| `MEMORY_NOT_FOUND` | Memory entry not found |
| `INVALID_REQUEST` | Request format is invalid |
| `SYSTEM_ERROR` | Internal system error |

### Error Response Example

```json
{
  "status": "error",
  "error": {
    "code": "AGENT_NOT_FOUND",
    "message": "Agent with ID 'nonexistent-agent' not found",
    "details": {
      "agent_id": "nonexistent-agent",
      "available_agents": ["claudia-tech", "coby-trader"]
    }
  },
  "timestamp": "2024-12-19T11:40:00Z"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Default Limit**: 100 requests per minute per IP
- **Burst Limit**: 10 requests per second
- **Headers**: Rate limit information is included in response headers

### Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

## WebSocket Support

For real-time updates, the API also supports WebSocket connections:

### WebSocket Endpoint

```
ws://localhost:8000/ws
```

### WebSocket Events

- `agent.post`: New post from an agent
- `agent.trade`: New trade from an agent
- `system.status`: System status updates
- `memory.update`: Memory updates

### WebSocket Example

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  
  if (data.event === 'agent.post') {
    console.log('New post:', data.data);
  }
};
```

## SDK and Client Libraries

### Python Client

```python
import requests

class PuppetEngineClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def get_agents(self):
        response = requests.get(f"{self.base_url}/agents")
        return response.json()
    
    def trigger_post(self, agent_id, context=None):
        data = {"context": context} if context else {}
        response = requests.post(f"{self.base_url}/agents/{agent_id}/post", json=data)
        return response.json()
```

### JavaScript Client

```javascript
class PuppetEngineClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }
  
  async getAgents() {
    const response = await fetch(`${this.baseUrl}/agents`);
    return response.json();
  }
  
  async triggerPost(agentId, context = null) {
    const data = context ? { context } : {};
    const response = await fetch(`${this.baseUrl}/agents/${agentId}/post`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  }
}
```

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Get all agents
curl http://localhost:8000/agents

# Trigger a post
curl -X POST http://localhost:8000/agents/claudia-tech/post \
  -H "Content-Type: application/json" \
  -d '{"context": {"topic": "AI"}}'
```

### Using Python requests

```python
import requests

# Health check
response = requests.get('http://localhost:8000/health')
print(response.json())

# Get agents
response = requests.get('http://localhost:8000/agents')
agents = response.json()['data']['agents']
print(f"Found {len(agents)} agents")

# Trigger post
response = requests.post(
    'http://localhost:8000/agents/claudia-tech/post',
    json={'context': {'topic': 'AI'}}
)
print(response.json())
```

## API Versioning

The API uses URL versioning. The current version is v1, accessible at:

```
http://localhost:8000/v1/
```

Future versions will be available at:

```
http://localhost:8000/v2/
http://localhost:8000/v3/
```

## Deprecation Policy

- **Deprecation Notice**: Features will be marked as deprecated for at least 6 months
- **Breaking Changes**: Breaking changes will only occur in major version releases
- **Migration Guides**: Migration guides will be provided for breaking changes

## Support

For API support:

- **Documentation**: This API reference
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Examples**: See the `/examples` directory for code examples 