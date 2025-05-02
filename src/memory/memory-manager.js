/**
 * Memory Manager for Puppet Engine agents
 * Handles storing, retrieving, and updating agent memories
 */

const { v4: uuidv4 } = require('uuid');
const { AgentMemory, MemoryItem, Relationship } = require('../core/types');

class MemoryManager {
  constructor(options = {}) {
    this.agentMemories = {};
    this.memoryLimit = options.memoryLimit || process.env.DEFAULT_AGENT_MEMORY_LIMIT || 100;
  }
  
  /**
   * Initialize an agent's memory from configuration
   */
  initializeAgentMemory(agentId, initialMemory = {}) {
    const memory = new AgentMemory();
    
    // Add core memories
    if (initialMemory.coreMemories && Array.isArray(initialMemory.coreMemories)) {
      initialMemory.coreMemories.forEach(content => {
        const memoryItem = new MemoryItem(content, 'core');
        memoryItem.id = uuidv4();
        memoryItem.importance = 1.0; // Core memories are maximally important
        memory.coreMemories.push(memoryItem);
      });
    }
    
    // Initialize relationships
    if (initialMemory.relationships && typeof initialMemory.relationships === 'object') {
      Object.keys(initialMemory.relationships).forEach(targetId => {
        const relationshipData = initialMemory.relationships[targetId];
        const relationship = new Relationship(targetId);
        
        // Copy relationship attributes
        Object.assign(relationship, relationshipData);
        
        memory.relationships[targetId] = relationship;
      });
    }
    
    // Add recent events
    if (initialMemory.recentEvents && Array.isArray(initialMemory.recentEvents)) {
      initialMemory.recentEvents.forEach(event => {
        const memoryItem = new MemoryItem(event.content || event, 'event');
        memoryItem.id = uuidv4();
        memoryItem.timestamp = event.timestamp ? new Date(event.timestamp) : new Date();
        memoryItem.importance = event.importance || 0.7;
        memory.recentEvents.push(memoryItem);
      });
    }
    
    this.agentMemories[agentId] = memory;
    return memory;
  }
  
  /**
   * Get agent memory, initializing if necessary
   */
  getAgentMemory(agentId) {
    if (!this.agentMemories[agentId]) {
      this.agentMemories[agentId] = new AgentMemory();
    }
    return this.agentMemories[agentId];
  }
  
  /**
   * Add a new memory to an agent
   */
  addMemory(agentId, content, type = 'general', options = {}) {
    const memory = this.getAgentMemory(agentId);
    const memoryItem = new MemoryItem(content, type);
    memoryItem.id = uuidv4();
    
    // Apply options
    if (options.importance !== undefined) memoryItem.importance = options.importance;
    if (options.emotionalValence !== undefined) memoryItem.emotionalValence = options.emotionalValence;
    if (options.associations) memoryItem.associations = options.associations;
    if (options.metadata) memoryItem.metadata = options.metadata;
    
    // Store in appropriate collection
    if (type === 'core') {
      memory.coreMemories.push(memoryItem);
    } else if (type === 'event') {
      memory.recentEvents.push(memoryItem);
      // Trim events if needed
      if (memory.recentEvents.length > this.memoryLimit / 2) {
        memory.recentEvents.sort((a, b) => b.importance - a.importance);
        memory.recentEvents = memory.recentEvents.slice(0, this.memoryLimit / 2);
      }
    } else {
      memory.longTermMemories.push(memoryItem);
      // Trim long-term memories if needed
      if (memory.longTermMemories.length > this.memoryLimit) {
        memory.longTermMemories.sort((a, b) => b.importance - a.importance);
        memory.longTermMemories = memory.longTermMemories.slice(0, this.memoryLimit);
      }
    }
    
    return memoryItem;
  }
  
