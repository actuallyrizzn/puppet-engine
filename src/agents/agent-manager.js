/**
 * Agent Manager for Puppet Engine
 * Handles loading, managing, and controlling agent behavior
 */

const fs = require('fs');
const path = require('path');
const { Agent, Personality, StyleGuide } = require('../core/types');
const MemoryManager = require('../memory/memory-manager');
const OpenAIProvider = require('../llm/openai-provider');
const TwitterClient = require('../twitter/twitter-client');
const cron = require('node-cron');
const behaviorRandomizer = require('./behavior-randomizer');

class AgentManager {
  constructor(options = {}) {
    this.agents = {};
    this.memoryManager = options.memoryManager || new MemoryManager();
    this.llmProvider = options.llmProvider || new OpenAIProvider();
    this.twitterClient = options.twitterClient || new TwitterClient();
    this.eventEngine = options.eventEngine;
    
    this.lastPostTime = {}; // Track when agents last posted
    this.postSchedules = {}; // Cron schedules for agent posts
    this.nextPostTimes = {}; // Track next scheduled post time for each agent
    
    // Setup event listeners
    if (this.eventEngine) {
      this.setupEventListeners();
    }
  }
  
  /**
   * Load agents from configuration files
   */
  async loadAgents(configDir = 'config/agents') {
    try {
      // Get all agent config files
      const files = fs.readdirSync(configDir);
      
      // Load each agent
      for (const file of files) {
        if (file.endsWith('.json')) {
          const configPath = path.join(configDir, file);
          const agentConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));
          await this.loadAgent(agentConfig);
        }
      }
      
