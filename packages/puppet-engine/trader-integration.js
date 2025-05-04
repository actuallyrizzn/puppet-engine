const path = require('path');
const fs = require('fs').promises;
const AutonomousTrader = require('../trading/autonomous-trader');

/**
 * TraderIntegration - Connects the autonomous trading functionality with the Puppet Engine
 * Handles agent config loading, trading scheduling, and tweet posting
 */
class TraderIntegration {
  constructor(agentId, agentConfigPath = null) {
    this.agentId = agentId;
    this.agentConfigPath = agentConfigPath || path.join(process.cwd(), 'config', 'agents', `${agentId}.json`);
    this.trader = null;
    this.twitterClient = null;
    this.initialized = false;
    this.checkInterval = null;
    this.lastCheckTimestamp = null;
    
    console.log(`TraderIntegration created for agent: ${agentId}`);
  }

  /**
   * Initialize the trader integration
   * @param {Object} twitterClient - Twitter client for posting tweets
   * @returns {Promise<boolean>} Whether initialization was successful
   */
  async init(twitterClient = null) {
    try {
      console.log(`Initializing trader integration for ${this.agentId}`);
      
      // Load agent config
      const agentConfig = await this.loadAgentConfig();
      
      if (!agentConfig) {
        console.error(`Failed to load agent config for ${this.agentId}`);
        return false;
      }
      
      // Check if trading is enabled for this agent
      if (!agentConfig.solana_integration || !agentConfig.solana_integration.trading_enabled) {
        console.log(`Trading is not enabled for agent ${this.agentId}`);
        return false;
      }
      
      // Initialize the trader
      console.log(`Creating AutonomousTrader for ${this.agentId}`);
      this.trader = new AutonomousTrader(agentConfig);
      this.twitterClient = twitterClient;
      this.initialized = true;
      
      console.log(`Trader integration initialized for agent ${this.agentId}`);
      return true;
    } catch (error) {
      console.error(`Failed to initialize trader integration for ${this.agentId}:`, error);
      return false;
    }
  }

  /**
   * Load the agent configuration
   * @returns {Promise<Object>} Agent configuration
   */
  async loadAgentConfig() {
    try {
      console.log(`Loading agent config from: ${this.agentConfigPath}`);
      
      let configData;
      try {
        configData = await fs.readFile(this.agentConfigPath, 'utf-8');
      } catch (err) {
        console.log(`Agent config file not found: ${this.agentConfigPath}`);
        console.log('Creating a minimal config for testing');
        
        // Create a minimal config for testing
        const testConfig = {
          id: this.agentId,
          name: `Test ${this.agentId}`,
          description: "Test agent for trading integration",
          solana_integration: {
            wallet_address: "",
            private_key: "", 
            network: "mainnet-beta",
            rpc_url: "https://api.mainnet-beta.solana.com",
            trade_safety: {
              max_trade_amount_sol: 0.1,
              min_wallet_balance_sol: 0.05,
              max_slippage_percent: 1.0
            },
            trading_enabled: true
          },
          behavior: {
            trading_behavior: {
              trading_frequency: {
                min_hours_between_trades: 12,
                max_hours_between_trades: 72,
                random_probability: 0.15
              },
              trade_decision_factors: ["trending_tokens", "top_gainers", "random_selection", "mood"],
              trade_tweet_probability: 1.0,
              allowed_tokens: {
                always_tradable: [
                  "So11111111111111111111111111111111111111112",
                  "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
                ],
                consider_trending: true,
                blacklist: []
              }
            }
          },
          agent_kit_integration: {
            enabled: true,
            methods: {
              allowed: ["getTokenInfo", "getTrendingTokens", "getTopGainers", "swapTokens", "getTokenPriceData", "getWalletBalance"],
              autonomous_only: ["swapTokens"] 
            },
            autonomy_rules: {
              ignore_human_trading_requests: true,
              max_daily_trades: 3,
              max_single_trade_amount_sol: 0.1,
              require_trending_validation: true
            }
          }
        };
        
        // Ensure the directory exists
        const dirPath = path.dirname(this.agentConfigPath);
        await fs.mkdir(dirPath, { recursive: true });
        
        // Save the test config
        await fs.writeFile(this.agentConfigPath, JSON.stringify(testConfig, null, 2), 'utf-8');
        
        return testConfig;
      }
      
      return JSON.parse(configData);
    } catch (error) {
      console.error(`Error loading agent config for ${this.agentId}:`, error);
      return null;
    }
  }

