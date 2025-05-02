/**
 * OpenAI provider for Puppet Engine
 * Handles LLM interactions for agent content generation
 */

const { OpenAI } = require('openai');

class OpenAIProvider {
  constructor(options = {}) {
    this.client = new OpenAI({
      apiKey: options.apiKey || process.env.OPENAI_API_KEY
    });
    
    this.defaultModel = options.model || process.env.OPENAI_MODEL || 'gpt-4-turbo';
    this.maxTokens = options.maxTokens || 1024;
    this.temperature = options.temperature || 0.7;
  }
  
  /**
   * Generate a prompt for the agent based on its persona and context
   */
  buildAgentPrompt(agent, options = {}) {
    const { personality, styleGuide, memory } = agent;
    
    // Custom system prompt override if provided
    if (options.customSystemPrompt) {
      return options.customSystemPrompt;
    }
    
    // Context setup
    let context = `You are ${agent.name}, ${agent.description}.\n\n`;
    
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
    
    // Content generation task
    if (options.task === 'reply' && options.replyTo) {
      context += "### Task: Reply to a Tweet\n";
      context += `You are replying to this tweet: "${options.replyTo.content}" from user ${options.replyTo.authorId}.\n\n`;
      
      // Add relationship context if available
      if (options.replyTo.authorId in memory.relationships) {
        const rel = memory.relationships[options.replyTo.authorId];
        context += `Your relationship with this user: Sentiment ${rel.sentiment.toFixed(1)}, Familiarity ${rel.familiarity.toFixed(1)}.\n\n`;
      }
    } else if (options.task === 'quote_tweet' && options.quoteTweet) {
      context += "### Task: Quote Tweet\n";
      context += `You are quote-tweeting this: "${options.quoteTweet.content}" from user ${options.quoteTweet.authorId}.\n\n`;
      
      // Add relationship context if available
      if (options.quoteTweet.authorId in memory.relationships) {
        const rel = memory.relationships[options.quoteTweet.authorId];
        context += `Your relationship with this user: Sentiment ${rel.sentiment.toFixed(1)}, Familiarity ${rel.familiarity.toFixed(1)}.\n\n`;
      }
    } else if (options.task === 'thread') {
      context += "### Task: Create a Thread\n";
      context += `Create a thread of ${options.threadLength || 'several'} tweets about ${options.topic || 'a topic of your choice'}.\n\n`;
    } else {
      context += "### Task: Create a New Tweet\n";
      
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
   * Generate content for an agent
   */
  async generateContent(agent, options = {}) {
    const prompt = this.buildAgentPrompt(agent, options);
    
    const requestOptions = {
      model: options.model || this.defaultModel,
      messages: [
        { role: 'system', content: prompt },
        { role: 'user', content: options.instruction || 'Write your tweet now.' }
      ],
      max_tokens: options.maxTokens || this.maxTokens,
      temperature: options.temperature || this.temperature
    };
    
    try {
      const response = await this.client.chat.completions.create(requestOptions);
      return response.choices[0].message.content.trim();
    } catch (error) {
      console.error('Error generating content with OpenAI:', error);
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
      console.error('Error generating reaction with OpenAI:', error);
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
          result.importance = parseFloat(line.slice('IMPORTANCE:'.length).trim()) || 0.5;
        } else if (line.startsWith('EMOTION:')) {
          result.emotion = line.slice('EMOTION:'.length).trim();
        } else if (line.startsWith('VALENCE_SHIFT:')) {
          result.valenceShift = parseFloat(line.slice('VALENCE_SHIFT:'.length).trim()) || 0;
        } else if (line.startsWith('AROUSAL_SHIFT:')) {
          result.arousalShift = parseFloat(line.slice('AROUSAL_SHIFT:'.length).trim()) || 0;
        } else if (line.startsWith('DOMINANCE_SHIFT:')) {
          result.dominanceShift = parseFloat(line.slice('DOMINANCE_SHIFT:'.length).trim()) || 0;
        }
      }
      
      // Ensure values are within bounds
      result.importance = Math.max(0, Math.min(1, result.importance));
      result.valenceShift = Math.max(-0.5, Math.min(0.5, result.valenceShift));
      result.arousalShift = Math.max(-0.5, Math.min(0.5, result.arousalShift));
      result.dominanceShift = Math.max(-0.5, Math.min(0.5, result.dominanceShift));
      
      return result;
    } catch (error) {
      console.error('Error generating memory update with OpenAI:', error);
      throw error;
    }
  }
  
  /**
   * Generate relationship update after interaction with another agent
   */
  async generateRelationshipUpdate(agent, targetAgentId, interaction, options = {}) {
    const memory = agent.memory;
    const relationship = memory.relationships[targetAgentId] || { 
      sentiment: 0, 
      familiarity: 0.1,
      trust: 0 
    };
    
    const prompt = `${agent.name} just had this interaction with ${targetAgentId}:
      "${interaction.description || JSON.stringify(interaction)}"
      
      Current relationship:
      - Sentiment: ${relationship.sentiment} (-1.0 to 1.0)
      - Familiarity: ${relationship.familiarity} (0.0 to 1.0)
      - Trust: ${relationship.trust} (0.0 to 1.0)
      
      How would this interaction affect their relationship? Respond in this format:
      SENTIMENT_CHANGE: [number between -0.2 and 0.2]
      FAMILIARITY_CHANGE: [number between 0 and 0.1]
      TRUST_CHANGE: [number between -0.2 and 0.2]
      NOTE: [brief note about this interaction to remember]`;
    
    const updateOptions = {
      ...options,
      instruction: prompt,
      maxTokens: 250,
      temperature: 0.6
    };
    
    try {
      const response = await this.generateContent(agent, updateOptions);
      
      // Parse the structured response
      const result = {
        sentimentChange: 0,
        familiarityChange: 0,
        trustChange: 0,
        note: ''
      };
      
      const lines = response.split('\n');
      for (const line of lines) {
        if (line.startsWith('SENTIMENT_CHANGE:')) {
          result.sentimentChange = parseFloat(line.slice('SENTIMENT_CHANGE:'.length).trim()) || 0;
        } else if (line.startsWith('FAMILIARITY_CHANGE:')) {
          result.familiarityChange = parseFloat(line.slice('FAMILIARITY_CHANGE:'.length).trim()) || 0;
        } else if (line.startsWith('TRUST_CHANGE:')) {
          result.trustChange = parseFloat(line.slice('TRUST_CHANGE:'.length).trim()) || 0;
        } else if (line.startsWith('NOTE:')) {
          result.note = line.slice('NOTE:'.length).trim();
        }
      }
      
      // Ensure values are within bounds
      result.sentimentChange = Math.max(-0.2, Math.min(0.2, result.sentimentChange));
      result.familiarityChange = Math.max(0, Math.min(0.1, result.familiarityChange));
      result.trustChange = Math.max(-0.2, Math.min(0.2, result.trustChange));
      
      return result;
    } catch (error) {
      console.error('Error generating relationship update with OpenAI:', error);
      throw error;
    }
  }
}

module.exports = OpenAIProvider; 