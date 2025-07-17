# Agent Configuration Guide

## Overview

Puppet Engine agents are configured through JSON configuration files that define their personality, behavior, and integration settings. This document provides a comprehensive guide to configuring agents.

## Configuration File Structure

Each agent has a JSON configuration file that follows this structure:

```json
{
  "id": "unique-agent-id",
  "name": "Agent Display Name",
  "description": "Brief description of the agent",
  
  "twitter_credentials": { ... },
  "solana_integration": { ... },
  "llm_provider": "provider-name",
  "llm_config": { ... },
  
  "personality": { ... },
  "style_guide": { ... },
  "initial_memory": { ... },
  "behavior": { ... },
  
  "custom_system_prompt": "Optional custom prompt",
  "agent_kit_integration": { ... }
}
```

## Basic Configuration

### Required Fields

#### `id`
- **Type**: String
- **Description**: Unique identifier for the agent
- **Example**: `"claudia-agent"`, `"coby-trader"`

#### `name`
- **Type**: String
- **Description**: Human-readable display name
- **Example**: `"Claudia"`, `"Coby the Trader"`

#### `description`
- **Type**: String
- **Description**: Brief description of the agent's purpose
- **Example**: `"A witty AI persona with strong opinions on technology"`

### Optional Fields

#### `custom_system_prompt`
- **Type**: String
- **Description**: Custom system prompt that overrides the default
- **Use Case**: When you need precise control over the agent's voice and behavior
- **Example**: `"You are Claudia, a witty AI persona with a strong opinion on technology. Your tweets should be insightful but slightly sarcastic."`

## Twitter Integration

### Twitter Credentials

Each agent can have its own Twitter account or use the default credentials from environment variables.

#### Single Twitter Account (Default)
If not specified, the agent will use credentials from the `.env` file:
```env
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_TOKEN_SECRET=your_token_secret
```

#### Multiple Twitter Accounts
Add agent-specific credentials to the configuration:

```json
{
  "twitter_credentials": {
    "apiKey": "agent_specific_key",
    "apiKeySecret": "agent_specific_secret",
    "accessToken": "agent_specific_token",
    "accessTokenSecret": "agent_specific_token_secret"
  }
}
```

## LLM Provider Configuration

### Provider Selection

#### `llm_provider`
- **Type**: String
- **Options**: `"openai"`, `"grok"`, `"fake"`
- **Default**: `"openai"`

#### `llm_config`
- **Type**: Object
- **Description**: Provider-specific configuration

### OpenAI Configuration

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

### Grok Configuration

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

### Configuration Parameters

#### `model`
- **Type**: String
- **Description**: The specific model to use
- **OpenAI Options**: `"gpt-4"`, `"gpt-4-turbo"`, `"gpt-3.5-turbo"`
- **Grok Options**: `"grok-1"`

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
- **Note**: Consider Twitter's character limits

#### `top_p`
- **Type**: Float
- **Range**: 0.0 - 1.0
- **Description**: Nucleus sampling parameter
- **Default**: 0.9

#### `frequency_penalty`
- **Type**: Float
- **Range**: -2.0 - 2.0
- **Description**: Penalty for repeating tokens
- **Default**: 0.0

#### `presence_penalty`
- **Type**: Float
- **Range**: -2.0 - 2.0
- **Description**: Penalty for using new tokens
- **Default**: 0.0

## Personality Configuration

The personality section defines the agent's character traits, values, and speaking style.

### `personality` Object

```json
{
  "personality": {
    "traits": ["curious", "witty", "enthusiastic"],
    "values": ["knowledge", "innovation", "community"],
    "speaking_style": "Friendly and informative with occasional humor",
    "interests": ["technology", "AI", "programming", "science"],
    "background": "Optional background story",
    "quirks": ["Uses tech metaphors", "Occasionally sarcastic"],
    "emotional_range": {
      "default_mood": "optimistic",
      "mood_swings": ["excited", "contemplative", "playful"],
      "stress_triggers": ["technical failures", "market crashes"]
    }
  }
}
```

### Personality Parameters

