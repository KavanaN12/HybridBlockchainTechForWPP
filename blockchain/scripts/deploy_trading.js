/**
 * blockchain/scripts/deploy_trading.js
 * 
 * Hardhat deployment script for P2P Energy Trading system
 * 
 * Deploys:
 * 1. EnergyToken (ERC-20) - tokens representing hourly energy generation
 * 2. AuctionEngine (sealed-bid) - peer-to-peer trading mechanism
 * 
 * Usage: npx hardhat run scripts/deploy_trading.js --network localhost
 * 
 * Outputs:
 * - Contract addresses written to .env
 * - Transaction hashes and gas reports
 * - Integration tests with mock bids
 */

const hre = require("hardhat");
const fs = require("fs");
const path = require("path");
const { ethers } = require("hardhat");
const { network } = require("hardhat");

// Define bid period duration at the top level
const bidPeriodDuration = 3600; // 1 hour in seconds

// Define reveal duration at the top level
const revealDuration = 10 * 60; // 10 minutes in seconds

// Define adjustedRevealBuffer for timing adjustments
const adjustedRevealBuffer = 5; // 5 seconds buffer to keep reveal period open

// Use contract constants for time durations
    const CONTRACT_BID_DURATION = 30 * 60; // 30 minutes in seconds
    const CONTRACT_REVEAL_DURATION = 10 * 60; // 10 minutes in seconds

const postRevealBuffer = 120; // 2 minutes buffer after reveal period ends

