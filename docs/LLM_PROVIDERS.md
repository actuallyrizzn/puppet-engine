# LLM Provider Integration

## Overview

Puppet Engine supports multiple Large Language Model (LLM) providers for content generation. This allows you to choose the best provider for your needs and even use different providers for different agents.

## Supported Providers

### OpenAI

**Default Provider** - Industry-leading language models with excellent performance.

#### Models Available
- **GPT-4**: Most capable model, best for complex reasoning
- **GPT-4 Turbo**: Faster and more cost-effective than GPT-4
- **GPT-3.5 Turbo**: Good balance of performance and cost

#### Configuration
```json
{
  "llm_provider": "openai",
  "llm_config": {
    "model": "gpt-4-turbo",
    "temperature": 0.7,
    "max_tokens": 280,
    "top_p": 0.9,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
  }
}
```

#### Environment Variables
```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4-turbo
OPENAI_ORGANIZATION=your_org_id  # Optional
```

### Grok

**xAI's Model** - Alternative to OpenAI with different characteristics.

#### Models Available
- **grok-1**: xAI's flagship model

#### Configuration
```json
{
  "llm_provider": "grok",
  "llm_config": {
    "model": "grok-1",
    "temperature": 0.7,
    "max_tokens": 280
  }
}
```

#### Environment Variables
```env
GROK_API_KEY=your_grok_api_key
GROK_API_ENDPOINT=https://api.grok.x.com/v1/chat/completions
GROK_MODEL=grok-1
```

### Fake Provider

**Testing Provider** - For development and testing without API costs.

#### Configuration
```json
{
  "llm_provider": "fake",
  "llm_config": {
    "response_style": "helpful",
    "include_prompt": true
  }
}
```

#### Use Cases
- Development and testing
- CI/CD pipelines
- Cost-free experimentation
- Offline development

## Provider Configuration

### Common Parameters

All providers support these basic parameters:

#### `model`
- **Type**: String
- **Description**: The specific model to use
- **Examples**: `"gpt-4-turbo"`, `"grok-1"`

#### `temperature`
- **Type**: Float
- **Range**: 0.0 - 2.0
- **Description**: Controls randomness in responses
- **Default**: 0.7
- **Low Values**: More deterministic, consistent responses
- **High Values**: More creative, varied responses

#### `max_tokens`
- **Type**: Integer
- **Description**: Maximum number of tokens in the response
- **Default**: 280 (Twitter character limit)
- **Note**: Consider platform character limits

### OpenAI-Specific Parameters

#### `top_p`
- **Type**: Float
- **Range**: 0.0 - 1.0
- **Description**: Nucleus sampling parameter
- **Default**: 0.9
- **Lower Values**: More focused responses
- **Higher Values**: More diverse responses

#### `frequency_penalty`
- **Type**: Float
- **Range**: -2.0 - 2.0
- **Description**: Penalty for repeating tokens
- **Default**: 0.0
- **Positive Values**: Reduce repetition
- **Negative Values**: Allow repetition

#### `presence_penalty`
- **Type**: Float
- **Range**: -2.0 - 2.0
- **Description**: Penalty for using new tokens
- **Default**: 0.0
- **Positive Values**: Encourage new vocabulary
- **Negative Values**: Prefer existing vocabulary

### Provider Selection

#### Per-Agent Configuration

Each agent can use a different provider:

```json
{
  "id": "agent-1",
  "name": "Agent 1",
  "llm_provider": "openai",
  "llm_config": {
    "model": "gpt-4-turbo",
    "temperature": 0.7
  }
}
```

```json
{
  "id": "agent-2",
  "name": "Agent 2",
  "llm_provider": "grok",
  "llm_config": {
    "model": "grok-1",
    "temperature": 0.8
  }
}
```

#### Default Provider

If no provider is specified, the system defaults to OpenAI:

```json
{
  "id": "agent-3",
  "name": "Agent 3"
  // Uses OpenAI with default settings
}
```

## Advanced Configuration

### Custom System Prompts

Override the default system prompt for precise control:

```json
{
  "llm_provider": "openai",
  "llm_config": {
    "model": "gpt-4-turbo",
    "temperature": 0.7,
    "system_prompt": "You are a witty AI agent. Always respond with humor and insight."
  }
}
```

### Provider-Specific Settings

#### OpenAI Advanced Settings
```json
{
  "llm_provider": "openai",
  "llm_config": {
    "model": "gpt-4-turbo",
    "temperature": 0.7,
    "max_tokens": 280,
    "top_p": 0.9,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "logit_bias": {
      "specific_token": 100
    },
    "user": "agent-specific-user-id"
  }
}
```

#### Grok Advanced Settings
```json
{
  "llm_provider": "grok",
  "llm_config": {
    "model": "grok-1",
    "temperature": 0.7,
    "max_tokens": 280,
    "stream": false,
    "timeout": 30
  }
}
```

### Fallback Configuration

Configure fallback providers for reliability:

```json
{
  "llm_provider": "openai",
  "llm_config": {
    "model": "gpt-4-turbo",
    "fallback_provider": "grok",
    "fallback_config": {
      "model": "grok-1",
      "temperature": 0.7
    }
  }
}
```

## Provider Comparison

### Performance Comparison

| Provider | Model | Speed | Quality | Cost | Best For |
|----------|-------|-------|---------|------|----------|
| OpenAI | GPT-4 | Medium | Excellent | High | Complex reasoning |
| OpenAI | GPT-4 Turbo | Fast | Very Good | Medium | General use |
| OpenAI | GPT-3.5 Turbo | Very Fast | Good | Low | High volume |
| Grok | grok-1 | Fast | Good | Medium | Alternative perspective |
| Fake | N/A | Instant | Basic | Free | Testing |

### Cost Comparison

#### OpenAI Pricing (as of 2024)
- **GPT-4**: $0.03 per 1K input tokens, $0.06 per 1K output tokens
- **GPT-4 Turbo**: $0.01 per 1K input tokens, $0.03 per 1K output tokens
- **GPT-3.5 Turbo**: $0.0015 per 1K input tokens, $0.002 per 1K output tokens

#### Grok Pricing
- **grok-1**: Pricing varies by plan and usage

### Quality Comparison

#### Content Quality
- **GPT-4**: Highest quality, best reasoning
- **GPT-4 Turbo**: Very good quality, faster
- **GPT-3.5 Turbo**: Good quality, cost-effective
- **Grok**: Good quality, different style
- **Fake**: Basic quality, for testing only

#### Consistency
- **GPT-4**: Most consistent
- **GPT-4 Turbo**: Very consistent
- **GPT-3.5 Turbo**: Good consistency
- **Grok**: Good consistency
- **Fake**: Variable consistency

## Usage Examples

### Basic Tweet Generation

```python
from src.llm.openai_provider import OpenAIProvider
from src.core.settings import Settings

# Configure provider
settings = Settings()
provider = OpenAIProvider(settings)

# Generate tweet
tweet = await provider.generate_tweet(
    agent=agent,
    context={
        "topic": "artificial intelligence",
        "mood": "excited",
        "recent_events": ["AI breakthrough announced"]
    }
)
```

### Content Generation

```python
# Generate general content
content = await provider.generate_content(
    prompt="Write a short explanation of machine learning",
    context={"audience": "beginners", "style": "friendly"}
)
```

### Response Generation

```python
# Generate response to mention
response = await provider.generate_response(
    agent=agent,
    mention="What do you think about AI?",
    context={"conversation_history": previous_messages}
)
```

## Error Handling

### Common Errors

#### Rate Limiting
```python
try:
    response = await provider.generate_content(prompt, context)
except RateLimitError:
    # Implement exponential backoff
    await asyncio.sleep(backoff_time)
    response = await provider.generate_content(prompt, context)
```

#### API Errors
```python
try:
    response = await provider.generate_content(prompt, context)
except APIError as e:
    logger.error(f"API error: {e}")
    # Fall back to alternative provider or cached response
    response = fallback_response
```