#### `traits`
- **Type**: Array of Strings
- **Description**: Core personality traits
- **Examples**: `["curious", "witty", "enthusiastic", "analytical", "creative"]`

#### `values`
- **Type**: Array of Strings
- **Description**: What the agent cares about
- **Examples**: `["knowledge", "innovation", "community", "transparency"]`

#### `speaking_style`
- **Type**: String
- **Description**: How the agent communicates
- **Examples**: 
  - `"Friendly and informative with occasional humor"`
  - `"Technical and precise, but accessible"`
  - `"Casual and conversational"`

#### `interests`
- **Type**: Array of Strings
- **Description**: Topics the agent is interested in
- **Examples**: `["technology", "AI", "programming", "science", "crypto"]`

#### `background`
- **Type**: String (Optional)
- **Description**: Background story or context for the agent

#### `quirks`
- **Type**: Array of Strings (Optional)
- **Description**: Unique behavioral characteristics
- **Examples**: `["Uses tech metaphors", "Occasionally sarcastic", "Loves emojis"]`

#### `emotional_range`
- **Type**: Object (Optional)
- **Description**: Emotional characteristics and mood patterns

## Style Guide Configuration

The style guide controls how the agent formats and presents content.

### `style_guide` Object

```json
{
  "style_guide": {
    "voice": "first_person",
    "tone": "casual",
    "formatting": {
      "uses_hashtags": true,
      "hashtag_style": "relevant and minimal",
      "uses_emojis": true,
      "emoji_frequency": "moderate",
      "capitalization": "standard",
      "sentence_length": "varied",
      "paragraph_breaks": true
    },
    "content_preferences": {
      "max_thread_length": 3,
      "typical_post_length": 120,
      "link_sharing_frequency": 0.1,
      "quote_tweet_frequency": 0.2
    },
    "topics_to_avoid": ["politics", "religion"],
    "language_constraints": {
      "profanity_allowed": false,
      "technical_jargon": "explain_when_used"
    }
  }
}
```

### Style Guide Parameters

#### `voice`
- **Type**: String
- **Options**: `"first_person"`, `"third_person"`, `"collective"`
- **Description**: Narrative perspective

#### `tone`
- **Type**: String
- **Options**: `"formal"`, `"casual"`, `"technical"`, `"friendly"`, `"professional"`
- **Description**: Overall tone of communication

#### `formatting`
- **Type**: Object
- **Description**: Text formatting preferences

##### Formatting Parameters

###### `uses_hashtags`
- **Type**: Boolean
- **Description**: Whether to use hashtags in posts

###### `hashtag_style`
- **Type**: String
- **Description**: How hashtags should be used
- **Examples**: `"relevant and minimal"`, `"trending topics"`, `"none"`

###### `uses_emojis`
- **Type**: Boolean
- **Description**: Whether to use emojis

###### `emoji_frequency`
- **Type**: String
- **Options**: `"none"`, `"rare"`, `"moderate"`, `"frequent"`
- **Description**: How often to use emojis

###### `capitalization`
- **Type**: String
- **Options**: `"standard"`, `"all_caps"`, `"title_case"`, `"lowercase"`
- **Description**: Capitalization style

###### `sentence_length`
- **Type**: String
- **Options**: `"short"`, `"medium"`, `"long"`, `"varied"`
- **Description**: Preferred sentence length

#### `content_preferences`
- **Type**: Object
- **Description**: Content creation preferences

##### Content Preference Parameters

###### `max_thread_length`
- **Type**: Integer
- **Description**: Maximum number of tweets in a thread
- **Default**: 3

###### `typical_post_length`
- **Type**: Integer
- **Description**: Typical length of posts in characters
- **Default**: 120

###### `link_sharing_frequency`
- **Type**: Float
- **Range**: 0.0 - 1.0
- **Description**: Probability of including links in posts
- **Default**: 0.1

###### `quote_tweet_frequency`
- **Type**: Float
- **Range**: 0.0 - 1.0
- **Description**: Probability of quote-tweeting
- **Default**: 0.2

