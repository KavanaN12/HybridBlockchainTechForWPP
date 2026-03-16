# PowerShell script to start Ganache local blockchain for Windows

Write-Host "=================================================="  -ForegroundColor Cyan
Write-Host "[>>] Starting Ganache Local Blockchain" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Check if ganache is installed
Write-Host "[*] Checking for Ganache..." -ForegroundColor Yellow
$ganacheInstalled = npm list -g ganache 2>$null | Select-String "ganache"

if (-not $ganacheInstalled) {
    Write-Host "[!] Ganache not found. Installing globally..." -ForegroundColor Red
    npm install -g ganache
}

# Start ganache
Write-Host "[*] Starting Ganache on http://127.0.0.1:8545..." -ForegroundColor Yellow
Write-Host "[*] Accounts: 10" -ForegroundColor Green
Write-Host "[*] Balance per account: 1000 ETH" -ForegroundColor Green
Write-Host ""

ganache --host 0.0.0.0 --port 8545 --accounts 10 --deterministic
