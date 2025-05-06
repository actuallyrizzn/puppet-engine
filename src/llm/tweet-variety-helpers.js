/**
 * Helper utilities for tweet generation
 * Designed to provide minimal additions since we now use comprehensive system prompts
 */

/**
 * Return the instruction with no additional guidance
 * @param {string} originalInstruction - The original instruction 
 * @returns {string} - The same instruction with no added text
 */
function enhanceTweetInstruction(originalInstruction) {
  // Just return the original instruction - no additional text needed
  return originalInstruction;
}

/**
 * Add randomness to reply instructions but no additional text
 * @param {string} originalInstruction - The original instruction
 * @param {Object} replyTo - The tweet being replied to
 * @returns {string} - The instruction with only randomness added
 */
function enhanceReplyInstruction(originalInstruction, replyTo) {
  // Just add randomness to avoid similar patterns - no other text
  const randomSeed = Date.now() + Math.random().toString().slice(2);
  return originalInstruction + `\n\nRANDOM_SEED: ${randomSeed}`;
}

module.exports = {
  enhanceTweetInstruction,
  enhanceReplyInstruction
}; 