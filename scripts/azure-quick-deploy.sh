#!/bin/bash
# Quick Azure Deployment Script for WPP Digital Twin
# Usage: bash azure-quick-deploy.sh

set -e

echo "=========================================="
echo "WPP Digital Twin - Azure Quick Deploy"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
RESOURCE_GROUP="wpp-rg"
LOCATION="eastus"
REGISTRY_NAME="wppdigitaltwin"
APP_NAME="wpp-dashboard"
COSMOS_DB_NAME="wpp-trading-db"

# Step 1: Check prerequisites
echo -e "${BLUE}[1/10] Checking prerequisites...${NC}"
command -v az >/dev/null 2>&1 || { echo "Azure CLI not found. Install from https://docs.microsoft.com/cli/azure/install-azure-cli"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "Docker not found. Install from https://www.docker.com/"; exit 1; }
echo -e "${GREEN}✓ Prerequisites met${NC}"

# Step 2: Login to Azure
echo -e "${BLUE}[2/10] Logging in to Azure...${NC}"
az login
echo -e "${GREEN}✓ Logged in${NC}"

# Step 3: Create resource group
echo -e "${BLUE}[3/10] Creating resource group...${NC}"
az group create --name $RESOURCE_GROUP --location $LOCATION
echo -e "${GREEN}✓ Resource group created${NC}"

# Step 4: Create Container Registry
echo -e "${BLUE}[4/10] Creating Azure Container Registry...${NC}"
az acr create --resource-group $RESOURCE_GROUP --name $REGISTRY_NAME --sku Basic
echo -e "${GREEN}✓ ACR created${NC}"

# Step 5: Build and push Docker image
echo -e "${BLUE}[5/10] Building and pushing Docker image...${NC}"
az acr build --registry $REGISTRY_NAME --image wpp-digital-twin:latest .
echo -e "${GREEN}✓ Image pushed to ACR${NC}"

# Step 6: Create Cosmos DB
echo -e "${BLUE}[6/10] Creating Azure Cosmos DB...${NC}"
az cosmosdb create \
  --resource-group $RESOURCE_GROUP \
  --name $COSMOS_DB_NAME \
  --kind GlobalDocumentDB
echo -e "${GREEN}✓ Cosmos DB created${NC}"

# Step 7: Create App Service Plan
echo -e "${BLUE}[7/10] Creating App Service Plan...${NC}"
az appservice plan create \
  --name wpp-appplan \
  --resource-group $RESOURCE_GROUP \
  --sku B1 \
  --is-linux
echo -e "${GREEN}✓ App Service Plan created${NC}"

# Step 8: Create Web App
echo -e "${BLUE}[8/10] Creating Web App...${NC}"
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan wpp-appplan \
  --name $APP_NAME \
  --deployment-container-image-name ${REGISTRY_NAME}.azurecr.io/wpp-digital-twin:latest
echo -e "${GREEN}✓ Web App created${NC}"

# Step 9: Configure container settings
echo -e "${BLUE}[9/10] Configuring container settings...${NC}"
REGISTRY_PASSWORD=$(az acr credential show --name $REGISTRY_NAME --query "passwords[0].value" -o tsv)
az webapp config container set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --docker-custom-image-name ${REGISTRY_NAME}.azurecr.io/wpp-digital-twin:latest \
  --docker-registry-server-url https://${REGISTRY_NAME}.azurecr.io \
  --docker-registry-server-user $REGISTRY_NAME \
  --docker-registry-server-password $REGISTRY_PASSWORD
echo -e "${GREEN}✓ Container configured${NC}"

# Step 10: Get app URL
echo -e "${BLUE}[10/10] Getting app URL...${NC}"
APP_URL=$(az webapp show --resource-group $RESOURCE_GROUP --name $APP_NAME --query defaultHostName -o tsv)
echo -e "${GREEN}✓ Deployment complete!${NC}"

echo ""
echo "=========================================="
echo "✅ DEPLOYMENT SUCCESSFUL"
echo "=========================================="
echo -e "Dashboard URL: ${GREEN}https://${APP_URL}${NC}"
echo ""
echo "📋 Next Steps:"
echo "1. Open: https://${APP_URL}"
echo "2. Setup GitHub Secrets:"
echo "   - Go to GitHub Repo → Settings → Secrets"
echo "   - Add AZURE_CREDENTIALS from:"
echo "     az ad sp create-for-rbac --name 'WPP-GitHub' --role contributor"
echo "3. Push code to trigger CI/CD:"
echo "   git push origin main"
echo ""
echo "📊 Resources Created:"
echo "  • Resource Group: $RESOURCE_GROUP"
echo "  • Container Registry: $REGISTRY_NAME"
echo "  • Web App: $APP_NAME"
echo "  • Cosmos DB: $COSMOS_DB_NAME"
echo ""
echo "💰 Estimated Cost: ~$44/month"
echo "=========================================="