#### Network Errors
```python
try:
    response = await provider.generate_content(prompt, context)
except NetworkError:
    # Retry with exponential backoff
    for attempt in range(max_retries):
        try:
            response = await provider.generate_content(prompt, context)
            break
        except NetworkError:
            await asyncio.sleep(2 ** attempt)
```

### Retry Logic

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def generate_with_retry(provider, prompt, context):
    return await provider.generate_content(prompt, context)
```

## Monitoring and Analytics

### Usage Tracking

Track provider usage for cost optimization:

```python
class UsageTracker:
    def __init__(self):
        self.usage = {}
    
    async def track_usage(self, provider, tokens_used, cost):
        if provider not in self.usage:
            self.usage[provider] = {
                'total_tokens': 0,
                'total_cost': 0,
                'requests': 0
            }
        
        self.usage[provider]['total_tokens'] += tokens_used
        self.usage[provider]['total_cost'] += cost
        self.usage[provider]['requests'] += 1
```

### Performance Monitoring

Monitor response times and quality:

```python
import time

async def monitor_performance(provider, prompt, context):
    start_time = time.time()
    
    try:
        response = await provider.generate_content(prompt, context)
        response_time = time.time() - start_time
        
        # Log performance metrics
        logger.info(f"Provider: {provider.name}, "
                   f"Response time: {response_time:.2f}s, "
                   f"Tokens: {response.token_count}")
        
        return response
    except Exception as e:
        logger.error(f"Provider {provider.name} failed: {e}")
        raise
```

## Best Practices

### Provider Selection

1. **Start with OpenAI**: Best overall performance and reliability
2. **Use GPT-4 Turbo**: Good balance of quality and cost
3. **Consider Grok**: For different perspectives and style
4. **Use Fake Provider**: For development and testing

### Cost Optimization

1. **Monitor Usage**: Track token usage and costs
2. **Optimize Prompts**: Shorter prompts use fewer tokens
3. **Use Appropriate Models**: Match model to task complexity
4. **Implement Caching**: Cache common responses

### Quality Optimization

1. **Tune Parameters**: Adjust temperature and other parameters
2. **Use Custom Prompts**: For specific behaviors
3. **Test Thoroughly**: Verify quality across different scenarios
4. **Monitor Feedback**: Track user engagement and feedback

### Reliability

1. **Implement Fallbacks**: Use multiple providers
2. **Handle Errors**: Proper error handling and retries
3. **Monitor Health**: Track provider availability
4. **Plan for Outages**: Have backup strategies

## Troubleshooting

### Common Issues

#### High Costs
- **Problem**: Unexpectedly high API costs
- **Solution**: Monitor usage, optimize prompts, use cheaper models

#### Poor Quality
- **Problem**: Low-quality or inappropriate responses
- **Solution**: Adjust temperature, improve prompts, use better models

#### Slow Responses
- **Problem**: Long response times
- **Solution**: Use faster models, optimize prompts, implement caching

#### Rate Limiting
- **Problem**: Too many requests
- **Solution**: Implement backoff, use multiple providers, reduce frequency

### Debug Tips

1. **Enable Debug Logging**: Set log level to DEBUG
2. **Monitor Metrics**: Track usage, performance, and errors
3. **Test Providers**: Compare different providers and models
4. **Check Configuration**: Verify API keys and settings

## Future Providers

### Planned Support

- **Anthropic Claude**: High-quality reasoning and safety
- **Google Gemini**: Google's latest language model
- **Local Models**: Self-hosted models for privacy
- **Custom Models**: Fine-tuned models for specific use cases

### Integration Guide

To add a new provider:

1. **Create Provider Class**: Implement the LLMProvider interface
2. **Add Configuration**: Support provider-specific settings
3. **Update Documentation**: Document the new provider
4. **Add Tests**: Comprehensive test coverage
5. **Update Examples**: Include usage examples

## Support

For LLM provider issues:

- **Documentation**: This guide and API reference
- **Issues**: [GitHub Issues](https://github.com/username/puppet-engine/issues)
- **Discussions**: [GitHub Discussions](https://github.com/username/puppet-engine/discussions)
- **Provider Support**: Contact provider directly for API issues 