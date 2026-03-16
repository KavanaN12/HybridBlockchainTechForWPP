#!/usr/bin/env bash
# Start local Ganache blockchain for testing

echo "=================================================="
echo "🚀 Starting Ganache Local Blockchain"
echo "=================================================="

# Check if ganache is installed globally
if ! command -v ganache &> /dev/null; then
    echo "❌ Ganache not found. Installing globally..."
    npm install -g ganache
fi

# Start ganache on port 8545
echo "⏳ Starting Ganache on http://127.0.0.1:8545..."
echo "📊 Accounts: 10"
echo "💰 Balance per account: 1000 ETH"
echo ""

ganache --host 0.0.0.0 --port 8545 --accounts 10 --deterministic
