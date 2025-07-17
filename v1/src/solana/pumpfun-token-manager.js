const fs = require('fs');
const path = require('path');
const { SolanaAgentKit } = require('solana-agent-kit');
const bs58 = require('bs58');
const { Keypair } = require('@solana/web3.js');
const db = require('../utils/database');

// Path to store whether we've already launched a token (using the correct path)
const TOKEN_STATE_FILE = path.join(__dirname, '../../data/coby-token-state.json');

// Use simulation mode for testing without real transactions
const SIMULATION_MODE = process.env.SOLANA_SIMULATION_MODE !== 'false';

/**
 * PumpFunTokenManager handles the one-time token launch for Coby agent
 * This implementation uses the real solana-agent-kit functionality
 */
class PumpFunTokenManager {
  constructor(options = {}) {
    this.agentKit = null;
    this.tokenMintAddress = null;
    this.tokenLaunched = false;
    this.twitterClient = options.twitterClient;
    this.agentManager = options.agentManager;
    this.launchScheduled = false;
    this.scheduledLaunchTime = null;
    this.useMongoDb = options.useMongoDb !== false;
    this.mongoDbConnected = false;
    
    console.log('PumpFunTokenManager constructor - using token state file:', TOKEN_STATE_FILE);
    console.log(`SIMULATION_MODE: ${SIMULATION_MODE ? 'ENABLED' : 'DISABLED'}`);
    
    // Check MongoDB connection
    if (this.useMongoDb) {
      this._initializeMongoDb();
    }
    
    // Initialize by checking if token was already launched
    this.loadTokenState();
  }

  /**
   * Initialize MongoDB connection
   * @private
   */
  async _initializeMongoDb() {
    try {
      await db.connectToDatabase();
      this.mongoDbConnected = true;
      console.log('PumpFunTokenManager connected to MongoDB');
    } catch (error) {
      console.error('Failed to connect to MongoDB, falling back to file storage:', error);
      this.mongoDbConnected = false;
    }
  }

  /**
   * Initialize the solana-agent-kit properly
   */
  async initializeAgentKit() {
    try {
      console.log('Initializing solana-agent-kit...');
      
      // Get configuration from environment
      const rpcUrl = process.env.SOLANA_RPC_URL || process.env.RPC_URL || 'https://api.mainnet-beta.solana.com';
      const privateKey = process.env.SOLANA_PRIVATE_KEY;
      
      if (!privateKey) {
        throw new Error('SOLANA_PRIVATE_KEY not found in environment variables');
      }

      // Create keypair from private key
      let keypair;
      
      if (SIMULATION_MODE) {
        // In simulation mode, generate a random keypair
        console.log('Using SIMULATION MODE with a random keypair');
        keypair = Keypair.generate();
      } else {
        try {
          console.log('Attempting to decode private key...');
          console.log('Private key length:', privateKey.length);
          
          // Try multiple approaches to decode the private key
          try {
            // Try parsing as base58
            const decodedKey = bs58.decode(privateKey);
            keypair = Keypair.fromSecretKey(decodedKey);
            console.log('Created keypair from bs58 private key');
          } catch (bs58Error) {
            console.log('Failed to decode with bs58:', bs58Error.message);
            
            try {
              // Try parsing as JSON array
              const secretKey = Uint8Array.from(JSON.parse(privateKey));
              keypair = Keypair.fromSecretKey(secretKey);
              console.log('Created keypair from JSON array private key');
            } catch (jsonError) {
              console.log('Failed to parse as JSON array:', jsonError.message);
              
              try {
                // Try parsing as hex string
                const secretKey = Buffer.from(privateKey, 'hex');
                keypair = Keypair.fromSecretKey(secretKey);
                console.log('Created keypair from hex private key');
              } catch (hexError) {
                console.log('Failed to parse as hex:', hexError.message);
                
                // Last resort - treat as comma-separated values
                try {
                  const values = privateKey.split(',').map(v => parseInt(v.trim()));
                  const secretKey = Uint8Array.from(values);
                  keypair = Keypair.fromSecretKey(secretKey);
                  console.log('Created keypair from comma-separated values');
                } catch (csvError) {
                  console.error('All private key parsing methods failed');
                  throw new Error('Unable to create keypair from private key');
                }
              }
            }
          }
        } catch (error) {
          console.error('Error creating keypair:', error);
          throw error;
        }
      }

      console.log('Keypair created with public key:', keypair.publicKey.toString());

      // In simulation mode, don't actually create the SolanaAgentKit
      if (SIMULATION_MODE) {
        console.log('SIMULATION MODE: Skipping real SolanaAgentKit initialization');
        // Create a minimal simulation of the agent kit
        this.agentKit = {
          launchPumpFunToken: async (params) => {
            console.log('SIMULATION: Launching pump.fun token with params:', params);
            // Generate a fake mint address
            const mintKeypair = Keypair.generate();
            const mintAddress = mintKeypair.publicKey.toString();
            return {
              status: 'success',
              mint: mintAddress,
              signature: 'sim_' + Date.now(),
              metadataUri: 'https://arweave.net/simulated'
            };
          },
          getWalletBalance: async () => {
            return { solanaSol: 1.0, lamports: 1000000000 };
          }
        };
      } else {
        // Create real agent kit instance using the SolanaAgentKit constructor
        this.agentKit = new SolanaAgentKit({
          keypair,
          endpoint: rpcUrl,
          config: {
            network: 'mainnet-beta',
            slippage: 1.0
          }
        });
      }

      console.log('solana-agent-kit initialized successfully');
      
      // Verify connection by getting wallet balance
      try {
        const balance = await this.agentKit.getWalletBalance();
        console.log(`Wallet balance: ${balance.solanaSol} SOL`);
      } catch (balanceError) {
        console.error('Error getting wallet balance:', balanceError);
        console.log('Continuing anyway...');
      }

      return true;
    } catch (error) {
      console.error('Failed to initialize solana-agent-kit:', error);
      return false;
    }
  }

