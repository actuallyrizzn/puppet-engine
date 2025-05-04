/**
 * Twitter client for Puppet Engine
 * Handles Twitter API interactions for agents
 */

const { TwitterApi, ETwitterStreamEvent } = require('twitter-api-v2');
const { Tweet } = require('../core/types');

class TwitterClient {
  constructor(options = {}) {
    this.clients = {};
    this.defaultClient = null;
    this.bearerClient = null;
    this.activeStreams = new Map();
    
    // If credentials provided, initialize a default client
    if (options.credentials) {
      this.defaultClient = this.createClient(options.credentials);
      
      // Create a bearer token client for elevated access endpoints
      if (options.credentials.bearerToken || process.env.TWITTER_BEARER_TOKEN) {
        const bearerToken = options.credentials.bearerToken || process.env.TWITTER_BEARER_TOKEN;
        if (bearerToken && bearerToken.length > 20) { // Simple validation
          this.bearerClient = new TwitterApi(bearerToken);
          console.log('Initialized bearer token client for elevated access');
        } else {
          console.warn('Bearer token appears to be invalid or too short');
        }
      } else {
        console.warn('No bearer token provided for streaming API access');
      }
    }
  }
  
  /**
   * Create a new Twitter client with credentials
   */
  createClient(credentials) {
    // Add detailed logging of credentials (with sensitive parts masked)
    console.log(`Creating Twitter client with credentials:
      API Key: ${credentials.apiKey ? credentials.apiKey.substring(0, 4) + '...' : 'undefined'}
      API Secret: ${credentials.apiKeySecret ? credentials.apiKeySecret.substring(0, 4) + '...' : 'undefined'}
      Access Token: ${credentials.accessToken ? credentials.accessToken.substring(0, 4) + '...' : 'undefined'}
      Access Token Secret: ${credentials.accessTokenSecret ? credentials.accessTokenSecret.substring(0, 4) + '...' : 'undefined'}
      Bearer Token: ${credentials.bearerToken ? 'Provided' : 'Not provided'}
    `);
    
    return new TwitterApi({
      appKey: credentials.apiKey || process.env.TWITTER_API_KEY,
      appSecret: credentials.apiKeySecret || process.env.TWITTER_API_KEY_SECRET,
      accessToken: credentials.accessToken || process.env.TWITTER_ACCESS_TOKEN,
      accessSecret: credentials.accessTokenSecret || process.env.TWITTER_ACCESS_TOKEN_SECRET
    });
  }
  
  /**
   * Register a Twitter client for an agent
   */
  registerAgentClient(agentId, credentials) {
    if (!credentials.apiKey || !credentials.apiKeySecret || 
        !credentials.accessToken || !credentials.accessTokenSecret) {
      console.warn(`Incomplete Twitter credentials for agent ${agentId}. The agent will use the default client if available.`);
      return null;
    }
    
    try {
      this.clients[agentId] = this.createClient(credentials);
      console.log(`Successfully registered Twitter client for agent ${agentId}`);
      return this.clients[agentId];
    } catch (error) {
      console.error(`Error registering Twitter client for agent ${agentId}:`, error);
      throw error;
    }
  }
  
  /**
   * Get the appropriate client for an agent
   */
  getClientForAgent(agentId) {
    const client = this.clients[agentId] || this.defaultClient;
    
    if (!client) {
      throw new Error(`No Twitter client available for agent ${agentId}. Please ensure Twitter credentials are provided either globally in .env or specifically in the agent configuration.`);
    }
    
    return client;
  }
  