  /**
   * Post a tweet using the Twitter client
   * @param {string} tweetText - Text to post
   * @returns {Promise<Object>} Tweet result
   */
  async postTweet(tweetText) {
    if (!this.twitterClient) {
      console.error('Twitter client not available for posting');
      return { success: false, error: 'Twitter client not available' };
    }
    
    try {
      console.log(`Posting tweet for ${this.agentId}: ${tweetText}`);
      
      // Post using the Twitter client
      const result = await this.twitterClient.tweet(tweetText);
      console.log(`Tweet posted for ${this.agentId}, id: ${result.id}`);
      return { success: true, tweetId: result.id };
    } catch (error) {
      console.error(`Failed to post tweet for ${this.agentId}:`, error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Start periodic trading check
   * @param {number} checkIntervalMinutes - Interval in minutes between checks
   * @returns {void}
   */
  startTradingChecks(checkIntervalMinutes = 5) {
    if (!this.initialized) {
      console.error(`Cannot start trading checks for ${this.agentId}: Not initialized`);
      return;
    }
    
    // Clear any existing interval
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
    }
    
    const intervalMs = checkIntervalMinutes * 60 * 1000;
    
    console.log(`Starting trading checks for ${this.agentId} every ${checkIntervalMinutes} minutes`);
    
    this.checkInterval = setInterval(async () => {
      await this.checkAndExecuteTrade();
    }, intervalMs);
    
    console.log(`Started trading checks for ${this.agentId} (every ${checkIntervalMinutes} minutes)`);
  }

  /**
   * Stop periodic trading checks
   * @returns {void}
   */
  stopTradingChecks() {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
      console.log(`Stopped trading checks for ${this.agentId}`);
    }
  }

  /**
   * Check if a trade should be executed and handle it
   * @returns {Promise<Object>} Trade result
   */
  async checkAndExecuteTrade() {
    if (!this.initialized || !this.trader) {
      return { success: false, error: 'Trader not initialized' };
    }
    
    try {
      console.log(`Checking for trading opportunities for ${this.agentId}`);
      this.lastCheckTimestamp = new Date();
      
      // Execute trade and generate tweet
      const tradeResult = await this.trader.executeTradeAndGenerateTweet();
      
      // If a trade was executed, post about it
      if (tradeResult.executed && tradeResult.tweet) {
        console.log(`Trade executed for ${this.agentId}, posting tweet`);
        await this.postTweet(tradeResult.tweet);
      } else {
        console.log(`No trade executed for ${this.agentId}: ${tradeResult.reason || 'Unknown reason'}`);
      }
      
      return tradeResult;
    } catch (error) {
      console.error(`Error checking and executing trade for ${this.agentId}:`, error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Get the current trading status
   * @returns {Promise<Object>} Trading status
   */
  async getStatus() {
    if (!this.initialized || !this.trader) {
      return { 
        initialized: false,
        trading_enabled: false 
      };
    }
    
    try {
      console.log(`Getting status for ${this.agentId}`);
      const walletBalance = await this.trader.getWalletBalance();
      
      return {
        initialized: this.initialized,
        trading_enabled: this.trader.tradingEnabled,
        wallet_address: this.trader.walletAddress,
        balance: walletBalance,
        last_check: this.lastCheckTimestamp,
        daily_trade_count: this.trader.dailyTradeCount,
        last_trade: this.trader.lastTradeTimestamp
      };
    } catch (error) {
      console.error(`Error getting trader status for ${this.agentId}:`, error);
      return { 
        initialized: this.initialized,
        trading_enabled: this.trader.tradingEnabled,
        error: error.message
      };
    }
  }

  /**
   * Register trading functionality with a Puppet Engine agent
   * @param {Object} agentInstance - Puppet Engine agent instance
   * @returns {Promise<Object>} Registration result
   */
  async registerWithAgent(agentInstance) {
    if (!agentInstance) {
      return { success: false, error: 'Invalid agent instance' };
    }
    
    try {
      console.log(`Registering trader with agent ${this.agentId}`);
      
      // Initialize with the agent's Twitter client
      const success = await this.init(agentInstance.twitterClient);
      
      if (!success) {
        return { success: false, error: 'Failed to initialize trader integration' };
      }
      
      // Start regular trading checks
      this.startTradingChecks(10); // Check every 10 minutes
      
      // Attach the trader to the agent instance for potential direct access
      agentInstance.trader = this;
      
      console.log(`Successfully registered trader with agent ${this.agentId}`);
      return { success: true };
    } catch (error) {
      console.error(`Error registering trader with agent ${this.agentId}:`, error);
      return { success: false, error: error.message };
    }
  }
}

module.exports = TraderIntegration; 