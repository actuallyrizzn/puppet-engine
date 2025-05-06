# Autonomous Agent Tokenization via Pump.fun

The Puppet Engine now includes a powerful tokenization feature that allows AI agents to autonomously create and launch their own tokens on the Solana blockchain through pump.fun. This represents a significant advancement in agent autonomy, enabling agents to establish their own on-chain presence without human intervention.

## 🚀 Core Features

- **Autonomous Token Creation**: Agents can independently create and launch Solana tokens with their own identity
- **One-Time Launch Logic**: Built-in state management ensures each agent launches only one token
- **Automatic Social Promotion**: Agents automatically tweet their token link after successful launch
- **Persistent Token Memory**: Token details are stored in the agent's memory for natural references in conversations
- **Simulation Mode**: Test the flow without spending real SOL or creating actual tokens

## 🔄 How It Works

The tokenization process follows these autonomous steps:

1. On startup, each agent checks if they've already launched a token (stored in `data/[agent-id]-token-state.json`)
2. If no token exists, the agent autonomously creates one with their predetermined parameters
3. The agent automatically posts about their new token on Twitter with the pump.fun link
4. Token information is stored in the agent's memory for natural integration into future interactions

## 🛠️ Implementation Details

### Direct Pump.fun API Integration

The implementation uses solana-agent-kit to interact with pump.fun's on-chain program:

1. Initialize a Solana connection and wallet keypair
2. Upload token metadata and image to IPFS via pump.fun's API
3. Create a token through direct interaction with pump.fun's on-chain program
4. In simulation mode, this process is simulated without actual on-chain transactions

### Token Parameters

The default configuration for tokens is minimal but can be customized per agent:
- **Name**: Test (configurable per agent)
- **Ticker**: TEST (configurable per agent)
- **Description**: Empty by default (configurable)
- **Initial Liquidity**: 0.05 SOL (configurable)

### Required Configuration

To enable agent tokenization, add these variables to your `.env` file:

```
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_PRIVATE_KEY=YOUR_PRIVATE_KEY_HERE
SOLANA_WALLET_ADDRESS=YOUR_WALLET_ADDRESS_HERE
```

Each wallet needs sufficient SOL for token creation and initial liquidity (~0.1 SOL recommended).

## 🧩 Extending The System

### Adding Tokenization to Other Agents

To enable any agent to create its own token:

1. Initialize the `PumpFunTokenManager` with the agent's Twitter client
2. Call `launchTokenIfNeeded` with the agent's ID
3. Add token references to the agent's memory for natural conversations

Example:
```javascript
// For any agent in your system
const result = await pumpFunTokenManager.launchTokenIfNeeded('agent-id');
if (result.success) {
  // Add to agent's memory
  agent.memory.addMemory(`I launched my own token at ${result.pumpFunLink}`, 'core', 0.8);
}
```

### Customizing Token Parameters

Modify the token launch parameters in the `launchTokenIfNeeded` method to customize:
- Token name and ticker
- Initial liquidity amount
- Token image URL
- Token description

## 🔍 System Usage

### Launching Tokens

To launch a token or check if one exists:

```bash
npm run token:launch
```

### Forcing a New Token

To force a new token creation (for testing or development):

```bash
npm run token:force-new
```

### Posting About Existing Tokens

To tweet about an existing token without creating a new one:

```bash
npm run token:tweet
```

## 📁 Implementation Files

- `src/solana/pumpfun-token-manager.js` - Core tokenization logic with solana-agent-kit integration
- `scripts/token-launch/coby-token-launcher.js` - Standalone token launcher script
- `data/[agent-id]-token-state.json` - Agent-specific token state storage
- `src/index.js` - Integration with the agent system
- `docs/token-launch-usage.md` - Detailed usage documentation

## 🔮 Future Enhancements

- Full transaction support for actual on-chain token creation (by disabling simulation mode)
- Multiple token support with agent-specific parameters
- Token utility integration (staking, governance, etc.)
- Cross-agent token interactions and trading
- Dynamic token image generation based on agent personality 