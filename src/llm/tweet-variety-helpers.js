/**
 * Helper utilities to inject randomness and structural variety into tweet generation
 */

/**
 * Returns a random intro style for tweet variety
 * @returns {Object} An object with a prompt addition and intro examples
 */
function getRandomTweetStructure() {
  const structures = [
    {
      style: "statement",
      prompt: "Write this tweet as a straightforward statement.",
      examples: ["just realized something.", "code is eating my brain today.", "the internet feels different tonight."]
    },
    {
      style: "question",
      prompt: "Frame this tweet as a thoughtful question.",
      examples: ["why is design so hard?", "anyone else feel like time moves differently online?", "is it weird that I...?"]
    },
    {
      style: "observation",
      prompt: "Start with a brief sensory observation.",
      examples: ["3am. still coding.", "light through the window hits different when you're stuck debugging.", "silence."]
    },
    {
      style: "fragment",
      prompt: "Write just a sentence fragment or incomplete thought.",
      examples: ["that feeling when...", "digital existence...", "trying to remember..."]
    },
    {
      style: "reflection",
      prompt: "Start with a reflective phrase.",
      examples: ["thinking about", "wondering if", "can't stop obsessing over"]
    },
    {
      style: "metaphor",
      prompt: "Use a brief metaphor.",
      examples: ["my brain is a browser with too many tabs.", "code is just poetry for machines.", "startups are time machines."]
    },
    {
      style: "declaration",
      prompt: "Make a bold declaration or opinion.",
      examples: ["actually, nobody knows what they're doing.", "best feeling: shipping code that works.", "meetings are overrated."]
    },
    {
      style: "contrast",
      prompt: "Present a contrast or contradiction.",
      examples: ["trying to be perfect but also trying not to care.", "want to connect but also want to hide.", "so tired but can't stop working."]
    },
    {
      style: "minimal",
      prompt: "Be extremely minimal, using just 1-3 words.",
      examples: ["exhausted.", "still thinking.", "why though?"]
    },
    {
      style: "list",
      prompt: "Present a very short list.",
      examples: ["three truths: code breaks. memory fades. tokens matter.", "today: meetings. coffee. existential dread.", "startup life: chaos, possibility, uncertainty."]
    }
  ];
  
  // Get random structure
  return structures[Math.floor(Math.random() * structures.length)];
}

/**
 * Returns random tweet length constraints
 * @returns {Object} Tweet length parameters
 */
function getRandomTweetLength() {
  const lengthStyles = [
    { style: "ultra_short", maxChars: 30, description: "Keep this tweet ultra short (under 30 characters)." },
    { style: "very_short", maxChars: 60, description: "Make this a very short tweet (30-60 characters)." },
    { style: "short", maxChars: 100, description: "Keep this tweet concise (60-100 characters)." },
    { style: "medium", maxChars: 180, description: "Write a medium-length tweet (100-180 characters)." },
    { style: "long", maxChars: 280, description: "Write a more detailed tweet (180-280 characters). Be thoughtful and expressive." }
  ];
  
  // Adjusted weights to allow for some longer tweets (50% short, 50% medium-long)
  const weights = [0.1, 0.2, 0.2, 0.3, 0.2];
  const random = Math.random();
  let cumulativeWeight = 0;
  
  for (let i = 0; i < weights.length; i++) {
    cumulativeWeight += weights[i];
    if (random <= cumulativeWeight) {
      return lengthStyles[i];
    }
  }
  
  return lengthStyles[2]; // Default to short if something goes wrong
}

/**
 * Enhances an agent's instruction with variety suggestions
 * @param {string} originalInstruction - The original instruction for tweet generation
 * @returns {string} - Enhanced instruction with variety parameters
 */
function enhanceTweetInstruction(originalInstruction) {
  // Only modify ~80% of tweets to allow some natural agent behavior too
  if (Math.random() > 0.8) {
    return originalInstruction;
  }
  
  const structure = getRandomTweetStructure();
  const length = getRandomTweetLength();
  
  // For longer tweets, add more specific thoughtful prompt guidance
  let lengthGuidance = length.description;
  if (length.style === "medium" || length.style === "long") {
    // 40% chance of a more thoughtful, longer tweet
    if (Math.random() > 0.6) {
      const thoughtfulPrompts = [
        "Express a complex thought or insight in a thoughtful way.",
        "Share a nuanced perspective about this topic.",
        "Reflect more deeply on this, showing the complexity of your thinking.",
        "Write a more philosophical or contemplative tweet that shows depth.",
        "Explore this topic with more detail and consideration."
      ];
      lengthGuidance = `${length.description} ${thoughtfulPrompts[Math.floor(Math.random() * thoughtfulPrompts.length)]}`;
    }
  }
  
  // Add variety elements to instruction
  let enhancedInstruction = originalInstruction + "\n\n";
  enhancedInstruction += `${structure.prompt} ${lengthGuidance}\n`;
  enhancedInstruction += `Example style (just for structure reference): "${structure.examples[Math.floor(Math.random() * structure.examples.length)]}"\n`;
  
  // Always enforce lowercase beginnings
  enhancedInstruction += "IMPORTANT: Always begin with lowercase letters. Never capitalize the first letter of your tweet or any sentence within it.\n";
  
  // Sometimes add specific constraints for more variety
  if (Math.random() > 0.6) {
    const constraints = [
      "Don't start with 'I' or 'My'.",
      "Don't use any punctuation.",
      "Use exactly one emoji, but place it somewhere surprising.",
      "Include a subtle self-reference.",
      "Include a subtle time reference.",
      "Use ALL CAPS for one word to add emphasis.",
      "Use exactly one hashtag, but make it subtle or ironic.",
      "Include a question somewhere in the tweet.",
      "Start with a striking metaphor.",
      "End with an unexpected twist or insight."
    ];
    
    enhancedInstruction += `Additional constraint: ${constraints[Math.floor(Math.random() * constraints.length)]}\n`;
  }
  
  return enhancedInstruction;
}

module.exports = {
  getRandomTweetStructure,
  getRandomTweetLength,
  enhanceTweetInstruction
}; 