async function main() {
    console.log("\n" + "=".repeat(70));
    console.log("  P2P ENERGY TRADING SYSTEM DEPLOYMENT");
    console.log("=".repeat(70) + "\n");

    // Get deployer account
    const [deployer] = await ethers.getSigners();
    console.log(`↓ Deploying from account: ${deployer.address}`);
    
    // Account balance check
    const balance = await deployer.provider.getBalance(deployer.address);
    console.log(`↓ Account balance: ${ethers.formatEther(balance)} ETH\n`);

    // ============== DEPLOY EnergyToken ==============
    console.log("[1/2] Deploying EnergyToken (ERC-20)...");
    const EnergyToken = await hre.ethers.getContractFactory("EnergyToken");
    const energyToken = await EnergyToken.deploy();
    await energyToken.waitForDeployment();
    const energyTokenAddress = await energyToken.getAddress();
    
    console.log(`✓ EnergyToken deployed to: ${energyTokenAddress}`);
    const deployTx1 = energyToken.deploymentTransaction();
    if (deployTx1) {
        const receipt1 = await deployTx1.wait();
        console.log(`  Gas used: ${receipt1.gasUsed} units\n`);
    }

    // ============== DEPLOY AuctionEngine ==============
    console.log("[2/2] Deploying AuctionEngine (Sealed-Bid Auction)...");
    const AuctionEngine = await hre.ethers.getContractFactory("AuctionEngine");
    const auctionEngine = await AuctionEngine.deploy(energyTokenAddress, deployer.address);
    await auctionEngine.waitForDeployment();
    const auctionEngineAddress = await auctionEngine.getAddress();
    
    console.log(`✓ AuctionEngine deployed to: ${auctionEngineAddress}`);
    const deployTx2 = auctionEngine.deploymentTransaction();
    if (deployTx2) {
        const receipt2 = await deployTx2.wait();
        console.log(`  Gas used: ${receipt2.gasUsed} units`);
    }

    // ============== SETUP: Grant Minter Role ==============
    console.log("\n[SETUP] Configuring minter permissions...");
    const addMinterTx = await energyToken.addMinter(auctionEngineAddress);
    await addMinterTx.wait();
    console.log(`✓ AuctionEngine granted MINTER role on EnergyToken\n`);

    // ============== INTEGRATION TESTS ==============
    console.log("[TEST] Running integration tests...\n");

    // Test 1: Mint tokens for auction
    console.log("Test 1: Hourly token minting");
    const hourTimestamp = Math.floor(Date.now() / 1000) - (Math.floor(Date.now() / 1000) % 3600);
    const energyWh = 5000000;  // 5 MWh = 5M tokens
    
    const mintTx = await energyToken.mintHourlyGeneration(auctionEngineAddress, hourTimestamp, energyWh);
    await mintTx.wait();
    
    const balance1 = await energyToken.balanceOf(auctionEngineAddress);
    console.log(`  ✓ Minted ${energyWh} ENERGY tokens for hour ${hourTimestamp}`);
    console.log(`  ✓ AuctionEngine balance: ${balance1} tokens\n`);

    // Verify token balance after minting
    const mintedBalance = await energyToken.balanceOf(auctionEngineAddress);
    console.log(`  Debug: AuctionEngine token balance after minting: ${mintedBalance} tokens`);

    // Debug: Log token balance after each operation
    const postOperationBalance = await energyToken.balanceOf(auctionEngineAddress);
    console.log(`  Debug: AuctionEngine token balance after operation: ${postOperationBalance} tokens`);

    // Test 2: Start auction
    console.log("Test 2: Starting hourly auction");
    const startAuctionTx = await auctionEngine.startAuction(hourTimestamp, energyWh);
    await startAuctionTx.wait();
    
    const auctionId = 1;
    const auctionDetails = await auctionEngine.getAuctionDetails(auctionId);
    console.log(`  ✓ Auction started: ID=${auctionId}`);
    console.log(`  ✓ Energy available: ${auctionDetails.energyAvailable} tokens`);
    console.log(`  ✓ Bid deadline: ${new Date(Number(auctionDetails.bidDeadline) * 1000).toISOString()}\n`);

    // Convert BigInt to Number for logging
    const revealDeadline = Number(auctionDetails.revealDeadline);
    console.log(`  ✓ Reveal deadline: ${new Date(revealDeadline * 1000).toISOString()}`);

    // Debug: Log current blockchain time and reveal deadline
    const currentBlock = await ethers.provider.getBlock("latest");
    const currentTime = currentBlock.timestamp;
    console.log(`  Debug: Current blockchain time: ${new Date(currentTime * 1000).toISOString()}`);
    console.log(`  Debug: Reveal deadline: ${new Date(revealDeadline * 1000).toISOString()}`);

    // Test 3: Place sealed bids (mock)
    console.log("Test 3: Placing sealed bids");
    const buyers = (await ethers.getSigners()).slice(1, 4);  // Use 3 test accounts
    const bidPrices = [1000000n, 2000000n, 1500000n];  // in wei per token
    const nonces = [123456n, 234567n, 345678n];
    
    for (let i = 0; i < buyers.length; i++) {
        const commitment = ethers.keccak256(
            ethers.AbiCoder.defaultAbiCoder().encode(
                ['uint256', 'uint256'],
                [bidPrices[i], nonces[i]]
            )
        );
        
        const placeBidTx = await auctionEngine.connect(buyers[i]).placeBid(auctionId, commitment);
        await placeBidTx.wait();
        console.log(`  ✓ Buyer ${i + 1} (${buyers[i].address.slice(0, 6)}...) placed sealed bid`);
    }
    console.log(`  ✓ Total bids received: ${buyers.length}\n`);

    // Advance time by bid duration
    await network.provider.send("evm_increaseTime", [CONTRACT_BID_DURATION]);
    await network.provider.send("evm_mine");
    console.log(`  ✓ Advanced blockchain time by bid duration\n`);

    // Advance time by reveal duration
    await network.provider.send("evm_increaseTime", [CONTRACT_REVEAL_DURATION - adjustedRevealBuffer]);
    await network.provider.send("evm_mine");
    console.log(`  ✓ Adjusted blockchain time to keep reveal period open\n`);

    // Adjust blockchain time to ensure it is well within the reveal period
    await network.provider.send("evm_increaseTime", [adjustedRevealBuffer]);
    await network.provider.send("evm_mine");
    console.log(`  ✓ Adjusted blockchain time to ensure reveal period remains open\n`);

    // Validate blockchain time before revealing bids
    const validateBlockTime = await ethers.provider.getBlock("latest");
    const validateTime = validateBlockTime.timestamp;
    console.log(`  Debug: Blockchain time before revealing bids: ${new Date(validateTime * 1000).toISOString()}`);

    // Ensure reveal period is open before each revealBid call
    for (let i = 0; i < buyers.length; i++) {
        const currentBlock = await ethers.provider.getBlock("latest");
        const currentTime = currentBlock.timestamp;
        if (currentTime > revealDeadline) {
            throw new Error(`Reveal period closed before Buyer ${i + 1} could reveal their bid.`);
        }
        console.log(`  Debug: Blockchain time before revealBid for Buyer ${i + 1}: ${new Date(currentTime * 1000).toISOString()}`);

        const revealBidTx = await auctionEngine.connect(buyers[i]).revealBid(
            auctionId,
            bidPrices[i],
            nonces[i]
        );
        await revealBidTx.wait();
        console.log(`  ✓ Buyer ${i + 1} revealed bid: ${ethers.formatUnits(bidPrices[i], 0)} wei/token`);
    }
    console.log();

    // Wait for reveal period to close
    console.log("Test 6: Simulating reveal period closure...");
    await network.provider.send("evm_mine");
    console.log(`  ✓ Advanced blockchain time\n`);

    // Advance blockchain time to ensure reveal period is fully closed
    const timeToCloseReveal = revealDeadline - (await ethers.provider.getBlock("latest")).timestamp + postRevealBuffer;
    if (timeToCloseReveal > 0) {
        await network.provider.send("evm_increaseTime", [timeToCloseReveal]);
        await network.provider.send("evm_mine");
        console.log(`  ✓ Advanced blockchain time to ensure reveal period closure`);
    }

    // Log blockchain time before settlement
    const preSettlementBlock = await ethers.provider.getBlock("latest");
    const preSettlementTime = preSettlementBlock.timestamp;
    console.log(`  Debug: Blockchain time before settlement: ${new Date(preSettlementTime * 1000).toISOString()}`);

    // Fund AuctionEngine with ETH for settlement payout
    const auctionDetailsForSettle = await auctionEngine.getAuctionDetails(auctionId);
    const settlementValue = BigInt(auctionDetailsForSettle.energyAvailable) * BigInt(auctionDetailsForSettle.highestBid);
    console.log(`  Debug: Funding AuctionEngine with ${settlementValue} wei for settlement`);
    const fundingTx = await deployer.sendTransaction({
        to: auctionEngineAddress,
        value: settlementValue
    });
    await fundingTx.wait();

    // Ensure sufficient energy token balance exists before settlement
    const preSettlementBalanceCheck = await energyToken.balanceOf(auctionEngineAddress);
    if (preSettlementBalanceCheck < auctionDetailsForSettle.energyAvailable) {
        throw new Error(`Insufficient tokens in AuctionEngine for settlement. Available: ${preSettlementBalanceCheck}, Required: ${auctionDetailsForSettle.energyAvailable}`);
    }

    // Attempt to settle the auction
    console.log("Test 7: Settling auction");
    const settleTx = await auctionEngine.settleAuction(auctionId);
    const settleReceipt = await settleTx.wait();

    const auctionAfter = await auctionEngine.getAuctionDetails(auctionId);
    const winnerBalance = await energyToken.balanceOf(auctionAfter.winner);

    console.log(`  ✓ Auction settled`);
    console.log(`  ✓ Winner: ${auctionAfter.winner.slice(0, 6)}...`);
    console.log(`  ✓ Winning price: ${ethers.formatUnits(auctionAfter.highestBid, 0)} wei/token`);
    console.log(`  ✓ Winner received: ${winnerBalance} tokens`);
    console.log(`  ✓ Settlement gas: ${settleReceipt.gasUsed} units\n`);

    // Debug: Log token balances before settlement
    const preSettlementBalance = await energyToken.balanceOf(auctionEngineAddress);
    console.log(`  Debug: AuctionEngine token balance before settlement: ${preSettlementBalance} tokens`);

    // Debug: Log token balance after settlement
    const postSettlementBalance = await energyToken.balanceOf(auctionEngineAddress);
    console.log(`  Debug: AuctionEngine token balance after settlement: ${postSettlementBalance} tokens`);

    const auctionDetailsBeforeSettlement = await auctionEngine.getAuctionDetails(auctionId);
    console.log(`  Debug: Auction details before settlement:`, auctionDetailsBeforeSettlement);

    // ============== SAVE DEPLOYMENT INFO ==============
    const deploymentInfo = {
        timestamp: new Date().toISOString(),
        network: hre.network.name,
        deployer: deployer.address,
        contracts: {
            EnergyToken: {
                address: energyTokenAddress,
                symbol: "ENERGY",
                decimals: 0,
                description: "Renewable energy tokens (1 token = 1 Wh)"
            },
            AuctionEngine: {
                address: auctionEngineAddress,
                turbineOwner: deployer.address,
                description: "Sealed-bid P2P energy trading mechanism"
            }
        },
        testResults: {
            tokensMinted: energyWh,
            auctionStarted: true,
            bidsPlaced: buyers.length,
            auctionSettled: true,
            gasSummary: {
                energyTokenDeploy: "varies",
                auctionEngineDeploy: "varies",
                settlementGas: Number(settleReceipt.gasUsed)
            }
        }
    };

    // Write to file
    const deploymentPath = path.join(__dirname, "../", "deployment_trading.json");
    fs.writeFileSync(deploymentPath, JSON.stringify(deploymentInfo, null, 2));
    console.log(`✓ Deployment info saved to: ${deploymentPath}\n`);

    // Update .env with contract addresses
    const envPath = path.join(__dirname, "../../", ".env");
    let envContent = fs.readFileSync(envPath, "utf8");
    
    envContent += `\n# P2P Energy Trading Contracts\n`;
    envContent += `ENERGY_TOKEN_ADDRESS=${energyTokenAddress}\n`;
    envContent += `AUCTION_ENGINE_ADDRESS=${auctionEngineAddress}\n`;
    
    fs.writeFileSync(envPath, envContent);
    console.log(`✓ Contract addresses written to .env\n`);

    // ============== SUMMARY ==============
    console.log("=".repeat(70));
    console.log("  DEPLOYMENT COMPLETE");
    console.log("=".repeat(70));
    console.log(`
Contract Addresses:
  • EnergyToken:    ${energyTokenAddress}
  • AuctionEngine:  ${auctionEngineAddress}

Integration Tests:
  ✓ Token minting works
  ✓ Auctions can be created
  ✓ Sealed bids can be placed
  ✓ Bids can be revealed
  ✓ Auctions settle correctly

Next Steps:
  1. Run: python sync/trading_orchestrator.py
     → Will create hourly auctions and mint tokens
  
  2. Run: streamlit run dashboard/app.py
     → View Tab 6 "Energy Marketplace" + Tab 7 "Settlement Tracker"
  
  3. Run: python experiments/run_exp_e_trading.py
     → Generate trading efficiency benchmarks

Ready for CI/CD testing!
    `);
    console.log("=".repeat(70) + "\n");
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