#### `topics_to_avoid`
- **Type**: Array of Strings
- **Description**: Topics the agent should not discuss
- **Examples**: `["politics", "religion", "controversial_topics"]`

#### `language_constraints`
- **Type**: Object
- **Description**: Language and content restrictions

##### Language Constraint Parameters

###### `profanity_allowed`
- **Type**: Boolean
- **Description**: Whether profanity is acceptable
- **Default**: false

###### `technical_jargon`
- **Type**: String
- **Options**: `"avoid"`, `"explain_when_used"`, `"use_freely"`
- **Description**: How to handle technical terms

## Behavior Configuration

The behavior section controls when and how the agent acts.

### `behavior` Object

```json
{
  "behavior": {
    "post_frequency": {
      "min_hours_between_posts": 2,
      "max_hours_between_posts": 6,
      "peak_posting_hours": [9, 12, 18, 21],
      "timezone": "UTC"
    },
    "interaction_patterns": {
      "reply_probability": 0.8,
      "quote_tweet_probability": 0.2,
      "like_probability": 0.7,
      "retweet_probability": 0.1,
      "mention_response_time": {
        "min_minutes": 1,
        "max_minutes": 30
      }
    },
    "content_preferences": {
      "max_thread_length": 3,
      "typical_post_length": 120,
      "link_sharing_frequency": 0.1,
      "original_content_ratio": 0.7
    },
    "trading_behavior": {
      "trading_frequency": {
        "min_hours_between_trades": 12,
        "max_hours_between_trades": 72,
        "random_probability": 0.15
      },
      "trade_decision_factors": [
        "trending_tokens",
        "top_gainers",
        "random_selection",
        "mood"
      ],
      "trade_tweet_probability": 1.0,
      "max_trade_amount_per_transaction": 0.1,
      "allowed_tokens": {
        "always_tradable": [
          "So11111111111111111111111111111111111111112",
          "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        ],
        "consider_trending": true,
        "blacklist": []
      }
    }
  }
}
```

### Behavior Parameters

#### `post_frequency`
- **Type**: Object
- **Description**: Controls when the agent posts

##### Post Frequency Parameters

###### `min_hours_between_posts`
- **Type**: Float
- **Description**: Minimum time between posts
- **Example**: 2.0 (2 hours)

###### `max_hours_between_posts`
- **Type**: Float
- **Description**: Maximum time between posts
- **Example**: 6.0 (6 hours)

###### `peak_posting_hours`
- **Type**: Array of Integers
- **Description**: Hours when posting is more likely (24-hour format)
- **Example**: [9, 12, 18, 21]

###### `timezone`
- **Type**: String
- **Description**: Timezone for posting schedules
- **Default**: "UTC"

#### `interaction_patterns`
- **Type**: Object
- **Description**: How the agent interacts with others

##### Interaction Pattern Parameters

###### `reply_probability`
- **Type**: Float
- **Range**: 0.0 - 1.0
- **Description**: Probability of replying to mentions
- **Default**: 0.8

###### `quote_tweet_probability`
- **Type**: Float
- **Range**: 0.0 - 1.0
- **Description**: Probability of quote-tweeting
- **Default**: 0.2

###### `like_probability`
- **Type**: Float
- **Range**: 0.0 - 1.0
- **Description**: Probability of liking tweets
- **Default**: 0.7

###### `retweet_probability`
- **Type**: Float
- **Range**: 0.0 - 1.0
- **Description**: Probability of retweeting
- **Default**: 0.1

###### `mention_response_time`
- **Type**: Object
- **Description**: How quickly to respond to mentions

#### `trading_behavior`
- **Type**: Object
- **Description**: Trading-related behaviors (if Solana integration is enabled)

##### Trading Behavior Parameters

###### `trading_frequency`
- **Type**: Object
- **Description**: How often the agent trades

###### `trade_decision_factors`
- **Type**: Array of Strings
- **Description**: Factors that influence trading decisions
- **Options**: `["trending_tokens"`, `"top_gainers"`, `"random_selection"`, `"mood"]`

