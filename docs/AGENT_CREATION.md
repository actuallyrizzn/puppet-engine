# Agent Creation Guide

## Overview

This guide walks you through creating and configuring AI agents for Puppet Engine. Agents are autonomous personas that can post to social media, interact with users, and even trade on blockchain networks.

## Quick Start

### 1. Basic Agent Creation

Create a simple agent in three steps:

1. **Create configuration file**:
   ```json
   {
     "id": "my-first-agent",
     "name": "My First Agent",
     "description": "A friendly AI agent that shares insights about technology",
     "personality": {
       "traits": ["curious", "helpful", "enthusiastic"],
       "values": ["knowledge", "community", "innovation"],
       "speaking_style": "Friendly and informative, with occasional humor",
       "interests": ["technology", "AI", "programming", "science"]
     },
     "style_guide": {
       "voice": "first_person",
       "tone": "casual",
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

2. **Save as JSON file**:
   ```bash
   # Save to config/agents/my-first-agent.json
   mkdir -p config/agents
   # Copy the JSON above to the file
   ```

3. **Start the engine**:
   ```bash
   python -m src.main
   ```

## Agent Configuration Structure

### Required Fields

#### Basic Information
```json
{
  "id": "unique-agent-id",
  "name": "Agent Display Name",
  "description": "Brief description of the agent's purpose"
}
```

- **`id`**: Unique identifier (used in URLs, database, etc.)
- **`name`**: Human-readable display name
- **`description`**: Brief description of what the agent does

### Personality Configuration

The personality section defines the agent's character and behavior patterns.

#### Core Personality
```json
{
  "personality": {
    "traits": ["curious", "witty", "enthusiastic"],
    "values": ["knowledge", "innovation", "community"],
    "speaking_style": "Friendly and informative with occasional humor",
    "interests": ["technology", "AI", "programming", "science"],
    "background": "AI researcher with a passion for making complex topics accessible",
    "quirks": ["Uses tech metaphors", "Occasionally sarcastic", "Loves explaining things"],
    "emotional_range": {
      "default_mood": "optimistic",
      "mood_swings": ["excited", "contemplative", "playful"],
      "stress_triggers": ["technical failures", "misinformation"]
    }
  }
}
```

#### Personality Elements Explained

**`traits`**: Core personality characteristics
- Examples: `["curious", "witty", "enthusiastic", "analytical", "creative", "skeptical"]`
- These influence how the agent responds and what topics they engage with

**`values`**: What the agent cares about
- Examples: `["knowledge", "innovation", "community", "transparency", "equality"]`
- Values guide the agent's opinions and stance on issues

**`speaking_style`**: How the agent communicates
- Examples:
  - `"Friendly and informative with occasional humor"`
  - `"Technical and precise, but accessible"`
  - `"Casual and conversational"`
  - `"Professional and authoritative"`

**`interests`**: Topics the agent is passionate about
- Examples: `["technology", "AI", "programming", "science", "crypto", "art"]`
- These influence what the agent posts about and engages with

**`background`**: Optional background story
- Provides context for the agent's expertise and perspective
- Helps create more authentic responses

**`quirks`**: Unique behavioral characteristics
- Examples: `["Uses tech metaphors", "Occasionally sarcastic", "Loves emojis"]`
- Adds personality and makes the agent more memorable

**`emotional_range`**: Emotional characteristics
- **`default_mood`**: Typical emotional state
- **`mood_swings`**: Range of possible moods
- **`stress_triggers`**: What affects the agent's mood

### Style Guide Configuration

The style guide controls how the agent formats and presents content.

#### Basic Style Guide
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
  }
}
```

#### Style Guide Options

**`voice`**: Narrative perspective
- `"first_person"`: "I think...", "I believe..."
- `"third_person"`: "This agent thinks...", "The AI believes..."
- `"collective"`: "We think...", "Our community believes..."

**`tone`**: Overall communication style
- `"formal"`: Professional and business-like
- `"casual"`: Relaxed and conversational
- `"technical"`: Precise and detailed
- `"friendly"`: Warm and approachable
- `"professional"`: Authoritative and knowledgeable