  /**
   * Post a tweet for an agent
   */
  async postTweet(agentId, content, options = {}) {
    console.log(`Attempting to post tweet for agent ${agentId}`);
    const client = this.getClientForAgent(agentId);
    
    if (!client) {
      throw new Error(`No Twitter client available for agent ${agentId}`);
    }
    
    try {
      // Test authentication before attempting to post
      console.log(`Testing Twitter API connection for agent ${agentId}...`);
      const meResult = await client.v2.me();
      console.log(`Successfully authenticated as: ${meResult.data.username}`);
      
      const tweetOptions = {};
      
      // Handle reply
      if (options.replyToTweetId) {
        tweetOptions.reply = { in_reply_to_tweet_id: options.replyToTweetId };
      }
      
      // Handle quote tweet
      if (options.quoteTweetId) {
        // Append the tweet URL to the content
        content = `${content} https://twitter.com/i/status/${options.quoteTweetId}`;
      }
      
      // Handle media attachments
      if (options.mediaIds && options.mediaIds.length > 0) {
        tweetOptions.media = { media_ids: options.mediaIds };
      }
      
      // Send the tweet
      console.log(`Sending tweet with content: "${content.substring(0, 20)}..."`);
      console.log(`Tweet options:`, JSON.stringify(tweetOptions));
      const result = await client.v2.tweet(content, tweetOptions);
      
      // Convert to internal Tweet format
      const tweet = new Tweet();
      tweet.id = result.data.id;
      tweet.content = content;
      tweet.createdAt = new Date();
      tweet.authorId = agentId;
      tweet.replyToId = options.replyToTweetId || null;
      tweet.quoteTweetId = options.quoteTweetId || null;
      
      console.log(`Successfully posted tweet with ID: ${tweet.id}`);
      return tweet;
    } catch (error) {
      console.error(`Error posting tweet for agent ${agentId}:`, error);
      throw error;
    }
  }
  
  /**
   * Post a thread of tweets
   */
  async postThread(agentId, contentArray, options = {}) {
    console.log(`Attempting to post thread for agent ${agentId} with ${contentArray.length} tweets`);
    
    if (!contentArray || contentArray.length === 0) {
      throw new Error('No content provided for thread');
    }
    
    const tweets = [];
    let previousTweetId = null;
    
    for (const content of contentArray) {
      const tweetOptions = { ...options };
      
      if (previousTweetId) {
        tweetOptions.replyToTweetId = previousTweetId;
      }
      
      const tweet = await this.postTweet(agentId, content, tweetOptions);
      previousTweetId = tweet.id;
      tweets.push(tweet);
    }
    
    // Mark all tweets as part of a thread
    tweets.forEach(tweet => {
      tweet.isThread = true;
      tweet.threadIds = tweets.map(t => t.id);
    });
    
    return tweets;
  }
  
  /**
   * Get a tweet by ID
   */
  async getTweet(tweetId) {
    try {
      // Use the bearer client if available for higher rate limits
      const client = this.bearerClient || this.defaultClient;
      
      const result = await client.v2.singleTweet(tweetId, {
        expansions: ['author_id', 'referenced_tweets.id'],
        'tweet.fields': ['created_at', 'text', 'author_id', 'conversation_id']
      });
      
      const tweet = new Tweet();
      tweet.id = result.data.id;
      tweet.content = result.data.text;
      tweet.createdAt = new Date(result.data.created_at);
      tweet.authorId = result.data.author_id;
      
      // Handle referenced tweets
      if (result.data.referenced_tweets) {
        const referencedTweet = result.data.referenced_tweets[0];
        if (referencedTweet.type === 'replied_to') {
          tweet.replyToId = referencedTweet.id;
        } else if (referencedTweet.type === 'quoted') {
          tweet.quoteTweetId = referencedTweet.id;
        }
      }
      
      return tweet;
    } catch (error) {
      console.error(`Error fetching tweet ${tweetId}:`, error);
      throw error;
    }
  }
  
