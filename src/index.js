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
const TwitterClient = require('./twitter/twitter-client');
const OpenAIProvider = require('./llm/openai-provider');
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
    // Create Twitter client
    const twitterClient = new TwitterClient({
      credentials: {
        apiKey: process.env.TWITTER_API_KEY,
        apiKeySecret: process.env.TWITTER_API_KEY_SECRET,
        accessToken: process.env.TWITTER_ACCESS_TOKEN,
        accessTokenSecret: process.env.TWITTER_ACCESS_TOKEN_SECRET,
        bearerToken: process.env.TWITTER_BEARER_TOKEN
      }
    });
    logger.info('Twitter client initialized');
    
    // Create LLM provider
    const llmProvider = new OpenAIProvider({
      apiKey: process.env.OPENAI_API_KEY,
      model: process.env.OPENAI_MODEL || 'gpt-4-turbo'
    });
    logger.info('LLM provider initialized');
    
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
      llmProvider,
      twitterClient,
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
    
    // Start monitoring Twitter for mentions
    await agentManager.startMonitoringMentions();
    
    // Set up periodic events
    const agentIds = Object.keys(agentManager.agents);
    eventEngine.setupRandomEvents(agentIds, {
      newsInterval: parseInt(process.env.NEWS_EVENT_INTERVAL || (6 * 60 * 60 * 1000)), // 6 hours default
      moodInterval: parseInt(process.env.MOOD_EVENT_INTERVAL || (4 * 60 * 60 * 1000)), // 4 hours default
      interactionInterval: parseInt(process.env.INTERACTION_EVENT_INTERVAL || (8 * 60 * 60 * 1000)) // 8 hours default
    });
    
    // Return the initialized components
    return {
      twitterClient,
      llmProvider,
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

module.exports = { initializePuppetEngine }; 