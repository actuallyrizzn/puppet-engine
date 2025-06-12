// Direct Solana and Jupiter integration (no Solana Agent Kit)
const bs58 = require('bs58').default;
const fs = require('fs');
const path = require('path');
const { Keypair, Connection, LAMPORTS_PER_SOL, VersionedTransaction, PublicKey } = require('@solana/web3.js');

/**
 * Helper function to ensure RPC URL is properly formatted
 * @param {string} url - The RPC URL to sanitize
 * @returns {string} - A properly formatted RPC URL
 */
function sanitizeRpcUrl(url) {
  if (!url) return 'https://api.mainnet-beta.solana.com';
  
  // Remove any whitespace
  let sanitizedUrl = url.trim();
  
  // Ensure URL starts with http:// or https://
  if (!sanitizedUrl.startsWith('http://') && !sanitizedUrl.startsWith('https://')) {
    sanitizedUrl = 'https://' + sanitizedUrl;
  }
  
  return sanitizedUrl;
}

/**
 * Get a swap quote from Jupiter API
 * @param {string} inputMint - Input token mint address
 * @param {string} outputMint - Output token mint address
 * @param {string} amount - Amount of input token (in smallest units)
 * @param {number} slippageBps - Slippage in basis points (e.g., 100 = 1%)
 * @returns {Promise<Object>} Jupiter quote response
 */
async function getJupiterQuote(inputMint, outputMint, amount, slippageBps = 100) {
  try {
    // Validate inputs to avoid Jupiter API errors
    if (!inputMint || !outputMint || !amount) {
      throw new Error('Missing required parameters: inputMint, outputMint, or amount');
    }
    
    if (inputMint === outputMint) {
      throw new Error('Input and output tokens cannot be the same');
    }
    
    // Check if amount is a valid number
    const amountNum = parseInt(amount);
    if (isNaN(amountNum) || amountNum <= 0) {
      throw new Error('Invalid amount: must be a positive number');
    }
    
    console.log(`Getting Jupiter quote for ${inputMint} to ${outputMint} with amount ${amount}`);
    
    const params = new URLSearchParams({
      inputMint,
      outputMint,
      amount,
      slippageBps: slippageBps.toString(),
      feeBps: "0"
    });
    
    const response = await fetch(`https://quote-api.jup.ag/v6/quote?${params}`);
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Jupiter API error: ${response.status} ${response.statusText} - ${errorText}`);
    }
    
    const quoteResponse = await response.json();
    return quoteResponse;
  } catch (error) {
    console.error('Error getting Jupiter quote:', error);
    throw error;
  }
}

/**
 * Get swap instructions from Jupiter
 * @param {object} quoteResponse - The quote response from Jupiter API
 * @param {string} userPublicKey - User's wallet public key
 * @returns {Promise<object>} Swap instructions
 */
async function getJupiterSwapInstructions(quoteResponse, userPublicKey) {
  try {
    // Validate inputs
    if (!quoteResponse || !userPublicKey) {
      throw new Error('Missing required parameters: quoteResponse or userPublicKey');
    }
    
    const response = await fetch('https://quote-api.jup.ag/v6/swap', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        quoteResponse,
        userPublicKey,
        wrapAndUnwrapSol: true
      })
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Jupiter API error: ${response.status} ${response.statusText} - ${errorText}`);
    }
    
    const swapResponse = await response.json();
    return swapResponse;
  } catch (error) {
    console.error('Error getting swap instructions:', error);
    throw error;
  }
}

/**
 * Execute a Jupiter swap directly
 * @param {string} fromToken - From token mint address
 * @param {string} toToken - To token mint address
 * @param {string} amount - Amount to swap (in lamports/smallest units)
 * @param {number} slippageBps - Slippage in basis points (1% = 100)
 * @param {Connection} connection - Solana connection
 * @param {Keypair} keypair - Wallet keypair
 * @returns {Promise<Object>} Swap result
 */