  /**
   * Get recent tweets from a user timeline
   */
  async getUserTimeline(userId, options = {}) {
    try {
      // Use the bearer client if available for higher rate limits
      const client = this.bearerClient || this.defaultClient;
      const limit = options.limit || 10;
      
      const result = await client.v2.userTimeline(userId, {
        max_results: limit,
        expansions: ['referenced_tweets.id'],
        'tweet.fields': ['created_at', 'text', 'author_id', 'conversation_id']
      });
      
      return result.data.data.map(tweetData => {
        const tweet = new Tweet();
        tweet.id = tweetData.id;
        tweet.content = tweetData.text;
        tweet.createdAt = new Date(tweetData.created_at);
        tweet.authorId = tweetData.author_id;
        
        // Handle referenced tweets
        if (tweetData.referenced_tweets) {
          const referencedTweet = tweetData.referenced_tweets[0];
          if (referencedTweet.type === 'replied_to') {
            tweet.replyToId = referencedTweet.id;
          } else if (referencedTweet.type === 'quoted') {
            tweet.quoteTweetId = referencedTweet.id;
          }
        }
        
        return tweet;
      });
    } catch (error) {
      console.error(`Error fetching timeline for user ${userId}:`, error);
      throw error;
    }
  }
  
  /**
   * Monitor mentions for an agent
   */
  async getAgentMentions(agentId, options = {}) {
    try {
      // Basic rate limiting - check if we should skip this request
      const enableRateLimitProtection = process.env.ENABLE_RATE_LIMIT_PROTECTION !== 'false';
      
      if (enableRateLimitProtection) {
        const now = Date.now();
        const lastRequestTime = this._lastMentionRequestTime || 0;
        const minInterval = 60000; // Minimum 1 minute between requests
        
        // If we've made a request in the last minute, skip this one
        if (now - lastRequestTime < minInterval) {
          console.log(`Rate limit protection: Skipping mention check for ${agentId} - too soon since last request`);
          return [];
        }
        
        // Track this request time
        this._lastMentionRequestTime = now;
      }
      
      const client = this.getClientForAgent(agentId);
      const limit = options.limit || 10;
      const sinceId = options.sinceId || null;
      
      // First, get the user ID for the authenticated user
      console.log(`Getting user ID for agent ${agentId}...`);
      const meResult = await client.v2.me();
      const userId = meResult.data.id;
      console.log(`Retrieved user ID ${userId} for agent ${agentId}`);
      
      const queryParams = {
        max_results: limit,
        expansions: ['author_id', 'referenced_tweets.id'],
        'tweet.fields': ['created_at', 'text', 'author_id'],
        'user.fields': ['name', 'username'] // Request username data
      };
      
      if (sinceId) {
        queryParams.since_id = sinceId;
      }
      
      console.log(`Fetching mentions for agent ${agentId} with params:`, JSON.stringify(queryParams));
      const result = await client.v2.userMentionTimeline(userId, queryParams);
      
      // Check if data exists and is not empty
      if (!result.data || !result.data.data || result.data.data.length === 0) {
        console.log(`No mentions found for agent ${agentId}`);
        return [];
      }
      
      console.log(`Found ${result.data.data.length} mentions for agent ${agentId}`);
      
      // Create a map of author IDs to usernames
      const userMap = {};
      if (result.data.includes && result.data.includes.users) {
        result.data.includes.users.forEach(user => {
          userMap[user.id] = user.username;
        });
      }
      
      return result.data.data.map(tweetData => {
        const tweet = new Tweet();
        tweet.id = tweetData.id;
        tweet.content = tweetData.text;
        tweet.createdAt = new Date(tweetData.created_at);
        tweet.authorId = tweetData.author_id;
        
        // Add author username if available
        if (userMap[tweetData.author_id]) {
          tweet.authorUsername = userMap[tweetData.author_id];
        }
        
        // Handle referenced tweets
        if (tweetData.referenced_tweets) {
          const referencedTweet = tweetData.referenced_tweets[0];
          if (referencedTweet.type === 'replied_to') {
            tweet.replyToId = referencedTweet.id;
          } else if (referencedTweet.type === 'quoted') {
            tweet.quoteTweetId = referencedTweet.id;
          }
        }
        
        return tweet;
      });
    } catch (error) {
      console.error(`Error fetching mentions for agent ${agentId}:`, error);
      // Return empty array instead of throwing to avoid crashing the application
      // This allows the application to continue running even if mentions can't be fetched
      return [];
    }
  }
  
