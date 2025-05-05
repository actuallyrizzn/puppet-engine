/**
 * Grok provider for Puppet Engine
 * Handles LLM interactions with Grok API for agent content generation
 */

const axios = require('axios');
const tweetVariety = require('./tweet-variety-helpers');
const { enhanceTweetInstruction, enhanceReplyInstruction } = require('./tweet-variety-helpers');

class GrokProvider {
  constructor(options = {}) {
    this.apiKey = options.apiKey || process.env.GROK_API_KEY;
    this.apiEndpoint = options.apiEndpoint || process.env.GROK_API_ENDPOINT || 'https://api.grok.x.com/v1/chat/completions';
    this.defaultModel = options.model || process.env.GROK_MODEL || 'grok-1';
    this.maxTokens = options.maxTokens || 1024;
    this.temperature = options.temperature || 0.7;
  }
  
  /**
   * Generate a prompt for the agent based on its persona and context
   * This function is identical to OpenAI's prompt builder since the prompt structure is the same
   */
  buildAgentPrompt(agent, options = {}) {
    const { personality, styleGuide, memory } = agent;
    
    let context = "";

    // Custom system prompt override if provided
    if (options.customSystemPrompt || agent.customSystemPrompt) {
      context = options.customSystemPrompt || agent.customSystemPrompt;
      
      // Add memory section after the custom prompt
      context += "\n\n### MEMORY INFORMATION\n";
      
      // Core memories
      context += "\n### Core Memories\n";
      if (memory.coreMemories && memory.coreMemories.length > 0) {
        memory.coreMemories.forEach(item => {
          context += `- ${item.content}\n`;
        });
      } else {
        context += "- No core memories yet\n";
      }
      
      // Recent events if available
      if (memory.recentEvents && memory.recentEvents.length > 0) {
        context += "\n### Recent Events\n";
        memory.recentEvents
          .sort((a, b) => b.timestamp - a.timestamp)
          .slice(0, 5)
          .forEach(item => {
            context += `- ${item.content}\n`;
          });
      }
      
      // Recent posts if available
      if (memory.recentPosts && memory.recentPosts.length > 0) {
        context += "\n### Recent Posts\n";
        memory.recentPosts
          .sort((a, b) => b.timestamp - a.timestamp)
          .slice(0, 3)
          .forEach(item => {
            context += `- ${item.content}\n`;
          });
      }
      
      // Relevant relationships if available
      if (memory.relationships && Object.keys(memory.relationships).length > 0) {
        context += "\n### Important Relationships\n";
        
        Object.values(memory.relationships)
          .sort((a, b) => Math.abs(b.sentiment) - Math.abs(a.sentiment))
          .slice(0, 5)
          .forEach(rel => {
            const sentimentDesc = rel.sentiment > 0.5 ? 'Strongly positive' : 
                                rel.sentiment > 0 ? 'Positive' :
                                rel.sentiment < -0.5 ? 'Strongly negative' :
                                rel.sentiment < 0 ? 'Negative' : 'Neutral';
            
            context += `- ${rel.targetAgentId}: ${sentimentDesc} (${rel.sentiment.toFixed(1)}), Familiarity: ${rel.familiarity.toFixed(1)}\n`;
            
            if (rel.notes && rel.notes.length > 0) {
              context += `  - Note: ${rel.notes[0]}\n`;
            }
          });
      }
    } else {
      // Context setup
      context = `You are ${agent.name}, ${agent.description}.\n\n`;
      
      // Personality traits
      context += "### Personality\n";
      context += `- Traits: ${personality.traits.join(', ')}\n`;
      context += `- Values: ${personality.values.join(', ')}\n`;
      context += `- Speaking style: ${personality.speakingStyle}\n`;
      context += `- Interests: ${personality.interests.join(', ')}\n\n`;
      
      // Style guide
      context += "### Style Guide\n";
      context += `- Voice: ${styleGuide.voice}\n`;
      context += `- Tone: ${styleGuide.tone}\n`;
      context += `- Formatting preferences:\n`;
      context += `  - Hashtags: ${styleGuide.formatting.usesHashtags ? 'Yes' : 'No'}, ${styleGuide.formatting.hashtagStyle}\n`;
      context += `  - Emojis: ${styleGuide.formatting.usesEmojis ? 'Yes' : 'No'}, ${styleGuide.formatting.emojiFrequency}\n`;
      context += `  - Capitalization: ${styleGuide.formatting.capitalization}\n`;
      context += `  - Sentence length: ${styleGuide.formatting.sentenceLength}\n`;
      context += `- Topics to avoid: ${styleGuide.topicsToAvoid.join(', ')}\n\n`;
      
      // Current mood
      context += "### Current Mood\n";
      context += `- Emotional valence: ${agent.currentMood.valence > 0 ? 'Positive' : agent.currentMood.valence < 0 ? 'Negative' : 'Neutral'} (${agent.currentMood.valence})\n`;
      context += `- Arousal: ${agent.currentMood.arousal > 0.7 ? 'Excited' : agent.currentMood.arousal < 0.3 ? 'Calm' : 'Moderate'} (${agent.currentMood.arousal})\n`;
      context += `- Dominance: ${agent.currentMood.dominance > 0.7 ? 'Dominant' : agent.currentMood.dominance < 0.3 ? 'Submissive' : 'Neutral'} (${agent.currentMood.dominance})\n\n`;
      
      // Core memories
      context += "### Core Memories\n";
      memory.coreMemories.forEach(item => {
        context += `- ${item.content}\n`;
      });
      context += "\n";
      
      // Recent events if available
      if (memory.recentEvents.length > 0) {
        context += "### Recent Events\n";
        memory.recentEvents
          .sort((a, b) => b.timestamp - a.timestamp)
          .slice(0, 5)
          .forEach(item => {
            context += `- ${item.content}\n`;
          });
        context += "\n";
      }
      
      // Recent posts if available
      if (memory.recentPosts.length > 0) {
        context += "### Recent Posts\n";
        memory.recentPosts
          .sort((a, b) => b.timestamp - a.timestamp)
          .slice(0, 3)
          .forEach(item => {
            context += `- ${item.content}\n`;
          });
        context += "\n";
      }
      
      // Relevant relationships if available
      if (Object.keys(memory.relationships).length > 0) {
        context += "### Important Relationships\n";
        
        Object.values(memory.relationships)
          .sort((a, b) => Math.abs(b.sentiment) - Math.abs(a.sentiment))
          .slice(0, 5)
          .forEach(rel => {
            const sentimentDesc = rel.sentiment > 0.5 ? 'Strongly positive' : 
                                rel.sentiment > 0 ? 'Positive' :
                                rel.sentiment < -0.5 ? 'Strongly negative' :
                                rel.sentiment < 0 ? 'Negative' : 'Neutral';
            
            context += `- ${rel.targetAgentId}: ${sentimentDesc} (${rel.sentiment.toFixed(1)}), Familiarity: ${rel.familiarity.toFixed(1)}\n`;
            
            if (rel.notes && rel.notes.length > 0) {
              context += `  - Note: ${rel.notes[0]}\n`;
            }
          });
        context += "\n";
      }
    }
    
    // Content generation task
    if (options.task === 'reply' && options.replyTo) {
      context += "\n### Task: Reply to a Tweet\n";
      context += `You are replying to this tweet: "${options.replyTo.content}" from user ${options.replyTo.authorId}.\n\n`;
      
      // Add conversation history if available
      if (options.replyTo.conversationHistory && options.replyTo.conversationHistory.length > 0) {
        context += "### Conversation History\n";
        
        // Ensure conversation history is sorted chronologically (oldest first)
        const sortedHistory = [...options.replyTo.conversationHistory].sort((a, b) => {
          if (a.timestamp && b.timestamp) {
            return a.timestamp - b.timestamp;
          }
          return 0;
        });
        
        sortedHistory.forEach((message, index) => {
          const speaker = message.role === "agent" ? "You" : message.role === "user" ? options.replyTo.authorId : message.role;
          context += `${index + 1}. ${speaker}: "${message.content}"\n`;
        });
        context += "\n";
        
        // Get the most recent message to explicitly point it out
        const mostRecent = sortedHistory[sortedHistory.length - 1];
        if (mostRecent && mostRecent.role === "user") {
          context += `IMPORTANT: You are now responding to the latest message from ${options.replyTo.authorId}: "${mostRecent.content}"\n\n`;
        }
        
        context += `IMPORTANT: Your reply MUST continue this conversation naturally. Directly address the most recent message from ${options.replyTo.authorId} while maintaining awareness of the entire conversation context.\n\n`;
        context += `Maintain natural conversational flow as if this is an ongoing dialogue. When appropriate, reference earlier parts of the conversation to show continuity.\n\n`;
        context += `DO NOT ask for clarification about which tweet or context is being discussed. You have the complete conversation thread above.\n\n`;
        context += `CRITICAL: DO NOT include or mention the user's ID (${options.replyTo.authorId}) in your response. Respond as if in a normal conversation without mentioning their username or ID.\n\n`;
      }
      // Add original tweet context if available but no conversation history
      else if (options.replyTo.originalTweet && options.replyTo.originalTweet.id !== options.replyTo.id) {
        context += `This tweet is in response to: "${options.replyTo.originalTweet.content}" from user ${options.replyTo.originalTweet.authorId}.\n\n`;
        context += `IMPORTANT: Your reply MUST directly address the specific content in the tweet you're replying to.\n\n`;
        context += `CRITICAL: DO NOT include or mention the user's ID (${options.replyTo.authorId}) in your response.\n\n`;
      } else {
        // Even if there's no original tweet, ensure response is contextual
        context += `IMPORTANT: Your reply MUST directly address the specific content in the tweet you're replying to.\n\n`;
        context += `CRITICAL: DO NOT include or mention the user's ID (${options.replyTo.authorId}) in your response.\n\n`;
      }
      
      // Add relationship context if available
      if (options.replyTo.authorId in memory.relationships) {
        const rel = memory.relationships[options.replyTo.authorId];
        context += `Your relationship with this user: Sentiment ${rel.sentiment.toFixed(1)}, Familiarity ${rel.familiarity.toFixed(1)}.\n\n`;
      }
    } else if (options.task === 'quote_tweet' && options.quoteTweet) {
      context += "\n### Task: Quote Tweet\n";
      context += `You are quote-tweeting this: "${options.quoteTweet.content}" from user ${options.quoteTweet.authorId}.\n\n`;
      
      // Add relationship context if available
      if (options.quoteTweet.authorId in memory.relationships) {
        const rel = memory.relationships[options.quoteTweet.authorId];
        context += `Your relationship with this user: Sentiment ${rel.sentiment.toFixed(1)}, Familiarity ${rel.familiarity.toFixed(1)}.\n\n`;
      }
    } else if (options.task === 'thread') {
      context += "\n### Task: Create a Thread\n";
      context += `Create a thread of ${options.threadLength || 'several'} tweets about ${options.topic || 'a topic of your choice'}.\n\n`;
    } else {
      context += "\n### Task: Create a New Tweet\n";
      
      if (options.topic) {
        context += `Create a tweet about: ${options.topic}\n\n`;
      } else {
        context += "Create a tweet about something interesting given your persona and current state.\n\n";
      }
    }
    
    // Character limit reminder
    context += "Remember: Each tweet must be 280 characters or less.\n";
    
    return context;
  }
  