async function executeJupiterSwap(fromToken, toToken, amount, slippageBps, connection, keypair) {
  try {
    console.log(`Executing Jupiter swap from ${fromToken} to ${toToken} with amount ${amount}`);
    
    // Validate tokens against known valid tokens
    const knownTokens = [
      "So11111111111111111111111111111111111111112", // SOL
      "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", // USDC
      "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So", // mSOL
      "7dHbWXmci3dT8UFYWYZweBLXgycu7Y3iL6trKn1Y7ARj", // stSOL
      "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R", // RAY
      "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263", // BONK
      "jtojtomepa8beP8AuQc6eXt5FriJwTzQvMZZpFEQz8m", // JTO
      "HZ1JovNiVvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3", // PYTH
      "orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE", // ORCA
      "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB", // USDT
      "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm"  // WIF
    ];
    
    if (!knownTokens.includes(fromToken)) {
      console.warn(`Warning: fromToken ${fromToken} is not in the list of known tokens`);
    }
    
    if (!knownTokens.includes(toToken)) {
      console.warn(`Warning: toToken ${toToken} is not in the list of known tokens`);
    }
    
    // 1. Get a quote
    let quoteResponse;
    try {
      quoteResponse = await getJupiterQuote(fromToken, toToken, amount, slippageBps);
      console.log('Jupiter quote received:', {
        inputAmount: quoteResponse.inAmount,
        outputAmount: quoteResponse.outAmount,
        priceImpact: quoteResponse.priceImpactPct
      });
    } catch (quoteError) {
      console.error('Error getting Jupiter quote:', quoteError);
      
      // If we tried to swap a less common token, try with SOL instead
      if (!knownTokens.includes(toToken)) {
        console.log('Trying fallback swap to SOL instead...');
        return executeJupiterSwap(fromToken, "So11111111111111111111111111111111111111112", amount, slippageBps, connection, keypair);
      }
      
      return { success: false, error: quoteError.message };
    }
    
    // 2. Get swap instructions
    const publicKey = keypair.publicKey.toString();
    
    let swapInstructions;
    try {
      swapInstructions = await getJupiterSwapInstructions(quoteResponse, publicKey);
    } catch (swapInstructionsError) {
      console.error('Error getting swap instructions:', swapInstructionsError);
      return { success: false, error: swapInstructionsError.message };
    }
    
    // 3. Execute the swap
    // Jupiter returns a versioned transaction
    try {
      const serializedTransaction = Buffer.from(swapInstructions.swapTransaction, 'base64');
      const transaction = VersionedTransaction.deserialize(serializedTransaction);
      
      // Sign the transaction
      transaction.sign([keypair]);
      
      // Send the transaction
      const signature = await connection.sendRawTransaction(transaction.serialize());
      
      // Wait for confirmation with increased timeout (120 seconds)
      const confirmOptions = {
        commitment: 'confirmed',
        skipPreflight: true,
        maxRetries: 5
      };
      
      const confirmation = await connection.confirmTransaction(signature, confirmOptions);
      
      return { 
        txid: signature,
        success: !confirmation.value.err,
        fromAmount: quoteResponse.inAmount,
        toAmount: quoteResponse.outAmount
      };
    } catch (transactionError) {
      console.error('Error executing transaction:', transactionError);
      return { success: false, error: transactionError.message };
    }
  } catch (error) {
    console.error('Error executing Jupiter swap:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Get trending tokens data from Birdeye API
 * @param {Connection} connection - Solana connection
 * @param {string} apiKey - Birdeye API key
 * @returns {Promise<Object>} List of trending tokens
 */
async function getBirdeyeTrendingTokens(connection, apiKey) {
  try {
    console.log('Fetching trending tokens from Birdeye...');
    
    if (!apiKey) {
      console.error('Birdeye API key not found. Please set BIRDEYE_API_KEY in your .env file.');
      throw new Error('Missing Birdeye API key');
    }
    
    // Use the correct endpoint for trending tokens from Birdeye documentation
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10-second timeout
    
    try {
      const response = await fetch('https://public-api.birdeye.so/defi/token_trending?chain=solana', {
        method: 'GET',
        headers: {
          'X-API-KEY': apiKey,
          'Content-Type': 'application/json'
        },
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`Birdeye API error: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Add debug output to see the actual response structure
      console.log('Birdeye API response structure:', JSON.stringify(data, null, 2).substring(0, 500) + '...');
      
      // More flexible validation
      if (!data.success) {
        console.error('Birdeye API returned an unsuccessful response');
        throw new Error('Birdeye API returned unsuccessful response');
      }
      
      // Extract tokens data based on response structure
      let tokens = [];
      
      if (data.data && Array.isArray(data.data)) {
        tokens = data.data;
        console.log(`Found ${tokens.length} tokens in data array`);
      } else if (data.data && data.data.tokens && Array.isArray(data.data.tokens)) {
        tokens = data.data.tokens;
        console.log(`Found ${tokens.length} tokens in data.tokens array`);
      } else if (data.data && typeof data.data === 'object') {
        // Try to extract tokens from the data object
        const possibleTokenArrays = Object.values(data.data).filter(val => Array.isArray(val) && val.length > 0);
        if (possibleTokenArrays.length > 0) {
          // Use the largest array as the tokens array
          tokens = possibleTokenArrays.reduce((largest, arr) => arr.length > largest.length ? arr : largest, []);
          console.log(`Found ${tokens.length} tokens in a nested array property`);
        } else {
          console.error('Could not find tokens array in response');
          throw new Error('Invalid response format from Birdeye API');
        }
      } else {
        console.error('Could not find tokens data in response');
        throw new Error('Invalid response format from Birdeye API');
      }
      
      // Filter tokens and extract relevant information
      const solToken = { 
        address: "So11111111111111111111111111111111111111112", 
        symbol: "SOL", 
        name: "Solana" 
      };
      
      // Format the tokens properly
      const trendingTokens = tokens.map(token => ({
        address: token.address || token.mint || '', 
        symbol: token.symbol || token.name || '',
        name: token.name || token.symbol || '',
        marketCap: token.marketCap || token.mc || 0,
        price: token.price || 0,
        priceChange24h: token.priceChange || token.priceChange24h || 0,
        volume24h: token.volume24h || token.volume || 0
      }));
      
      // Filter out potential scam tokens and tokens with missing data
      const filteredTokens = trendingTokens.filter(token => {
        return token && 
          token.symbol && 
          token.address && 
          token.name &&
          token.symbol.length < 10 && // Avoid extremely long symbol names
          token.symbol !== token.address && // Filter out tokens where symbol is just the address
          !token.symbol.startsWith('0x') && // Filter out likely tokens with ETH address format 
          !token.symbol.includes(' ') && // Filter out likely fake tokens with spaces
          token.address !== solToken.address; // Exclude SOL from the list as we'll add it separately
      });
      
      // Always include SOL as a base currency option
      const finalTokens = [solToken, ...filteredTokens];
      
      // Log information about the discovered tokens
      console.log('🔍 Discovered trending tokens from Birdeye:');
      finalTokens.forEach((token, i) => {
        const priceChange = token.priceChange24h ? `(${token.priceChange24h > 0 ? '+' : ''}${token.priceChange24h.toFixed(2)}%)` : '';
        console.log(` ${i}. ${token.symbol} - ${token.name} ${priceChange}`);
      });
      
      // Prepare high-risk trading tokens - tokens with high 24h volatility but sufficient market cap
      const highRiskTokens = filteredTokens
        // Filter tokens with high price change (either positive or negative)
        .filter(token => token.priceChange24h && Math.abs(token.priceChange24h) > 10)
        // Sort by volatility (absolute price change)
        .sort((a, b) => Math.abs(b.priceChange24h) - Math.abs(a.priceChange24h))
        .slice(0, 5);
      
      if (highRiskTokens.length > 0) {
        console.log('🔥 High-risk trading opportunities:');
        highRiskTokens.forEach((token, i) => {
          console.log(` ${i}. ${token.symbol} - ${token.name} (${token.priceChange24h > 0 ? '+' : ''}${token.priceChange24h.toFixed(2)}%)`);
        });
      }
      
      return { 
        tokens: finalTokens,
        highRiskTokens: highRiskTokens
      };
    } catch (fetchError) {
      clearTimeout(timeoutId);
      if (fetchError.name === 'AbortError') {
        console.error('Birdeye API request timed out after 10 seconds');
        throw new Error('Birdeye API request timed out');
      }
      throw fetchError;
    }
  } catch (error) {
    console.error('Error fetching trending tokens from Birdeye:', error);
    // Fallback to Jupiter API if Birdeye fails
    console.log('Falling back to Jupiter API...');
    return getTrendingTokensFromJupiter(connection);
  }
}

/**
 * Fallback function to get tokens from Jupiter API
 * @param {Connection} connection - Solana connection
 * @returns {Promise<Object>} List of tokens
 */
async function getTrendingTokensFromJupiter(connection) {
  try {
    console.log('Discovering tokens from Jupiter API...');
    
    // Use Jupiter's V6 API endpoint for tokens
    const response = await fetch('https://quote-api.jup.ag/v6/tokens');
    
    if (!response.ok) {
      throw new Error(`Jupiter API error: ${response.status} ${response.statusText}`);
    }
    
    const allTokens = await response.json();
    console.log(`Analyzing ${allTokens.length} tokens from Jupiter API`);
    
    // Only SOL is needed as a base for swaps
    const solToken = { 
      address: "So11111111111111111111111111111111111111112", 
      symbol: "SOL", 
      name: "Solana" 
    };
    
    // Filter tokens with good metadata - focusing on discovering newer/interesting tokens
    const validTokens = allTokens.filter(token => {
      return token && 
        token.symbol && 
        token.address && 
        token.name &&
        token.symbol.length < 10 && // Avoid extremely long symbol names
        token.symbol !== token.address && // Filter out tokens where symbol is just the address
        !token.symbol.startsWith('0x') && // Filter out likely tokens with ETH address format 
        !token.symbol.includes(' ') && // Filter out likely fake tokens with spaces
        token.address !== solToken.address; // Exclude SOL from the list as we'll add it separately
    });
    
    console.log(`Found ${validTokens.length} tokens with valid metadata`);
    
    // Shuffle all tokens to make it more adventurous
    const shuffledTokens = [...validTokens].sort(() => 0.5 - Math.random());
    
    // Get a diverse set of tokens - let the agent be wild!
    const wildcardSelection = shuffledTokens.slice(0, 25);
    
    // Always include SOL as a base currency option, but keep the focus on discovered tokens
    const finalTokens = [solToken, ...wildcardSelection];
    
    // Format the tokens properly
    const formattedTokens = finalTokens.map(token => ({
      address: token.address,
      symbol: token.symbol,
      name: token.name || token.symbol
    }));
    
    // Log the discovered tokens
    console.log('🔍 Discovered tokens from Jupiter for potential trading:');
    formattedTokens.forEach((token, i) => {
      console.log(` ${i}. ${token.symbol} - ${token.name}`);
    });
    
    return { tokens: formattedTokens, highRiskTokens: [] };
  } catch (error) {
    console.error('Error discovering tokens from Jupiter:', error);
    // Fallback to just SOL for safety
    console.log('Falling back to SOL');
    return { 
      tokens: [
        { address: "So11111111111111111111111111111111111111112", symbol: "SOL", name: "Solana" }
      ],
      highRiskTokens: []
    };
  }
}

/**
 * Get top gainers data
 * @param {Connection} connection - Solana connection
 * @param {string} timeframe - Timeframe (e.g., "24h")
 * @returns {Promise<Object>} List of top gainer tokens
 */
async function getTopGainers(connection, timeframe = "24h") {
  try {
    console.log('Fetching top gainers...');
    
    // Use Jupiter's V6 API endpoint for tokens
    const response = await fetch('https://quote-api.jup.ag/v6/tokens');
    
    if (!response.ok) {
      throw new Error(`Jupiter API error: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    
    // Since Jupiter doesn't provide price change data, we'll use popular tokens
    // In production, you'd want to use a price API like CoinGecko
    console.log(`Got ${data.length} tokens from Jupiter API`);
    
    // Get some interesting tokens that are good for demonstration
    const interestingTokens = [
      // BONK
      data.find(t => t.symbol === "BONK") || 
        { address: "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263", symbol: "BONK", name: "Bonk" },
      // JTO
      data.find(t => t.symbol === "JTO") || 
        { address: "jtojtomepa8beP8AuQc6eXt5FriJwTzQvMZZpFEQz8m", symbol: "JTO", name: "Jito" },
      // RAY
      data.find(t => t.symbol === "RAY") || 
        { address: "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R", symbol: "RAY", name: "Raydium" },
      // ORCA
      data.find(t => t.symbol === "ORCA") || 
        { address: "orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE", symbol: "ORCA", name: "Orca" },
      // MSOL
      data.find(t => t.symbol === "mSOL") || 
        { address: "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So", symbol: "mSOL", name: "Marinade Staked SOL" }
    ].filter(Boolean);
    
    console.log('Interesting tokens:', interestingTokens.map(t => t.symbol).join(', '));
    
    return { tokens: interestingTokens };
  } catch (error) {
    console.error('Error getting top gainers:', error);
    // Fallback to a default set
    console.log('Falling back to default top gainers');
    return { 
      tokens: [
        { address: "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R", symbol: "RAY", name: "Raydium" },
        { address: "SLNDpmoWTVADgEdndyvWzroNL7zSi1dF9PC3xHGtPwp", symbol: "SLND", name: "Solend" },
        { address: "orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE", symbol: "ORCA", name: "Orca" },
        { address: "7i5KKsX2weiTkry7jA4ZwSuXGhs5eJBEjY8vVxR4pfRx", symbol: "GMT", name: "STEPN" }
      ]
    };
  }
}

/**
 * Get token price data
 * @param {string[]} tokens - Array of token mint addresses
 * @returns {Promise<Object>} Price data for requested tokens
 */
async function getTokenPriceData(tokens) {
  try {
    console.log('Fetching token price data...');
    
    // Jupiter doesn't have a direct price API, but we could use CoinGecko in production
    // For now, we'll use hardcoded prices as a fallback
    
    // Return fallback data
    console.log('Using default price data');
    
    const fallbackData = {};
    tokens.forEach(token => {
      // Sample prices based on market data as of today
      if (token === "So11111111111111111111111111111111111111112") {
        fallbackData[token] = { usd: 103.50 }; // SOL price
      } else if (token === "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v") {
        fallbackData[token] = { usd: 1.00 }; // USDC
      } else if (token === "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So") {
        fallbackData[token] = { usd: 108.75 }; // mSOL
      } else if (token === "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263") {
        fallbackData[token] = { usd: 0.00001954 }; // BONK
      } else if (token === "jtojtomepa8beP8AuQc6eXt5FriJwTzQvMZZpFEQz8m") {
        fallbackData[token] = { usd: 2.54 }; // JTO
      } else {
        fallbackData[token] = { usd: 1.00 }; // Default
      }
    });
    
    return fallbackData;
  } catch (error) {
    console.error('Error getting token price data:', error);
    // Return fallback data
    console.log('Falling back to default price data');
    
    const fallbackData = {};
    tokens.forEach(token => {
      fallbackData[token] = { usd: token === "So11111111111111111111111111111111111111112" ? 103.50 : 1.00 };
    });
    return fallbackData;
  }
}

/**
 * AutonomousTrader - Handles autonomous trading decisions for AI agents
 * Uses direct Jupiter API integration for Solana token swaps
 */
class AutonomousTrader {
  constructor(agentConfig) {
    this.config = agentConfig;
    this.agentId = agentConfig.id;
    this.walletAddress = agentConfig.solana_integration.wallet_address;
    
    // Try to get the private key with priority:
    // 1. Config file (not recommended but supported)
    // 2. Agent-specific environment variable (SOLANA_PRIVATE_KEY_AGENT_ID)
    // 3. Fallback to generic environment variable (SOLANA_PRIVATE_KEY)
    this.privateKey = agentConfig.solana_integration.private_key || 
      process.env[`SOLANA_PRIVATE_KEY_${this.agentId.toUpperCase().replace(/-/g, '_')}`] || 
      process.env.SOLANA_PRIVATE_KEY;
    
    // Get Birdeye API key
    this.birdeyeApiKey = process.env.BIRDEYE_API_KEY;
    
    // Sanitize the RPC URL
    this.networkRpc = sanitizeRpcUrl(
      agentConfig.solana_integration.rpc_url || process.env.RPC_URL
    );
    
    this.tradingBehavior = agentConfig.behavior.trading_behavior;
    this.tradingSafety = agentConfig.solana_integration.trade_safety;
    this.tradingEnabled = agentConfig.solana_integration.trading_enabled;
    this.autonomyRules = agentConfig.agent_kit_integration.autonomy_rules;
    this.lastTradeTimestamp = null;
    this.dailyTradeCount = 0;
    this.dailyTradeReset = null;
    this.connection = null;
    this.keypair = null;
    
    // Cache for trending tokens data
    this.cachedTrendingTokens = null;
    this.trendingTokensTimestamp = null;
    
    console.log(`AutonomousTrader initialized with RPC URL: ${this.networkRpc}`);
    
    // Initialize direct Solana connection and wallet
    this.initDirect();
  }

  /**
   * Initialize direct Solana connection and wallet
   */
  async initDirect() {
    try {
      if (!this.privateKey) {
        console.error(`Private key not found for agent ${this.agentId}. Please set either SOLANA_PRIVATE_KEY_${this.agentId.toUpperCase().replace(/-/g, '_')} or SOLANA_PRIVATE_KEY in your environment variables. Trading functionality disabled.`);
        this.tradingEnabled = false;
        return;
      }

      // Create a Solana keypair from the private key
      try {
        const privateKeyBuffer = Uint8Array.from(bs58.decode(this.privateKey));
        this.keypair = Keypair.fromSecretKey(privateKeyBuffer);
        
        // If the wallet address wasn't provided, set it from the keypair
        if (!this.walletAddress) {
          this.walletAddress = this.keypair.publicKey.toString();
        }
        
        console.log(`Created keypair for agent ${this.agentId} with public key: ${this.keypair.publicKey.toString()}`);
      } catch (keyError) {
        console.error(`Failed to create keypair for agent ${this.agentId}:`, keyError);
        this.tradingEnabled = false;
        return;
      }
      
      // Create Solana connection
      try {
        this.connection = new Connection(this.networkRpc, 'confirmed');
        const version = await this.connection.getVersion();
        console.log(`Connected to Solana ${version['solana-core']} at ${this.networkRpc}`);
        
        // Check wallet balance 
        const balance = await this.connection.getBalance(this.keypair.publicKey);
        console.log(`Wallet balance: ${balance / LAMPORTS_PER_SOL} SOL`);
        
        console.log(`Direct Solana connection established for agent ${this.agentId}`);
      } catch (connError) {
        console.error(`Error connecting to Solana for agent ${this.agentId}:`, connError);
        this.tradingEnabled = false;
        return;
      }

      console.log(`Direct Jupiter/Solana integration initialized for agent ${this.agentId} with wallet: ${this.walletAddress}`);
      
      // Prefetch trending tokens in the background to fill the cache
      if (this.tradingEnabled && this.birdeyeApiKey) {
        this.prefetchTrendingTokens()
          .catch(error => console.warn(`Error prefetching trending tokens: ${error.message}`));
      }
    } catch (error) {
      console.error(`Failed to initialize direct integration for agent ${this.agentId}:`, error);
      this.tradingEnabled = false;
    }
  }

  /**
   * Prefetch trending tokens to fill the cache
   */
  async prefetchTrendingTokens() {
    try {
      console.log(`Prefetching trending tokens for agent ${this.agentId}...`);
      const trendingTokens = await getBirdeyeTrendingTokens(this.connection, this.birdeyeApiKey);
      this.cachedTrendingTokens = trendingTokens;
      this.trendingTokensTimestamp = new Date();
      console.log(`Successfully cached trending tokens for agent ${this.agentId}`);
    } catch (error) {
      console.error(`Error prefetching trending tokens: ${error.message}`);
    }
  }

  /**
   * Check if a trade should be executed based on timing and probability
   * @returns {boolean} Whether a trade should be executed
   */
  shouldTrade() {
    if (!this.tradingEnabled) return false;
    
    // Check daily trade limit
    const now = new Date();
    
    // Reset daily counter if it's a new day
    if (!this.dailyTradeReset || now > this.dailyTradeReset) {
      this.dailyTradeCount = 0;
      this.dailyTradeReset = new Date(now);
      this.dailyTradeReset.setHours(23, 59, 59, 999); // End of current day
    }
    
    if (this.dailyTradeCount >= this.autonomyRules.max_daily_trades) {
      return false;
    }
    
    // Check if enough time has passed since last trade
    if (this.lastTradeTimestamp) {
      const hoursSinceLastTrade = (now - this.lastTradeTimestamp) / (1000 * 60 * 60);
      if (hoursSinceLastTrade < this.tradingBehavior.trading_frequency.min_hours_between_trades) {
        return false;
      }
    }
    
    // Random probability check
    if (Math.random() > this.tradingBehavior.trading_frequency.random_probability) {
      return false;
    }
    
    return true;
  }

  /**
   * Get wallet balance information using direct Solana connection
   * @returns {Promise<Object>} Wallet balance info
   */
  async getWalletBalance() {
    if (!this.connection || !this.keypair) {
      await this.initDirect();
    }
    
    if (this.connection && this.keypair) {
      try {
        const balance = await this.connection.getBalance(this.keypair.publicKey);
        
        // For a more complete solution, you would fetch token balances as well
        return { 
          sol: balance, 
          tokens: [] 
        };
      } catch (error) {
        console.error(`Error getting wallet balance for ${this.agentId}:`, error);
      }
    }
    
    return { sol: 0, tokens: [] };
  }

  /**
   * Get trending tokens data with caching
   * @returns {Promise<Object>} List of trending tokens and high-risk tokens
   */
  async getTrendingTokens() {
    if (!this.connection) {
      await this.initDirect();
    }
    
    // Check if we have cached data less than 10 minutes old
    const now = new Date();
    if (this.cachedTrendingTokens && this.trendingTokensTimestamp && 
        (now.getTime() - this.trendingTokensTimestamp.getTime() < 10 * 60 * 1000)) {
      console.log('Using cached trending tokens data');
      return this.cachedTrendingTokens;
    }
    
    // Fetch new data from Birdeye API
    const trendingTokens = await getBirdeyeTrendingTokens(this.connection, this.birdeyeApiKey);
    
    // Cache the results
    this.cachedTrendingTokens = trendingTokens;
    this.trendingTokensTimestamp = now;
    
    return trendingTokens;
  }

  /**
   * Get top gaining tokens
   * @param {string} timeframe - Timeframe for top gainers (e.g., "24h")
   * @returns {Promise<Array>} List of top gaining tokens
   */
  async getTopGainers(timeframe = "24h") {
    if (!this.connection) {
      await this.initDirect();
    }
    
    return getTopGainers(this.connection, timeframe);
  }

  /**
   * Get price data for tokens
   * @param {Array<string>} tokenMints - Array of token mint addresses
   * @returns {Promise<Object>} Price data for requested tokens
   */
  async getTokenPriceData(tokenMints) {
    return getTokenPriceData(tokenMints);
  }

  /**
   * Select a token to trade based on configured decision factors
   * @returns {Promise<Object>} Selected token information
   */
  async selectTokenToTrade() {
    const decisionFactors = this.tradingBehavior.trade_decision_factors;
    let possibleTokens = [];
    let highRiskTokens = [];
    
    try {
      // First check for trending tokens from Birdeye
      if (decisionFactors.includes("trending_tokens")) {
        const trending = await this.getTrendingTokens();
        if (trending && trending.tokens) {
          possibleTokens = [...possibleTokens, ...trending.tokens];
          
          // Add high-risk tokens to the selection
          if (trending.highRiskTokens && trending.highRiskTokens.length > 0) {
            highRiskTokens = trending.highRiskTokens;
          }
          
          // If we got valid trending data, don't call getTopGainers
          if (trending.tokens.length > 1) {  // More than just SOL
            console.log('Using trending tokens data for token selection');
          } else {
            // Only fallback to top gainers if trending tokens failed
            if (decisionFactors.includes("top_gainers")) {
              console.log('Falling back to top gainers due to insufficient trending data');
              const gainers = await this.getTopGainers("24h");
              if (gainers && gainers.tokens) {
                possibleTokens = [...possibleTokens, ...gainers.tokens];
              }
            }
          }
        } else {
          // Only fallback to top gainers if trending tokens failed
          if (decisionFactors.includes("top_gainers")) {
            console.log('Falling back to top gainers due to missing trending data');
            const gainers = await this.getTopGainers("24h");
            if (gainers && gainers.tokens) {
              possibleTokens = [...possibleTokens, ...gainers.tokens];
            }
          }
        }
      } else if (decisionFactors.includes("top_gainers")) {
        // Only if trending tokens is not included in decision factors
        console.log('Using top gainers as decision factor');
        const gainers = await this.getTopGainers("24h");
        if (gainers && gainers.tokens) {
          possibleTokens = [...possibleTokens, ...gainers.tokens];
        }
      }
    } catch (error) {
      console.error("Error getting token data:", error);
    }
    
    // If no tokens found, default to always tradable
    if (possibleTokens.length === 0) {
      // Get token info for always tradable tokens
      const SOL = {
        address: "So11111111111111111111111111111111111111112",
        symbol: "SOL",
        name: "Solana"
      };
      
      const USDC = {
        address: "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        symbol: "USDC",
        name: "USD Coin"
      };
      
      possibleTokens = [SOL, USDC];
    }
    
    // Filter out blacklisted tokens
    const blacklist = this.tradingBehavior.allowed_tokens.blacklist || [];
    possibleTokens = possibleTokens.filter(token => 
      !blacklist.includes(token.address)
    );
    
    // Sometimes choose a high-risk token for more exciting trades (20% chance)
    if (highRiskTokens.length > 0 && Math.random() < 0.2) {
      const randomHighRiskIndex = Math.floor(Math.random() * highRiskTokens.length);
      console.log('🎲 Selected a high-risk token for trading!');
      return highRiskTokens[randomHighRiskIndex];
    }
    
    // Otherwise random selection from the possible tokens
    const randomIndex = Math.floor(Math.random() * possibleTokens.length);
    return possibleTokens[randomIndex];
  }

  /**
   * Decide whether to buy or sell the selected token
   * @returns {string} "buy" or "sell"
   */
  decideTradeDirection() {
    // Simple 50/50 chance
    return Math.random() > 0.5 ? "buy" : "sell";
  }

  /**
   * Determine trade amount based on safety settings
   * @param {Object} balance - Wallet balance information
   * @returns {string} Amount to trade in lamports/smallest unit
   */
  determineTradeAmount(balance) {
    const maxAmount = this.tradingSafety.max_trade_amount_sol * 1e9; // Convert SOL to lamports
    const minWalletBalance = this.tradingSafety.min_wallet_balance_sol * 1e9;
    
    // Ensure we don't trade below minimum wallet balance
    const availableBalance = Math.max(0, balance.sol - minWalletBalance);
    
    // Calculate a random amount between 10% and 100% of max allowed amount
    const randomPercentage = 0.1 + (Math.random() * 0.9);
    const calculatedAmount = Math.min(
      availableBalance * 0.5, // Don't use more than 50% of available balance
      maxAmount * randomPercentage,
      this.autonomyRules.max_single_trade_amount_sol * 1e9 // Respect the autonomy rule limit
    );
    
    // Ensure we have a positive amount
    if (calculatedAmount <= 0) return "0";
    
    // Return as string (lamports)
    return Math.floor(calculatedAmount).toString();
  }

  /**
   * Execute a token swap using Jupiter API
   * @param {string} fromToken - From token mint address
   * @param {string} toToken - To token mint address
   * @param {string} amount - Amount to swap (in smallest units)
   * @param {number} slippage - Slippage in basis points (100 = 1%)
   * @returns {Promise<Object>} Swap result
   */
  async executeSwap(fromToken, toToken, amount, slippage) {
    if (!this.connection || !this.keypair) {
      await this.initDirect();
    }
    
    if (!this.connection || !this.keypair) {
      return { success: false, error: "Connection or keypair not available" };
    }
    
    try {
      return await executeJupiterSwap(
        fromToken,
        toToken,
        amount,
        slippage,
        this.connection,
        this.keypair
      );
    } catch (error) {
      console.error(`Error executing swap for ${this.agentId}:`, error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Generate a tweet about the trade using LLM to match agent's personality
   * @param {Object} tradeInfo - Information about the executed trade
   * @returns {Promise<string>} Tweet text about the trade
   */
  async generateTradeTweet(tradeInfo) {
    const { tokenIn, tokenOut, direction, success, amount } = tradeInfo;
    
    try {
      // If OpenAI is available, use it to generate a tweet
      const { OpenAI } = require('openai');
      
      // Initialize OpenAI client
      const openai = new OpenAI({
        apiKey: process.env.OPENAI_API_KEY
      });
      
      if (!openai || !process.env.OPENAI_API_KEY) {
        console.log('OpenAI API not available, falling back to simpler tweet generation');
        return this._generateSimpleTweet(tradeInfo);
      }
      
      // Prepare the context for the LLM
      const tradeAmount = parseInt(amount) / 1e9; // Convert lamports to SOL
      
      const fromTokenSymbol = tokenIn.symbol;
      const toTokenSymbol = tokenOut.symbol;
      
      // Create a context-aware prompt that doesn't focus on the transaction details
      const systemPrompt = this.config.custom_system_prompt || 
        `You are ${this.config.name}, ${this.config.description}. Generate a casual tweet that mentions ${direction === 'buy' ? toTokenSymbol : fromTokenSymbol} in some way.`;
      
      // Create context but make it less transaction-focused
      let tweetContext = '';
      
      if (success) {
        if (direction === 'buy') {
          tweetContext = `You've been thinking about ${toTokenSymbol} lately. Maybe you bought some, maybe you're just interested in it. Generate a casual tweet that mentions ${toTokenSymbol} in some authentic, non-formal way.`;
        } else {
          tweetContext = `You've been looking at ${fromTokenSymbol} recently. Maybe you sold some, maybe you're just paying attention to it. Generate a casual tweet that mentions ${fromTokenSymbol} in some authentic, non-formal way.`;
        }
      } else {
        // For failed transactions, just mention the token casually
        const tokenSymbol = direction === 'buy' ? toTokenSymbol : fromTokenSymbol;
        tweetContext = `You're curious about ${tokenSymbol}. Generate a casual tweet that mentions ${tokenSymbol} in some way.`;
      }
      
      // Additional style instructions based on agent config
      let styleInstructions = '';
      
      if (this.config.style_guide) {
        const style = this.config.style_guide;
        
        // Extract styling information
        if (style.formatting && style.formatting.capitalization) {
          styleInstructions += `- ${style.formatting.capitalization}\n`;
        }
        
        if (style.voice) {
          styleInstructions += `- Voice: ${style.voice}\n`;
        }
        
        if (style.tone) {
          styleInstructions += `- Tone: ${style.tone}\n`;
        }
        
        // Emoji usage
        if (style.formatting && style.formatting.uses_emojis) {
          styleInstructions += `- Emoji usage: ${style.formatting.emoji_frequency}\n`;
        }
        
        // Hashtag usage
        if (style.formatting && style.formatting.uses_hashtags) {
          styleInstructions += `- Hashtag style: ${style.formatting.hashtag_style}\n`;
        }
        
        // Topics to avoid
        if (style.topics_to_avoid && style.topics_to_avoid.length > 0) {
          styleInstructions += `- Avoid these topics: ${style.topics_to_avoid.join(', ')}\n`;
        }
      }
      
      // User message with the context and request
      const userMessage = `${tweetContext}

IMPORTANT STYLE GUIDELINES:
${styleInstructions}
- Keep it casual, authentic, and sounding like a real person (preferably under 100 characters)
- Avoid making it sound like an announcement about buying or selling
- Avoid stock phrases like "just bought X" or "transaction failed"
- Don't give financial advice or suggest others should trade the same way
- Make it sound like a genuine thought, the way a real person might tweet
- Be original - avoid using templates or common trading phrases
- Maximum tweet length: 280 characters

Write a tweet that casually mentions ${direction === 'buy' ? toTokenSymbol : fromTokenSymbol} while feeling natural and authentic:`;
      
      console.log('Generating authentic tweet for agent:', this.agentId);
      
      // Make the API call
      const response = await openai.chat.completions.create({
        model: process.env.OPENAI_MODEL || 'gpt-4-turbo',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userMessage }
        ],
        max_tokens: 100,
        temperature: 0.9 // Higher temperature for more creativity
      });
      
      // Extract the tweet from the response
      let tweet = response.choices[0].message.content.trim();
      
      // Remove any prefixes that might have been added
      tweet = tweet
        .replace(/^(TWEET|Tweet|tweet):/, '')
        .replace(/^["']|["']$/g, '') // Remove quotes if present
        .trim();
      
      console.log('Generated tweet:', tweet);
      return tweet;
    } catch (error) {
      console.error('Error generating tweet with LLM:', error);
      // Fall back to simpler tweet generation
      console.log('Falling back to simple tweet generation');
      return this._generateSimpleTweet(tradeInfo);
    }
  }

  /**
   * Fallback method to generate simple tweets
   * @param {Object} tradeInfo - Information about the executed trade
   * @returns {string} Tweet text about the token
   * @private
   */
  _generateSimpleTweet(tradeInfo) {
    const { tokenIn, tokenOut, direction, success } = tradeInfo;
    
    // Choose which token to focus on
    const tokenSymbol = direction === 'buy' ? tokenOut.symbol : tokenIn.symbol;
    
    try {
      // Try to use a model call tailored to the agent's character
      const { OpenAI } = require('openai');
      
      // Try to initialize OpenAI with a simple client
      const openai = new OpenAI({
        apiKey: process.env.OPENAI_API_KEY
      });
      
      // Get agent's custom system prompt or use a default
      const agentSystemPrompt = this.config.custom_system_prompt || 
        `You are ${this.config.name}, a casual crypto enthusiast who sometimes trades on Solana.`;
        
      // Get agent's style guide if available
      let styleGuide = "";
      if (this.config.style_guide) {
        const style = this.config.style_guide;
        
        if (style.tone) {
          styleGuide += `- Tone: ${style.tone}\n`;
        }
        
        if (style.voice) {
          styleGuide += `- Voice: ${style.voice}\n`;
        }
        
        if (style.formatting && style.formatting.capitalization) {
          styleGuide += `- Capitalization: ${style.formatting.capitalization}\n`;
        }
        
        if (style.formatting && style.formatting.emoji_frequency) {
          styleGuide += `- Emoji usage: ${style.formatting.emoji_frequency}\n`;
        }
      }
      
      // Create a tailored prompt based on trade action
      let promptContext = '';
      if (direction === 'buy') {
        promptContext = `You just bought some ${tokenSymbol} tokens. You're not trying to shill it, just casually mentioning it in a laid-back way. It's just something you did, no big deal.`;
      } else {
        promptContext = `You just sold some ${tokenSymbol} tokens. Not for any dramatic reason, just a casual trade you decided to make.`;
      }
      
      if (!success) {
        promptContext = `You've been thinking about ${tokenSymbol} lately, but your transaction didn't go through. No big deal though.`;
      }
      
      // Create the user prompt
      const userPrompt = `${promptContext}

Write a very casual, laid-back tweet that subtly mentions your interaction with ${tokenSymbol}, but doesn't sound like an announcement or financial advice. Keep it under 100 characters if possible, and make it sound like a passing thought.

${styleGuide ? `STYLE GUIDELINES:\n${styleGuide}` : ''}
- Don't use phrases like "just bought" or "just sold" or "just traded"
- Don't give financial advice
- Don't use hashtags like #crypto or #trading
- Keep it personal and genuine
- Sound like a real person, not a bot
- Be subtle about the fact that you traded this token`;
      
      // Make a simple API call with the tailored prompt
      console.log('Using character-aligned fallback for tweet generation');
      
      // Use an async IIFE to handle the async call
      return (async () => {
        try {
          const response = await openai.chat.completions.create({
            model: 'gpt-3.5-turbo', // Use a more capable but still economical model
            messages: [
              { role: 'system', content: agentSystemPrompt },
              { role: 'user', content: userPrompt }
            ],
            max_tokens: 60,
            temperature: 0.9
          });
          
          let tweet = response.choices[0].message.content.trim();
          tweet = tweet.replace(/^["']|["']$/g, ''); // Remove quotes if present
          console.log('Generated character-aligned fallback tweet:', tweet);
          return tweet;
        } catch (fallbackError) {
          console.error('Error in character-aligned fallback tweet generation:', fallbackError);
          
          // As a last resort, create a simple non-templated message that hints at trading
          const randomPhrases = [
            `got some ${tokenSymbol} in my wallet now...`,
            `${tokenSymbol} looking interesting today`,
            `kinda like what ${tokenSymbol} is doing lately`,
            `${tokenSymbol} might be worth watching`,
            `been messing with ${tokenSymbol} a bit`,
            `${tokenSymbol} caught my attention today`
          ];
          
          const randomPhrase = randomPhrases[Math.floor(Math.random() * randomPhrases.length)];
          return randomPhrase;
        }
      })();
    } catch (error) {
      console.error('Error in tweet fallback:', error);
      // Absolute last resort
      return `${tokenSymbol} on my mind...`;
    }
  }

  /**
   * Execute a complete trading cycle - decision, execution, and tweet generation
   * @returns {Promise<Object>} Trade result including tweet text
   */
  async executeTradeAndGenerateTweet() {
    if (!this.shouldTrade()) {
      return { executed: false, reason: "Trading conditions not met" };
    }
    
    try {
      // Get wallet balance
      const balance = await this.getWalletBalance();
      
      // Select token to trade
      const selectedToken = await this.selectTokenToTrade();
      
      // Decide direction (buy/sell)
      const direction = this.decideTradeDirection();
      
      // Determine from/to tokens based on direction
      let fromToken, toToken;
      if (direction === "buy") {
        // When buying, we use SOL to purchase the selected token
        fromToken = {
          address: "So11111111111111111111111111111111111111112",
          symbol: "SOL",
          name: "Solana"
        };
        toToken = selectedToken;
      } else {
        // When selling, we sell the selected token for SOL
        fromToken = selectedToken;
        toToken = {
          address: "So11111111111111111111111111111111111111112",
          symbol: "SOL",
          name: "Solana"
        };
      }
      
      // Determine amount
      const amount = this.determineTradeAmount(balance);
      
      // Execute the swap
      const swapResult = await this.executeSwap(
        fromToken.address,
        toToken.address,
        amount,
        this.tradingSafety.max_slippage_percent * 100 // Convert percent to basis points
      );
      
      // Generate tweet text
      const tradeInfo = {
        tokenIn: fromToken,
        tokenOut: toToken,
        direction,
        amount,
        success: swapResult.success !== false
      };
      
      const tweetText = await this.generateTradeTweet(tradeInfo);
      
      // Update trade tracking if successful
      if (swapResult.success) {
        this.lastTradeTimestamp = new Date();
        this.dailyTradeCount++;
      }
      
      return {
        executed: true,
        success: swapResult.success !== false,
        transaction: swapResult.txid || null,
        tweet: tweetText,
        tradeInfo
      };
    } catch (error) {
      console.error("Error in trade execution:", error);
      
      // Generate an error-related tweet using the model instead of a hardcoded message
      try {
        // Create a simple token object for SOL (default fallback)
        const solToken = {
          address: "So11111111111111111111111111111111111111112",
          symbol: "SOL",
          name: "Solana"
        };
        
        // Generate a natural tweet about crypto/trading without mentioning the error
        const errorTradeInfo = {
          tokenIn: solToken,
          tokenOut: solToken,
          direction: 'buy', // Default
          amount: '0',
          success: false
        };
        
        // Use our existing tweet generator with error context
        const errorTweet = await this.generateTradeTweet(errorTradeInfo);
        
        return {
          executed: false,
          success: false,
          error: error.message,
          tweet: errorTweet
        };
      } catch (tweetError) {
        console.error("Error generating error tweet:", tweetError);
        
        // Absolute last resort - generate a simple message
        return {
          executed: false,
          success: false,
          error: error.message,
          tweet: "thoughts on crypto today? curious what everyone is watching."
        };
      }
    }
  }
}

module.exports = AutonomousTrader; 