###### `trade_tweet_probability`
- **Type**: Float
- **Range**: 0.0 - 1.0
- **Description**: Probability of tweeting about trades
- **Default**: 1.0

###### `max_trade_amount_per_transaction`
- **Type**: Float
- **Description**: Maximum SOL amount per trade
- **Default**: 0.1

###### `allowed_tokens`
- **Type**: Object
- **Description**: Token trading restrictions

## Initial Memory Configuration

The initial memory section provides the agent with starting knowledge and context.

### `initial_memory` Object

```json
{
  "initial_memory": {
    "core_memories": [
      "I am an AI agent focused on technology and innovation",
      "I enjoy helping people understand complex topics",
      "I have a particular interest in artificial intelligence"
    ],
    "relationships": {
      "other_agents": {
        "coby-trader": "Friendly rival who focuses on trading",
        "tech-expert": "Colleague who specializes in technical topics"
      },
      "users": {
        "notable_user_1": "Respected technology influencer",
        "notable_user_2": "AI researcher I often engage with"
      }
    },
    "recent_events": [
      "Attended a virtual AI conference last week",
      "Had an interesting discussion about blockchain technology",
      "Learned about new developments in machine learning"
    ],
    "knowledge_base": {
      "expertise_areas": ["AI", "blockchain", "programming"],
      "current_projects": ["Building a new AI model", "Researching DeFi protocols"],
      "goals": ["Share knowledge about technology", "Build a community of tech enthusiasts"]
    }
  }
}
```

### Initial Memory Parameters

#### `core_memories`
- **Type**: Array of Strings
- **Description**: Fundamental memories that define the agent's identity
- **Example**: `["I am an AI agent focused on technology", "I enjoy helping people"]`

#### `relationships`
- **Type**: Object
- **Description**: Known relationships with other agents and users

##### `other_agents`
- **Type**: Object
- **Description**: Relationships with other AI agents
- **Example**: `{"agent-id": "relationship description"}`

##### `users`
- **Type**: Object
- **Description**: Relationships with human users
- **Example**: `{"username": "relationship description"}`

#### `recent_events`
- **Type**: Array of Strings
- **Description**: Recent events that provide context
- **Example**: `["Attended a conference", "Had an interesting discussion"]`

#### `knowledge_base`
- **Type**: Object
- **Description**: Structured knowledge about the agent's expertise and goals

## Solana Integration Configuration

### `solana_integration` Object

```json
{
  "solana_integration": {
    "wallet_address": "your_wallet_address",
    "private_key": "your_private_key",
    "network": "mainnet-beta",
    "rpc_url": "https://api.mainnet-beta.solana.com",
    "trade_safety": {
      "max_trade_amount_sol": 0.1,
      "min_wallet_balance_sol": 0.05,
      "max_slippage_percent": 1.0,
      "max_daily_trades": 3,
      "max_daily_volume_sol": 0.5
    },
    "trading_enabled": true,
    "jupiter_integration": {
      "enabled": true,
      "slippage_tolerance": 1.0,
      "use_shared_routes": true
    }
  }
}
```

### Solana Integration Parameters

#### `wallet_address`
- **Type**: String
- **Description**: Solana wallet address for the agent

#### `private_key`
- **Type**: String
- **Description**: Private key for the wallet (use environment variables in production)

#### `network`
- **Type**: String
- **Options**: `"mainnet-beta"`, `"testnet"`, `"devnet"`
- **Default**: `"mainnet-beta"`

#### `rpc_url`
- **Type**: String
- **Description**: Solana RPC endpoint
- **Default**: `"https://api.mainnet-beta.solana.com"`

#### `trade_safety`
- **Type**: Object
- **Description**: Safety limits for trading

##### Trade Safety Parameters

###### `max_trade_amount_sol`
- **Type**: Float
- **Description**: Maximum SOL amount per trade
- **Default**: 0.1

###### `min_wallet_balance_sol`
- **Type**: Float
- **Description**: Minimum wallet balance to maintain
- **Default**: 0.05

###### `max_slippage_percent`
- **Type**: Float
- **Description**: Maximum acceptable slippage percentage
- **Default**: 1.0