  /**
   * Record a new post by the agent
   */
  recordPost(agentId, tweetContent, tweetId, metadata = {}) {
    const memory = this.getAgentMemory(agentId);
    const postMemory = new MemoryItem(`I posted: "${tweetContent}"`, 'post');
    postMemory.id = uuidv4();
    postMemory.metadata = {
      tweetId,
      fullText: tweetContent,
      ...metadata
    };
    
    memory.recentPosts.push(postMemory);
    
    // Keep only the last 20 posts in recent memory
    if (memory.recentPosts.length > 20) {
      memory.recentPosts.shift();
    }
    
    return postMemory;
  }
  
  /**
   * Update or create a relationship with another agent
   */
  updateRelationship(agentId, targetAgentId, changes = {}) {
    const memory = this.getAgentMemory(agentId);
    const relationship = memory.getRelationship(targetAgentId);
    
    // Apply changes
    Object.keys(changes).forEach(key => {
      if (key === 'sentiment' || key === 'familiarity' || key === 'trust') {
        // Ensure values are within bounds
        relationship[key] = Math.max(-1, Math.min(1, changes[key]));
      } else if (key === 'recentInteractions' && Array.isArray(changes[key])) {
        relationship.recentInteractions = [
          ...changes[key],
          ...relationship.recentInteractions
        ].slice(0, 10); // Keep only 10 most recent
      } else if (key === 'notes' && Array.isArray(changes[key])) {
        relationship.notes = [...changes[key], ...relationship.notes];
      } else if (key === 'sharedExperiences' && Array.isArray(changes[key])) {
        relationship.sharedExperiences = [
          ...changes[key],
          ...relationship.sharedExperiences
        ];
      } else {
        relationship[key] = changes[key];
      }
    });
    
    relationship.lastInteractionDate = new Date();
    return relationship;
  }
  
  /**
   * Search for relevant memories based on a query
   */
  searchMemories(agentId, query, options = {}) {
    const memory = this.getAgentMemory(agentId);
    const limit = options.limit || 10;
    const threshold = options.threshold || 0.3;
    
    // Simple keyword-based relevance for now
    // In a real implementation, this would use semantic search or embeddings
    const relevanceScore = (memoryItem) => {
      const content = memoryItem.content.toLowerCase();
      const queryTerms = query.toLowerCase().split(' ');
      
      // Count matching terms
      const matches = queryTerms.filter(term => content.includes(term)).length;
      return matches / queryTerms.length;
    };
    
    // Combine all memories
    const allMemories = [
      ...memory.coreMemories,
      ...memory.recentEvents,
      ...memory.longTermMemories
    ];
    
    // Score and filter memories
    const scoredMemories = allMemories
      .map(item => ({ 
        item,
        score: relevanceScore(item) * item.importance
      }))
      .filter(({ score }) => score > threshold)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);
    
    return scoredMemories.map(({ item }) => item);
  }
  
  /**
   * Get all memories to serialize for an agent
   */
  serializeAgentMemory(agentId) {
    const memory = this.getAgentMemory(agentId);
    return {
      coreMemories: memory.coreMemories,
      recentEvents: memory.recentEvents,
      recentPosts: memory.recentPosts,
      relationships: memory.relationships,
      longTermMemories: memory.longTermMemories
    };
  }
  
  /**
   * Load serialized memory for an agent
   */
  deserializeAgentMemory(agentId, serializedMemory) {
    const memory = new AgentMemory();
    
    if (serializedMemory.coreMemories) memory.coreMemories = serializedMemory.coreMemories;
    if (serializedMemory.recentEvents) memory.recentEvents = serializedMemory.recentEvents;
    if (serializedMemory.recentPosts) memory.recentPosts = serializedMemory.recentPosts;
    if (serializedMemory.relationships) memory.relationships = serializedMemory.relationships;
    if (serializedMemory.longTermMemories) memory.longTermMemories = serializedMemory.longTermMemories;
    
    this.agentMemories[agentId] = memory;
    return memory;
  }
}

module.exports = MemoryManager; 