  /**
   * Like a tweet
   */
  async likeTweet(agentId, tweetId) {
    console.log(`Attempting to like tweet ${tweetId} for agent ${agentId}`);
    const client = this.getClientForAgent(agentId);
    
    // First get the user ID
    const meResult = await client.v2.me();
    const userId = meResult.data.id;
    
    await client.v2.like(userId, tweetId);
    console.log(`Successfully liked tweet ${tweetId}`);
    return true;
  }

  /**
   * Check if we have appropriate access for filtered stream
   * @private
   */
  async _validateStreamAccess(client) {
    try {
      console.log("Validating Twitter account API access level...");
      
      // First check if we can read stream rules - this requires proper elevated access
      const rulesResponse = await client.v2.streamRules();
      console.log("Access check success: Can read stream rules");
      
      // Test if we can add/delete rules
      const testAddRule = await client.v2.updateStreamRules({
        add: [{ value: 'test rule access', tag: 'access_test' }]
      });
      
      if (testAddRule.meta?.summary?.created) {
        console.log("Access check success: Can add stream rules");
        
        // Clean up the test rule
        if (testAddRule.data && testAddRule.data.length > 0) {
          const ruleIds = testAddRule.data.map(rule => rule.id);
          await client.v2.updateStreamRules({
            delete: { ids: ruleIds }
          });
          console.log("Access check success: Can delete stream rules");
        }
        
        return true;
      }
      
      // If we get here, something isn't right with adding rules
      return false;
    } catch (error) {
      console.error("Stream API access validation failed:", error.message);
      if (error.code === 403) {
        console.error("ERROR: Your Twitter API credentials don't have the required Elevated access level for filtered stream API");
        console.error("You need to apply for Elevated access at https://developer.twitter.com/en/portal/products/elevated");
      }
      return false;
    }
  }

