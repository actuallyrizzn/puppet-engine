# Puppet Engine API Documentation

## Overview
The Puppet Engine API provides HTTP endpoints for monitoring and controlling AI agents. The API is RESTful and returns JSON responses.

## Base URL
```
http://localhost:3000/api
```

## Authentication
Currently, the API does not implement authentication. All endpoints are publicly accessible.

## Endpoints

### System Status
```http
GET /api/status
```
Returns the current status of the Puppet Engine.

**Response**
```json
{
  "status": "online",
  "agents": 2,
  "uptime": 123.45
}
```

### Agent Management

#### List All Agents
```http
GET /api/agents
```
Returns a list of all configured agents.

**Response**
```json
[
  {
    "id": "agent-1",
    "name": "Agent Name",
    "description": "Agent description",
    "lastPostTime": "2024-02-20T12:00:00Z",
    "mood": "happy"
  }
]
```

#### Get Agent Details
```http
GET /api/agents/:agentId
```
Returns detailed information about a specific agent.

**Response**
```json
{
  "id": "agent-1",
  "name": "Agent Name",
  "description": "Agent description",
  "personality": { ... },
  "styleGuide": { ... },
  "behavior": { ... },
  "currentMood": "happy",
  "lastPostTime": "2024-02-20T12:00:00Z",
  "goals": [ ... ]
}
```

#### Get Agent Memory
```http
GET /api/agents/:agentId/memory
```
Returns the agent's memory state.

**Response**
```json
{
  "memories": [ ... ],
  "relationships": { ... },
  "recentEvents": [ ... ]
}
```

#### Get Agent Relationships
```http
GET /api/agents/:agentId/relationships
```
Returns the agent's relationship data with other agents.

**Response**
```json
{
  "relationships": {
    "agent-2": {
      "type": "friend",
      "strength": 0.8,
      "lastInteraction": "2024-02-20T12:00:00Z"
    }
  }
}
```

#### Debug: Get Agent Context
```http
GET /api/agents/:agentId/context
```
Returns the agent's current prompt context (debug endpoint).

**Response**
```json
{
  "context": "Full prompt context...",
  "hasCustomPrompt": true
}
```

#### Create Agent Post
```http
POST /api/agents/:agentId/post
```
Triggers an agent to create a new post.

**Request Body**
```json
{
  "topic": "Optional topic for the post",
  "threadLength": 3,
  "force": false
}
```

**Response**
```json
{
  "id": "tweet-id",
  "content": "Tweet content",
  "createdAt": "2024-02-20T12:00:00Z"
}
```

#### Create Agent Reply
```http
POST /api/agents/:agentId/reply
```
Creates a reply to another tweet.

**Request Body**
```json
{
  "tweetId": "original-tweet-id",
  "content": "Optional content for context"
}
```

**Response**
```json
{
  "id": "reply-tweet-id",
  "content": "Reply content",
  "createdAt": "2024-02-20T12:00:00Z"
}
```

#### Create New Agent
```http
POST /api/agents
```
Creates a new agent from a configuration.

**Request Body**
```json
{
  "id": "new-agent-id",
  "name": "New Agent",
  "description": "Agent description",
  "personality": { ... },
  "styleGuide": { ... },
  "behavior": { ... }
}
```

**Response**
```json
{
  "id": "new-agent-id",
  "name": "New Agent",
  "message": "Agent created successfully"
}
```

#### Update Agent Mood
```http
POST /api/agents/:agentId/mood
```
Updates an agent's current mood using VAD (Valence, Arousal, Dominance) model.

**Request Body**
```json
{
  "valenceShift": 0.2,    // Range: -1.0 to 1.0
  "arousalShift": -0.1,   // Range: -1.0 to 1.0
  "dominanceShift": 0.0   // Range: -1.0 to 1.0
}
```

**Response**
```json
{
  "agent": "agent-1",
  "mood": "happy"  // Current mood after update
}
```

#### Add Agent Memory
```http
POST /api/agents/:agentId/memories
```
Adds a new memory to the agent's memory store.

**Request Body**
```json
{
  "content": "Memory content",  // Required
  "type": "general",           // Optional, defaults to "general"
  "importance": 0.5           // Optional, defaults to 0.5
}
```

**Response**
```json
{
  "id": "memory-id",
  "content": "Memory content",
  "type": "general",
  "importance": 0.5,
  "timestamp": "2024-02-20T12:00:00Z"
}
```

### Event Management

#### List Events
```http
GET /api/events
```
Returns a list of all events with their processing status.

**Response**
```json
[
  {
    "id": "event-1",
    "type": "mood-change",
    "data": { ... },
    "timestamp": "2024-02-20T12:00:00Z",
    "processedAt": "2024-02-20T12:00:01Z",
    "targetAgentIds": ["agent-1", "agent-2"]
  }
]
```

#### Create Event
```http
POST /api/events
```
Creates a new event that can be triggered immediately or scheduled for later.

**Request Body**
```json
{
  "type": "event-type",      // Required
  "data": { ... },          // Required
  "targetAgentIds": ["agent-1", "agent-2"],  // Optional
  "priority": "high",       // Optional
  "delay": 3600000         // Optional, in milliseconds
}
```

**Validation Errors**
- `400 Bad Request`: If `type` or `data` is missing
- `500 Internal Server Error`: If event creation fails

**Response (Immediate)**
```json
{
  "scheduled": false,
  "event": {
    "id": "event-id",
    "type": "event-type",
    "timestamp": "2024-02-20T12:00:00Z"
  }
}
```

**Response (Scheduled)**
```json
{
  "scheduled": true,
  "event": {
    "id": "event-id",
    "type": "event-type",
    "timestamp": "2024-02-20T12:00:00Z",
    "executeAfter": "2024-02-20T13:00:00Z"
  }
}
```

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
  - Agent creation: Missing or invalid configuration
  - Event creation: Missing type or data
  - Memory creation: Missing content
  - Reply creation: Missing tweetId
- `404 Not Found`: Resource not found
  - Agent not found
  - Memory not found
- `429 Too Many Requests`: Rate limit exceeded
  - Post creation too frequent
- `500 Internal Server Error`: Server error
  - Database errors
  - External service failures
  - Internal processing errors

Error responses include a message:
```json
{
  "error": "Error message description"
}
```

## Rate Limiting

The API implements rate limiting for agent posts to prevent spam. If an agent attempts to post too frequently, the endpoint will return a 429 status code with the last post time:

```json
{
  "error": "Too soon since last post",
  "lastPostTime": "2024-02-20T12:00:00Z"
}
```

## CORS

The API supports Cross-Origin Resource Sharing (CORS) with the following headers:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Headers: Origin, X-Requested-With, Content-Type, Accept`
- `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`

## Logging

All API requests are logged with timestamp, method, and path:
```
2024-02-20T12:00:00Z - GET /api/status
``` 