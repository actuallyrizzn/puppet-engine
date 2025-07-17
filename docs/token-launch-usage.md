# Using the Autonomous Token Launch Feature

This guide explains how to use the autonomous token launch functionality for agents using the Solana Agent Kit integration with pump.fun.

## Prerequisites

Before running the token launcher, make sure:

1. You have set up the required environment variables in `.env`:
   ```
   SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
   SOLANA_PRIVATE_KEY=YOUR_PRIVATE_KEY_HERE
   ```

2. Your wallet has sufficient SOL for token creation and initial liquidity (at least 0.1 SOL recommended)

3. Twitter API credentials are configured correctly for posting tweets

## Running the Token Launcher

We've added several Python scripts to make token launching easier:

### Basic Token Launch

This checks whether an agent already has a token, and if not, creates a new one.

```bash
python scripts/token_launch.py
```

### Force a New Token Launch

This deletes any existing token state and forces the creation of a new token. Use this cautiously on mainnet as it will use real SOL.

```bash
python scripts/token_launch.py --force-new
```

### Force a Tweet About Existing Token

If an agent already has a token, this will force a new tweet about the existing token without creating a new one.

```bash
python scripts/token_launch.py --force-tweet
```

## Customizing the Launch

### Custom Tweet Messages

You can set a custom tweet message by adding the following to your `.env` file:

```
CUSTOM_TWEET_MESSAGE="just launched my test token on pump.fun, probably worthless but yolo"
```

### Running Directly with Python

You can also run the launcher directly with additional options:

```bash
# Basic launch
python scripts/token_launch.py

# Force new token launch
python scripts/token_launch.py --force-new

# Force tweet about existing token
python scripts/token_launch.py --force-tweet

# Both force new and force tweet
python scripts/token_launch.py --force-new --force-tweet
```

## Understanding Launch Results

The token launcher will output:

- Step-by-step progress of the token launch process
- Token mint address if successful
- pump.fun URL for the token
- Transaction signature for verification
- Tweet ID if a tweet was posted

## Simulation Mode

By default, the token launcher runs in simulation mode to avoid using real SOL for testing. To enable actual on-chain token creation:

1. Edit `src/solana/pumpfun_token_manager.py`
2. Set `SIMULATION_MODE = false` at the top of the file
3. Ensure your wallet has enough SOL for the operation

## Troubleshooting

If the launch fails, check:

1. Your SOLANA_PRIVATE_KEY is correct and has sufficient SOL
2. The RPC URL is accessible
3. Twitter API credentials are valid
4. Network connectivity to Solana and pump.fun APIs

Logs will be printed to the console with detailed error information if any step fails. 