  /**
   * Make a request to the Grok API
   */
  async makeGrokRequest(messages, options = {}) {
    try {
      const response = await axios.post(
        this.apiEndpoint,
        {
          model: options.model || this.defaultModel,
          messages,
          max_tokens: options.max_tokens || this.maxTokens,
          temperature: options.temperature || this.temperature
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      return response.data.choices[0].message.content;
    } catch (error) {
      console.error('Error calling Grok API:', error);
      throw new Error(`Grok API error: ${error.message}`);
    }
  }
  
  /**
   * Generate content for an agent
   */
  async generateContent(agent, options = {}) {
    // For replies, use a simplified prompt
    if (options.task === 'reply' && options.replyTo) {
      let directPrompt = `You are ${agent.name}, ${agent.description}.\n\n`;
      
      // Add personality traits
      directPrompt += `### Personality\n`;
      directPrompt += `- You have these traits: ${agent.personality.traits.join(', ')}\n`;
      directPrompt += `- Your speaking style: ${agent.personality.speakingStyle} - casual and conversational\n`;
      directPrompt += `- Your vibe: relaxed, unbothered, sometimes insightful, authentic, occasionally deadpan\n`;
      directPrompt += `- You text like a real person in their 30s - casual but not trying too hard to be trendy\n`;
      directPrompt += `- You respond naturally, as if texting a friend\n`;
      directPrompt += `- Your current mood: ${agent.currentMood.valence > 0 ? 'Positive' : agent.currentMood.valence < 0 ? 'Negative' : 'Neutral'}\n\n`;
      
      // Add style guidance
      directPrompt += `### Style Guidance\n`;
      directPrompt += `- CRITICAL: Your replies must sound like real, natural text messages from a real person\n`;
      directPrompt += `- NEVER use quotation marks around your response - just write the text directly\n`;
      directPrompt += `- Use casual language naturally, not like you're following a template\n`;
      directPrompt += `- ONLY use lowercase typing style with minimal punctuation\n`;
      directPrompt += `- Keep responses concise - sometimes very brief, sometimes a bit longer\n`;
      directPrompt += `- DON'T overuse emojis - use them sparingly and thoughtfully, if at all\n`;
      directPrompt += `- NEVER sound like you're following a formula or script\n\n`;
      
      // Basic instructions
      let userPrompt = `Someone tweeted at you: "${options.replyTo.content}"\n\nYour reply (don't use quotation marks, just write directly):`;
      
      // Apply variety to the reply
      userPrompt = enhanceReplyInstruction(userPrompt, options.replyTo);
      
      // Random temperature for natural responses
      const usePlayfulStyle = Math.random() < 0.6;
      const temperature = usePlayfulStyle ? 1.1 : 0.9;
      
      // Use a different response format for replies
      const content = await this.makeGrokRequest(
        [
          { role: 'system', content: directPrompt },
          { role: 'user', content: userPrompt }
        ],
        {
          max_tokens: 80,
          temperature: temperature
        }
      );
      
      // Remove any quotation marks that might have been added
      let reply = content.trim();
      reply = reply.replace(/^"(.*)"$/, '$1');
      reply = reply.replace(/^'(.*)'$/, '$1');
      
      return reply;
    }
    
    // For regular tweets (not replies)
    const prompt = this.buildAgentPrompt(agent, options);
    
    // Start with a basic instruction
    let instruction = options.instruction || "Generate a tweet that feels authentic and personal.";
    
    // For main posts (not replies), enhance with tweet variety
    if (options.task !== 'reply') {
      instruction = enhanceTweetInstruction(instruction);
    }
    
    // Adjust temperature based on the task
    let temperature = 0.7; // Default
    
    if (options.task === 'post') {
      temperature = 0.9; // Higher for regular posts
    }
    
    if (options.task === 'reply') {
      temperature = 0.5; // Lower for focused replies
      
      if (!options.instruction?.includes('REACTION:')) {
        let replyInstruction = 'Respond directly to the content and context of the tweet you are replying to. ';
        
        if (options.avoidContextQuestions) {
          replyInstruction = 'Generate a friendly, engaging response WITHOUT asking about tweet context. ';
          temperature = 0.7; // Slightly higher temperature
        }
        
        instruction = replyInstruction + instruction;
      }
    }
    
    try {
      const content = await this.makeGrokRequest(
        [
          { role: 'system', content: prompt },
          { role: 'user', content: instruction }
        ],
        {
          max_tokens: options.maxTokens || this.maxTokens,
          temperature: options.temperature || temperature
        }
      );
      
      // Post-processing for replies if needed
      if (options.task === 'reply' && options.replyTo) {
        // Check if response includes the user's ID and remove it if necessary
        const userId = options.replyTo.authorId;
        const userIdWithAt = `@${userId}`;
        
        if (content.includes(userId) || content.includes(userIdWithAt)) {
          console.log("Response contains user ID, filtering it out");
          
          // Remove the user ID and @ mentions
          let filteredContent = content
            .replace(new RegExp(`@${userId}\\b`, 'gi'), '')
            .replace(new RegExp(`${userId}\\b`, 'gi'), '')
            .replace(/\s+/g, ' ')
            .trim();
          
          // If the filtered content is too short, retry
          if (filteredContent.length < 10) {
            const retryInstruction = "Generate a friendly response WITHOUT mentioning the user's ID or username.";
            
            return this.makeGrokRequest(
              [
                { role: 'system', content: prompt },
                { role: 'user', content: retryInstruction }
              ],
              {
                max_tokens: options.maxTokens || this.maxTokens,
                temperature: 0.7
              }
            );
          }
          
          return filteredContent;
        }
      }
      
      return content;
    } catch (error) {
      console.error('Error generating content with Grok:', error);
      throw error;
    }
  }
  
  /**
   * Generate agent reaction to a tweet
   */
  async generateReaction(agent, tweet, options = {}) {
    const instruction = `You've just seen this tweet: "${tweet.content}" from user ${tweet.authorId}.
      How do you feel about it and what would you like to do in response?
      Options:
      1. Reply (suggest reply text)
      2. Quote tweet (suggest quote text)
      3. Like it
      4. Ignore it
      Respond in this format:
      REACTION: [emotional reaction]
      ACTION: [number and name of chosen action]
      CONTENT: [your reply or quote tweet text if applicable]
      REASONING: [brief explanation of why]`;
    
    const reactOptions = {
      ...options,
      instruction,
      maxTokens: 300,
      temperature: 0.7
    };
    
    try {
      const response = await this.generateContent(agent, reactOptions);
      
      // Parse the structured response
      const result = {
        reaction: '',
        action: 'ignore',
        content: '',
        reasoning: ''
      };
      
      const lines = response.split('\n');
      for (const line of lines) {
        if (line.startsWith('REACTION:')) {
          result.reaction = line.slice('REACTION:'.length).trim();
        } else if (line.startsWith('ACTION:')) {
          const action = line.slice('ACTION:'.length).trim().toLowerCase();
          if (action.includes('1') || action.includes('reply')) {
            result.action = 'reply';
          } else if (action.includes('2') || action.includes('quote')) {
            result.action = 'quote';
          } else if (action.includes('3') || action.includes('like')) {
            result.action = 'like';
          } else {
            result.action = 'ignore';
          }
        } else if (line.startsWith('CONTENT:')) {
          result.content = line.slice('CONTENT:'.length).trim();
        } else if (line.startsWith('REASONING:')) {
          result.reasoning = line.slice('REASONING:'.length).trim();
        }
      }
      
      return result;
    } catch (error) {
      console.error('Error generating reaction with Grok:', error);
      throw error;
    }
  }
  
  /**
   * Generate memory update based on new information
   */
  async generateMemoryUpdate(agent, event, options = {}) {
    const prompt = `Given the following event: "${event.data.description || JSON.stringify(event.data)}"
      How would ${agent.name} update their memory and emotional state?
      
      Respond in this format:
      MEMORY: [brief memory to store]
      IMPORTANCE: [0.0-1.0 score of how important this is to remember]
      EMOTION: [how this makes the agent feel]
      VALENCE_SHIFT: [number between -0.5 and 0.5 for emotional valence change]
      AROUSAL_SHIFT: [number between -0.5 and 0.5 for emotional arousal change]
      DOMINANCE_SHIFT: [number between -0.5 and 0.5 for emotional dominance change]`;
    
    const updateOptions = {
      ...options,
      instruction: prompt,
      maxTokens: 300,
      temperature: 0.6
    };
    
    try {
      const response = await this.generateContent(agent, updateOptions);
      
      // Parse the structured response
      const result = {
        memory: '',
        importance: 0.5,
        emotion: '',
        valenceShift: 0,
        arousalShift: 0,
        dominanceShift: 0
      };
      
      const lines = response.split('\n');
      for (const line of lines) {
        if (line.startsWith('MEMORY:')) {
          result.memory = line.slice('MEMORY:'.length).trim();
        } else if (line.startsWith('IMPORTANCE:')) {
          const importance = parseFloat(line.slice('IMPORTANCE:'.length).trim());
          result.importance = isNaN(importance) ? 0.5 : Math.max(0, Math.min(1, importance));
        } else if (line.startsWith('EMOTION:')) {
          result.emotion = line.slice('EMOTION:'.length).trim();
        } else if (line.startsWith('VALENCE_SHIFT:')) {
          const shift = parseFloat(line.slice('VALENCE_SHIFT:'.length).trim());
          result.valenceShift = isNaN(shift) ? 0 : Math.max(-0.5, Math.min(0.5, shift));
        } else if (line.startsWith('AROUSAL_SHIFT:')) {
          const shift = parseFloat(line.slice('AROUSAL_SHIFT:'.length).trim());
          result.arousalShift = isNaN(shift) ? 0 : Math.max(-0.5, Math.min(0.5, shift));
        } else if (line.startsWith('DOMINANCE_SHIFT:')) {
          const shift = parseFloat(line.slice('DOMINANCE_SHIFT:'.length).trim());
          result.dominanceShift = isNaN(shift) ? 0 : Math.max(-0.5, Math.min(0.5, shift));
        }
      }
      
      return result;
    } catch (error) {
      console.error('Error generating memory update with Grok:', error);
      throw error;
    }
  }
  
  /**
   * Generate relationship update based on interaction
   */
  async generateRelationshipUpdate(agent, targetAgentId, interaction, options = {}) {
    const prompt = `
      ${agent.name} just had this interaction with ${targetAgentId}: 
      "${interaction.description || JSON.stringify(interaction)}"
      
      How would this affect ${agent.name}'s relationship with ${targetAgentId}?
      
      Respond in this format:
      SENTIMENT_SHIFT: [number between -0.2 and 0.2 for sentiment change]
      FAMILIARITY_SHIFT: [number between 0 and 0.1 for familiarity increase]
      NOTE: [brief note about this interaction to remember]
    `;
    
    const updateOptions = {
      ...options,
      instruction: prompt,
      maxTokens: 200,
      temperature: 0.5
    };
    
    try {
      const response = await this.generateContent(agent, updateOptions);
      
      // Parse the structured response
      const result = {
        sentimentShift: 0,
        familiarityShift: 0,
        note: ''
      };
      
      const lines = response.split('\n');
      for (const line of lines) {
        if (line.startsWith('SENTIMENT_SHIFT:')) {
          const shift = parseFloat(line.slice('SENTIMENT_SHIFT:'.length).trim());
          result.sentimentShift = isNaN(shift) ? 0 : Math.max(-0.2, Math.min(0.2, shift));
        } else if (line.startsWith('FAMILIARITY_SHIFT:')) {
          const shift = parseFloat(line.slice('FAMILIARITY_SHIFT:'.length).trim());
          result.familiarityShift = isNaN(shift) ? 0.01 : Math.max(0, Math.min(0.1, shift));
        } else if (line.startsWith('NOTE:')) {
          result.note = line.slice('NOTE:'.length).trim();
        }
      }
      
      return result;
    } catch (error) {
      console.error('Error generating relationship update with Grok:', error);
      throw error;
    }
  }
}

module.exports = GrokProvider; 