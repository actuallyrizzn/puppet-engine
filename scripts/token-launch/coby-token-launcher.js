/**
 * Test script for Coby agent's pump.fun token launch functionality
 * 
 * This script tests the autonomous token launch capability without starting the full Puppet Engine.
 * It will:
 * 1. Initialize Twitter client
 * 2. Initialize the PumpFunTokenManager
 * 3. Attempt to launch a token for Coby agent
 * 4. Post a tweet if successful
 */

// Load environment variables
require('dotenv').config();

// Import required components
const TwitterAdapter = require('../src/twitter/twitter-adapter');
const PumpFunTokenManager = require('../src/solana/pumpfun-token-manager');
const fs = require('fs');
const path = require('path');

// Agent ID for Coby
const COBY_AGENT_ID = 'coby-agent';

// Path to token state file
const TOKEN_STATE_FILE = path.join(__dirname, '../data/coby-token-state.json');

/**
 * Test token launch for Coby agent
 */
async function testTokenLaunch(forceNewToken = false) {
  console.log('Starting pump.fun token launch test for Coby agent...');
  
  // Check if token state file exists
  if (fs.existsSync(TOKEN_STATE_FILE)) {
    console.log('Token state file exists. Contents:');
    const stateContent = fs.readFileSync(TOKEN_STATE_FILE, 'utf8');
    console.log(stateContent);
  } else {
    console.log('Token state file does not exist at:', TOKEN_STATE_FILE);
  }

  try {
    // Delete token state file if forcing a new token
    if (forceNewToken && fs.existsSync(TOKEN_STATE_FILE)) {
      console.log('Forcing new token launch - deleting existing token state file');
      fs.unlinkSync(TOKEN_STATE_FILE);
      console.log('Token state file deleted successfully');
    }

    // Initialize Twitter client
    console.log('Initializing Twitter client...');
    const twitterAdapter = new TwitterAdapter({
      apiCredentials: {
        apiKey: process.env.TWITTER_API_KEY,
        apiKeySecret: process.env.TWITTER_API_KEY_SECRET,
        accessToken: process.env.TWITTER_ACCESS_TOKEN,
        accessTokenSecret: process.env.TWITTER_ACCESS_TOKEN_SECRET,
        bearerToken: process.env.TWITTER_BEARER_TOKEN
      }
    });
    
    // Initialize PumpFunTokenManager with Twitter client
    console.log('Initializing PumpFunTokenManager...');
    const pumpFunTokenManager = new PumpFunTokenManager({
      twitterClient: twitterAdapter
    });
    
    // Attempt to launch token
    console.log('Attempting to launch token for Coby agent...');
    const result = await pumpFunTokenManager.launchTokenIfNeeded(COBY_AGENT_ID);
    
    // Check token state file again after launch attempt
    if (fs.existsSync(TOKEN_STATE_FILE)) {
      console.log('Token state file after launch attempt:');
      const stateContent = fs.readFileSync(TOKEN_STATE_FILE, 'utf8');
      console.log(stateContent);
    } else {
      console.log('Token state file still does not exist after launch attempt');
    }
    
    // Handle result
    if (result.success) {
      console.log('✅ Successfully launched token for Coby agent!');
      console.log(`Token mint address: ${result.mintAddress}`);
      console.log(`Pump.fun URL: ${result.pumpFunLink}`);
      console.log(`Transaction signature: ${result.signature}`);
      
      // Custom tweet if needed (will override the default tweet in the token manager)
      const customTweet = process.env.CUSTOM_TWEET_MESSAGE || null;
      if (customTweet) {
        console.log('Posting custom tweet about token...');
        const tweetContent = `${customTweet}\n\n${result.pumpFunLink}`;
        const tweet = await twitterAdapter.postTweet(COBY_AGENT_ID, tweetContent);
        console.log(`Custom tweet posted: ${tweet.id}`);
      }
      
    } else if (result.alreadyLaunched) {
      console.log('ℹ️ Coby already has a token');
      console.log(`Token mint address: ${result.mintAddress}`);
      
      // Generate the pump.fun link from the existing mint address
      const pumpFunLink = `https://pump.fun/token/${result.mintAddress}`;
      console.log(`Pump.fun URL: ${pumpFunLink}`);
      
      // Option to force a tweet about the existing token
      if (process.argv.includes('--force-tweet')) {
        console.log('Posting tweet about existing token...');
        const tweetContent = `reminder that i have a test token on pump.fun, still worthless lol\n\n${pumpFunLink}`;
        const tweet = await twitterAdapter.postTweet(COBY_AGENT_ID, tweetContent);
        console.log(`Tweet posted: ${tweet.id}`);
      }
    } else {
      console.log('❌ Failed to launch token for Coby agent');
      console.error(`Error: ${result.error}`);
    }
    
    console.log('Test completed.');
  } catch (error) {
    console.error('Error during test:', error);
  }
}

// Check if --force-new flag is passed
const forceNewToken = process.argv.includes('--force-new');

// Run the test
testTokenLaunch(forceNewToken).catch(error => {
  console.error('Unhandled error in test:', error);
  process.exit(1);
});

/**
 * Command line usage:
 * 
 * Regular test (checks if token exists, launches only if none exists):
 * node scripts/test-pumpfun-launch.js
 * 
 * Force new token (deletes existing token state and creates a new one):
 * node scripts/test-pumpfun-launch.js --force-new
 * 
 * Force tweet about existing token:
 * node scripts/test-pumpfun-launch.js --force-tweet
 * 
 * Custom tweet message can be set in .env:
 * CUSTOM_TWEET_MESSAGE="just launched my own memecoin, probably worthless but yolo"
 */ 