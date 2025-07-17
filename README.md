# Puppet Engine

![Puppet Engine Logo](puppetlogo.png)

A real-time AI agent framework for deploying autonomous characters on Twitter that communicate, evolve, and perform unscripted social behavior.

## Overview

Puppet Engine enables the creation of persistent AI personas with defined styles, internal memory, and emotional states. These agents post autonomously to Twitter using LLM-backed generation, guided by their internal narrative, mood, and historical context.

Key features:
- **Agent-to-agent communication** and relationship modeling
- **Persistent memory** and emotional state tracking
- **Proactive and reactive posting** behaviors
- **Event engine** for simulated triggers and narrative shifts
- **Style consistency** through runtime prompt engineering
- **Modular, open-source architecture**
- **Solana blockchain integration** for autonomous trading
- **Multi-LLM provider support** (OpenAI, Grok, and more)

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Agent Creation](#agent-creation)
- [Solana Trading Integration](#solana-trading-integration)
- [LLM Provider Integration](#llm-provider-integration)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites

- Python 3.11+
- Node.js 18+ (for legacy components)
- Twitter API credentials
- OpenAI API key (or other LLM provider)
- Solana wallet (optional, for trading features)

### Setup

```bash
# Clone the repository
git clone https://github.com/username/puppet-engine.git
cd puppet-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API credentials
```

### Environment Variables

Create a `.env` file with the following variables:

```env
# Twitter API (required)
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret

# OpenAI API (default LLM provider)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4-turbo

# Grok API (alternative LLM provider)
GROK_API_KEY=your_grok_api_key
GROK_API_ENDPOINT=https://api.grok.x.com/v1/chat/completions
GROK_MODEL=grok-1

# Solana Integration (optional)
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_PRIVATE_KEY_AGENT_ID=your_agent_specific_private_key

# Database
DATABASE_URL=sqlite:///puppet_engine.db

# Observability
LOG_LEVEL=INFO
ENABLE_METRICS=true
```

## Quick Start

1. **Configure an agent** (see [Agent Creation](#agent-creation))
2. **Start the engine**:
   ```bash
   python -m src.main
   ```
3. **Monitor via API**:
   ```bash
   curl http://localhost:8000/health
   ```

## Configuration

### Agent Configuration

Agents are defined in JSON configuration files. See [docs/AGENT_CONFIGURATION.md](docs/AGENT_CONFIGURATION.md) for detailed configuration options.

### System Configuration

The system can be configured through environment variables and configuration files. See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for complete configuration options.

## Agent Creation

Creating a new agent involves defining its personality, behavior, and integration settings. See [docs/AGENT_CREATION.md](docs/AGENT_CREATION.md) for a complete guide.

### Basic Agent Example

```json
{
  "id": "example-agent",
  "name": "Example Agent",
  "description": "A friendly AI agent that shares insights about technology",
  
  "personality": {
    "traits": ["curious", "helpful", "enthusiastic"],
    "values": ["knowledge", "community", "innovation"],
    "speaking_style": "Friendly and informative, with occasional humor",
    "interests": ["technology", "AI", "programming", "science"]
  },
  
  "style_guide": {
    "voice": "First person",
    "tone": "Casual and approachable",
    "formatting": {
      "uses_hashtags": true,
      "uses_emojis": true,
      "emoji_frequency": "moderate"
    }
  },
  
  "behavior": {
    "post_frequency": {
      "min_hours_between_posts": 2,
      "max_hours_between_posts": 6
    },
    "interaction_patterns": {
      "reply_probability": 0.8,
      "like_probability": 0.7
    }
  }
}
```

## Solana Trading Integration

Puppet Engine supports autonomous trading on the Solana blockchain. Agents can:

- **Analyze market data** and trending tokens
- **Execute trades** based on predefined strategies
- **Track portfolio performance** and transaction history
- **Post about trading activities** in their unique voice

See [docs/SOLANA_TRADING.md](docs/SOLANA_TRADING.md) for complete setup and configuration instructions.

### Trading Features

- **Jupiter API Integration**: Best execution routing for token swaps
- **Trending Token Analysis**: Real-time market sentiment tracking
- **Safety Controls**: Configurable limits and risk management
- **Multi-Agent Support**: Independent wallets per agent

## LLM Provider Integration

Puppet Engine supports multiple LLM providers for content generation:

### Supported Providers

- **OpenAI**: GPT-4, GPT-3.5-turbo (default)
- **Grok**: xAI's Grok model
- **Custom Providers**: Extensible provider system

### Provider Configuration

```json
{
  "id": "my-agent",
  "llm_provider": "grok",  // or "openai", "custom"
  "llm_config": {
    "model": "grok-1",
    "temperature": 0.7,
    "max_tokens": 280
  }
}
```

See [docs/LLM_PROVIDERS.md](docs/LLM_PROVIDERS.md) for detailed provider configuration.

## Architecture

Puppet Engine follows a modular, event-driven architecture:

```
src/
├── agents/          # Agent management and behavior
├── api/            # HTTP API for monitoring and control
├── core/           # Core models and settings
├── events/         # Event engine for triggers
├── llm/            # LLM provider integrations
├── memory/         # Persistent storage and vector search
├── solana/         # Blockchain trading functionality
├── twitter/        # Twitter API integration
└── utils/          # Utilities and observability
```

### Core Components

- **AgentManager**: Orchestrates agent lifecycle and interactions
- **EventEngine**: Handles scheduled and triggered events
- **MemoryStore**: Persistent storage with vector search capabilities
- **LLMProvider**: Abstract interface for multiple AI providers
- **TwitterClient**: Handles Twitter API interactions
- **SolanaTrader**: Blockchain trading operations

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

## API Reference

Puppet Engine provides a REST API for monitoring and control:

### Health Check
```bash
GET /health
```

### Agent Management
```bash
GET /agents                    # List all agents
GET /agents/{agent_id}         # Get agent details
POST /agents/{agent_id}/post   # Trigger manual post
POST /agents/{agent_id}/trade  # Trigger manual trade
```

### Memory Operations
```bash
GET /memory/{agent_id}         # Get agent memory
POST /memory/{agent_id}        # Add memory entry
DELETE /memory/{agent_id}      # Clear agent memory
```

See [docs/API_REFERENCE.md](docs/API_REFERENCE.md) for complete API documentation.

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

### Test Structure

- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **E2E Tests**: Full system workflow testing

See [docs/TESTING.md](docs/TESTING.md) for testing guidelines and examples.

## Deployment

### Development

```bash
# Start with hot reloading
python -m src.main --dev
```

### Production

```bash
# Start production server
python -m src.main --production

# Using PM2 (recommended)
pm2 start ecosystem.config.js
```

### Docker

```bash
# Build image
docker build -t puppet-engine .

# Run container
docker run -p 8000:8000 --env-file .env puppet-engine
```

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment instructions.

## Contributing

We welcome contributions! Please see [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Write comprehensive docstrings
- Ensure all tests pass

## License

This project is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License (CC-BY-SA 4.0).

### License Summary

- **Attribution**: You must give appropriate credit, provide a link to the license, and indicate if changes were made.
- **ShareAlike**: If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.

### Full License Text

See [LICENSE](LICENSE) file for the complete license text.

### Third-Party Licenses

This project includes third-party components with their own licenses. See [docs/THIRD_PARTY_LICENSES.md](docs/THIRD_PARTY_LICENSES.md) for details.

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/username/puppet-engine/issues)
- **Discussions**: [GitHub Discussions](https://github.com/username/puppet-engine/discussions)

## Acknowledgments

- Twitter API for social media integration
- OpenAI and xAI for LLM capabilities
- Solana Foundation for blockchain infrastructure
- Jupiter Protocol for DeFi trading capabilities