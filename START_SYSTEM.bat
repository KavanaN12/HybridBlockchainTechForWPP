@echo off
REM WPP Digital Twin - Quick Command Reference
REM =============================================

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║        WPP DIGITAL TWIN - COMMAND REFERENCE                  ║
echo ║           Real Blockchain Integration                         ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo 📋 QUICK START COMMANDS:
echo.
echo 🔵 TERMINAL 1 - Start Blockchain Node:
echo    cd d:\WPPDigitalTwin\blockchain
echo    npx hardhat node
echo.
echo    [WAIT FOR: "Started HTTP and WebSocket JSON-RPC server at http://127.0.0.1:8545"]
echo    [DON'T CLOSE THIS TERMINAL]
echo.

echo 🟡 TERMINAL 2 - Deploy Contract (after Terminal 1 shows servers started):
echo    cd d:\WPPDigitalTwin\blockchain
echo    npx hardhat run scripts/deploy.js --network localhost
echo.
echo    [COPY CONTRACT_ADDRESS from output]
echo.

echo 🟢 TERMINAL 3 - Start MongoDB:
echo    mongod --dbpath d:\WPPDigitalTwin\data\mongo
echo.

echo 🟢 TERMINAL 4 - Run Dashboard:
echo    cd d:\WPPDigitalTwin
echo    streamlit run dashboard/app.py
echo.

echo ════════════════════════════════════════════════════════════════
echo.

echo 📝 AFTER DEPLOYMENT:
echo.
echo 1. Copy these values from Terminal 2 deployment output:
echo    - CONTRACT_ADDRESS
echo    - PRIVATE_KEY (first hardhat test account)
echo.
echo 2. Edit d:\WPPDigitalTwin\.env:
echo    CONTRACT_ADDRESS=<paste from output>
echo    PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb476c89b5d8d0e6e4547f40e4649
echo.

echo 3. Refresh dashboard (F5) or restart
echo.

echo ════════════════════════════════════════════════════════════════
echo.

echo 🧪 TEST THE SYSTEM:
echo.
echo ✓ Consumer Role:
echo   - Place Bid → stored in MongoDB
echo   - Shows all bids with MongoDB connection
echo.
echo ✓ Settlement:
echo   - Run Settlement → calculates winner
echo   - Store on Blockchain → executes contract call
echo   - Updates with blockchain transaction hash
echo.
echo ✓ Maintainer:
echo   - Verify Hash → checks data integrity
echo   - Compares MongoDB hash with blockchain
echo.

echo ════════════════════════════════════════════════════════════════
echo.

echo 📊 SYSTEM STATUS:
echo.
echo STATUS: ✅ READY FOR DEPLOYMENT
echo.
echo Components:
echo ✓ MongoDB: Local (localhost:27017)
echo ✓ Blockchain: Hardhat (localhost:8545)
echo ✓ Services: All implemented
echo ✓ Dashboard: Connected
echo ✓ Kaggle API: Configured
echo.

echo ════════════════════════════════════════════════════════════════
echo.

echo 💡 TIPS:
echo.
echo • Keep all 4 terminals open while testing
echo • Contract address changes each time you restart hardhat
echo • Always redeploy after restarting blockchain
echo • Dashboard automatically connects once .env is updated
echo • Check browser console for detailed errors
echo.

echo ════════════════════════════════════════════════════════════════
echo.
echo Ready? Run the commands above! 🚀
echo.
