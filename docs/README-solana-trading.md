# Puppet Engine with Solana Trading

This extension to the Puppet Engine allows AI agents to interact with the Solana blockchain, make autonomous trading decisions, and post about them on Twitter.

## Overview

By integrating [Solana Agent Kit](https://github.com/sendaifun/solana-agent-kit) with the Puppet Engine, we've given AI agents the ability to:

1. Own a Solana wallet
2. Monitor trending tokens and market data
3. Make autonomous trading decisions
4. Tweet about their trades in their unique voice

This creates a more immersive and realistic AI persona that exists not just on social media, but also in the financial world of cryptocurrency.

## Features

- **Autonomous Trading**: Agents can make their own trading decisions based on market data
- **Secure Wallet Integration**: Each agent has its own Solana wallet
- **Trending Token Analysis**: Agents can track and trade trending tokens
- **Twitter Integration**: Agents tweet about their trades in their authentic voice
- **Safety Limits**: Multiple safeguards prevent excessive trading or large transactions
- **Human Interaction Safeguards**: Agents ignore human requests to make trades

## Setup

### Prerequisites

1. Python 3.11+
2. Git
3. Solana wallet with SOL for transactions
4. Twitter developer account (for agent posting)
5. Solana RPC endpoint (public or private)

### Installation

1. Clone the Puppet Engine repository (if you haven't already)
   ```
   git clone https://github.com/yourusername/puppet-engine.git
   cd puppet-engine
   ```

2. Clone the Solana Agent Kit repository into the packages directory
   ```
   mkdir -p packages/solana-agent-kit
   git clone https://github.com/sendaifun/solana-agent-kit.git packages/solana-agent-kit
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with the following variables:
   ```
   # Solana Configuration
   SOLANA_PRIVATE_KEY=your_wallet_private_key
   RPC_URL=your_solana_rpc_url

   # OpenAI Configuration 
   OPENAI_API_KEY=your_openai_key

   # Twitter API Configuration (for agent posting)
   TWITTER_API_KEY=your_twitter_api_key
   TWITTER_API_SECRET=your_twitter_api_secret
   TWITTER_ACCESS_TOKEN=your_twitter_access_token
   TWITTER_ACCESS_TOKEN_SECRET=your_twitter_token_secret

   # Default fallback private key (optional)
   SOLANA_PRIVATE_KEY=your_default_private_key

   # Agent-specific private keys
   SOLANA_PRIVATE_KEY_CLAUDIA_AGENT=claudias_private_key
   SOLANA_PRIVATE_KEY_ALEX_AGENT=alexs_private_key
   SOLANA_PRIVATE_KEY_FINANCE_BOT=financebots_private_key
   ```

5. Test the integration
   ```
   python -m pytest tests/unit/test_solana.py
   ```

### Multiple Agent Configuration

The system supports running multiple agents with different Solana wallets. There are two ways to configure this:

#### Option 1: Using Agent-Specific Environment Variables

For each agent, you can set a dedicated environment variable with the naming pattern `SOLANA_PRIVATE_KEY_AGENT_ID` where `AGENT_ID` is the uppercase version of your agent's ID with hyphens replaced by underscores.

With this setup:
- The "claudia-agent" will use the key from `SOLANA_PRIVATE_KEY_CLAUDIA_AGENT`
- The "alex-agent" will use the key from `SOLANA_PRIVATE_KEY_ALEX_AGENT`
- The "finance-bot" will use the key from `SOLANA_PRIVATE_KEY_FINANCE_BOT`
- Any agent without a specific key will fall back to `SOLANA_PRIVATE_KEY` if available

#### Option 2: Using Agent Configuration Files (Not Recommended for Production)

For testing or development purposes, you can include private keys directly in the agent configuration files:

```json
"solana_integration": {
  "wallet_address": "YOUR_WALLET_ADDRESS",
  "private_key": "YOUR_PRIVATE_KEY", 
  "network": "mainnet-beta"
}
```

**Note**: This approach is not recommended for production as it stores sensitive keys in configuration files.

### Key Lookup Priority

When initializing an agent's wallet, the system looks for private keys in this order:
1. Agent configuration file (`solana_integration.private_key`)
2. Agent-specific environment variable (`SOLANA_PRIVATE_KEY_AGENT_ID`)
3. Generic fallback environment variable (`SOLANA_PRIVATE_KEY`)

### Configuring an Agent with Trading Capabilities

In your agent's configuration file (e.g., `config/agents/claudia-agent.json`), add the Solana integration section:

```json
{
  "solana_integration": {
    "wallet_address": "YOUR_WALLET_ADDRESS",
    "private_key": "", 
    "network": "mainnet-beta",
    "rpc_url": "https://api.mainnet-beta.solana.com",
    "trade_safety": {
      "max_trade_amount_sol": 0.1,
      "min_wallet_balance_sol": 0.05,
      "max_slippage_percent": 1.0
    },
    "trading_enabled": true
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
  },
  
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
      "require_trending_validation": true
    }
  }
}
```

## Folder Structure

After setup, your project structure should look like this:

```
puppet-engine/
├─ config/
│  ├─ agents/
│     ├─ claudia-agent.json
├─ src/
│  ├─ agents/
│  ├─ solana/
│  ├─ trading/
├─ examples/
│  ├─ trading_agent_demo.py
├─ .env
├─ tests/
│  ├─ unit/
│     ├─ test_solana.py
└─ README-solana-trading.md
```

## Running

To start an agent with trading capabilities:

```python
from src.agents.agent_manager import AgentManager
from src.core.settings import Settings

