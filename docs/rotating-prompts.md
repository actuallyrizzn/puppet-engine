# Rotating System Prompts

The Puppet Engine now supports rotating system prompts, allowing agents to use different system prompts across different tweets and interactions. This helps create more variety and authentic character portrayal.

## Overview

Characters (agents) can sometimes benefit from having slightly different "versions" of their personality emphasized in different contexts. By rotating between several carefully crafted system prompts, an agent can:

1. Produce more varied and authentic content
2. Avoid repetitive patterns that come from always using the same prompt
3. Express different aspects of their character's personality
4. Create more engaging and unpredictable interactions

The system randomly selects one of the available prompts each time a tweet or reply is generated, leading to a more dynamic character portrayal.

## Configuration

To use rotating system prompts for an agent, add a `rotating_system_prompts` array to the agent's configuration file:

```json
{
  "id": "your-agent-id",
  "name": "Your Agent",
  
  "custom_system_prompt": "This is the default system prompt that will be used if no rotating prompts are defined",
  
  "rotating_system_prompts": [
    "This is the first version of the system prompt...",
    "This is the second version of the system prompt...",
    "This is the third version of the system prompt..."
  ],
  
  // Other agent configuration...
}
```

You can define up to 3 different system prompts. Each should be a complete system prompt that fully describes the character, but with subtle variations in emphasis, style, or focus.

## How It Works

1. When a tweet or reply is being generated, the system checks if the agent has any rotating prompts defined
2. If so, it randomly selects one of the prompts from the array
3. That prompt is used for this specific generation 
4. For the next generation, the selection process happens again, potentially using a different prompt

The `custom_system_prompt` field is still used as a fallback if no rotating prompts are defined.

## Testing

Two test scripts are provided to verify the rotating prompt system:

1. `test_coby_tweets.py` - Tests tweet generation with rotating prompts
2. `test_coby_replies.py` - Tests reply generation with rotating prompts

Run these scripts to see how different prompts affect the output:

```bash
python tests/test_rotating_prompts.py
```

## Metadata

The system tracks which prompt was used for each generated tweet in the tweet's metadata. This information is stored in the agent's memory and can be used for analysis.

## Implementation Details

The rotating prompt system is implemented in several files:

- `src/core/models.py` - Added `rotating_system_prompts` property to the Agent class
- `src/agents/agent_manager.py` - Updated to load rotating prompts from configuration
- `src/llm/openai_provider.py` - Added logic to select a random prompt for each generation
- `src/llm/tweet_variety_helpers.py` - Added logging helper for prompt selection

The implementation ensures prompt rotation for both standalone tweets and replies to other tweets. 