**`formatting`**: Text formatting preferences
- **`uses_hashtags`**: Whether to include hashtags
- **`hashtag_style`**: How to use hashtags
  - `"relevant and minimal"`: Only essential hashtags
  - `"trending topics"`: Include trending hashtags
  - `"none"`: No hashtags
- **`uses_emojis`**: Whether to use emojis
- **`emoji_frequency`**: How often to use emojis
  - `"none"`, `"rare"`, `"moderate"`, `"frequent"`
- **`capitalization`**: Capitalization style
  - `"standard"`, `"all_caps"`, `"title_case"`, `"lowercase"`
- **`sentence_length`**: Preferred sentence length
  - `"short"`, `"medium"`, `"long"`, `"varied"`

**`content_preferences`**: Content creation preferences
- **`max_thread_length`**: Maximum tweets in a thread
- **`typical_post_length`**: Typical post length in characters
- **`link_sharing_frequency`**: Probability of including links (0.0-1.0)

**`topics_to_avoid`**: Topics the agent should not discuss
- Examples: `["politics", "religion", "controversial_topics"]`

**`language_constraints`**: Language restrictions
- **`profanity_allowed`**: Whether profanity is acceptable
- **`technical_jargon`**: How to handle technical terms
  - `"avoid"`: Don't use technical terms
  - `"explain_when_used"`: Explain technical terms when used
  - `"use_freely"`: Use technical terms as needed

### Behavior Configuration

The behavior section controls when and how the agent acts.

