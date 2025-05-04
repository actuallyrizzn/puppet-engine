/**
 * PuppetEngine - Core engine for managing AI agents
 */
class PuppetEngine {
  constructor(config = {}) {
    this.config = config;
    this.apiKey = config.apiKey || process.env.OPENAI_API_KEY;
    this.agents = {};
    
    console.log('PuppetEngine initialized');
  }

  /**
   * Create an agent instance
   * @param {Object} agentConfig - Agent configuration
   * @returns {Object} Agent instance
   */
  async createAgent(agentConfig) {
    if (!agentConfig || !agentConfig.id) {
      throw new Error('Invalid agent configuration: missing id');
    }

    const agentId = agentConfig.id;
    console.log(`Creating agent: ${agentId}`);

    // Create a twitter client for the agent
    const twitterClient = this._createTwitterClient(agentConfig.twitter_credentials);

    // Create agent instance
    const agent = {
      id: agentId,
      config: agentConfig,
      twitterClient,
      memory: {
        coreMemories: agentConfig.initial_memory?.core_memories || [],
        relationships: agentConfig.initial_memory?.relationships || {},
        recentEvents: agentConfig.initial_memory?.recent_events || []
      },
      status: {
        lastPostTime: null,
        mood: 'neutral',
        active: true
      }
    };

    // Store the agent
    this.agents[agentId] = agent;
    
    console.log(`Agent created: ${agentId}`);
    return agent;
  }

  /**
   * Create a Twitter client for an agent
   * @param {Object} credentials - Twitter API credentials
   * @returns {Object} Twitter client
   */
  _createTwitterClient(credentials = {}) {
    // Use agent-specific credentials if provided, otherwise fallback to environment variables
    const apiKey = credentials.apiKey || process.env.TWITTER_API_KEY;
    const apiKeySecret = credentials.apiKeySecret || process.env.TWITTER_API_KEY_SECRET;
    const accessToken = credentials.accessToken || process.env.TWITTER_ACCESS_TOKEN;
    const accessTokenSecret = credentials.accessTokenSecret || process.env.TWITTER_ACCESS_TOKEN_SECRET;
    const bearerToken = credentials.bearerToken || process.env.TWITTER_BEARER_TOKEN;

    // Check if we have necessary credentials to use the real Twitter API
    const hasRealCredentials = apiKey && apiKeySecret && accessToken && accessTokenSecret;
    
    if (hasRealCredentials && process.env.USE_TWITTER_API === 'true') {
      try {
        console.log('Initializing real Twitter API client');
        // Use the Twitter API v2 client
        const { TwitterApi } = require('twitter-api-v2');
        const client = new TwitterApi({
          appKey: apiKey,
          appSecret: apiKeySecret,
          accessToken: accessToken,
          accessSecret: accessTokenSecret
        });
        
        // Return a wrapper with our standard interface
        return {
          tweet: async (text) => {
            console.log(`Posting real tweet: ${text}`);
            try {
              const result = await client.v2.tweet(text);
              console.log(`Tweet posted successfully with ID: ${result.data.id}`);
              return { id: result.data.id, text };
            } catch (error) {
              console.error('Error posting tweet:', error);
              throw error;
            }
          },
          reply: async (text, inReplyToId) => {
            console.log(`Posting real reply to ${inReplyToId}: ${text}`);
            try {
              const result = await client.v2.reply(text, inReplyToId);
              return { id: result.data.id, text };
            } catch (error) {
              console.error('Error posting reply:', error);
              throw error;
            }
          },
          like: async (tweetId) => {
            console.log(`Liking real tweet: ${tweetId}`);
            try {
              const userId = await this._getUserId(client);
              const result = await client.v2.like(userId, tweetId);
              return { success: true };
            } catch (error) {
              console.error('Error liking tweet:', error);
              throw error;
            }
          }
        };
      } catch (error) {
        console.error('Failed to initialize real Twitter client:', error);
        console.log('Falling back to mock Twitter client');
      }
    }

    // Use a mock client if real credentials not available or TwitterApi failed to initialize
    console.log('Using mock Twitter client');
    return {
      tweet: async (text) => {
        console.log(`Tweet (MOCK): ${text}`);
        // For demonstration purposes, we'll just log the tweet
        return { id: `mock-tweet-${Date.now()}`, text };
      },
      reply: async (text, inReplyToId) => {
        console.log(`Reply to ${inReplyToId} (MOCK): ${text}`);
        return { id: `mock-reply-${Date.now()}`, text };
      },
      like: async (tweetId) => {
        console.log(`Like tweet ${tweetId} (MOCK)`);
        return { success: true };
      }
    };
  }

  /**
   * Helper to get the authenticated user ID
   * @private
   */
  async _getUserId(client) {
    const me = await client.v2.me();
    return me.data.id;
  }

  /**
   * Get an agent by ID
   * @param {string} agentId - Agent ID
   * @returns {Object} Agent instance
   */
  getAgent(agentId) {
    return this.agents[agentId];
  }

  /**
   * Get all agents
   * @returns {Object} Map of agent instances
   */
  getAllAgents() {
    return this.agents;
  }
}

module.exports = PuppetEngine; 