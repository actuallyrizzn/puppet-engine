# Configuration Guide

## Overview

Puppet Engine can be configured through environment variables, configuration files, and runtime settings. This guide covers all configuration options and their usage.

## Configuration Sources

Configuration is loaded in the following order (later sources override earlier ones):

1. **Environment Variables** (highest priority)
2. **Configuration Files** (`.env`, `config.json`)
3. **Default Values** (lowest priority)

## Environment Variables

### Core Configuration

#### Database Settings
```env
# Database connection
DATABASE_URL=sqlite:///puppet_engine.db
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30
```

#### Server Settings
```env
# Server configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4
RELOAD=false
```

#### Logging Settings
```env
# Logging configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/puppet-engine/app.log
LOG_MAX_SIZE=10485760  # 10MB
LOG_BACKUP_COUNT=5
```

#### Environment Settings
```env
# Environment
ENVIRONMENT=production
DEBUG=false
ENABLE_METRICS=true
METRICS_PORT=9090
```

### API Keys

#### Twitter API
```env
# Twitter API credentials
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
```

#### LLM Providers
```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4-turbo
OPENAI_ORGANIZATION=your_org_id

# Grok
GROK_API_KEY=your_grok_api_key
GROK_API_ENDPOINT=https://api.grok.x.com/v1/chat/completions
GROK_MODEL=grok-1
```

#### Solana Configuration
```env
# Solana settings
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_NETWORK=mainnet-beta
SOLANA_COMMITMENT=confirmed

# Agent-specific private keys (pattern: SOLANA_PRIVATE_KEY_AGENT_ID)
SOLANA_PRIVATE_KEY_AGENT_1=your_private_key_1
SOLANA_PRIVATE_KEY_AGENT_2=your_private_key_2
```

### Security Settings

#### Authentication
```env
# API authentication
API_KEY=your_api_key
JWT_SECRET=your_jwt_secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600
```

#### Rate Limiting
```env
# Rate limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
RATE_LIMIT_BURST=10
```

### Performance Settings

#### Caching
```env
# Cache configuration
CACHE_ENABLED=true
CACHE_TTL=3600
CACHE_MAX_SIZE=1000
REDIS_URL=redis://localhost:6379
```

#### Connection Pools
```env
# Connection pool settings
HTTP_POOL_SIZE=20
HTTP_MAX_RETRIES=3
HTTP_TIMEOUT=30
```

## Configuration Files

### .env File

Create a `.env` file in the project root:

```env
# Core Configuration
ENVIRONMENT=development
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///dev_puppet_engine.db

# API Keys
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
OPENAI_API_KEY=your_openai_api_key

# Server Settings
HOST=127.0.0.1
PORT=8000
WORKERS=1
RELOAD=true

# Development Settings
DEBUG=true
ENABLE_METRICS=false
```

### config.json

For more complex configurations, use a JSON file:

```json
{
  "database": {
    "url": "sqlite:///puppet_engine.db",
    "pool_size": 10,
    "max_overflow": 20,
    "pool_timeout": 30
  },
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "workers": 4,
    "reload": false
  },
  "logging": {
    "level": "INFO",
    "format": "json",
    "file": "/var/log/puppet-engine/app.log",
    "max_size": 10485760,
    "backup_count": 5
  },
  "api_keys": {
    "twitter": {
      "api_key": "your_twitter_api_key",
      "api_secret": "your_twitter_api_secret",
      "access_token": "your_twitter_access_token",
      "access_token_secret": "your_twitter_access_token_secret"
    },
    "openai": {
      "api_key": "your_openai_api_key",
      "model": "gpt-4-turbo"
    }
  },
  "solana": {
    "rpc_url": "https://api.mainnet-beta.solana.com",
    "network": "mainnet-beta",
    "commitment": "confirmed"
  },
  "security": {
    "api_key": "your_api_key",
    "jwt_secret": "your_jwt_secret",
    "rate_limit_requests": 100,
    "rate_limit_window": 60
  },
  "performance": {
    "cache_enabled": true,
    "cache_ttl": 3600,
    "http_pool_size": 20,
    "http_max_retries": 3
  }
}
```

## Runtime Configuration

### Settings Class

The main configuration is handled by the `Settings` class:

```python
from src.core.settings import Settings

# Load settings from environment and files
settings = Settings()

# Access configuration values
database_url = settings.database_url
log_level = settings.log_level
twitter_api_key = settings.twitter_api_key
```

### Configuration Validation

Settings are validated on startup:

```python
# Validate configuration
try:
    settings = Settings()
    settings.validate()
except ValidationError as e:
    print(f"Configuration error: {e}")
    exit(1)
```

## Environment-Specific Configuration

### Development Environment

```env
# Development settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///dev_puppet_engine.db
HOST=127.0.0.1
PORT=8000
WORKERS=1
RELOAD=true
ENABLE_METRICS=false
```

### Production Environment

```env
# Production settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///puppet_engine.db
HOST=0.0.0.0
PORT=8000
WORKERS=4
RELOAD=false
ENABLE_METRICS=true
METRICS_PORT=9090
```

### Testing Environment

```env
# Testing settings
ENVIRONMENT=testing
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///test_puppet_engine.db
HOST=127.0.0.1
PORT=8001
WORKERS=1
RELOAD=false
ENABLE_METRICS=false
```

## Agent Configuration

### Agent-Specific Settings

Each agent can have its own configuration:

```json
{
  "id": "my-agent",
  "name": "My Agent",
  "llm_provider": "openai",
  "llm_config": {
    "model": "gpt-4-turbo",
    "temperature": 0.7,
    "max_tokens": 280
  },
  "twitter_credentials": {
    "api_key": "agent_specific_key",
    "api_secret": "agent_specific_secret",
    "access_token": "agent_specific_token",
    "access_token_secret": "agent_specific_token_secret"
  },
  "solana_integration": {
    "wallet_address": "agent_wallet_address",
    "private_key": "agent_private_key",
    "network": "mainnet-beta"
  }
}
```

### Agent Configuration Loading

```python
from src.agents.agent_manager import AgentManager

# Load agent configurations
agent_configs = AgentManager.load_agent_configs("config/agents/")

# Create agents with configurations
for config in agent_configs:
    agent = await agent_manager.create_agent(config)
```

## Database Configuration

### SQLite Configuration

```env
# SQLite settings
DATABASE_URL=sqlite:///puppet_engine.db
DATABASE_POOL_SIZE=1
DATABASE_MAX_OVERFLOW=0
```

### PostgreSQL Configuration

```env
# PostgreSQL settings
DATABASE_URL=postgresql://user:password@localhost:5432/puppet_engine
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30
```

### MongoDB Configuration

```env
# MongoDB settings
MONGODB_URL=mongodb://localhost:27017/puppet_engine
MONGODB_DATABASE=puppet_engine
MONGODB_COLLECTION=memories
```

## Logging Configuration

### Basic Logging

```env
# Basic logging
LOG_LEVEL=INFO
LOG_FORMAT=text
```

### Advanced Logging

```env
# Advanced logging
LOG_LEVEL=DEBUG
LOG_FORMAT=json
LOG_FILE=/var/log/puppet-engine/app.log
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5
LOG_ROTATION=daily
```

### Logging Configuration File

Create `logging.conf`:

```ini
[loggers]
keys=root,puppet_engine

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter,jsonFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_puppet_engine]
level=DEBUG
handlers=consoleHandler,fileHandler
qualname=puppet_engine
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=handlers.RotatingFileHandler
level=DEBUG
formatter=jsonFormatter
args=('/var/log/puppet-engine/app.log', 'a', 10485760, 5)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s

[formatter_jsonFormatter]
class=pythonjsonlogger.jsonlogger.JsonFormatter
format=%(asctime)s %(name)s %(levelname)s %(message)s
```

## Security Configuration

### API Security

```env
# API security
API_KEY=your_secure_api_key
JWT_SECRET=your_secure_jwt_secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
```

### Rate Limiting

```env
# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
RATE_LIMIT_BURST=10
RATE_LIMIT_STORAGE_URL=redis://localhost:6379
```

### CORS Configuration

```env
# CORS settings
CORS_ENABLED=true
CORS_ORIGINS=http://localhost:3000,https://your-domain.com
CORS_METHODS=GET,POST,PUT,DELETE
CORS_HEADERS=Content-Type,Authorization
```

## Performance Configuration

### Caching

```env
# Cache settings
CACHE_ENABLED=true
CACHE_TTL=3600
CACHE_MAX_SIZE=1000
REDIS_URL=redis://localhost:6379
CACHE_PREFIX=puppet_engine
```

