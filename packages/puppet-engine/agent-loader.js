const path = require('path');
const fs = require('fs').promises;
const TraderIntegration = require('./trader-integration');

/**
 * AgentLoader - Loads and initializes AI agents with trading capabilities
 */
class AgentLoader {
  constructor(agentsDirectoryPath = null) {
    this.agentsDirectoryPath = agentsDirectoryPath || path.join(process.cwd(), 'config', 'agents');
    this.loadedAgents = {};
    this.traderIntegrations = {};
    
    console.log(`AgentLoader initialized with directory: ${this.agentsDirectoryPath}`);
  }

  /**
   * Load all agents from the config directory
   * @returns {Promise<Object>} Loaded agents
   */
  async loadAllAgents() {
    try {
      console.log(`Loading agents from ${this.agentsDirectoryPath}`);
      
      let files;
      try {
        files = await fs.readdir(this.agentsDirectoryPath);
      } catch (err) {
        console.log(`Directory not found or empty. Creating directory: ${this.agentsDirectoryPath}`);
        // Create the directory if it doesn't exist
        await fs.mkdir(this.agentsDirectoryPath, { recursive: true });
        files = [];
      }
      
      const agentFiles = files.filter(file => file.endsWith('.json'));
      console.log(`Found ${agentFiles.length} agent configuration files`);
      
      for (const file of agentFiles) {
        const agentId = file.replace('.json', '');
        await this.loadAgent(agentId);
      }
      
      return this.loadedAgents;
    } catch (error) {
      console.error('Error loading agents:', error);
      return {};
    }
  }

  /**
   * Load a specific agent by ID
   * @param {string} agentId - ID of the agent to load
   * @returns {Promise<Object>} Loaded agent
   */
  async loadAgent(agentId) {
    try {
      console.log(`Loading agent: ${agentId}`);
      
      const agentPath = path.join(this.agentsDirectoryPath, `${agentId}.json`);
      
      let agentConfig;
      try {
        const agentData = await fs.readFile(agentPath, 'utf-8');
        agentConfig = JSON.parse(agentData);
      } catch (err) {
        console.log(`Agent file not found or invalid. For testing, creating a placeholder for ${agentId}`);
        // For testing, create a minimal agent config if file doesn't exist
        agentConfig = {
          id: agentId,
          name: `Test ${agentId}`,
          description: "Test agent for development",
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
      }
      
      this.loadedAgents[agentId] = {
        id: agentId,
        config: agentConfig,
        instance: null
      };
      
      console.log(`Agent ${agentId} loaded successfully`);
      return this.loadedAgents[agentId];
    } catch (error) {
      console.error(`Error loading agent ${agentId}:`, error);
      return null;
    }
  }

  /**
   * Initialize an agent instance with a puppet engine
   * @param {string} agentId - ID of the agent to initialize
   * @param {Object} puppetEngine - Puppet Engine instance
   * @returns {Promise<Object>} Initialized agent
   */
  async initializeAgent(agentId, puppetEngine) {
    if (!this.loadedAgents[agentId]) {
      console.log(`Agent ${agentId} not loaded yet. Loading now.`);
      await this.loadAgent(agentId);
    }
    
    if (!this.loadedAgents[agentId]) {
      console.error(`Agent ${agentId} not found`);
      return null;
    }
    
    try {
      const agentConfig = this.loadedAgents[agentId].config;
      
      console.log(`Initializing agent ${agentId} with Puppet Engine`);
      // Initialize the agent with puppet engine
      const agentInstance = await puppetEngine.createAgent(agentConfig);
      
      this.loadedAgents[agentId].instance = agentInstance;
      
      // Check if this agent has trading capabilities
      if (agentConfig.solana_integration && agentConfig.solana_integration.trading_enabled) {
        console.log(`Agent ${agentId} has trading capabilities. Initializing trading.`);
        await this.initializeTrading(agentId, agentInstance);
      } else {
        console.log(`Agent ${agentId} does not have trading enabled.`);
      }
      
      return agentInstance;
    } catch (error) {
      console.error(`Error initializing agent ${agentId}:`, error);
      return null;
    }
  }

  /**
   * Initialize trading functionality for an agent
   * @param {string} agentId - ID of the agent
   * @param {Object} agentInstance - Agent instance
   * @returns {Promise<Object>} Trader integration
   */
  async initializeTrading(agentId, agentInstance) {
    try {
      console.log(`Initializing trading for agent ${agentId}`);
      
      // Create trader integration
      const traderIntegration = new TraderIntegration(agentId);
      
      // Register with the agent
      const result = await traderIntegration.registerWithAgent(agentInstance);
      
      if (!result.success) {
        console.error(`Failed to register trader with agent ${agentId}:`, result.error);
        return null;
      }
      
      // Store for reference
      this.traderIntegrations[agentId] = traderIntegration;
      
      console.log(`Trading functionality initialized for agent ${agentId}`);
      return traderIntegration;
    } catch (error) {
      console.error(`Error initializing trading for agent ${agentId}:`, error);
      return null;
    }
  }

  /**
   * Get a trader integration for an agent
   * @param {string} agentId - ID of the agent
   * @returns {Object} Trader integration
   */
  getTraderIntegration(agentId) {
    return this.traderIntegrations[agentId] || null;
  }

  /**
   * Update an agent's configuration
   * @param {string} agentId - ID of the agent to update
   * @param {Object} updatedConfig - Updated configuration
   * @returns {Promise<boolean>} Whether update was successful
   */
  async updateAgentConfig(agentId, updatedConfig) {
    try {
      const agentPath = path.join(this.agentsDirectoryPath, `${agentId}.json`);
      
      // Write updated config to file
      await fs.writeFile(agentPath, JSON.stringify(updatedConfig, null, 2), 'utf-8');
      
      // Update in memory
      if (this.loadedAgents[agentId]) {
        this.loadedAgents[agentId].config = updatedConfig;
      }
      
      // Handle trading integration update if needed
      if (updatedConfig.solana_integration && 
          this.traderIntegrations[agentId] && 
          this.loadedAgents[agentId].instance) {
        
        // Reinitialize trading if configuration changed
        await this.initializeTrading(agentId, this.loadedAgents[agentId].instance);
      }
      
      return true;
    } catch (error) {
      console.error(`Error updating agent config ${agentId}:`, error);
      return false;
    }
  }
}

module.exports = AgentLoader; 