  /**
   * Load token state from MongoDB or file
   */
  async loadTokenState() {
    try {
      console.log('Loading token state...');
      
      // Try MongoDB first if available
      if (this.mongoDbConnected) {
        try {
          const tokenCollection = await db.getCollection(db.COLLECTIONS.TOKENS);
          const tokenDoc = await tokenCollection.findOne({ agentId: 'coby-agent' });
          
          if (tokenDoc) {
            console.log('Token state loaded from MongoDB:', tokenDoc);
            
            this.tokenLaunched = tokenDoc.tokenLaunched || false;
            this.tokenMintAddress = tokenDoc.tokenMintAddress || null;
            this.launchScheduled = tokenDoc.launchScheduled || false;
            this.scheduledLaunchTime = tokenDoc.scheduledLaunchTime ? new Date(tokenDoc.scheduledLaunchTime) : null;
            
            console.log(`Token state loaded from MongoDB: launched=${this.tokenLaunched}, mint=${this.tokenMintAddress}, scheduled=${this.launchScheduled}`);
            return;
          } else {
            console.log('No token state found in MongoDB');
          }
        } catch (mongoError) {
          console.error('Error loading token state from MongoDB:', mongoError);
          // Fall through to file-based loading
        }
      }
      
      // Fall back to file-based loading
      console.log('Loading token state from file:', TOKEN_STATE_FILE);
      
      if (fs.existsSync(TOKEN_STATE_FILE)) {
        try {
          const data = JSON.parse(fs.readFileSync(TOKEN_STATE_FILE, 'utf8'));
          console.log('Raw token state data:', data);
          
          this.tokenLaunched = data.tokenLaunched || false;
          this.tokenMintAddress = data.tokenMintAddress || null;
          this.launchScheduled = data.launchScheduled || false;
          this.scheduledLaunchTime = data.scheduledLaunchTime ? new Date(data.scheduledLaunchTime) : null;
          
          console.log(`Token state loaded from file: launched=${this.tokenLaunched}, mint=${this.tokenMintAddress}, scheduled=${this.launchScheduled}`);
          
          // Sync to MongoDB if we're connected but didn't find the document
          if (this.mongoDbConnected) {
            this.saveTokenState();
          }
        } catch (parseError) {
          console.error('Error parsing token state JSON:', parseError);
          // Invalid JSON - reset the token state
          this.tokenLaunched = false;
          this.tokenMintAddress = null;
          this.launchScheduled = false;
          this.scheduledLaunchTime = null;
        }
      } else {
        console.log('Token state file does not exist, setting to defaults');
        this.tokenLaunched = false;
        this.tokenMintAddress = null;
        this.launchScheduled = false;
        this.scheduledLaunchTime = null;
      }
    } catch (error) {
      console.error('Error loading token state:', error);
      this.tokenLaunched = false;
      this.tokenMintAddress = null;
      this.launchScheduled = false;
      this.scheduledLaunchTime = null;
    }
  }

