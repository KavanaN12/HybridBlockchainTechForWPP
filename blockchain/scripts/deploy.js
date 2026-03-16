/**
 * Hardhat deployment script for DataAnchor smart contract
 * Deploy to local Ganache or public testnet
 */

async function main() {
  console.log("=".repeat(60));
  console.log("🚀 Deploying DataAnchor Smart Contract");
  console.log("=".repeat(60));

  // Get deployer account
  const [deployer] = await ethers.getSigners();
  console.log(`\n📍 Deployer Address: ${deployer.address}`);

  // Get account balance
  const balance = await ethers.provider.getBalance(deployer.address);
  console.log(`💰 Account Balance: ${ethers.formatEther(balance)} ETH`);

  // Deploy DataAnchor contract
  console.log("\n⏳ Deploying DataAnchor contract...");
  const DataAnchor = await ethers.getContractFactory("DataAnchor");
  const contract = await DataAnchor.deploy();

  await contract.waitForDeployment();

  const contractAddress = await contract.getAddress();
  console.log(`\n✅ DataAnchor deployed successfully!`);
  console.log(`📋 Contract Address: ${contractAddress}`);

  // Get deployment receipt for gas details
  const deploymentTx = contract.deploymentTransaction();
  const receipt = await deploymentTx.wait();
  console.log(`⛽ Gas Used: ${receipt.gasUsed}`);

  // Test basic functionality
  console.log("\n🧪 Testing contract functionality...");

  const testHour = 1;
  const testHash = ethers.keccak256(ethers.toUtf8Bytes("test-batch-1"));
  const testEnergy = ethers.parseUnits("1000", "wei");

  console.log(`  Storing test hash: ${testHash}`);
  const tx = await contract.storeBatchHash(testHour, testHash, testEnergy);
  await tx.wait();
  console.log(`  ✓ Batch stored`);

  const batch = await contract.getBatch(testHour);
  console.log(`  ✓ Retrieved batch hash: ${batch.batchHash}`);
  console.log(`  ✓ Energy recorded: ${batch.totalEnergy}`);

  const isValid = await contract.verifyIntegrity(testHour, testHash);
  console.log(`  ✓ Integrity verification: ${isValid ? "PASSED" : "FAILED"}`);

  const batchCount = await contract.batchCount();
  console.log(`  ✓ Total batches stored: ${batchCount}`);

  console.log("\n" + "=".repeat(60));
  console.log("✅ Deployment and testing complete!");
  console.log("=".repeat(60));

  const deploymentInfo = {
    network: (await ethers.provider.getNetwork()).name,
    contractAddress: contractAddress,
    deployerAddress: deployer.address,
    deploymentTime: new Date().toISOString(),
    gasUsed: receipt.gasUsed.toString(),
  };

  console.log("\n📊 Deployment Info:");
  console.log(JSON.stringify(deploymentInfo, null, 2));

  return deploymentInfo;
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });