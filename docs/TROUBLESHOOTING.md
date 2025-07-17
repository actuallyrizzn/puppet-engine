# Troubleshooting Guide

This guide helps you resolve common issues with Puppet Engine. If you can't find your issue here, please check the [GitHub Issues](https://github.com/username/puppet-engine/issues) or create a new one.

## 🚨 Quick Fixes

### Common Startup Issues

**Problem**: `ModuleNotFoundError: No module named 'src'`
```bash
# Solution: Run from project root directory
cd /path/to/puppet-engine
python -m src.main
```

**Problem**: `ImportError: cannot import name 'X' from 'Y'`
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Problem**: `sqlite3.OperationalError: no such table`
```bash
# Solution: Database needs initialization
python -m src.main --init-db
```

## 🔧 Installation & Setup

### Python Environment Issues

**Problem**: Python version compatibility
```bash
# Check Python version (requires 3.11+)
python --version

# If using older version, upgrade Python
# Windows: Download from python.org
# macOS: brew install python@3.11
# Linux: sudo apt install python3.11
```

**Problem**: Virtual environment not activated
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

**Problem**: Dependencies installation fails
```bash
# Upgrade pip first
pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v

# If specific package fails, install individually
pip install fastapi uvicorn pydantic
```

### Environment Configuration

**Problem**: Missing environment variables
```bash
# Check if .env file exists
ls -la .env

# Create from template
cp .env.example .env
# Edit .env with your actual values
```

**Problem**: Environment variables not loaded
```python
# In your code, ensure dotenv is loaded
from dotenv import load_dotenv
load_dotenv()
```

## 🤖 Agent Issues

### Agent Loading Problems

**Problem**: Agent configuration not found
```
Error: Agent configuration file not found: config/agents/my-agent.json
```

**Solutions**:
1. Check file path and name
2. Ensure JSON syntax is valid
3. Verify file permissions

**Problem**: Invalid agent configuration
```json
// Common JSON errors:
{
  "id": "my-agent",  // Missing quotes
  "name": "My Agent", // Trailing comma
  "personality": {    // Missing closing brace
    "traits": ["friendly"]
}
```

**Solution**: Validate JSON syntax
```bash
# Use online JSON validator or Python
python -c "import json; json.load(open('config/agents/my-agent.json'))"
```

### Agent Behavior Issues

**Problem**: Agent not posting
- Check Twitter API credentials
- Verify agent is active in configuration
- Check logs for rate limiting errors
- Ensure LLM provider is configured

**Problem**: Agent posting too frequently
```json
// Adjust posting frequency in agent config
{
  "behavior": {
    "post_frequency": {
      "min_hours_between_posts": 4,
      "max_hours_between_posts": 8
    }
  }
}
```

**Problem**: Agent personality inconsistent
- Review system prompt in configuration
- Check for conflicting personality traits
- Ensure style guide is properly configured

## 🧠 LLM Provider Issues

### OpenAI Issues

**Problem**: `openai.AuthenticationError`
```bash
# Check API key
echo $OPENAI_API_KEY

# Verify key format (starts with sk-)
# Regenerate key if needed
```

**Problem**: Rate limiting
```python
# Add retry logic in configuration
{
  "llm_config": {
    "retry_attempts": 3,
    "retry_delay": 1.0
  }
}
```

**Problem**: Model not available
```python
# Check available models
# Use gpt-4-turbo or gpt-3.5-turbo
{
  "llm_config": {
    "model": "gpt-4-turbo"
  }
}
```

### Grok Issues

**Problem**: Grok API endpoint not responding
```bash
# Check endpoint URL
echo $GROK_API_ENDPOINT

# Default: https://api.grok.x.com/v1/chat/completions
# Verify network connectivity
```

**Problem**: Grok authentication failed
```bash
# Check API key format
echo $GROK_API_KEY

# Ensure key is valid for Grok API
```

## 🐦 Twitter Integration Issues

### Authentication Problems

**Problem**: `Twitter API authentication failed`
```bash
# Verify all Twitter credentials
echo $TWITTER_API_KEY
echo $TWITTER_API_SECRET
echo $TWITTER_ACCESS_TOKEN
echo $TWITTER_ACCESS_TOKEN_SECRET

# Regenerate credentials if needed
```

**Problem**: Rate limiting
```
Error: Rate limit exceeded. Try again in 15 minutes.
```

**Solutions**:
- Reduce posting frequency
- Implement exponential backoff
- Check Twitter API limits

### Posting Issues

**Problem**: Tweet too long
```python
# Check tweet length (280 characters)
# Truncate or split long content
```

**Problem**: Invalid characters in tweet
```python
# Remove or encode special characters
# Check for unsupported Unicode
```