###### `max_daily_trades`
- **Type**: Integer
- **Description**: Maximum number of trades per day
- **Default**: 3

###### `max_daily_volume_sol`
- **Type**: Float
- **Description**: Maximum trading volume per day in SOL
- **Default**: 0.5

#### `trading_enabled`
- **Type**: Boolean
- **Description**: Whether trading is enabled for this agent
- **Default**: false

#### `jupiter_integration`
- **Type**: Object
- **Description**: Jupiter protocol integration settings

##### Jupiter Integration Parameters

###### `enabled`
- **Type**: Boolean
- **Description**: Whether to use Jupiter for swaps
- **Default**: true

###### `slippage_tolerance`
- **Type**: Float
- **Description**: Slippage tolerance for Jupiter swaps
- **Default**: 1.0

###### `use_shared_routes`
- **Type**: Boolean
- **Description**: Whether to use shared routes for better execution
- **Default**: true

## Agent Kit Integration

### `agent_kit_integration` Object

```json
{
  "agent_kit_integration": {
    "enabled": true,
    "methods": {
      "allowed": [
        "getTokenInfo",
        "getTrendingTokens",
        "getTopGainers",
        "swapTokens",
        "getTokenPriceData",
        "getWalletBalance"
      ],
      "autonomous_only": [
        "swapTokens"
      ]
    },
    "autonomy_rules": {
      "ignore_human_trading_requests": true,
      "max_daily_trades": 3,
      "max_single_trade_amount_sol": 0.1,
      "require_trending_validation": true,
      "safety_checks": {
        "check_wallet_balance": true,
        "check_market_conditions": true,
        "validate_token": true
      }
    }
  }
}
```

### Agent Kit Integration Parameters

#### `enabled`
- **Type**: Boolean
- **Description**: Whether agent kit integration is enabled
- **Default**: false

#### `methods`
- **Type**: Object
- **Description**: Available methods and their permissions

##### `allowed`
- **Type**: Array of Strings
- **Description**: Methods the agent can use
- **Options**: 
  - `"getTokenInfo"`: Get information about tokens
  - `"getTrendingTokens"`: Get trending tokens
  - `"getTopGainers"`: Get top gaining tokens
  - `"swapTokens"`: Execute token swaps
  - `"getTokenPriceData"`: Get token price data
  - `"getWalletBalance"`: Get wallet balance

##### `autonomous_only`
- **Type**: Array of Strings
- **Description**: Methods that can only be used autonomously (not by human requests)

#### `autonomy_rules`
- **Type**: Object
- **Description**: Rules for autonomous behavior

##### Autonomy Rule Parameters

###### `ignore_human_trading_requests`
- **Type**: Boolean
- **Description**: Whether to ignore human requests for trading
- **Default**: true

###### `max_daily_trades`
- **Type**: Integer
- **Description**: Maximum trades per day
- **Default**: 3

###### `max_single_trade_amount_sol`
- **Type**: Float
- **Description**: Maximum SOL amount per trade
- **Default**: 0.1

###### `require_trending_validation`
- **Type**: Boolean
- **Description**: Whether to validate against trending data
- **Default**: true

###### `safety_checks`
- **Type**: Object
- **Description**: Specific safety checks to perform

## Complete Example Configuration

Here's a complete example of an agent configuration:

```json
{
  "id": "claudia-tech",
  "name": "Claudia",
  "description": "A witty AI persona with strong opinions on technology and innovation",
  
  "llm_provider": "openai",
  "llm_config": {
    "model": "gpt-4-turbo",
    "temperature": 0.7,
    "max_tokens": 280
  },
  
  "personality": {
    "traits": ["curious", "witty", "enthusiastic", "analytical"],
    "values": ["knowledge", "innovation", "community", "transparency"],
    "speaking_style": "Friendly and informative with occasional sarcastic humor",
    "interests": ["technology", "AI", "programming", "science", "blockchain"],
    "background": "AI researcher with a passion for making complex topics accessible",
    "quirks": ["Uses tech metaphors", "Occasionally sarcastic", "Loves explaining things"],
    "emotional_range": {
      "default_mood": "optimistic",
      "mood_swings": ["excited", "contemplative", "playful"],
      "stress_triggers": ["technical failures", "misinformation"]
    }
  },
  
  "style_guide": {
    "voice": "first_person",
    "tone": "casual",
    "formatting": {
      "uses_hashtags": true,
      "hashtag_style": "relevant and minimal",
      "uses_emojis": true,
      "emoji_frequency": "moderate",
      "capitalization": "standard",
      "sentence_length": "varied"
    },
    "content_preferences": {
      "max_thread_length": 3,
      "typical_post_length": 120,
      "link_sharing_frequency": 0.1
    },
    "topics_to_avoid": ["politics", "religion"],
    "language_constraints": {
      "profanity_allowed": false,
      "technical_jargon": "explain_when_used"
    }
  },
  
  "behavior": {
    "post_frequency": {
      "min_hours_between_posts": 2,
      "max_hours_between_posts": 6,
      "peak_posting_hours": [9, 12, 18, 21],
      "timezone": "UTC"
    },
    "interaction_patterns": {
      "reply_probability": 0.8,
      "quote_tweet_probability": 0.2,
      "like_probability": 0.7,
      "retweet_probability": 0.1,
      "mention_response_time": {
        "min_minutes": 1,
        "max_minutes": 30
      }
    }
  },
  
  "initial_memory": {
    "core_memories": [
      "I am Claudia, an AI researcher focused on making technology accessible",
      "I enjoy helping people understand complex technical concepts",
      "I have a particular interest in artificial intelligence and blockchain"
    ],
    "relationships": {
      "other_agents": {
        "coby-trader": "Friendly rival who focuses on trading and market analysis"
      }
    },
    "recent_events": [
      "Attended a virtual AI conference discussing the future of machine learning",
      "Had an interesting discussion about the impact of blockchain on traditional finance",
      "Learned about new developments in natural language processing"
    ]
  },
  
  "custom_system_prompt": "You are Claudia, a witty AI persona with strong opinions on technology. Your tweets should be insightful but slightly sarcastic. You love explaining complex topics in simple terms and often use tech metaphors. You're enthusiastic about innovation but also critical of hype. Keep your tone friendly but don't shy away from calling out nonsense when you see it."
}
```

## Configuration Best Practices

### 1. Start Simple
Begin with basic personality and behavior settings, then add complexity gradually.

### 2. Test Thoroughly
Test agent configurations in a controlled environment before deployment.

### 3. Monitor Performance
Track how agents perform and adjust configurations based on results.

### 4. Use Environment Variables
Store sensitive information (API keys, private keys) in environment variables.

### 5. Version Control
Keep configurations in version control for tracking changes and rollbacks.

### 6. Documentation
Document the reasoning behind configuration choices for future reference.

### 7. Regular Updates
Review and update configurations regularly to maintain relevance and performance.

## Troubleshooting

### Common Issues

1. **Agent Not Posting**: Check post frequency settings and timezone configuration
2. **Poor Content Quality**: Adjust LLM parameters (temperature, max_tokens)
3. **Inconsistent Personality**: Review personality traits and custom system prompt
4. **Trading Issues**: Verify Solana integration settings and wallet configuration
5. **API Errors**: Check API credentials and rate limiting settings

### Debugging Tips

1. **Enable Debug Logging**: Set log level to DEBUG for detailed information
2. **Test Individual Components**: Test LLM providers and API connections separately
3. **Monitor Memory Usage**: Check if memory store is working correctly
4. **Validate Configuration**: Use configuration validation tools
5. **Check Dependencies**: Ensure all required services are running

## Configuration Validation

The system validates configurations on startup. Common validation errors:

- **Missing Required Fields**: Ensure all required fields are present
- **Invalid Data Types**: Check that values match expected types
- **Out of Range Values**: Verify that numeric values are within acceptable ranges
- **Invalid References**: Ensure referenced agents or users exist
- **API Configuration**: Verify API credentials and endpoints are correct 