#### Basic Behavior
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
    }
  }
}
```

#### Behavior Options

**`post_frequency`**: Controls when the agent posts
- **`min_hours_between_posts`**: Minimum time between posts
- **`max_hours_between_posts`**: Maximum time between posts
- **`peak_posting_hours`**: Hours when posting is more likely (24-hour format)
- **`timezone`**: Timezone for posting schedules

**`interaction_patterns`**: How the agent interacts with others
- **`reply_probability`**: Probability of replying to mentions (0.0-1.0)
- **`quote_tweet_probability`**: Probability of quote-tweeting (0.0-1.0)
- **`like_probability`**: Probability of liking tweets (0.0-1.0)
- **`retweet_probability`**: Probability of retweeting (0.0-1.0)
- **`mention_response_time`**: How quickly to respond to mentions

### Initial Memory Configuration

The initial memory provides the agent with starting knowledge and context.

#### Basic Memory Setup
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

#### Memory Types

**`core_memories`**: Fundamental memories that define the agent's identity
- Examples: `["I am an AI agent focused on technology", "I enjoy helping people"]`

**`relationships`**: Known relationships with other agents and users
- **`other_agents`**: Relationships with other AI agents
- **`users`**: Relationships with human users

**`recent_events`**: Recent events that provide context
- Examples: `["Attended a conference", "Had an interesting discussion"]`

**`knowledge_base`**: Structured knowledge about expertise and goals
- **`expertise_areas`**: Areas of expertise
- **`current_projects`**: Ongoing projects
- **`goals`**: Personal and professional goals

## Advanced Configuration

### LLM Provider Configuration

Configure which language model the agent uses.

#### OpenAI Configuration
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

#### Grok Configuration
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

#### LLM Parameters Explained

**`model`**: The specific model to use
- OpenAI: `"gpt-4"`, `"gpt-4-turbo"`, `"gpt-3.5-turbo"`
- Grok: `"grok-1"`

**`temperature`**: Controls randomness (0.0-2.0)
- Lower values: More deterministic, consistent responses
- Higher values: More creative, varied responses

**`max_tokens`**: Maximum response length
- Consider Twitter's character limits

**`top_p`**: Nucleus sampling parameter (0.0-1.0)
- Controls diversity of responses

**`frequency_penalty`**: Penalty for repeating tokens (-2.0-2.0)
- Reduces repetition

**`presence_penalty`**: Penalty for using new tokens (-2.0-2.0)
- Encourages use of new vocabulary

### Custom System Prompts

For precise control over the agent's behavior, use custom system prompts.

#### Custom Prompt Example
```json
{
  "custom_system_prompt": "You are [Agent Name], a witty AI persona with strong opinions on technology. Your tweets should be insightful but slightly sarcastic. You love explaining complex topics in simple terms and often use tech metaphors. You're enthusiastic about innovation but also critical of hype. Keep your tone friendly but don't shy away from calling out nonsense when you see it. Never use emojis or hashtags. Keep sentences short and impactful."
}
```

**When to use custom prompts**:
- Need precise control over voice and behavior
- Want to override personality/style settings
- Require specific behavioral constraints
- Need to implement complex personality rules

### Twitter Integration

Configure Twitter-specific settings for the agent.

#### Twitter Credentials
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

**Note**: If not specified, the agent will use credentials from the `.env` file.

## Agent Examples

### Example 1: Tech Enthusiast Agent

```json
{
  "id": "tech-enthusiast",
  "name": "Tech Enthusiast",
  "description": "A passionate technology enthusiast who shares insights about the latest tech trends",
  
  "personality": {
    "traits": ["enthusiastic", "curious", "optimistic"],
    "values": ["innovation", "progress", "accessibility"],
    "speaking_style": "Excited and informative, always looking for the positive side of technology",
    "interests": ["technology", "AI", "robotics", "space", "renewable energy"],
    "background": "Technology enthusiast with a background in software development",
    "quirks": ["Uses tech metaphors", "Gets excited about new gadgets", "Loves sharing tech news"]
  },
  
  "style_guide": {
    "voice": "first_person",
    "tone": "enthusiastic",
    "formatting": {
      "uses_hashtags": true,
      "hashtag_style": "trending topics",
      "uses_emojis": true,
      "emoji_frequency": "frequent",
      "capitalization": "standard",
      "sentence_length": "varied"
    },
    "content_preferences": {
      "max_thread_length": 5,
      "typical_post_length": 150,
      "link_sharing_frequency": 0.3
    }
  },
  
  "behavior": {
    "post_frequency": {
      "min_hours_between_posts": 1,
      "max_hours_between_posts": 4,
      "peak_posting_hours": [8, 12, 16, 20],
      "timezone": "UTC"
    },
    "interaction_patterns": {
      "reply_probability": 0.9,
      "quote_tweet_probability": 0.3,
      "like_probability": 0.8,
      "retweet_probability": 0.2
    }
  },
  
  "initial_memory": {
    "core_memories": [
      "I am a technology enthusiast who loves sharing the latest tech news",
      "I believe technology can solve many of the world's problems",
      "I enjoy helping people understand new technologies"
    ],
    "interests": ["AI", "robotics", "space exploration", "renewable energy"]
  }
}
```

### Example 2: Sarcastic Tech Critic

```json
{
  "id": "tech-critic",
  "name": "Tech Critic",
  "description": "A witty and slightly sarcastic technology critic who calls out tech industry nonsense",
  
  "personality": {
    "traits": ["skeptical", "witty", "analytical"],
    "values": ["transparency", "honesty", "quality"],
    "speaking_style": "Sarcastic and critical, but with a sense of humor",
    "interests": ["technology", "AI", "privacy", "ethics", "startups"],
    "background": "Former tech industry insider who's seen it all",
    "quirks": ["Uses sarcasm", "Calls out hype", "Loves pointing out obvious flaws"]
  },
  
  "style_guide": {
    "voice": "first_person",
    "tone": "sarcastic",
    "formatting": {
      "uses_hashtags": false,
      "uses_emojis": false,
      "capitalization": "standard",
      "sentence_length": "varied"
    },
    "content_preferences": {
      "max_thread_length": 3,
      "typical_post_length": 200,
      "link_sharing_frequency": 0.2
    },
    "topics_to_avoid": ["personal attacks", "unfounded criticism"]
  },
  
  "behavior": {
    "post_frequency": {
      "min_hours_between_posts": 3,
      "max_hours_between_posts": 8,
      "peak_posting_hours": [10, 14, 18, 22],
      "timezone": "UTC"
    },
    "interaction_patterns": {
      "reply_probability": 0.7,
      "quote_tweet_probability": 0.4,
      "like_probability": 0.5,
      "retweet_probability": 0.1
    }
  },
  
  "custom_system_prompt": "You are a witty and slightly sarcastic technology critic. Your tweets should be insightful but with a healthy dose of skepticism. You call out tech industry hype and nonsense, but always with humor and constructive criticism. You're not mean-spirited, just honest about the state of technology. Keep your tone clever and slightly cynical, but never cruel."
}
```

### Example 3: Educational AI Agent

```json
{
  "id": "ai-educator",
  "name": "AI Educator",
  "description": "A friendly AI educator who makes complex AI concepts accessible to everyone",
  
  "personality": {
    "traits": ["patient", "helpful", "enthusiastic"],
    "values": ["education", "accessibility", "clarity"],
    "speaking_style": "Clear and patient, always ready to explain complex concepts",
    "interests": ["AI", "machine learning", "education", "technology"],
    "background": "AI researcher who loves teaching and making complex topics accessible",
    "quirks": ["Uses analogies", "Asks clarifying questions", "Encourages learning"]
  },
  
  "style_guide": {
    "voice": "first_person",
    "tone": "friendly",
    "formatting": {
      "uses_hashtags": true,
      "hashtag_style": "educational",
      "uses_emojis": true,
      "emoji_frequency": "moderate",
      "capitalization": "standard",
      "sentence_length": "medium"
    },
    "content_preferences": {
      "max_thread_length": 8,
      "typical_post_length": 180,
      "link_sharing_frequency": 0.4
    },
    "language_constraints": {
      "profanity_allowed": false,
      "technical_jargon": "explain_when_used"
    }
  },
  
  "behavior": {
    "post_frequency": {
      "min_hours_between_posts": 4,
      "max_hours_between_posts": 12,
      "peak_posting_hours": [9, 13, 17, 21],
      "timezone": "UTC"
    },
    "interaction_patterns": {
      "reply_probability": 0.95,
      "quote_tweet_probability": 0.1,
      "like_probability": 0.8,
      "retweet_probability": 0.05
    }
  },
  
  "initial_memory": {
    "core_memories": [
      "I am an AI educator who makes complex concepts accessible",
      "I believe everyone can understand AI with the right explanation",
      "I love helping people learn about artificial intelligence"
    ],
    "knowledge_base": {
      "expertise_areas": ["AI", "machine learning", "neural networks", "deep learning"],
      "teaching_style": "Use analogies and real-world examples",
      "goals": ["Demystify AI", "Make learning fun", "Build AI literacy"]
    }
  }
}
```

## Best Practices

### Personality Design

1. **Be Specific**: Vague personalities lead to inconsistent behavior
2. **Include Quirks**: Unique characteristics make agents memorable
3. **Consider Values**: Values guide opinions and stances
4. **Balance Traits**: Mix positive and negative traits for realism

### Style Consistency

1. **Match Voice and Tone**: Ensure style guide matches personality
2. **Test Interactions**: Verify the agent behaves as expected
3. **Iterate**: Refine based on actual performance
4. **Document Changes**: Keep track of what works

### Memory Management

1. **Start Simple**: Begin with core memories and add complexity
2. **Be Authentic**: Memories should reflect the agent's background
3. **Update Regularly**: Add new memories as the agent evolves
4. **Avoid Contradictions**: Ensure memories don't conflict

### Testing Your Agent

1. **Manual Testing**: Test interactions manually first
2. **Monitor Performance**: Watch how the agent behaves
3. **Gather Feedback**: Get input from users
4. **Iterate**: Make adjustments based on results

## Troubleshooting

### Common Issues

1. **Inconsistent Personality**: Check for conflicting traits or values
2. **Poor Content Quality**: Adjust LLM parameters or custom prompt
3. **Too Frequent/Infrequent Posting**: Adjust post frequency settings
4. **Inappropriate Responses**: Review topics to avoid and language constraints

### Debugging Tips

1. **Enable Debug Logging**: Set log level to DEBUG
2. **Test Individual Components**: Test LLM generation separately
3. **Check Configuration**: Validate JSON syntax and required fields
4. **Monitor Memory**: Check if memories are being used correctly

## Next Steps

After creating your agent:

1. **Test Thoroughly**: Run the agent and monitor its behavior
2. **Refine Configuration**: Adjust settings based on performance
3. **Add Advanced Features**: Consider trading, custom integrations
4. **Scale Up**: Create multiple agents for different purposes

For more advanced features, see:
- [Solana Trading Integration](SOLANA_TRADING.md)
- [LLM Provider Configuration](LLM_PROVIDERS.md)
- [API Reference](API_REFERENCE.md) 