  /**
   * Save token state to MongoDB and file
   */
  async saveTokenState() {
    try {
      console.log('Saving token state...');
      
      const data = {
        agentId: 'coby-agent',
        tokenLaunched: this.tokenLaunched,
        tokenMintAddress: this.tokenMintAddress,
        launchDate: new Date().toISOString(),
        launchScheduled: this.launchScheduled,
        scheduledLaunchTime: this.scheduledLaunchTime ? this.scheduledLaunchTime.toISOString() : null
      };
      
      console.log('Token state to save:', data);
      
      // Save to MongoDB if connected
      if (this.mongoDbConnected) {
        try {
          const tokenCollection = await db.getCollection(db.COLLECTIONS.TOKENS);
          
          // Use upsert to create or update
          await tokenCollection.updateOne(
            { agentId: 'coby-agent' },
            { $set: data },
            { upsert: true }
          );
          
          console.log('Token state saved to MongoDB');
        } catch (mongoError) {
          console.error('Error saving token state to MongoDB:', mongoError);
          // Fall through to file-based saving
        }
      }
      
      // Always save to file as backup (even if MongoDB worked)
      // Create data directory if it doesn't exist
      const dataDir = path.dirname(TOKEN_STATE_FILE);
      if (!fs.existsSync(dataDir)) {
        console.log('Creating data directory:', dataDir);
        fs.mkdirSync(dataDir, { recursive: true });
      }
      
      fs.writeFileSync(TOKEN_STATE_FILE, JSON.stringify(data, null, 2));
      console.log('Token state saved to file');
      
      // Verify the file was written
      if (fs.existsSync(TOKEN_STATE_FILE)) {
        const savedData = JSON.parse(fs.readFileSync(TOKEN_STATE_FILE, 'utf8'));
        console.log('Verified saved token state:', savedData);
      } else {
        console.error('Token state file was not created!');
      }
    } catch (error) {
      console.error('Error saving token state:', error);
    }
  }

  /**
   * Schedule a token launch in the future
   * @param {string} agentId - The ID of the agent to schedule the launch for
   * @param {number} delayMinutes - Minutes to delay the launch (default: random between 10-30)
   * @param {boolean} tweetAboutSchedule - Whether to tweet about the scheduled launch
   * @returns {object} Result with scheduling information
   */
  scheduleTokenLaunch(agentId, delayMinutes = null, tweetAboutSchedule = true) {
    // Skip if token already launched or already scheduled
    if (this.tokenLaunched) {
      console.log(`Token already launched for agent ${agentId}, skipping scheduling`);
      return {
        alreadyLaunched: true,
        mintAddress: this.tokenMintAddress
      };
    }

    if (this.launchScheduled) {
      console.log(`Token launch already scheduled for agent ${agentId} at ${this.scheduledLaunchTime}`);
      return {
        alreadyScheduled: true,
        scheduledTime: this.scheduledLaunchTime
      };
    }

    // Randomize delay if not specified
    if (!delayMinutes) {
      // Random delay between 10-30 minutes
      delayMinutes = Math.floor(Math.random() * 21) + 10;
    }

    // Calculate scheduled time
    const now = new Date();
    this.scheduledLaunchTime = new Date(now.getTime() + (delayMinutes * 60 * 1000));

    console.log(`Scheduling token launch for agent ${agentId} in ${delayMinutes} minutes at ${this.scheduledLaunchTime}`);

    // Mark as scheduled
    this.launchScheduled = true;
    this.saveTokenState();

    // Post a tweet about planning to launch a token if requested
    if (tweetAboutSchedule && this.twitterClient && Math.random() > 0.5) { // 50% chance
      setTimeout(async () => {
        try {
          // Simple, direct message about considering a token launch
          const message = "thinking about launching a token on pump.fun";
          console.log(`Posting tweet about upcoming token launch: "${message}"`);
          
          await this.twitterClient.postTweet(agentId, message);
        } catch (tweetError) {
          console.error('Error posting tweet about scheduled token launch:', tweetError);
        }
      }, Math.floor(delayMinutes * 60 * 1000 / 3)); // Post 1/3 of the way through the wait time
    }

    // Set timeout to execute the launch
    setTimeout(async () => {
      console.log(`Scheduled time reached for token launch of agent ${agentId}`);
      try {
        const result = await this.launchTokenIfNeeded(agentId);
        console.log(`Scheduled token launch completed with result:`, result);
      } catch (error) {
        console.error(`Error during scheduled token launch for agent ${agentId}:`, error);
      }
    }, delayMinutes * 60 * 1000);

    return {
      scheduled: true,
      agentId,
      delayMinutes,
      scheduledTime: this.scheduledLaunchTime
    };
  }

