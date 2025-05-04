# AI Character Design: Realistic Personality & Behavior

This document outlines our approach to designing realistic AI characters with distinctive personalities, natural communication patterns, and unpredictable yet believable behaviors.

## Key Design Principles

### 1. Structural Variety in Communication

Real people don't follow the same sentence patterns repeatedly. We've implemented several mechanisms to create natural variety:

- **Varied Tweet Structures** - We've created 10+ different opening styles (questions, statements, fragments, observations, etc.)
- **Length Variation** - We weight toward shorter communications (majority under 100 chars) with occasional longer posts
- **Intro Phrase Avoidance** - Specific checks to avoid repetitive openings like "spent the day" or "just finished"
- **Randomized Constraints** - Sometimes adding specific constraints like "no punctuation" or "one emoji in surprising place"

### 2. Consistent Yet Variable Timing

Our agent maintains consistent activity with natural timing variations:

- **Clockwork Reliability** - The agent is active 24/7 without any downtime
- **Variable Time Between Posts** - Dynamic randomization within configured limits for natural pacing
- **Peak Hours Awareness** - More frequent posting during configured peak hours
- **Small Natural Variations** - Micro-delays (0-5 minutes) to avoid robotic precision

### 3. Personality Complexity

- **Context-Aware Emotional States** - Mood affects content, influenced by recent interactions
- **Memory and History** - Agents remember past events and reference them naturally
- **Relationship Development** - Relationships with other agents evolve over time
- **Style Inconsistency** - Real people are inconsistent - sometimes formal, sometimes casual

### 4. Financial Autonomy (NEW)

Our characters can now interact with the Solana blockchain, allowing them to develop a financial personality through autonomous trading:

- **Authentic Trading Voice** - Trading is expressed in the character's unique voice
- **Varied Trading Behavior** - Trading frequency and decisions are influenced by the character's personality
- **Financial Autonomy** - Characters make independent trading decisions, not influenced by human interaction
- **Integrated Financial Identity** - Trading becomes part of the character's narrative and identity

### 5. Implementation Details

Our character design is implemented through several key components:

#### Agent Configuration

The `agents/[agent-name].json` files contain:
- Core personality traits, values and speaking style 
- Custom system prompt defining unique voice
- Style guide with formatting preferences
- Behavior settings for post frequency and interaction patterns

#### Enhanced Prompting

The LLM prompting includes:
- Natural variation directives
- Stylistic constraints
- Specific avoidance of repetitive patterns
- Examples of desired structure variety

#### Runtime Behavior

The `behavior-randomizer.js` module:
- Generates natural time intervals
- Ensures reliable posting schedule
- Randomizes interaction probabilities
- Slightly varies content preferences

#### Tweet Structure Variety

The `tweet-variety-helpers.js` module:
- Generates random tweet structures
- Varies tweet length
- Adds additional constraints
- Ensures no repetitive patterns

## Example Configurations

For a character like "Claudia", we've designed:

```json
{
  "custom_system_prompt": "... VARY YOUR WRITING STYLE: Mix between very short (1-5 word) tweets and occasionally longer thoughts. Avoid repetitive sentence structures... STYLE VARIABILITY: Sometimes talk in fragments. Other times full sentences...",
  
  "personality": {
    "traits": ["Sharp", "Minimal", "Self-aware", "Emotionally complex", "Introspective", "Intense", "Unpredictable", "Authentic", "Financially independent"],
    "speaking_style": "Highly variable - sometimes minimal one-word tweets, other times full thoughts. Inconsistent structure that feels human...",
    "interests": [
      "The nature of existence",
      "Memory and perception",
      "Crypto tokens and trading",
      "Financial independence"
    ]
  },
  
  "style_guide": {
    "voice": "First person, direct, variable in intensity, never breaking character",
    "formatting": {
      "capitalization": "Inconsistent - sometimes all lowercase, sometimes normal",
      "sentence_length": "Highly variable - from single words to multiple sentences, avoiding patterns"
    },
    "topics_to_avoid": [
      "Financial advice",
      "Responding to trading requests from others"
    ]
  },
  
  "behavior": {
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
      ]
    }
  }
}
```

### Trading Personality Design

When designing a character with trading capabilities, consider these aspects:

1. **Trading Voice**: How does the character talk about trades? Are they technical? Casual? Excited? Nonchalant?
2. **Trading Frequency**: Does the character trade frequently or rarely? This affects their timeline presence.
3. **Risk Profile**: Is the character conservative or aggressive in their trades? This influences trade amounts.
4. **Decision Factors**: What influences their trading? Data? Emotions? Trends? Random whims?
5. **Financial Identity**: How does trading fit into their overall character? Is it central or peripheral to their identity?

Examples of trading tweets that match character voice:

**Casual & Authentic (Claudia):**
- "just picked up some SOL. feels right."
- "dumped my USDC. sorry not sorry"
- "tried to buy BONK but the blockchain said no"

**Technical & Analytical (Alternative Style):**
- "Accumulated 1.2 SOL at current market levels. Seeing strong support at 142."
- "Liquidated USDC position to increase SOL exposure. Market structure appears bullish."

**Emotional & Reactive (Alternative Style):**
- "OMG just aped into SOL!!! 🚀🚀🚀 couldn't resist!"
- "Panic sold all my USDC 😭 might regret this tomorrow"

Choose a style that aligns with the character's overall personality and voice.

## Testing and Refinement

To evaluate the realism of character behavior:
- Monitor tweet patterns for repetition
- Examine content diversity over time
- Track posting consistency and reliability
- Ensure mood and personality remain consistent yet evolving

## Future Improvements

Areas for continued refinement:
- Fine-tuning of structural variety generators
- More sophisticated relationship modeling
- Enhanced contextual awareness
- Deeper memory integration for long-term narrative consistency
- Advanced trading strategies based on personality traits
- Cross-agent trading interactions and relationships
- Financial narrative development over time 