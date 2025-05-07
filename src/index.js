/**
 * Puppet Engine - Main Entry Point
 * 
 * A real-time AI agent framework for deploying autonomous characters on Twitter
 * who communicate, evolve, and perform unscripted social behavior.
 */

// Load environment variables
require('dotenv').config();

// Core components
const MemoryManager = require('./memory/memory-manager');
const TwitterAdapter = require('./twitter/twitter-adapter');
const OpenAIProvider = require('./llm/openai-provider');
const GrokProvider = require('./llm/grok-provider');
const EventEngine = require('./events/event-engine');
const AgentManager = require('./agents/agent-manager');
const ApiServer = require('./api/api-server');
// DISABLED: Token launch feature completely turned off
// const PumpFunTokenManager = require('./solana/pumpfun-token-manager');
const db = require('./utils/database');

// Utilities
const winston = require('winston');
const fs = require('fs');
const path = require('path');

// Path to token state file
const TOKEN_STATE_FILE = path.join(__dirname, '../data/coby-token-state.json');

// Configure logger
const logger = winston.createLogger({
  level: process.env.ENGINE_LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    new winston.transports.File({ filename: 'puppet-engine.log' })
  ]
});

// Override console.log with winston logger
console.log = (...args) => logger.info(args.join(' '));
console.error = (...args) => logger.error(args.join(' '));
console.warn = (...args) => logger.warn(args.join(' '));
console.info = (...args) => logger.info(args.join(' '));

/**
 * Initialize the Puppet Engine
 */
