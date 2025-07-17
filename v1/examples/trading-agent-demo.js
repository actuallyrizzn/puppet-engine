const AgentLoader = require('../packages/puppet-engine/agent-loader');
const PuppetEngine = require('../packages/puppet-engine/puppet-engine');
require('dotenv').config();

/**
 * Trading Agent Demo
 * 
 * This script demonstrates how to initialize an AI agent with Solana trading capabilities.
 * The agent can autonomously make trading decisions and post about them on Twitter.
 */
async function runTradingAgentDemo() {
  try {
    console.log("Starting Trading Agent Demo...");
    
    // Check for required environment variables
    if (!process.env.SOLANA_PRIVATE_KEY) {
      console.error('Missing required environment variable: SOLANA_PRIVATE_KEY');
      console.log('Please update your .env file with the necessary Solana credentials.');
      return;
    }
    
    if (!process.env.OPENAI_API_KEY) {
      console.error('Missing OpenAI API key. Please set OPENAI_API_KEY in your .env file.');
      return;
    }
    
    // Initialize Puppet Engine
    const puppetEngine = new PuppetEngine({
      apiKey: process.env.OPENAI_API_KEY,
      // Add any other needed configurations
    });
    console.log('PuppetEngine initialized');
    
    // Load agents
    const agentLoader = new AgentLoader();
    
    // Load and initialize Claudia agent
    const claudiaAgentId = 'claudia-agent';
    console.log(`Loading agent: ${claudiaAgentId}`);
    await agentLoader.loadAgent(claudiaAgentId);
    
    console.log(`Initializing agent: ${claudiaAgentId}`);
    const claudiaInstance = await agentLoader.initializeAgent(claudiaAgentId, puppetEngine);
    
    if (!claudiaInstance) {
      console.error('Failed to initialize Claudia agent');
      return;
    }
    
    console.log('Claudia agent initialized successfully');
    
    // Get the trader integration
    const traderIntegration = agentLoader.getTraderIntegration(claudiaAgentId);
    
    if (!traderIntegration) {
      console.log('Claudia agent does not have trading integration enabled');
      return;
    }
    
    console.log('Trader integration found for Claudia agent');
    
    // Get current status
    const status = await traderIntegration.getStatus();
    console.log('Trader status:', status);
    
    // Display configured trade safety parameters
    if (status.initialized) {
      console.log('\nTrade Safety Parameters:');
      if (traderIntegration.trader && traderIntegration.trader.tradingSafety) {
        console.log('- Max trade amount: ', traderIntegration.trader.tradingSafety.max_trade_amount_sol || 'N/A', 'SOL');
        console.log('- Min wallet balance: ', traderIntegration.trader.tradingSafety.min_wallet_balance_sol || 'N/A', 'SOL');
        console.log('- Max slippage: ', traderIntegration.trader.tradingSafety.max_slippage_percent || 'N/A', '%');
        console.log('- Max daily trades: ', traderIntegration.trader.autonomyRules?.max_daily_trades || 'N/A');
        
        console.log('\nAllowed Trade Decision Factors:');
        if (traderIntegration.trader.tradingBehavior?.trade_decision_factors) {
          const factors = traderIntegration.trader.tradingBehavior.trade_decision_factors;
          factors.forEach(factor => console.log(`- ${factor}`));
        } else {
          console.log('No trade decision factors configured');
        }
      } else {
        console.log('Trade safety parameters not available');
      }
    }
    
    // Force a trading check for demo purposes
    console.log('\nChecking for trading opportunity...');
    const tradeResult = await traderIntegration.checkAndExecuteTrade();
    
    if (tradeResult.executed) {
      console.log('Trade executed!');
      console.log('Transaction:', tradeResult.transaction || 'No transaction ID available');
      console.log('Tweet:', tradeResult.tweet || 'No tweet generated');
      
      if (tradeResult.tradeInfo) {
        console.log('\nTrade Details:');
        console.log('From token:', tradeResult.tradeInfo.tokenIn?.symbol || 'Unknown');
        console.log('To token:', tradeResult.tradeInfo.tokenOut?.symbol || 'Unknown');
        console.log('Direction:', tradeResult.tradeInfo.direction || 'Unknown');
        console.log('Amount (lamports):', tradeResult.tradeInfo.amount || 'Unknown');
      }
    } else {
      console.log('No trade executed:', tradeResult.reason || 'Trading conditions not met');
    }
    
    // Create a second agent with a different wallet
    const secondAgentId = 'test-agent';
    console.log(`\nLoading second agent: ${secondAgentId}`);
    await agentLoader.loadAgent(secondAgentId);
    
    console.log(`Initializing second agent: ${secondAgentId}`);
    const secondAgentInstance = await agentLoader.initializeAgent(secondAgentId, puppetEngine);
    
    if (secondAgentInstance) {
      console.log('Second agent initialized successfully');
      
      // Get the trader integration for the second agent
      const secondTraderIntegration = agentLoader.getTraderIntegration(secondAgentId);
      
      if (secondTraderIntegration) {
        console.log('Trader integration found for second agent');
        
        // Get current status
        const secondStatus = await secondTraderIntegration.getStatus();
        console.log('Second agent trader status:', secondStatus);
      } else {
        console.log('Second agent does not have trading integration enabled');
      }
    } else {
      console.log('Failed to initialize second agent');
    }
    
    console.log('\nDemo completed. In a real scenario, agents would run continuously checking for trading opportunities.');
    console.log('To run continuously, start your application and the trading checks will happen automatically at the configured intervals.');
  } catch (error) {
    console.error('Error in trading agent demo:', error);
  }
}

// Run the demo if this script is executed directly
if (require.main === module) {
  runTradingAgentDemo()
    .then(() => {
      console.log('Demo completed successfully');
      process.exit(0);
    })
    .catch(error => {
      console.error('Demo failed:', error);
      process.exit(1);
    });
}

module.exports = { runTradingAgentDemo }; 