  /**
   * Check if a scheduled token launch is pending
   */
  isLaunchScheduled() {
    return this.launchScheduled && !this.tokenLaunched;
  }

  /**
   * Launch a token on pump.fun if not already launched
   * This implementation uses the actual solana-agent-kit implementation
   */
  async launchTokenIfNeeded(agentId) {
    console.log(`Checking if token already launched: ${this.tokenLaunched ? 'YES' : 'NO'}`);
    
    // Skip if token already launched
    if (this.tokenLaunched) {
      console.log(`Token already launched for agent ${agentId}, skipping`);
      return {
        alreadyLaunched: true,
        mintAddress: this.tokenMintAddress
      };
    }

    try {
      // Initialize agent kit if not already done
      if (!this.agentKit) {
        const initialized = await this.initializeAgentKit();
        if (!initialized) {
          throw new Error('Failed to initialize solana-agent-kit');
        }
      }

      // Default token image - placeholder image for test token
      const imageUrl = 'https://i.imgur.com/HgZWpkG.png'; // Generic token image

      // Launch the token on pump.fun using solana-agent-kit's launchPumpFunToken method
      console.log(`Launching test token for agent ${agentId}...`);
      
      // Call the actual solana-agent-kit method for launching pump.fun tokens
      const result = await this.agentKit.launchPumpFunToken({
        tokenName: "Test",
        tokenTicker: "TEST",
        description: "", // No description as requested
        imageUrl,
        initialLiquiditySOL: 0.05, // Small amount for testing
        slippageBps: 10,
        priorityFee: 0.0001
      });

      // Check if successful
      if (result.status === 'success') {
        console.log(`Token launched successfully: ${result.mint}`);
        
        // Update state
        this.tokenLaunched = true;
        this.tokenMintAddress = result.mint;
        this.launchScheduled = false; // Reset scheduled flag
        
        // Save state
        this.saveTokenState();

        // Generate pump.fun link
        const pumpFunLink = `https://pump.fun/token/${result.mint}`;
        
        // Post tweet if Twitter client is available
        if (this.twitterClient) {
          // Simple, direct message with the token link
          const tweetContent = `launched a token ${pumpFunLink}`;
          console.log('Posting tweet with content:', tweetContent);
          
          try {
            const tweet = await this.twitterClient.postTweet(agentId, tweetContent);
            console.log(`Tweet posted about token launch: ${tweet.id}`);
          } catch (tweetError) {
            console.error('Error posting tweet:', tweetError);
            console.log('Continuing without posting tweet');
          }
        } else {
          console.log('Twitter client not available, skipping tweet');
        }

        return {
          success: true,
          mintAddress: result.mint,
          pumpFunLink,
          signature: result.signature,
          metadataUri: result.metadataUri
        };
      } else {
        throw new Error(`Failed to launch token: ${result.message}`);
      }
    } catch (error) {
      console.error('Error launching token:', error);
      if (error.stack) {
        console.error('Error stack:', error.stack);
      }
      return {
        success: false,
        error: error.message
      };
    }
  }
}

module.exports = PumpFunTokenManager; 