#!/usr/bin/env python3
"""
Sepolia Testnet Deployment Helper
Guides you through the entire Sepolia deployment process
"""

import sys
import os
import json
from pathlib import Path

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_env():
    """Check if .env is configured for Sepolia."""
    print_header("1️⃣  CHECKING ENVIRONMENT CONFIGURATION")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("\n📝 Creating .env template...")
        with open(".env", "w") as f:
            f.write("""# Sepolia Testnet Configuration
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_KEY
PRIVATE_KEY=0xyour_private_key_here
CONTRACT_ADDRESS=  # Will be filled after deployment
""")
        print("✅ Created .env file")
        print("\n⚠️  NEXT STEPS:")
        print("1. Get Infura API key: https://www.infura.io/")
        print("2. Get Sepolia ETH: https://www.alchemy.com/faucets/ethereum-sepolia")
        print("3. Export private key from MetaMask or create new account")
        print("4. Update .env with your values")
        return False
    
    # Check required keys
    with open(".env") as f:
        content = f.read()
    
    has_rpc = "SEPOLIA_RPC_URL=" in content and "YOUR_INFURA_KEY" not in content
    has_key = "PRIVATE_KEY=" in content and "0x" in content and "your_private_key" not in content
    
    if has_rpc and has_key:
        print("✅ .env is configured for Sepolia")
        return True
    else:
        print("⚠️  .env needs configuration:")
        if not has_rpc:
            print("  - SEPOLIA_RPC_URL not set")
        if not has_key:
            print("  - PRIVATE_KEY not set")
        return False

def get_account_info():
    """Display account information."""
    print_header("2️⃣  CHECKING ACCOUNT & BALANCE")
    
    print("""
To check your account balance:
1. Get your wallet address (MetaMask: Account details)
2. Visit: https://sepolia.etherscan.io/
3. Search your address
4. You should see ETH balance

Need testnet ETH? Visit:
https://www.alchemy.com/faucets/ethereum-sepolia
""")

def deploy_contract():
    """Deploy contract to Sepolia."""
    print_header("3️⃣  DEPLOYING TO SEPOLIA")
    
    print("""
To deploy DataAnchor to Sepolia:

$ cd blockchain
$ npx hardhat run scripts/deploy.js --network sepolia

Expected output:
  ✅ DataAnchor deployed successfully!
  📋 Contract Address: 0x1234567890abcdef...
  
Save the contract address - you'll need it!
""")

def verify_contract():
    """Verify contract on Etherscan."""
    print_header("4️⃣  VERIFYING CONTRACT ON ETHERSCAN")
    
    print("""
To verify contract on Etherscan:

1. Visit: https://sepolia.etherscan.io/
2. Search your contract address
3. Go to "Code" tab
4. Click "Verify and Publish"
5. Select "Solidity" compiler
6. Choose compiler version: 0.8.20
7. Select license: MIT
8. Paste DataAnchor.sol code
9. Click verify

This allows anyone to see and audit your contract code!
""")

def test_contract():
    """Test contract interactions."""
    print_header("5️⃣  TESTING CONTRACT ON SEPOLIA")
    
    print("""
To test contract interactions:

$ cd blockchain
$ npx hardhat console --network sepolia

Then run:
> const DataAnchor = await ethers.getContractFactory("DataAnchor");
> const contract = await DataAnchor.attach("0x1234...");
> await contract.batchCount();  // Should show 0
> 
> // Store a test batch
> const tx = await contract.storeBatchHash(1, ethers.id("test"), 1000);
> await tx.wait();
> console.log("✓ Batch stored!");
> 
> // Verify it was stored
> const batch = await contract.getBatch(1);
> console.log(batch);

Type 'exit' to exit console
""")

def monitor_deployment():
    """Monitor the deployment."""
    print_header("6️⃣  MONITORING YOUR DEPLOYMENT")
    
    contract_address = input("Enter your contract address (0x...): ").strip()
    
    if not contract_address.startswith("0x"):
        print("❌ Invalid address format")
        return
    
    print(f"\n✅ Monitoring {contract_address}")
    print(f"\nVisit these links to monitor your contract:\n")
    print(f"📊 Contract Details:")
    print(f"   https://sepolia.etherscan.io/address/{contract_address}")
    print(f"\n💰 Transactions:")
    print(f"   https://sepolia.etherscan.io/address/{contract_address}#txs")
    print(f"\n📈 Gas Analytics:")
    print(f"   https://sepolia.etherscan.io/gastracker")
    
    print("\n⚠️  TIPS:")
    print("  - Save this address in your notes")
    print("  - Monitor gas prices before sending transactions")
    print("  - Each batch storage costs ~50,000 gas")
    print("  - At 20 gwei, that's ~$1-2 per transaction")

def save_deployment():
    """Save deployment info to file."""
    print_header("7️⃣  SAVING DEPLOYMENT INFO")
    
    contract_address = input("Enter deployed contract address (0x...): ").strip()
    rpc_url = input("Enter Sepolia RPC URL: ").strip()
    
    deployment_info = {
        "network": "sepolia",
        "contract_address": contract_address,
        "rpc_url": rpc_url,
        "deployer": "current wallet",
        "timestamp": str(__import__("datetime").datetime.now()),
        "explorer_url": f"https://sepolia.etherscan.io/address/{contract_address}"
    }
    
    with open("blockchain/SEPOLIA_DEPLOYMENT.json", "w") as f:
        json.dump(deployment_info, f, indent=2)
    
    print(f"\n✅ Saved to blockchain/SEPOLIA_DEPLOYMENT.json")
    print(f"\nExplorer: {deployment_info['explorer_url']}")

def main():
    """Main menu."""
    print_header("🌐 SEPOLIA TESTNET DEPLOYMENT HELPER")
    print("""
This tool guides you through deploying DataAnchor to Sepolia testnet.

Steps:
1. Check environment configuration
2. Display account information
3. Deploy contract to Sepolia
4. Verify on Etherscan
5. Test contract interactions
6. Monitor your deployment
7. Save deployment info
""")
    
    while True:
        print("\n" + "-"*60)
        print("OPTIONS:")
        print("  1 - Check .env configuration")
        print("  2 - Check account balance")
        print("  3 - Deploy to Sepolia")
        print("  4 - Verify on Etherscan")
        print("  5 - Test contract interactions")
        print("  6 - Monitor deployment")
        print("  7 - Save deployment info")
        print("  0 - Exit")
        print("-"*60)
        
        choice = input("\nEnter choice (0-7): ").strip()
        
        if choice == "1":
            if check_env():
                print("\n✅ Go to NEXT STEPS (2-7)")
            else:
                print("\n⏸️  Update .env file first, then restart this tool")
        elif choice == "2":
            get_account_info()
        elif choice == "3":
            deploy_contract()
        elif choice == "4":
            verify_contract()
        elif choice == "5":
            test_contract()
        elif choice == "6":
            monitor_deployment()
        elif choice == "7":
            save_deployment()
        elif choice == "0":
            print("\n✅ Goodbye! Happy deploying! 🚀")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✅ Exiting...")
        sys.exit(0)