  /**
   * Start streaming mentions for an agent in real-time
   * This method sets up a rules-based filtered stream using Twitter API v2
   * @param {string} agentId - The ID of the agent to stream mentions for
   * @param {function} onMention - Callback function to handle each mention
   * @param {Object} options - Additional options
   * @returns {Object} - Stream connection object
   */
  async startMentionStream(agentId, onMention, options = {}) {
    try {
      console.log(`Setting up real-time mention stream for agent ${agentId}`);
      
      // Check if we already have an active stream for this agent
      if (this.activeStreams.has(agentId)) {
        console.log(`Stream already active for agent ${agentId}, reusing existing stream`);
        return this.activeStreams.get(agentId);
      }
      
      // Check for bearer token client first - required for filtered stream API
      if (!this.bearerClient) {
        // Try to create one if not already available
        if (process.env.TWITTER_BEARER_TOKEN) {
          this.bearerClient = new TwitterApi(process.env.TWITTER_BEARER_TOKEN);
          console.log('Created new bearer token client for streaming');
        } else {
          throw new Error('Bearer token is required for filtered stream API access');
        }
      }
      
      // Get the user client to obtain username
      const client = this.getClientForAgent(agentId);
      
      // Get the user ID and username for the agent
      const meResult = await client.v2.me();
      const userId = meResult.data.id;
      const username = meResult.data.username;
      console.log(`Retrieved user ID ${userId} and username ${username} for agent ${agentId}`);
      
      // Validate proper access for filtered stream API
      const hasStreamAccess = await this._validateStreamAccess(this.bearerClient);
      if (!hasStreamAccess) {
        throw new Error('Twitter API account lacks required elevated access for filtered stream API');
      }
      
      // Use the bearer token client for stream operations
      const streamClient = this.bearerClient.v2;
      
      // Set up rules for the filtered stream
      try {
        // Get existing rules
        console.log('Retrieving existing filtered stream rules...');
        const currentRules = await streamClient.streamRules();
        console.log('Current rules:', JSON.stringify(currentRules));
        
        // Delete existing rules if any exist
        if (currentRules.data && currentRules.data.length > 0) {
          const ruleIds = currentRules.data.map(rule => rule.id);
          console.log(`Found ${ruleIds.length} existing rules, deleting...`);
          
          await streamClient.updateStreamRules({
            delete: { ids: ruleIds }
          });
          console.log(`Deleted ${ruleIds.length} existing stream rules`);
        } else {
          console.log('No existing stream rules found');
        }
        
        // Add new rule to track mentions of this user
        const mentionRule = `@${username}`;
        console.log(`Adding stream rule to track mentions: ${mentionRule}`);
        
        const addResult = await streamClient.updateStreamRules({
          add: [{ value: mentionRule, tag: `mentions-${agentId}` }]
        });
        console.log('Rule addition result:', JSON.stringify(addResult));
        
        // Verify rules were added
        const updatedRules = await streamClient.streamRules();
        console.log('Current stream rules:', JSON.stringify(updatedRules.data || []));
        
        if (!updatedRules.data || updatedRules.data.length === 0) {
          throw new Error('Failed to add stream rules');
        }
      } catch (error) {
        console.error('Error setting up filtered stream rules:', error);
        throw new Error(`Failed to set up stream rules: ${error.message}`);
      }
      
      // Configure stream parameters
      const streamParams = {
        'tweet.fields': 'created_at,author_id,conversation_id,referenced_tweets',
        'expansions': 'author_id,referenced_tweets.id,in_reply_to_user_id',
        'user.fields': 'name,username'
      };
      
      console.log(`Starting filtered stream with params: ${JSON.stringify(streamParams)}`);
      
      try {
        // Connect to the filtered stream
        const stream = await streamClient.searchStream(streamParams);
        
        // Track stream connection
        let isConnected = true;
        
        // Handle stream events
        stream.on(ETwitterStreamEvent.Data, async tweetData => {
          // Validate the data
          if (!tweetData || !tweetData.data) {
            console.log('Received invalid data from stream, ignoring');
            return;
          }
          
          console.log(`Received real-time tweet from stream: "${tweetData.data.text.substring(0, 30)}..."`);
          
          try {
            // Convert to internal Tweet format
            const tweet = new Tweet();
            tweet.id = tweetData.data.id;
            tweet.content = tweetData.data.text;
            tweet.createdAt = new Date(tweetData.data.created_at);
            tweet.authorId = tweetData.data.author_id;
            tweet.isDirectMention = true;
            
            // Extract author username if available
            if (tweetData.includes && tweetData.includes.users) {
              const author = tweetData.includes.users.find(user => user.id === tweet.authorId);
              if (author) {
                tweet.authorUsername = author.username;
              }
            }
            
            // Handle referenced tweets
            if (tweetData.data.referenced_tweets) {
              for (const ref of tweetData.data.referenced_tweets) {
                if (ref.type === 'replied_to') {
                  tweet.replyToId = ref.id;
                } else if (ref.type === 'quoted') {
                  tweet.quoteTweetId = ref.id;
                }
              }
            }
            
            // Process context and conversation history if it's a reply
            if (tweet.replyToId) {
              try {
                console.log(`Fetching context for tweet reply ${tweet.replyToId}`);
                const originalTweet = await this.getTweet(tweet.replyToId);
                tweet.originalTweet = originalTweet;
                
                // Create conversation history
                const conversationHistory = [];
                
                // Build conversation history recursively using bearer client
                await this._fetchConversationThread(tweet.replyToId, conversationHistory, agentId);
                
                // Sort and add current tweet
                if (conversationHistory.length > 0) {
                  // Sort chronologically
                  conversationHistory.sort((a, b) => {
                    if (a.timestamp && b.timestamp) {
                      return a.timestamp - b.timestamp;
                    }
                    return 0;
                  });
                  
                  // Add current mention
                  conversationHistory.push({
                    role: "user",
                    content: tweet.content,
                    timestamp: tweet.createdAt.getTime()
                  });
                  
                  tweet.conversationHistory = conversationHistory;
                }
              } catch (error) {
                console.error(`Error fetching context for tweet ${tweet.id}:`, error);
                // Continue processing without thread context
              }
            }
            
            // Process the mention via callback
            if (onMention && typeof onMention === 'function') {
              console.log(`Processing mention callback for tweet ${tweet.id}`);
              onMention(tweet);
            }
          } catch (error) {
            console.error(`Error processing mention from stream: ${error.message}`);
          }
        });
        
        // Handle other stream events
        stream.on(ETwitterStreamEvent.Connected, () => {
          console.log(`Stream connected for agent ${agentId}`);
          isConnected = true;
        });
        
        // Handle stream connection errors
        stream.on(ETwitterStreamEvent.Error, error => {
          console.error(`Stream error for agent ${agentId}:`, error);
          isConnected = false;
          
          // For rate limit errors, use a longer delay
          const retryDelay = error.code === 429 ? 60000 : 15000;
          console.log(`Will retry stream connection in ${retryDelay/1000} seconds`);
          
          setTimeout(() => {
            if (!isConnected) {
              console.log(`Attempting to reconnect stream for agent ${agentId}...`);
              this.startMentionStream(agentId, onMention, options)
                .catch(err => {
                  console.error(`Reconnection attempt failed for agent ${agentId}:`, err);
                });
            }
          }, retryDelay);
        });
        
        // Handle graceful disconnection
        stream.on(ETwitterStreamEvent.ConnectionClosed, () => {
          console.log(`Stream connection closed for agent ${agentId}`);
          this.activeStreams.delete(agentId);
          isConnected = false;
        });
        
        // Add helper methods to the stream
        stream.close = async () => {
          console.log(`Manually closing stream for agent ${agentId}`);
          try {
            // Clean up rules when closing
            const rules = await streamClient.streamRules();
            if (rules.data && rules.data.length > 0) {
              const ruleIds = rules.data.map(rule => rule.id);
              await streamClient.updateStreamRules({
                delete: { ids: ruleIds }
              });
              console.log(`Cleaned up ${ruleIds.length} stream rules`);
            }
            // Disconnect the stream
            await stream.close();
            this.activeStreams.delete(agentId);
            isConnected = false;
          } catch (error) {
            console.error(`Error closing stream for agent ${agentId}:`, error);
          }
        };
        
        // Store the active stream
        this.activeStreams.set(agentId, stream);
        
        console.log(`Successfully connected to filtered stream for agent ${agentId}`);
        return stream;
      } catch (error) {
        console.error('Stream connection error:', error.message);
        throw new Error(`Failed to connect to stream: ${error.message}`);
      }
    } catch (error) {
      console.error(`Error starting mention stream for agent ${agentId}:`, error);
      throw error;
    }
  }
  
