# Quick Azure Deployment Script for WPP Digital Twin (Windows)
# Usage: .\azure-quick-deploy.ps1

param(
    [string]$ResourceGroup = "wpp-rg",
    [string]$Location = "eastus",
    [string]$RegistryName = "wppdigitaltwin",
    [string]$AppName = "wpp-dashboard"
)

# Color functions
function Write-Info { Write-Host $args -ForegroundColor Blue }
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "WPP Digital Twin - Azure Quick Deploy" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check prerequisites
Write-Info "[1/10] Checking prerequisites..."
try {
    az --version | Out-Null
    Write-Success "✓ Azure CLI found"
} catch {
    Write-Host "❌ Azure CLI not found. Install from https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
}

try {
    docker --version | Out-Null
    Write-Success "✓ Docker found"
} catch {
    Write-Host "❌ Docker not found. Install from https://www.docker.com/"
    exit 1
}

# Step 2: Login to Azure
Write-Info "[2/10] Logging in to Azure..."
az login
Write-Success "✓ Logged in to Azure"

# Step 3: Create resource group
Write-Info "[3/10] Creating resource group..."
az group create --name $ResourceGroup --location $Location
Write-Success "✓ Resource group created: $ResourceGroup"

# Step 4: Create Container Registry
Write-Info "[4/10] Creating Azure Container Registry..."
az acr create --resource-group $ResourceGroup --name $RegistryName --sku Basic
Write-Success "✓ Container Registry created: $RegistryName"

# Step 5: Build and push Docker image
Write-Info "[5/10] Building and pushing Docker image to ACR..."
$CurrentLocation = Get-Location
Set-Location $PSScriptRoot\..\
az acr build --registry $RegistryName --image wpp-digital-twin:latest .
Set-Location $CurrentLocation
Write-Success "✓ Docker image pushed to ACR"

# Step 6: Create Cosmos DB
Write-Info "[6/10] Creating Azure Cosmos DB..."
az cosmosdb create `
    --resource-group $ResourceGroup `
    --name "wpp-trading-db" `
    --kind GlobalDocumentDB
Write-Success "✓ Cosmos DB created"

# Step 7: Create App Service Plan
Write-Info "[7/10] Creating App Service Plan..."
az appservice plan create `
    --name "wpp-appplan" `
    --resource-group $ResourceGroup `
    --sku B1 `
    --is-linux
Write-Success "✓ App Service Plan created"

# Step 8: Create Web App
Write-Info "[8/10] Creating Web App..."
az webapp create `
    --resource-group $ResourceGroup `
    --plan "wpp-appplan" `
    --name $AppName `
    --deployment-container-image-name "$RegistryName.azurecr.io/wpp-digital-twin:latest"
Write-Success "✓ Web App created: $AppName"

# Step 9: Configure container settings
Write-Info "[9/10] Configuring container settings..."
$RegistryPassword = az acr credential show --name $RegistryName --query "passwords[0].value" -o tsv
az webapp config container set `
    --resource-group $ResourceGroup `
    --name $AppName `
    --docker-custom-image-name "$RegistryName.azurecr.io/wpp-digital-twin:latest" `
    --docker-registry-server-url "https://$RegistryName.azurecr.io" `
    --docker-registry-server-user $RegistryName `
    --docker-registry-server-password $RegistryPassword
Write-Success "✓ Container configured"

# Step 10: Get app URL
Write-Info "[10/10] Getting app URL..."
$AppUrl = az webapp show --resource-group $ResourceGroup --name $AppName --query defaultHostName -o tsv

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "✅ DEPLOYMENT SUCCESSFUL" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Dashboard URL: " -NoNewline
Write-Host "https://$AppUrl" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Open: https://$AppUrl"
Write-Host "2. Setup GitHub Secrets:"
Write-Host "   - Go to GitHub Repo → Settings → Secrets"
Write-Host "   - Add AZURE_CREDENTIALS by running:"
Write-Host "     az ad sp create-for-rbac --name 'WPP-GitHub' --role contributor"
Write-Host "3. Push code to trigger CI/CD:"
Write-Host "     git push origin main"
Write-Host ""
Write-Host "📊 Resources Created:" -ForegroundColor Cyan
Write-Host "  • Resource Group: $ResourceGroup"
Write-Host "  • Container Registry: $RegistryName"
Write-Host "  • Web App: $AppName"
Write-Host "  • Cosmos DB: wpp-trading-db"
Write-Host ""
Write-Host "💰 Estimated Cost: ~$44/month" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
