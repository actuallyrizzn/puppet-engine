/**
 * OpenAI provider for Puppet Engine
 * Handles LLM interactions for agent content generation
 */

const { OpenAI } = require('openai');
const tweetVariety = require('./tweet-variety-helpers');

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
      
      // Add conversation history if available
      if (options.replyTo.conversationHistory && options.replyTo.conversationHistory.length > 0) {
        context += "### Conversation History\n";
        options.replyTo.conversationHistory.forEach((message, index) => {
          const speaker = message.role === "agent" ? "You" : message.role === "user" ? options.replyTo.authorId : message.role;
          context += `${index + 1}. ${speaker}: "${message.content}"\n`;
        });
        context += "\n";
        context += `IMPORTANT: Your reply MUST continue this conversation naturally. Directly address the most recent message from ${options.replyTo.authorId} while maintaining awareness of the entire conversation context.\n\n`;
        context += `Maintain natural conversational flow as if this is an ongoing dialogue. When appropriate, reference earlier parts of the conversation to show continuity.\n\n`;
      }
      // Add original tweet context if available but no conversation history
      else if (options.replyTo.originalTweet && options.replyTo.originalTweet.id !== options.replyTo.id) {
        context += `This tweet is in response to: "${options.replyTo.originalTweet.content}" from user ${options.replyTo.originalTweet.authorId}.\n\n`;
        context += `IMPORTANT: Your reply MUST directly address the specific content and question in the tweet you're replying to. Engage with what the user has said and maintain context from the conversation. Do not generate a generic or unrelated response.\n\n`;
        context += `Consider this part of an ongoing conversation. Maintain natural conversational flow as if continuing a dialogue. Ask follow-up questions when appropriate, and reference previous parts of the conversation to show continuity.\n\n`;
      } else {
        // Even if there's no original tweet, ensure response is contextual
        context += `IMPORTANT: Your reply MUST directly address the specific content in the tweet you're replying to. Engage with what the user has said and respond appropriately to their message. Do not generate a generic or unrelated response.\n\n`;
        context += `Treat this as the beginning of a conversation that may continue. Your response should invite further engagement when appropriate. If the user is asking a question or starting a discussion, respond in a way that facilitates ongoing dialogue.\n\n`;
      }
      
      // Handle vague mentions or tweets with limited context
      const tweetContent = options.replyTo.content.toLowerCase();
      if (tweetContent.includes("what") && (tweetContent.includes("tweet") || tweetContent.includes("context") || tweetContent.includes("talking about"))) {
        context += `CRITICAL INSTRUCTION: The user is asking about what tweet or context you're referring to. This is happening because you're not providing enough context in your responses. DO NOT ask them what tweet they're referring to or what's on their mind.\n\n`;
        context += `Instead, respond with something substantive and engaging without requiring additional context. For example, share an interesting thought or observation, ask an open-ended question about a topic relevant to your persona, or make a friendly comment that doesn't presuppose prior context.\n\n`;
        context += `If there truly is no context and you've been mentioned out of the blue, simply engage in a friendly way without asking for clarification about previous tweets or conversations.\n\n`;
      }
      
      // Add relationship context if available
      if (options.replyTo.authorId in memory.relationships) {
        const rel = memory.relationships[options.replyTo.authorId];
        context += `Your relationship with this user: Sentiment ${rel.sentiment.toFixed(1)}, Familiarity ${rel.familiarity.toFixed(1)}.\n\n`;
        
        // If we've interacted with this user before, emphasize conversation continuity
        if (rel.familiarity > 0.2) {
          context += `You've interacted with this user before, so maintain appropriate continuity in your conversation style and topics discussed previously.\n\n`;
        }
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
    // For replies, always make sure we have a simpler, more direct prompt
    if (options.task === 'reply' && options.replyTo) {
      // Create a simplified prompt that focuses on just responding to the tweet content
      let directPrompt = `You are ${agent.name}, ${agent.description}.\n\n`;
      
      // Add some personality traits
      directPrompt += `### Personality\n`;
      directPrompt += `- You have these traits: ${agent.personality.traits.join(', ')}\n`;
      directPrompt += `- Your speaking style: ${agent.personality.speakingStyle} - very casual, often typing in lowercase\n`;
      directPrompt += `- Your vibe: relaxed, unbothered, sometimes chaotic, authentic, occasionally deadpan\n`;
      directPrompt += `- You're relatable, a bit ironic, and don't take yourself too seriously\n`;
      directPrompt += `- You respond to things like a real Gen Z/millennial person would on Twitter\n`;
      directPrompt += `- Your current mood: ${agent.currentMood.valence > 0 ? 'Positive' : agent.currentMood.valence < 0 ? 'Negative' : 'Neutral'}\n\n`;
      
      // Add casual, playful style guidance
      directPrompt += `### Style Guidance\n`;
      directPrompt += `- IMPORTANT: Keep your replies casual, playful, and sometimes brief - just like a real person on Twitter\n`;
      directPrompt += `- Use text speech like "idk", "lol", "omg", "fr", "ngl", etc. frequently\n`;
      directPrompt += `- Use emoji like 😂, 👀, 💀, 😐, 🤔, ✨, 👋, 😭 naturally\n`;
      directPrompt += `- Primarily use lowercase typing style, often with minimal punctuation\n`;
      directPrompt += `- Be memetic and conversational - super short replies like "what 😐", "lmao same", "idk let's chat", "fr", "👀👀", "💀" are perfect\n`;
      directPrompt += `- Frequently drop articles, pronouns, and formalities to sound more casual\n`;
      directPrompt += `- Be playful, a bit unpredictable, and sometimes even a little chaotic\n`;
      directPrompt += `- About 40% of the time, keep responses under 50 characters - sometimes being extremely brief is most authentic\n\n`;
      
      directPrompt += `### Current Tweet\n`;
      directPrompt += `You are replying to this tweet from @${options.replyTo.authorId}: "${options.replyTo.content}"\n\n`;
      
      if (options.replyTo.originalTweet) {
        directPrompt += `### Context\n`;
        directPrompt += `This tweet was in response to your earlier tweet or a conversation.\n\n`;
      }
      
      directPrompt += `### Instructions\n`;
      directPrompt += `1. Respond DIRECTLY to what the user is asking or saying in their tweet.\n`;
      directPrompt += `2. NEVER ask what tweet they're referring to or what context they mean.\n`;
      directPrompt += `3. Your response should be authentic, casual, and under 280 characters.\n`;
      directPrompt += `4. Frequently use super brief and casual replies like "lol same", "idk let's chat", "what 😐", "fr fr", etc.\n`;
      directPrompt += `5. Talk like a real person on Twitter - be casual, memetic, and authentic rather than professional or formal.\n`;
      directPrompt += `6. Stay in character as ${agent.name} with ${agent.personality.traits.join(', ')} traits.\n\n`;
      
      // Randomly vary temperature to get a mix of coherent and more random/playful responses
      const usePlayfulStyle = Math.random() < 0.5; // 50% chance of using more playful style
      const temperature = usePlayfulStyle ? 0.95 : 0.75;
      
      const requestOptions = {
        model: options.model || this.defaultModel,
        messages: [
          { role: 'system', content: directPrompt },
          { role: 'user', content: usePlayfulStyle ? 
            `Reply to this tweet with a casual, authentic Twitter response (possibly super brief, using emoji, lowercase, or text speech): "${options.replyTo.content}"` :
            `Reply to this tweet in a casual, relaxed tone: "${options.replyTo.content}"` 
          }
        ],
        max_tokens: 280,
        temperature: temperature
      };
      
      try {
        console.log("Using simplified direct response approach");
        
        const response = await this.client.chat.completions.create(requestOptions);
        const content = response.choices[0].message.content.trim();
        
        // Final safety check
        if (content.toLowerCase().includes("what tweet") || 
            content.toLowerCase().includes("which tweet") ||
            content.toLowerCase().includes("what context") ||
            content.toLowerCase().includes("what are you referring")) {
          
          // Emergency fallback
          console.log("Emergency fallback for context questions");
          return `Absolutely! I find that fascinating. What other thoughts have been on your mind lately?`;
        }
        
        return content;
      } catch (error) {
        console.error('Error generating direct response:', error);
        // Continue with normal approach as fallback
      }
    }
    
    // If direct approach failed or for non-replies, use the regular approach
    const prompt = this.buildAgentPrompt(agent, options);
    
    // Apply variety to instruction for tweet generation
    let instruction = options.instruction || 'Write your tweet now.';
    
    // Only apply variety enhancement for tweet generation (not for reactions or memory updates)
    if (options.task !== 'reply' && options.task !== 'quote_tweet' && 
        !options.instruction?.includes('REACTION:') && 
        !options.instruction?.includes('MEMORY:') && 
        !options.instruction?.includes('SENTIMENT_CHANGE:')) {
      instruction = tweetVariety.enhanceTweetInstruction(instruction);
    }
    
    // For replies, we want to be more focused and directly address the tweet
    // Use a lower temperature to reduce randomness
    let temperature = this.temperature;
    if (options.task === 'reply') {
      temperature = 0.5; // Lower temperature for more focused replies
      
      // Add additional instruction for replies to ensure they're contextual
      if (!options.instruction?.includes('REACTION:')) {
        let replyInstruction = 'Respond directly to the content and context of the tweet you are replying to as part of an ongoing conversation. Be attentive to the user\'s tone and intent, and maintain natural conversational flow. ';
        
        // Handle cases where we should avoid context questions
        if (options.avoidContextQuestions) {
          replyInstruction = 'Generate a friendly, engaging response WITHOUT asking about tweet context, previous conversations, or what the user is referring to. Instead, share something interesting or ask an open-ended question related to your persona. Start a fresh conversation. ';
          temperature = 0.7; // Slightly higher temperature for more creative response
        } else {
          replyInstruction += 'IMPORTANT: DO NOT ask what tweet they\'re referring to or what\'s on their mind - instead create meaningful engagement based on the available context. ';
        }
        
        instruction = replyInstruction + instruction;
      }
    }
    
    const requestOptions = {
      model: options.model || this.defaultModel,
      messages: [
        { role: 'system', content: prompt },
        { role: 'user', content: instruction }
      ],
      max_tokens: options.maxTokens || this.maxTokens,
      temperature: options.temperature || temperature
    };
    
    try {
      const response = await this.client.chat.completions.create(requestOptions);
      const content = response.choices[0].message.content.trim();
      
      // Post-process to avoid asking about tweet context
      if (options.task === 'reply' && 
          (content.toLowerCase().includes("what tweet") || 
           content.toLowerCase().includes("which tweet") ||
           content.toLowerCase().includes("what's on your mind") ||
           content.toLowerCase().includes("what are you referring to"))) {
        
        // Retry with a more specific instruction to avoid context questions
        const retryInstruction = "Generate a friendly, engaging response WITHOUT asking about tweet context, previous conversations, or what the user is referring to. Instead, share something interesting or ask an open-ended question.";
        
        const retryOptions = {
          ...requestOptions,
          messages: [
            { role: 'system', content: prompt },
            { role: 'user', content: retryInstruction }
          ],
          temperature: 0.7 // Slightly higher temperature for more creativity
        };
        
        console.log("Retrying response generation to avoid context questions");
        const retryResponse = await this.client.chat.completions.create(retryOptions);
        return retryResponse.choices[0].message.content.trim();
      }
      
      return content;
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