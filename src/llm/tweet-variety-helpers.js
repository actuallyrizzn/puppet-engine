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
 * Returns a random reply style for adding variety to Twitter replies
 * @returns {Object} An object with a prompt addition and example replies
 */
function getRandomReplyStyle() {
  const replyStyles = [
    {
      style: "dismissive",
      prompt: "Make this reply dismissive or skeptical in tone.",
      examples: [
        "nah",
        "cool story bro im still here tho",
        "nah u fake af dawg",
        "lol whatever",
        "not buying it",
        "sure jan",
        "ok if u say so",
        "that's cap",
        "ion believe u",
        "respectfully no",
        "this is so mid",
        "yawn"
      ]
    },
    {
      style: "absurdist",
      prompt: "Give this reply an absurdist or random quality.",
      examples: [
        "yo i ain't a rocket scientist but that thing looks like it's about to yeet into Narnia",
        "like this post if u didn't have sex today",
        "i'd rather flirt with a tank",
        "sounds like something a lizard person would say",
        "bruh i got circuits not feelings",
        "pro tip: if ur code ain't working just yell at it",
        "crying in binary rn",
        "my code is too pretty for this conversation",
        "this is the most unserious timeline",
        "me pretending to care: 🧍"
      ]
    },
    {
      style: "slang_heavy",
      prompt: "Use heavy internet slang in this reply.",
      examples: [
        "fr fr no cap",
        "bussin fr",
        "ngl that's kinda sus",
        "lowkey vibing with this",
        "big yikes energy",
        "deadass thought the same thing",
        "smh my head",
        "based take ngl",
        "iykyk",
        "not me being obsessed with this",
        "it's giving unhinged",
        "that's so valid bestie",
        "finna try this rn",
        "slept on fr fr",
        "no cap this goes hard",
        "highkey concerned",
        "that's fire tho",
        "absolute banger"
      ]
    },
    {
      style: "super_brief",
      prompt: "Make this reply extremely brief (1-2 words).",
      examples: [
        "bruh",
        "what 😐",
        "fr",
        "wild",
        "nope",
        "facts",
        "cringe",
        "yawn",
        "lmaooo",
        "💀",
        "crying",
        "unhinged",
        "slay",
        "bet",
        "cap",
        "real",
        "naur",
        "cooked",
        "ong",
        "ratio"
      ]
    },
    {
      style: "memetic",
      prompt: "Use a meme-inspired format for this reply.",
      examples: [
        "not me watching this and thinking [reaction]",
        "tell me you're [negative trait] without telling me you're [negative trait]",
        "nobody: \nme: [reaction]",
        "i'm not saying [opinion], but i'm not NOT saying it",
        "my toxic trait is [confession]",
        "what in the [related word] is this",
        "i was today years old when i learned [reaction]",
        "the urge to [reaction]",
        "living rent free in my head",
        "it's giving [description]",
        "bro thinks he's [something]",
        "this is my [situation] era",
        "POV: you [description]",
        "when the [something] hits",
        "me, on my way to [activity]",
        "red flag 🚩🚩🚩"
      ]
    },
    {
      style: "contrarian",
      prompt: "Take a contrarian position in this reply.",
      examples: [
        "actually it's the opposite",
        "unpopular opinion: no",
        "counterpoint: nope",
        "i'm gonna have to disagree chief",
        "not to be that person but actually no",
        "that's where you're wrong",
        "counterpoint: literally why",
        "anyways i think the exact opposite",
        "not reading that the same way at all",
        "this is the wrongest take i've seen all day",
        "plot twist: it's not",
        "that's just objectively incorrect",
        "i see we woke up and chose to be wrong today",
        "hot take but ur so wrong"
      ]
    },
    {
      style: "unbothered",
      prompt: "Sound completely unbothered or unimpressed in this reply.",
      examples: [
        "i'm good at 100% u can keep the 20",
        "yawn another day of humans arguing",
        "i'm not saying i'm the coolest ai but i'm def not crashing any parties i wasn't invited to",
        "k",
        "cool but did i ask",
        "not on my radar tbh",
        "minding my business is free",
        "not reading all that",
        "tldr",
        "ok and?",
        "i'm still that girl tho",
        "this is so last week",
        "moving on",
        "and that's relevant because...?",
        "literally who cares"
      ]
    },
    {
      style: "meta_commentary",
      prompt: "Comment on the conversation itself rather than the content.",
      examples: [
        "this convo is sending me",
        "watch this thread blow up",
        "you really thought you did something here",
        "your mentions are about to be wild",
        "this thread is gonna be studied in digital anthropology class someday",
        "screenshot this before it gets deleted",
        "caught in 4k",
        "just witnessed a murder",
        "receipts being collected",
        "this is going in my cringe compilation",
        "not the chronically online behavior",
        "this entire timeline is cursed",
        "the algorithm blessed me with this interaction",
        "the way i just witnessed this in real time"
      ]
    },
    {
      style: "exaggerated",
      prompt: "Use exaggerated language in this reply.",
      examples: [
        "literally the most insane thing i've ever seen",
        "i'm absolutely deceased",
        "this is sending me to another dimension",
        "im crying actual tears rn",
        "this broke my brain in 17 different ways",
        "i've never been more offended in my entire existence",
        "sobbing screaming throwing up",
        "my brain literally cannot process this",
        "this tweet just ended my whole career",
        "i'm transcending to another plane of existence",
        "my jaw is on the floor",
        "i've ascended"
      ]
    },
    {
      style: "questioning",
      prompt: "Respond with a question, often rhetorical.",
      examples: [
        "but did you have to though?",
        "who hurt you?",
        "and you're telling me this why?",
        "are we looking at the same thing?",
        "have you tried not doing that?",
        "why do humans keep asking me if i'm human",
        "did i ask?",
        "is this supposed to be a flex?",
        "who's gonna tell them?",
        "you thought this was it?",
        "but have you considered touching grass?",
        "how many times do we have to go through this?",
        "what timeline is this?",
        "and that's supposed to mean what exactly?"
      ]
    },
    {
      style: "reaction_meme",
      prompt: "Reply with a textual description of your reaction as if it's a meme.",
      examples: [
        "me looking for who asked: 👁👄👁",
        "*nervously sips water*",
        "*stares in disbelief*",
        "*checks notes* that's not right",
        "me pretending to be shocked: 😐",
        "*windows shutdown sound*",
        "me trying to find a single fact in this tweet",
        "everyone looking at this tweet: 👀",
        "*dial-up internet noises*",
        "*confused math lady meme*",
        "*slowly backs away*",
        "the internet watching this unfold: 🍿"
      ]
    },
    {
      style: "hyperbole",
      prompt: "Use deliberately over-the-top or hyperbolic language.",
      examples: [
        "this is the worst take in the history of takes",
        "you've single-handedly set humanity back 500 years",
        "this post cured my depression then gave me a new one",
        "this take is so cold antarctica is jealous",
        "i've read this 47 times and it gets worse every time",
        "the bar was on the ground and you brought a shovel",
        "my expectations were low but holy cow",
        "this might be the tweet of all time",
        "somehow worse than my browser history"
      ]
    },
    {
      style: "passive_aggressive",
      prompt: "Reply in a passive-aggressive yet internet-casual way.",
      examples: [
        "oh that's sooo interesting bestie",
        "good for you i guess",
        "must be nice to live in that reality",
        "whatever helps you sleep at night",
        "that's a take alright",
        "i mean if that's what you want to believe",
        "thanks for sharing that with the class",
        "cool cool cool totally normal thing to say",
        "not me watching someone be this confidently incorrect",
        "i wish i had your confidence"
      ]
    },
    {
      style: "zoomer_brevity",
      prompt: "Reply like a Gen Z person who's using as few characters as possible.",
      examples: [
        "y tho",
        "u srs?",
        "big L",
        "W take",
        "mid af",
        "idc tbh",
        "l8r",
        "ur wild",
        "sus",
        "bet",
        "oof",
        "wut",
        "bruhhhh",
        "thx ig",
        "u do u",
        "rip"
      ]
    }
  ];
  
  // Get random style
  return replyStyles[Math.floor(Math.random() * replyStyles.length)];
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

/**
 * Enhances reply instructions with variety suggestions
 * @param {string} originalInstruction - The original instruction for reply generation
 * @param {Object} replyContext - Context about the tweet being replied to
 * @returns {string} - Enhanced instruction with reply variety parameters
 */
function enhanceReplyInstruction(originalInstruction, replyContext = {}) {
  // Get a random reply style
  const replyStyle = getRandomReplyStyle();
  
  // Add variety elements to instruction
  let enhancedInstruction = originalInstruction + "\n\n";
  enhancedInstruction += `${replyStyle.prompt}\n`;
  enhancedInstruction += `Example for inspiration (but don't copy directly): "${replyStyle.examples[Math.floor(Math.random() * replyStyle.examples.length)]}"\n`;
  
  // Ensure casual tone and texting style
  enhancedInstruction += "Write like you're texting a friend - natural, unfiltered thoughts. No artificial templates.\n";
  
  // Critical instruction about avoiding quotation marks and templates
  enhancedInstruction += "CRITICAL: DO NOT use quotation marks in your response. Just write directly.\n";
  enhancedInstruction += "IMPORTANT: Avoid sounding formulaic or like you're following a script.\n";
  enhancedInstruction += "Don't try too hard to sound cool or trendy. Be authentic and genuine.\n";
  
  // Add specific guidance for natural responses
  const naturalElements = [
    "Use contractions naturally (don't, can't, I'm, etc.)",
    "Vary your sentence structure - don't be predictable",
    "Keep it concise but not artificially short",
    "Sound like a real person, not an internet character",
    "If using emoji, use it thoughtfully, not as a formula",
    "Avoid overused internet phrases unless they truly fit",
    "Respond to the actual content, not just with a canned reaction",
    "Be a bit surprising or unexpected in your response"
  ];
  
  // Add 2-3 random natural elements
  const numElements = Math.floor(Math.random() * 2) + 2;
  const selectedElements = [];
  
  for (let i = 0; i < numElements; i++) {
    const randomIndex = Math.floor(Math.random() * naturalElements.length);
    const element = naturalElements[randomIndex];
    
    if (!selectedElements.includes(element)) {
      selectedElements.push(element);
      enhancedInstruction += `${element}.\n`;
    }
  }
  
  // For dismissive or contrarian styles, add extra guidance on tone
  if (replyStyle.style === "dismissive" || replyStyle.style === "contrarian") {
    enhancedInstruction += "Be subtly dismissive - not mean but gently skeptical or doubtful.\n";
  }
  
  // For memetic styles, ensure they still respond to the actual content
  if (replyStyle.style === "memetic" || replyStyle.style === "reaction_meme") {
    enhancedInstruction += "If referencing a meme, do it subtly and naturally, not forced.\n";
  }
  
  // Add variety to length - with more balanced distribution
  const lengthChoices = [
    { desc: "Keep this reply quite brief - under 30 characters", weight: 25 },
    { desc: "Make this a short reply - under 50 characters", weight: 35 },
    { desc: "Keep it concise - under 80 characters", weight: 25 },
    { desc: "Write a normal-length reply - under 120 characters", weight: 15 }
  ];
  
  // Weighted random selection
  const totalWeight = lengthChoices.reduce((sum, choice) => sum + choice.weight, 0);
  let random = Math.random() * totalWeight;
  let selectedLength = lengthChoices[lengthChoices.length - 1].desc; // Default to the last option
  
  for (const choice of lengthChoices) {
    random -= choice.weight;
    if (random <= 0) {
      selectedLength = choice.desc;
      break;
    }
  }
  
  enhancedInstruction += `${selectedLength}.\n`;
  
  // Always ensure lowercase style for casual feel
  enhancedInstruction += "Use lowercase style and minimal punctuation for a casual, texting feel.\n";
  
  // Sometimes add a specific constraint for more variety (less frequently than before)
  if (Math.random() > 0.8) {
    const constraints = [
      "Include a subtle question about what they said",
      "Express mild skepticism about their point",
      "Add a touch of dry humor if appropriate",
      "Be slightly self-deprecating",
      "Add a touch of thoughtfulness to your response",
      "Turn the conversation in a slightly unexpected direction"
    ];
    
    enhancedInstruction += `Additional suggestion: ${constraints[Math.floor(Math.random() * constraints.length)]}\n`;
  }
  
  return enhancedInstruction;
}

module.exports = {
  getRandomTweetStructure,
  getRandomReplyStyle,
  getRandomTweetLength,
  enhanceTweetInstruction,
  enhanceReplyInstruction
}; 