      console.log(`Loaded ${Object.keys(this.agents).length} agents`);
    } catch (error) {
      console.error('Error loading agents:', error);
      throw error;
    }
  }
  
  /**
   * Load a single agent from configuration
   */
  async loadAgent(config) {
    try {
      if (!config.id) {
        throw new Error('Agent config must have an ID');
      }
      
      // Create new agent
      const agent = new Agent();
      agent.id = config.id;
      agent.name = config.name || config.id;
      agent.description = config.description || '';
      
      // Set up personality
      if (config.personality) {
        agent.personality.traits = config.personality.traits || [];
        agent.personality.values = config.personality.values || [];
        agent.personality.speakingStyle = config.personality.speaking_style || '';
        agent.personality.interests = config.personality.interests || [];
      }
      
      // Set up style guide
      if (config.style_guide) {
        agent.styleGuide.voice = config.style_guide.voice || '';
        agent.styleGuide.tone = config.style_guide.tone || '';
        
        if (config.style_guide.formatting) {
          agent.styleGuide.formatting.usesHashtags = config.style_guide.formatting.uses_hashtags || false;
          agent.styleGuide.formatting.hashtagStyle = config.style_guide.formatting.hashtag_style || '';
          agent.styleGuide.formatting.usesEmojis = config.style_guide.formatting.uses_emojis || false;
          agent.styleGuide.formatting.emojiFrequency = config.style_guide.formatting.emoji_frequency || '';
          agent.styleGuide.formatting.capitalization = config.style_guide.formatting.capitalization || '';
          agent.styleGuide.formatting.sentenceLength = config.style_guide.formatting.sentence_length || '';
        }
        
        agent.styleGuide.topicsToAvoid = config.style_guide.topics_to_avoid || [];
      }
      
      // Set up custom system prompt if provided
      if (config.custom_system_prompt) {
        agent.customSystemPrompt = config.custom_system_prompt;
        console.log(`Loaded custom system prompt for agent ${agent.id}`);
      }
      
      // Set up behavior
      if (config.behavior) {
        if (config.behavior.post_frequency) {
          agent.behavior.postFrequency.minHoursBetweenPosts = 
            config.behavior.post_frequency.min_hours_between_posts || 3;
          agent.behavior.postFrequency.maxHoursBetweenPosts = 
            config.behavior.post_frequency.max_hours_between_posts || 12;
          agent.behavior.postFrequency.peakPostingHours = 
            config.behavior.post_frequency.peak_posting_hours || [];
        }
        
        if (config.behavior.interaction_patterns) {
          agent.behavior.interactionPatterns.replyProbability = 
            config.behavior.interaction_patterns.reply_probability || 0.5;
          agent.behavior.interactionPatterns.quoteTweetProbability = 
            config.behavior.interaction_patterns.quote_tweet_probability || 0.3;
          agent.behavior.interactionPatterns.likeProbability = 
            config.behavior.interaction_patterns.like_probability || 0.7;
        }
        
        if (config.behavior.content_preferences) {
          agent.behavior.contentPreferences.maxThreadLength = 
            config.behavior.content_preferences.max_thread_length || 3;
          agent.behavior.contentPreferences.typicalPostLength = 
            config.behavior.content_preferences.typical_post_length || 240;
          agent.behavior.contentPreferences.linkSharingFrequency = 
            config.behavior.content_preferences.link_sharing_frequency || 0.2;
        }
      }
      
      // Initialize memory
      if (config.initial_memory) {
        agent.memory = this.memoryManager.initializeAgentMemory(
          agent.id, 
          config.initial_memory
        );
      } else {
        agent.memory = this.memoryManager.getAgentMemory(agent.id);
      }
      
      // Register agent-specific Twitter client if credentials are provided
      if (config.twitter_credentials) {
        console.log(`Registering Twitter client for agent ${agent.id}`);
        
        // Check if we're using API or web scraping
        const useTwitterAPI = process.env.USE_TWITTER_API !== 'false';
        
        if (useTwitterAPI) {
          // Using official API - check for API keys
          if (config.twitter_credentials.apiKey && 
              config.twitter_credentials.apiKeySecret && 
              config.twitter_credentials.accessToken && 
              config.twitter_credentials.accessTokenSecret) {
            this.twitterClient.registerAgentClient(agent.id, config.twitter_credentials);
          } else {
            console.log(`No valid Twitter API credentials for agent ${agent.id}, using default client`);
          }
        } else {
          // Using web scraping - check for username/password
          if (config.twitter_credentials.username && 
              config.twitter_credentials.password) {
            this.twitterClient.registerAgentClient(agent.id, config.twitter_credentials);
          } else {
            // Check if credentials exist in environment variables
            const envUsername = process.env[`TWITTER_USERNAME_${agent.id}`];
            const envPassword = process.env[`TWITTER_PASSWORD_${agent.id}`];
            
            if (envUsername && envPassword) {
              this.twitterClient.registerAgentClient(agent.id, {
                username: envUsername,
                password: envPassword
              });
            } else {
              console.log(`No valid Twitter credentials for agent ${agent.id}, using default client`);
            }
          }
        }
      } else {
        console.log(`No Twitter credentials provided for agent ${agent.id}, using default client`);
      }
      
      // Store the agent
      this.agents[agent.id] = agent;
      
      // Schedule posts for this agent
      this.scheduleAgentPosts(agent.id);
      
      return agent;
    } catch (error) {
      console.error(`Error loading agent from config:`, error);
      throw error;
    }
  }
  
  /**
   * Get an agent by ID
   */
  getAgent(agentId) {
    const agent = this.agents[agentId];
    if (!agent) {
      throw new Error(`Agent not found: ${agentId}`);
    }
    return agent;
  }
  
  /**
   * Schedule posts for an agent based on their posting frequency
   */
  scheduleAgentPosts(agentId) {
    const agent = this.getAgent(agentId);
    
    // Cancel existing schedule if any
    if (this.postSchedules[agentId]) {
      this.postSchedules[agentId].stop();
    }
    
    // Use a recurring check that schedules the next post dynamically
    // This allows for timing variations while maintaining consistent activity
    const checkInterval = 60 * 1000; // Check every minute
    
    // Schedule the recurring check
    this.postSchedules[agentId] = cron.schedule('* * * * *', () => {
      const now = Date.now();
      
      // If we have a next post time and it's in the past, create a post
      if (this.nextPostTimes[agentId] && now >= this.nextPostTimes[agentId]) {
        // Reset next post time
        this.nextPostTimes[agentId] = null;
        
        // Create the post
        this.createAgentPost(agentId);
        
        // Schedule the next post with randomized timing
        this.scheduleNextPost(agentId);
      } 
      // If we don't have a next post time scheduled, create one
      else if (!this.nextPostTimes[agentId]) {
        this.scheduleNextPost(agentId);
      }
    });
    
    // Schedule the first post with a short delay to start things off
    setTimeout(() => {
      this.scheduleNextPost(agentId);
    }, 10000); // 10 seconds delay
    
    console.log(`Scheduled posting for agent ${agentId}`);
  }
  
  /**
   * Schedule the next post for an agent with natural timing variations
   */
  scheduleNextPost(agentId) {
    const agent = this.getAgent(agentId);
    
    // Get randomized interval for next post
    const nextPostInterval = behaviorRandomizer.getNextPostInterval(agent);
    const nextPostTime = Date.now() + nextPostInterval;
    
    // Store the next post time
    this.nextPostTimes[agentId] = nextPostTime;
    
    // Log the schedule
    const minutesUntilPost = Math.round(nextPostInterval / (60 * 1000));
    console.log(`Scheduled next post for agent ${agentId} in ~${minutesUntilPost} minutes`);
  }
  
  /**
   * Create a new post for an agent
   */
  async createAgentPost(agentId, options = {}) {
    try {
      const agent = this.getAgent(agentId);
      
      // Check if enough time has passed since last post
      const now = Date.now();
      const minTimeBetweenPosts = agent.behavior.postFrequency.minHoursBetweenPosts * 60 * 60 * 1000;
      
      if (
        agent.lastPostTime && 
        now - agent.lastPostTime < minTimeBetweenPosts &&
        !options.ignoreTimeConstraint
      ) {
        console.log(`Too soon for agent ${agentId} to post again`);
        return null;
      }
      
      // Get custom system prompt from agent config or environment
      let customSystemPrompt = null;
      
      // First check if agent has a custom system prompt
      if (agent.customSystemPrompt) {
        customSystemPrompt = agent.customSystemPrompt;
        console.log(`Using custom system prompt from agent config for ${agentId}`);
      }
      // Fall back to environment variable if needed
      else if (process.env.CUSTOM_SYSTEM_PROMPT) {
        customSystemPrompt = process.env.CUSTOM_SYSTEM_PROMPT;
        console.log(`Using custom system prompt from environment for ${agentId}`);
      }
      
      // Randomize content preferences to add variety
      const contentPreferences = behaviorRandomizer.randomizeContentPreferences(
        agent.behavior.contentPreferences
      );
      
      // Create a shallow copy of the agent with randomized content preferences
      const agentWithRandomPrefs = { 
        ...agent,
        behavior: {
          ...agent.behavior,
          contentPreferences,
          interactionPatterns: behaviorRandomizer.randomizeInteractionPatterns(
            agent.behavior.interactionPatterns
          )
        }
      };
      
      // Generate content using LLM
      const postContent = await this.llmProvider.generateContent(agentWithRandomPrefs, {
        task: options.task || 'post',
        topic: options.topic,
        replyTo: options.replyTo,
        quoteTweet: options.quoteTweet,
        threadLength: options.threadLength,
        customSystemPrompt: customSystemPrompt
      });
      
      // Handle thread creation
      if (options.threadLength && options.threadLength > 1) {
        const threadContent = postContent.split('\n\n')
          .filter(text => text.trim().length > 0)
          .slice(0, options.threadLength);
        
        // Post the thread
        const tweets = await this.twitterClient.postThread(agentId, threadContent);
        
        // Record in memory
        tweets.forEach(tweet => {
          this.memoryManager.recordPost(agentId, tweet.content, tweet.id, {
            isThread: true,
            threadIds: tweets.map(t => t.id)
          });
        });
        
        // Update last post time
        agent.lastPostTime = now;
        
        return tweets;
      } else {
        // Post as a single tweet
        const tweetOptions = {};
        
        if (options.replyTo) {
          tweetOptions.replyToTweetId = options.replyTo.id;
        } else if (options.quoteTweet) {
          tweetOptions.quoteTweetId = options.quoteTweet.id;
        }
        
        // Send the tweet
        const tweet = await this.twitterClient.postTweet(agentId, postContent, tweetOptions);
        
        // Record in memory
        this.memoryManager.recordPost(agentId, tweet.content, tweet.id, {
          isReply: !!options.replyTo,
          isQuote: !!options.quoteTweet
        });
        
        // Update last post time
        agent.lastPostTime = now;
        
        // Schedule next post after a successful post
        if (!options.replyTo && !options.quoteTweet) {
          this.scheduleNextPost(agentId);
        }
        
        return tweet;
      }
    } catch (error) {
      console.error(`Error creating post for agent ${agentId}:`, error);
      throw error;
    }
  }
  
  /**
   * Process an agent reaction to a tweet
   */
  async processAgentReaction(agentId, tweet) {
    try {
      const agent = this.getAgent(agentId);
      
      // Skip if the tweet is from the agent itself
      if (tweet.authorId === agentId) {
        return null;
      }
      
      // For mentions and replies, always reply
      // Check for mentions in different ways to be thorough
      const isMention = 
        tweet.isDirectMention || // Check the direct mention flag first
        tweet.content.toLowerCase().includes(`@${agent.name.toLowerCase()}`) || 
        tweet.content.toLowerCase().includes(`@${agentId.toLowerCase()}`) || 
        tweet.replyToId && String(tweet.replyToId).includes(agentId);
      
      console.log(`Checking mention status for tweet: "${tweet.content.substring(0, 30)}..."`);
      console.log(`isMention: ${isMention}, author: ${tweet.authorId}, replyToId: ${tweet.replyToId}`);
      
      if (isMention) {
        console.log(`Detected mention of ${agentId}, creating reply immediately`);
        
        // For replies, we need to check if this is a reply to another tweet
        // If so, fetch that tweet to include in the context
        let originalTweet = null;
        let conversationHistory = [];
        let hasMeaningfulContext = false;
        
        if (tweet.replyToId) {
          try {
            console.log(`Fetching original tweet ${tweet.replyToId} for context`);
            originalTweet = await this.twitterClient.getTweet(tweet.replyToId);
            console.log(`Found original tweet: "${originalTweet.content.substring(0, 30)}..."`);
            hasMeaningfulContext = true;
            
            // Add to conversation history
            conversationHistory.push({
              role: originalTweet.authorId === agentId ? "agent" : "user",
              content: originalTweet.content
            });
            
            // Try to get one more level of conversation if possible
            if (originalTweet.replyToId) {
              try {
                console.log(`Fetching earlier tweet ${originalTweet.replyToId} for additional context`);
                const earlierTweet = await this.twitterClient.getTweet(originalTweet.replyToId);
                console.log(`Found earlier tweet: "${earlierTweet.content.substring(0, 30)}..."`);
                
                // Add to conversation history (in reverse chronological order)
                conversationHistory.unshift({
                  role: earlierTweet.authorId === agentId ? "agent" : "user",
                  content: earlierTweet.content
                });
              } catch (error) {
                console.error(`Error fetching earlier tweet ${originalTweet.replyToId}:`, error);
                // Continue anyway even if we couldn't fetch the earlier tweet
              }
            }
            
            // Add current tweet to conversation history
            conversationHistory.push({
              role: "user",
              content: tweet.content
            });
            
            // Enhance the context with the original tweet and conversation history
            tweet.originalTweet = originalTweet;
            tweet.conversationHistory = conversationHistory;
          } catch (error) {
            console.error(`Error fetching original tweet ${tweet.replyToId}:`, error);
            // Continue anyway even if we couldn't fetch the original
          }
        }
        
        // If there's no meaningful context, provide some default context
        if (!hasMeaningfulContext) {
          // Check if the tweet content is asking about context
          const tweetContent = tweet.content.toLowerCase();
          if (tweetContent.includes("what") && 
              (tweetContent.includes("tweet") || 
               tweetContent.includes("context") || 
               tweetContent.includes("talking about"))) {
            
            console.log("User is asking about context. Providing a response with fresh conversation starter.");
            
            // Create a reply immediately, with special flag to avoid context questions
            return this.createAgentPost(agentId, {
              task: 'reply',
              replyTo: tweet,
              avoidContextQuestions: true,  // Special flag to handle this case
              ignoreTimeConstraint: true // Allow replies anytime
            });
          }
        }
        
        // Create a reply immediately, bypassing the usual reaction generation
        return this.createAgentPost(agentId, {
          task: 'reply',
          replyTo: tweet,
          ignoreTimeConstraint: true // Allow replies anytime
        });
      }
      
      // Generate reaction using LLM
      const reaction = await this.llmProvider.generateReaction(agent, tweet);
      
      // Adjust probabilities based on configuration
      const { replyProbability, quoteTweetProbability, likeProbability } = 
        agent.behavior.interactionPatterns;
      
      // Strong preference for replies over quote tweets
      if (reaction.action === 'quote' && Math.random() > quoteTweetProbability * 0.5) {
        // 50% reduced chance of quote tweeting compared to configured probability
        console.log(`Agent ${agentId} chose to ignore instead of quote tweet based on probability settings`);
        reaction.action = 'ignore';
      }
      
      // Determine action based on reaction
      switch (reaction.action) {
        case 'reply':
          // Only reply if probability check passes
          if (Math.random() <= replyProbability) {
            // For regular replies, also fetch the original tweet for context if needed
            if (!tweet.originalTweet && tweet.id) {
              try {
                console.log(`Fetching tweet ${tweet.id} for reply context`);
                // We already have this tweet, just ensure it's properly assigned
                tweet.originalTweet = tweet;
              } catch (error) {
                console.error(`Error ensuring tweet context for ${tweet.id}:`, error);
              }
            }
            
            // Create a reply
            return this.createAgentPost(agentId, {
              task: 'reply',
              replyTo: tweet,
              ignoreTimeConstraint: true // Allow replies anytime
            });
          } else {
            console.log(`Agent ${agentId} chose not to reply based on probability settings`);
            return null;
          }
          
        case 'quote':
          // Create a quote tweet
          return this.createAgentPost(agentId, {
            task: 'quote_tweet',
            quoteTweet: tweet,
            ignoreTimeConstraint: true // Allow quotes anytime
          });
          
        case 'like':
          // Like the tweet
          if (Math.random() <= likeProbability) {
            await this.twitterClient.likeTweet(agentId, tweet.id);
            
            // Record the interaction
            this.updateAgentRelationship(agentId, tweet.authorId, {
              description: `I liked ${tweet.authorId}'s tweet: "${tweet.content.substring(0, 50)}..."`
            });
            
            return { action: 'like', tweetId: tweet.id };
          } else {
            console.log(`Agent ${agentId} chose not to like based on probability settings`);
            return null;
          }
          
        case 'ignore':
        default:
          // No action
          return null;
      }
    } catch (error) {
      console.error(`Error processing reaction for agent ${agentId}:`, error);
      throw error;
    }
  }
  
  /**
   * Process an event for an agent
   */
  async processAgentEvent(agentId, event) {
    try {
      const agent = this.getAgent(agentId);
      
      // Skip if not targeted at this agent and not a broadcast
      if (
        event.targetAgentIds && 
        event.targetAgentIds.length > 0 && 
        !event.targetAgentIds.includes(agentId)
      ) {
        return;
      }
      
      switch (event.type) {
        case 'news':
          // Process news event - might trigger a post
          const newsUpdate = await this.llmProvider.generateMemoryUpdate(agent, event);
          
          // Update memory
          this.memoryManager.addMemory(
            agentId,
            newsUpdate.memory || `News: ${event.data.headline}`,
            'event',
            { importance: newsUpdate.importance }
          );
          
          // Update mood
          agent.updateMood(
            newsUpdate.valenceShift,
            newsUpdate.arousalShift,
            newsUpdate.dominanceShift
          );
          
          // Possibly create a post about this news
          if (newsUpdate.importance > 0.7 || Math.random() < 0.3) {
            return this.createAgentPost(agentId, {
              topic: event.data.headline
            });
          }
          break;
          
        case 'mood_shift':
          // Process mood event
          this.memoryManager.addMemory(
            agentId,
            event.data.description,
            'event',
            { importance: 0.6 }
          );
          
          // Update mood
          agent.updateMood(
            event.data.valenceShift,
            event.data.arousalShift,
            event.data.dominanceShift
          );
          
          // High arousal events might trigger a post
          if (event.data.arousalShift > 0.3 || Math.random() < 0.2) {
            return this.createAgentPost(agentId);
          }
          break;
          
        case 'interaction_prompt':
          // Process interaction prompt
          if (event.data.initiatorId === agentId) {
            // This agent is prompted to interact with another
            const targetId = event.data.targetId;
            
            // Get some recent posts from the target agent
            // In a real implementation, this would fetch from Twitter
            // For now, we'll just generate a post to respond to
            const fakePost = {
              id: `fake-${Date.now()}`,
              content: `This is a fake post about ${event.data.topic} for testing`,
              authorId: targetId,
              createdAt: new Date()
            };
            
            // Process reaction to the post
            return this.processAgentReaction(agentId, fakePost);
          }
          break;
      }
    } catch (error) {
      console.error(`Error processing event for agent ${agentId}:`, error);
      throw error;
    }
  }
  
  /**
   * Update an agent's relationship with another agent
   */
  async updateAgentRelationship(agentId, targetAgentId, interaction) {
    try {
      const agent = this.getAgent(agentId);
      
      // Generate relationship update
      const update = await this.llmProvider.generateRelationshipUpdate(
        agent, 
        targetAgentId, 
        interaction
      );
      
      // Apply the update
      this.memoryManager.updateRelationship(agentId, targetAgentId, {
        sentiment: (agent.memory.relationships[targetAgentId]?.sentiment || 0) + update.sentimentChange,
        familiarity: (agent.memory.relationships[targetAgentId]?.familiarity || 0) + update.familiarityChange,
        trust: (agent.memory.relationships[targetAgentId]?.trust || 0) + update.trustChange,
        notes: update.note ? [update.note] : [],
        recentInteractions: [interaction.description]
      });
      
      return update;
    } catch (error) {
      console.error(`Error updating relationship for agent ${agentId} with ${targetAgentId}:`, error);
      throw error;
    }
  }
  
  /**
   * Set up event listeners
   */
  setupEventListeners() {
    // Listen for all events
    this.eventEngine.addEventListener('all', async (event) => {
      // Process the event for each agent
      for (const agentId of Object.keys(this.agents)) {
        await this.processAgentEvent(agentId, event);
      }
    });
  }
  
  /**
   * Start monitoring Twitter for mentions for all agents
   */
  async startMonitoringMentions(intervalMs = 30000) {
    console.log(`Starting to monitor Twitter mentions every ${intervalMs/1000} seconds`);
    
    // Track last seen mention ID per agent
    const lastMentionIds = {};
    
    // Set up periodic checking
    setInterval(async () => {
      // Only check one agent at a time in rotation to avoid rate limits
      const agentIds = Object.keys(this.agents);
      const currentTime = Date.now();
      const agentIndex = Math.floor(currentTime / intervalMs) % agentIds.length;
      const agentId = agentIds[agentIndex];
      
      try {
        console.log(`Checking mentions for agent ${agentId}...`);
        // Get mentions for this agent
        const mentions = await this.twitterClient.getAgentMentions(
          agentId, 
          { sinceId: lastMentionIds[agentId] }
        );
        
        if (mentions.length > 0) {
          console.log(`Found ${mentions.length} new mentions for agent ${agentId}`);
          
          // Update last seen mention ID
          lastMentionIds[agentId] = mentions[0].id;
          
          // Process each mention - immediately reply to all
          for (const mention of mentions) {
            // Add more details to the mention
            mention.isDirectMention = true;  // Force treating as direct mention
            
            // If this is a reply to another tweet, fetch that tweet for context
            if (mention.replyToId) {
              try {
                console.log(`Fetching original tweet ${mention.replyToId} for mention context`);
                const originalTweet = await this.twitterClient.getTweet(mention.replyToId);
                console.log(`Found original tweet: "${originalTweet.content.substring(0, 30)}..."`);
                
                // Create conversation history
                let conversationHistory = [];
                
                // Add original tweet to conversation history
                conversationHistory.push({
                  role: originalTweet.authorId === agentId ? "agent" : "user",
                  content: originalTweet.content
                });
                
                // Try to get one more level of conversation if possible
                if (originalTweet.replyToId) {
                  try {
                    console.log(`Fetching earlier tweet ${originalTweet.replyToId} for additional context`);
                    const earlierTweet = await this.twitterClient.getTweet(originalTweet.replyToId);
                    console.log(`Found earlier tweet: "${earlierTweet.content.substring(0, 30)}..."`);
                    
                    // Add to conversation history (in reverse chronological order)
                    conversationHistory.unshift({
                      role: earlierTweet.authorId === agentId ? "agent" : "user",
                      content: earlierTweet.content
                    });
                  } catch (error) {
                    console.error(`Error fetching earlier tweet ${originalTweet.replyToId}:`, error);
                    // Continue anyway even if we couldn't fetch the earlier tweet
                  }
                }
                
                // Add current mention to conversation history
                conversationHistory.push({
                  role: "user",
                  content: mention.content
                });
                
                // Enhance the mention with context
                mention.originalTweet = originalTweet;
                mention.conversationHistory = conversationHistory;
              } catch (error) {
                console.error(`Error fetching original tweet for mention ${mention.id}:`, error);
              }
            }
            
            await this.processAgentReaction(agentId, mention);
          }
        }
      } catch (error) {
        console.error(`Error checking mentions for agent ${agentId}:`, error);
      }
    }, intervalMs);
  }
}

module.exports = AgentManager; 