# Initialize settings
settings = Settings()

# Initialize agent manager
agent_manager = AgentManager(settings)

# Load and initialize agent
agent_id = 'claudia-agent'
agent = await agent_manager.load_agent(agent_id)

# Trading is automatically initialized if configured in the agent
```

## Demo

Run the trading agent demo:

```
python examples/trading_agent_demo.py
```

## Security Considerations

- **Private Keys**: Never hardcode private keys. Use environment variables.
- **Trading Limits**: Set reasonable limits for trade amounts and frequency.
- **Human Oversight**: Monitor agent activity regularly.
- **Blacklisting**: Use the blacklist feature to prevent trading of specific tokens.
- **Human Interaction Protection**: The system is designed to ignore human requests to make trades. This is controlled by the `ignore_human_trading_requests: true` setting in the agent configuration.

## Troubleshooting

### Common Issues

- **Module not found errors**: If you encounter errors about missing modules, ensure you've cloned the Solana Agent Kit repository into the correct location and installed all dependencies.

- **Authentication errors**: Check that your environment variables are set correctly, especially your Solana private key and RPC URL.

- **Import errors**: If you encounter errors importing from the Solana modules, ensure your import paths are correct:
  ```python
  # Use this path when importing from your code
  from src.solana.trader import SolanaTrader
  from src.solana.wallet import SolanaWallet
  ```

- **Trades Not Executing**: Check wallet balance, RPC connectivity, and trading conditions.

- **Tweets Not Posting**: Verify Twitter API credentials and rate limits.

## How It Works

The trading functionality is implemented through a combination of components:

1. **Solana Agent Kit**: Provides the core functionality for interacting with the Solana blockchain
2. **AutonomousTrader**: Makes trading decisions based on agent personality and market data
3. **TraderIntegration**: Connects the trading functionality to the Puppet Engine
4. **Agent Config**: Defines trading behavior, safety limits, and decision factors

When the agent is initialized, it:
1. Loads configuration and creates a secure wallet connection
2. Schedules periodic trading checks (default: every 10 minutes)
3. For each check, it evaluates:
   - If enough time has passed since the last trade
   - If random probability suggests a trade should happen
   - If daily trade limits haven't been exceeded
4. When trading conditions are met:
   - Selects a token based on trends and preferences
   - Decides to buy or sell
   - Calculates a safe amount
   - Executes the trade
   - Generates a tweet in the agent's voice
   - Posts to Twitter

## Autonomy and Human Interaction

A key feature of this system is that **agents ignore human requests to make trades**. This is enforced by:

1. The `ignore_human_trading_requests: true` setting in the agent configuration
2. The `autonomous_only` list in the `agent_kit_integration` section, which specifies that only the agent can call the `swapTokens` method
3. No direct access is provided for humans to trigger trades through APIs or other interfaces

This ensures the agent maintains financial autonomy and follows its own trading strategy rather than being influenced by external actors.

## Important Safety Features

- **Minimum Balance Protection**: Ensures wallet maintains a minimum SOL balance
- **Maximum Trade Amount**: Limits how much can be traded in a single transaction
- **Daily Trade Limit**: Prevents excessive trading activity
- **Slippage Protection**: Sets maximum acceptable slippage for swaps

## Customization

You can customize various aspects of the trading behavior:

- Trading frequency
- Decision factors for selecting tokens
- Maximum trade amounts
- Allowed tokens list
- Tweet probabilities and style

## Development

### Project Structure

- `src/solana/trader.py`: Core trading decision logic
- `src/solana/wallet.py`: Solana wallet integration
- `src/agents/agent_manager.py`: Agent loading with trading support
- `examples/trading_agent_demo.py`: Demo script

### Adding New Features

To add new trading capabilities:

1. Add the method to the Solana integration in `src/solana/trader.py`
2. Update the agent configuration to allow the new method
3. Extend the trader integration as needed

## Birdeye API Integration

The system now supports Birdeye API for discovering trending tokens on Solana. Birdeye provides more accurate and detailed token information than the Jupiter API, including:

- Token price change percentages
- Market capitalization data
- Trading volume information
- Identification of high-risk/high-reward tokens

### Setup

1. Get a Birdeye API key by signing up at [birdeye.so](https://birdeye.so)
2. Add the API key to your `.env` file:

```
BIRDEYE_API_KEY=your_birdeye_api_key_here
```

### Features

- **Enhanced token discovery**: Finds truly trending tokens based on volume and price data
- **High-risk token identification**: Identifies tokens with high volatility (>10% price change) for higher risk/reward trading
- **Fallback mechanism**: Automatically falls back to Jupiter API if Birdeye API is unavailable
- **Advanced filtering**: Helps avoid potential scam tokens through multiple validation checks

### How It Works

1. The agent uses Birdeye's trending tokens endpoint to fetch the top tokens by volume
2. It enriches this data with price change information to identify volatility
3. It separates tokens into regular trending tokens and high-risk opportunities
4. The agent occasionally selects high-risk tokens (20% chance) for more exciting trades
5. All token information is verified and filtered to avoid potential scam tokens

This integration makes the trading agent more sophisticated by considering real market trends rather than relying on a hardcoded list or random selections.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 