**Problem**: Media upload fails
```python
# Check file size (max 5MB for images)
# Verify file format (JPG, PNG, GIF)
# Ensure media URL is accessible
```

## 💰 Solana Trading Issues

### Wallet Problems

**Problem**: `Invalid private key`
```bash
# Check private key format
echo $SOLANA_PRIVATE_KEY

# Ensure key is base58 encoded
# Verify key length (88 characters)
```

**Problem**: Insufficient SOL balance
```bash
# Check wallet balance
solana balance YOUR_WALLET_ADDRESS

# Add SOL to wallet for transactions
```

**Problem**: RPC endpoint not responding
```bash
# Check RPC URL
echo $SOLANA_RPC_URL

# Try alternative endpoints:
# https://api.mainnet-beta.solana.com
# https://solana-api.projectserum.com
```

### Trading Issues

**Problem**: Token swap fails
```python
# Check token addresses
# Verify sufficient balance
# Check slippage tolerance
```

**Problem**: Jupiter API errors
```python
# Check Jupiter API status
# Verify token is supported
# Check for maintenance windows
```

## 🗄️ Database Issues

### SQLite Problems

**Problem**: Database locked
```bash
# Check for multiple processes
ps aux | grep python

# Kill conflicting processes
pkill -f "src.main"
```

**Problem**: Database corruption
```bash
# Backup current database
cp puppet_engine.db puppet_engine.db.backup

# Recreate database
rm puppet_engine.db
python -m src.main --init-db
```

**Problem**: Memory not persisting
```python
# Check database path
# Verify write permissions
# Ensure proper database initialization
```

## 🌐 API Server Issues

### Server Startup Problems

**Problem**: Port already in use
```bash
# Check what's using the port
netstat -tulpn | grep :8000

# Kill process or change port
python -m src.main --port 8001
```

**Problem**: CORS errors
```python
# Configure CORS in API server
# Add allowed origins
# Check request headers
```

### API Endpoint Issues

**Problem**: 404 Not Found
```bash
# Check endpoint URL
# Verify API routes are registered
# Check server logs
```

**Problem**: 500 Internal Server Error
```bash
# Check application logs
# Verify database connection
# Check environment variables
```

## 🔍 Debugging Techniques

### Enable Debug Logging

```python
# Set log level to DEBUG
LOG_LEVEL=DEBUG

# Or in code
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Application Logs

```bash
# View real-time logs
tail -f logs/puppet-engine.log

# Search for errors
grep -i error logs/puppet-engine.log

# Check specific time period
grep "2025-07-17" logs/puppet-engine.log
```

### Test Individual Components

```bash
# Test database connection
python -c "from src.memory.sqlite_store import SQLiteMemoryStore; print('DB OK')"

# Test Twitter client
python -c "from src.twitter.client import TwitterClient; print('Twitter OK')"

# Test LLM provider
python -c "from src.llm.openai_provider import OpenAILLMProvider; print('LLM OK')"
```

## 📊 Performance Issues

### High Memory Usage

**Problem**: Memory leaks
```bash
# Monitor memory usage
ps aux | grep python

# Check for memory leaks in code
# Use memory profiling tools
```

**Problem**: Slow response times
```python
# Optimize database queries
# Add caching layer
# Check network latency
```

### Slow Agent Processing

**Problem**: LLM response delays
```python
# Check LLM provider performance
# Implement request timeouts
# Use faster models if available
```

**Problem**: Database bottlenecks
```python
# Add database indexes
# Optimize queries
# Consider connection pooling
```

## 🔒 Security Issues

### API Key Exposure

**Problem**: Keys in logs
```python
# Mask sensitive data in logs
# Use environment variables
# Implement secure logging
```

**Problem**: Unauthorized access
```python
# Implement authentication
# Use API keys for endpoints
# Add rate limiting
```

## 🆘 Getting Help

### Before Asking for Help

1. **Check this guide** for your specific issue
2. **Search existing issues** on GitHub
3. **Enable debug logging** and check logs
4. **Test with minimal configuration**
5. **Document your environment** (OS, Python version, etc.)

### Creating a Good Issue Report

```markdown
## Issue Description
Brief description of the problem

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: Windows 10
- Python: 3.11.0
- Puppet Engine: 2.0.0

## Logs
Relevant log output (with sensitive data removed)

## Configuration
Relevant configuration files (with sensitive data removed)
```

### Community Resources

- **[GitHub Issues](https://github.com/username/puppet-engine/issues)** - Bug reports and feature requests
- **[GitHub Discussions](https://github.com/username/puppet-engine/discussions)** - Community help and questions
- **[Documentation](README.md)** - Complete documentation index

---

**Last updated**: July 2025  
**Puppet Engine version**: 2.0.0 