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

// Utilities
const winston = require('winston');

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
      memoryLimit: parseInt(process.env.DEFAULT_AGENT_MEMORY_LIMIT || '100')
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
      apiServer
    };
  } catch (error) {
    logger.error('Error initializing Puppet Engine:', error);
    throw error;
  }
}

// Start the engine if this script is run directly
if (require.main === module) {
  initializePuppetEngine()
    .then(() => {
      logger.info('Puppet Engine started successfully. 🎭');
      logger.info(`API server running on port ${process.env.ENGINE_PORT || 3000}`);
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
  const engine = require.main === module ? global.puppetEngine : null;
  
  if (engine && engine.twitterClient) {
    // Clean up resources
    await engine.twitterClient.close().catch(err => 
      logger.error('Error closing Twitter client:', err)
    );
  }
  
  logger.info('Puppet Engine shut down successfully');
  process.exit(0);
});

// Store the engine instance globally for cleanup
global.puppetEngine = null;

module.exports = { initializePuppetEngine }; 