/**
 * Twitter client for Puppet Engine
 * Handles Twitter API interactions for agents
 */

const { TwitterApi } = require('twitter-api-v2');
const { Tweet } = require('../core/types');

class TwitterClient {
  constructor(options = {}) {
    this.clients = {};
    this.defaultClient = null;
    
    // If credentials provided, initialize a default client
    if (options.credentials) {
      this.defaultClient = this.createClient(options.credentials);
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
      // Use the default client for reading
      const result = await this.defaultClient.v2.singleTweet(tweetId, {
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
      const client = this.defaultClient;
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
        'tweet.fields': ['created_at', 'text', 'author_id']
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
}

module.exports = TwitterClient; 