  /**
   * Close all active streams
   */
  async close() {
    console.log('Closing all active Twitter streams');
    for (const [agentId, stream] of this.activeStreams.entries()) {
      if (stream && typeof stream.close === 'function') {
        try {
          await stream.close();
          console.log(`Closed stream for agent ${agentId}`);
        } catch (error) {
          console.error(`Error closing stream for agent ${agentId}:`, error);
        }
      }
    }
    this.activeStreams.clear();
  }
  
  /**
   * Helper method to recursively fetch a conversation thread
   * @private
   */
  async _fetchConversationThread(tweetId, conversationHistory, agentId, depth = 0, maxDepth = 5) {
    // Limit recursion depth to avoid infinite loops
    if (depth >= maxDepth) return;
    
    try {
      // Fetch the tweet using bearer client if available (higher rate limits)
      const client = this.bearerClient || this.defaultClient;
      const tweet = await this.getTweet(tweetId);
      
      // Add to conversation history
      conversationHistory.push({
        role: tweet.authorId === agentId ? "agent" : "user",
        content: tweet.content,
        timestamp: tweet.createdAt.getTime()
      });
      
      // If this tweet is a reply to another, recursively fetch that one too
      if (tweet.replyToId) {
        await this._fetchConversationThread(
          tweet.replyToId, 
          conversationHistory, 
          agentId, 
          depth + 1, 
          maxDepth
        );
      }
    } catch (error) {
      console.error(`Error fetching tweet ${tweetId} for conversation thread:`, error);
      // Continue even if we can't fetch a tweet in the thread
    }
  }
}

module.exports = TwitterClient; 