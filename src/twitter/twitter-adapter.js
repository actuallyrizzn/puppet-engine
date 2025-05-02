/**
 * Twitter Adapter
 * Provides a unified interface to the Twitter API client
 */

const TwitterClient = require('./twitter-client');

class TwitterAdapter {
  /**
   * Create a new TwitterAdapter
   * @param {Object} options Configuration options
   * @param {Object} options.apiCredentials Twitter API credentials
   */
  constructor(options = {}) {
    console.log('Using official Twitter API client');
    this.client = new TwitterClient({
      credentials: options.apiCredentials
    });
  }
  
  /**
   * Register a Twitter client for an agent
   */
  async registerAgentClient(agentId, credentials) {
    return this.client.registerAgentClient(agentId, credentials);
  }
  
  /**
   * Get the appropriate client for an agent
   */
  getClientForAgent(agentId) {
    return this.client.getClientForAgent(agentId);
  }
  
  /**
   * Post a tweet for an agent
   */
  async postTweet(agentId, content, options = {}) {
    return this.client.postTweet(agentId, content, options);
  }
  
  /**
   * Post a thread of tweets
   */
  async postThread(agentId, contentArray, options = {}) {
    return this.client.postThread(agentId, contentArray, options);
  }
  
  /**
   * Get a tweet by ID
   */
  async getTweet(tweetId) {
    return this.client.getTweet(tweetId);
  }
  
  /**
   * Get recent tweets from a user timeline
   */
  async getUserTimeline(userId, options = {}) {
    return this.client.getUserTimeline(userId, options);
  }
  
  /**
   * Monitor mentions for an agent
   */
  async getAgentMentions(agentId, options = {}) {
    return this.client.getAgentMentions(agentId, options);
  }
  
  /**
   * Like a tweet
   */
  async likeTweet(agentId, tweetId) {
    return this.client.likeTweet(agentId, tweetId);
  }
  
  /**
   * Cleanup resources
   */
  async close() {
    // No cleanup needed for the official API client
    return;
  }
}

module.exports = TwitterAdapter; 