async function initializePuppetEngine() {
  logger.info('Starting Puppet Engine...');
  
  try {
    // Delete token state file if it exists (token launch feature is disabled)
    if (fs.existsSync(TOKEN_STATE_FILE)) {
      logger.info(`Removing token state file: ${TOKEN_STATE_FILE}`);
      fs.unlinkSync(TOKEN_STATE_FILE);
      logger.info('Token state file removed successfully');
    }
    
    // Delete token-launch directory if it exists
    const tokenLaunchDir = path.join(__dirname, '../scripts/token-launch');
    if (fs.existsSync(tokenLaunchDir)) {
      logger.info(`Removing token-launch directory: ${tokenLaunchDir}`);
      fs.rmSync(tokenLaunchDir, { recursive: true, force: true });
      logger.info('Token-launch directory removed successfully');
    }

    // Initialize MongoDB
    let mongoDbConnected = false;
    try {
      await db.connectToDatabase();
      mongoDbConnected = true;
      logger.info('Successfully connected to MongoDB');
      
      // Remove token records from MongoDB if they exist
      try {
        const collections = await db.getCollections();
        if (collections.includes(db.COLLECTIONS.TOKENS)) {
          const tokenCollection = await db.getCollection(db.COLLECTIONS.TOKENS);
          const result = await tokenCollection.deleteMany({ agentId: 'coby-agent' });
          if (result.deletedCount > 0) {
            logger.info(`Removed ${result.deletedCount} token records from MongoDB`);
          }
        }
      } catch (tokenError) {
        logger.error('Error removing token records from MongoDB:', tokenError);
      }
    } catch (mongoError) {
      logger.error('Failed to connect to MongoDB, falling back to file storage:', mongoError);
      mongoDbConnected = false;
    }
    
    // Create Twitter adapter with the API client
    const twitterAdapter = new TwitterAdapter({
      apiCredentials: {
        apiKey: process.env.TWITTER_API_KEY,
        apiKeySecret: process.env.TWITTER_API_KEY_SECRET,
        accessToken: process.env.TWITTER_ACCESS_TOKEN,
        accessTokenSecret: process.env.TWITTER_ACCESS_TOKEN_SECRET,
        bearerToken: process.env.TWITTER_BEARER_TOKEN
      }
    });
    
    logger.info('Twitter client initialized');
    
    // Initialize LLM providers
    const llmProviders = {
      openai: new OpenAIProvider({
        apiKey: process.env.OPENAI_API_KEY,
        model: process.env.OPENAI_MODEL || 'gpt-4-turbo'
      }),
      grok: new GrokProvider({
        apiKey: process.env.GROK_API_KEY,
        apiEndpoint: process.env.GROK_API_ENDPOINT,
        model: process.env.GROK_MODEL || 'grok-1'
      })
    };
    
    // Default to OpenAI if not specified
    const defaultLLMProvider = llmProviders.openai;
    
    logger.info('LLM providers initialized');
    
    // Create memory manager
    const memoryManager = new MemoryManager({
      memoryLimit: parseInt(process.env.DEFAULT_AGENT_MEMORY_LIMIT || '100'),
      useMongoDb: mongoDbConnected
    });
    logger.info('Memory manager initialized');
    
    // Create event engine
    const eventEngine = new EventEngine();
    logger.info('Event engine initialized');
    
    // Create agent manager
    const agentManager = new AgentManager({
      memoryManager,
      llmProvider: defaultLLMProvider,
      llmProviders,
      twitterClient: twitterAdapter,
      eventEngine
    });
    logger.info('Agent manager initialized');
    
    // Load agents from configuration
    await agentManager.loadAgents();
    
    // Initialize PumpFunTokenManager for Coby agent
    // DISABLED: Token launch feature completely turned off
    // const pumpFunTokenManager = new PumpFunTokenManager({
    //   twitterClient: twitterAdapter,
    //   agentManager: agentManager,
    //   useMongoDb: mongoDbConnected
    // });
    // logger.info('PumpFunTokenManager disabled - token launch feature turned off');
    
    // Schedule token launch for Coby agent if not already launched
    // DISABLED: Token launch feature completely turned off
    // try {
    //   const cobyAgentId = 'coby-agent';
    //   if (agentManager.agents[cobyAgentId]) {
    //     logger.info('Scheduling token launch for Coby agent...');
    //     
    //     // Check if token is already launched
    //     if (pumpFunTokenManager.tokenLaunched) {
    //       logger.info(`Coby already has a token: ${pumpFunTokenManager.tokenMintAddress}`);
    //     } 
    //     // Check if already scheduled
    //     else if (pumpFunTokenManager.isLaunchScheduled()) {
    //       logger.info(`Token launch already scheduled for ${cobyAgentId} at ${pumpFunTokenManager.scheduledLaunchTime}`);
    //     } 
    //     // Schedule the token launch
    //     else {
    //       // Get delay from environment variable or use random
    //       let delayMinutes;
    //       if (process.env.TOKEN_LAUNCH_DELAY_MINUTES) {
    //         delayMinutes = parseInt(process.env.TOKEN_LAUNCH_DELAY_MINUTES);
    //         logger.info(`Using configured TOKEN_LAUNCH_DELAY_MINUTES: ${delayMinutes}`);
    //       } else {
    //         // Default: Schedule with random delay between 5-15 minutes
    //         delayMinutes = Math.floor(Math.random() * 11) + 5;
    //         logger.info(`Using random token launch delay: ${delayMinutes} minutes`);
    //       }
    //       
    //       // Determine if we should tweet before launch
    //       const tweetBeforeLaunch = process.env.TOKEN_PRELAUNCH_TWEET !== 'false';
    //       logger.info(`Tweet about scheduled launch: ${tweetBeforeLaunch ? 'ENABLED' : 'DISABLED'}`);
    //       
    //       const result = await pumpFunTokenManager.scheduleTokenLaunch(cobyAgentId, delayMinutes, tweetBeforeLaunch);
    //       logger.info('Token launch scheduled:', result);
    //     }
    //   } else {
    //     logger.warn(`Coby agent not found, skipping token launch setup`);
    //   }
    // } catch (error) {
    //   logger.error('Error scheduling token launch:', error);
    // }
    
    // Create API server
    const apiServer = new ApiServer({
      port: process.env.ENGINE_PORT || 3000,
      agentManager,
      eventEngine,
      memoryManager
    });
    
    // Start API server
    await apiServer.start();
    
    // Start real-time streaming for Twitter mentions
    await agentManager.startStreamingMentions();
    
    // Set up periodic events
    const agentIds = Object.keys(agentManager.agents);
    eventEngine.setupRandomEvents(agentIds, {
      newsInterval: parseInt(process.env.NEWS_EVENT_INTERVAL || (6 * 60 * 60 * 1000)), // 6 hours default
      moodInterval: parseInt(process.env.MOOD_EVENT_INTERVAL || (4 * 60 * 60 * 1000)), // 4 hours default
      interactionInterval: parseInt(process.env.INTERACTION_EVENT_INTERVAL || (8 * 60 * 60 * 1000)) // 8 hours default
    });
    
    // Return the initialized components
    return {
      twitterClient: twitterAdapter,
      llmProviders,
      memoryManager,
      eventEngine,
      agentManager,
      apiServer,
      // pumpFunTokenManager, // DISABLED: Token launch feature completely turned off
      mongoDbConnected
    };
  } catch (error) {
    logger.error('Error initializing Puppet Engine:', error);
    throw error;
  }
}

// Start the engine if this script is run directly
if (require.main === module) {
  initializePuppetEngine()
    .then((engine) => {
      logger.info('Puppet Engine started successfully. 🎭');
      logger.info(`API server running on port ${process.env.ENGINE_PORT || 3000}`);
      logger.info(`MongoDB connection: ${engine.mongoDbConnected ? 'ACTIVE' : 'INACTIVE - using file storage'}`);
      // Store the engine instance globally for cleanup
      global.puppetEngine = engine;
    })
    .catch(error => {
      logger.error('Failed to start Puppet Engine:', error);
      process.exit(1);
    });
}

// Clean up resources when the application exits
process.on('SIGINT', async () => {
  logger.info('Shutting down Puppet Engine...');
  
  // Get the current engine instance
  const engine = global.puppetEngine;
  
  if (engine) {
    // Close the Twitter client
    if (engine.twitterClient) {
      await engine.twitterClient.close().catch(err => 
        logger.error('Error closing Twitter client:', err)
      );
    }
    
    // Close MongoDB connection
    try {
      await db.closeConnection();
      logger.info('MongoDB connection closed');
    } catch (err) {
      logger.error('Error closing MongoDB connection:', err);
    }
  }
  
  logger.info('Puppet Engine shut down successfully');
  process.exit(0);
});

module.exports = { initializePuppetEngine }; 