### Connection Pools

```env
# HTTP connection pool
HTTP_POOL_SIZE=20
HTTP_MAX_RETRIES=3
HTTP_TIMEOUT=30
HTTP_KEEPALIVE_TIMEOUT=30
HTTP_MAX_REDIRECTS=5
```

### Database Optimization

```env
# Database optimization
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600
DATABASE_ECHO=false
```

## Monitoring Configuration

### Metrics

```env
# Metrics settings
ENABLE_METRICS=true
METRICS_PORT=9090
METRICS_PATH=/metrics
METRICS_PREFIX=puppet_engine
```

### Health Checks

```env
# Health check settings
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10
HEALTH_CHECK_PATH=/health
```

### Tracing

```env
# Tracing settings
TRACING_ENABLED=true
TRACING_SERVICE_NAME=puppet_engine
TRACING_AGENT_HOST=localhost
TRACING_AGENT_PORT=6831
```

## Configuration Validation

### Schema Validation

```python
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    database_url: str
    log_level: str
    twitter_api_key: str
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'log_level must be one of {valid_levels}')
        return v.upper()
    
    @validator('database_url')
    def validate_database_url(cls, v):
        if not v.startswith(('sqlite://', 'postgresql://', 'mongodb://')):
            raise ValueError('Invalid database URL format')
        return v
```

### Required Fields

```python
class Settings(BaseSettings):
    # Required fields
    twitter_api_key: str
    openai_api_key: str
    
    # Optional fields with defaults
    log_level: str = "INFO"
    database_url: str = "sqlite:///puppet_engine.db"
    
    class Config:
        env_file = ".env"
```

## Configuration Management

### Environment-Specific Files

Create environment-specific configuration files:

```bash
# Development
cp .env.example .env.development

# Production
cp .env.example .env.production

# Testing
cp .env.example .env.testing
```

### Configuration Loading

```python
import os
from src.core.settings import Settings

# Load environment-specific configuration
env = os.getenv("ENVIRONMENT", "development")
env_file = f".env.{env}"

settings = Settings(_env_file=env_file)
```

### Configuration Updates

```python
# Update configuration at runtime
settings.update({
    "log_level": "DEBUG",
    "cache_enabled": True
})

# Reload configuration
settings.reload()
```

## Best Practices

### Security

1. **Never commit secrets**: Use environment variables for sensitive data
2. **Use strong secrets**: Generate secure API keys and secrets
3. **Validate configuration**: Always validate configuration on startup
4. **Use HTTPS**: Use HTTPS in production environments

### Performance

1. **Optimize database connections**: Use appropriate pool sizes
2. **Enable caching**: Use Redis for caching when possible
3. **Monitor resources**: Track memory and CPU usage
4. **Use connection pooling**: Configure HTTP and database pools

### Maintainability

1. **Use environment variables**: For environment-specific settings
2. **Document configuration**: Document all configuration options
3. **Validate configuration**: Validate configuration on startup
4. **Use defaults**: Provide sensible defaults for all settings

### Development

1. **Use .env files**: For local development
2. **Separate environments**: Use different configurations for different environments
3. **Test configuration**: Test configuration in CI/CD
4. **Version control**: Version control configuration templates

## Troubleshooting

### Common Issues

#### Configuration Not Loading
- **Problem**: Configuration not being loaded
- **Solution**: Check file paths and environment variables

#### Validation Errors
- **Problem**: Configuration validation failing
- **Solution**: Check required fields and data types

#### Environment Variables Not Set
- **Problem**: Environment variables not being read
- **Solution**: Check variable names and casing

#### File Permissions
- **Problem**: Cannot read configuration files
- **Solution**: Check file permissions and ownership

### Debug Configuration

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Print configuration
settings = Settings()
print(settings.dict())
```

### Configuration Testing

```python
# Test configuration loading
def test_configuration():
    try:
        settings = Settings()
        settings.validate()
        print("Configuration is valid")
    except Exception as e:
        print(f"Configuration error: {e}")
```

## Support

For configuration issues:

- **Documentation**: This guide and API reference
- **Issues**: [GitHub Issues](https://github.com/username/puppet-engine/issues)
- **Discussions**: [GitHub Discussions](https://github.com/username/puppet-engine/discussions) 