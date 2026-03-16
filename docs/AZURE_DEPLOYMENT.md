# Azure Deployment Guide for WPP Digital Twin

**Status**: Production-Ready  
**Platform**: Azure (App Service, Azure Cosmos DB, Container Registry)  
**Estimated Deployment Time**: 25 minutes  

---

## **Architecture Overview**

```
┌─────────────────────────────────────────────────────────┐
│                    AZURE DEPLOYMENT                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Azure Front Door / CDN                   │   │
│  │         (Global Load Balancing)                  │   │
│  └────────────────────┬─────────────────────────────┘   │
│                       │                                   │
│       ┌───────────────┴──────────────┬──────────────┐    │
│       │                              │              │    │
│  ┌────▼──────────┐  ┌────────────┐ ┌─▼──────────┐  │    │
│  │ App Service   │  │  Container │ │ Functions  │  │    │
│  │ (Dashboard)   │  │  Instances │ │(Orchestr.) │  │    │
│  └────┬──────────┘  └────┬───────┘ └─┬──────────┘  │    │
│       │                  │            │             │    │
│       └──────────────────┼────────────┘             │    │
│                          │                          │    │
│  ┌───────────────────────▼────────────────────────┐ │    │
│  │     Azure Cosmos DB / SQL Database              │ │    │
│  │    (Trading Logs + Blockchain State)            │ │    │
│  └────────────────────────────────────────────────┘ │    │
│                                                     │    │
│  ┌────────────────────────────────────────────────┐ │    │
│  │  Azure Key Vault                               │ │    │
│  │  (API Keys, Blockchain Credentials)            │ │    │
│  └────────────────────────────────────────────────┘ │    │
│                                                     │    │
│  ┌────────────────────────────────────────────────┐ │    │
│  │  Azure Monitor + Application Insights          │ │    │
│  │  (Logging & Performance Metrics)                │ │    │
│  └────────────────────────────────────────────────┘ │    │
│                                                      │    │
└──────────────────────────────────────────────────────┘   
```

---

## **Prerequisites**

- Azure Account with subscription
- Azure CLI installed: `choco install azure-cli` (or download from Microsoft)
- Docker installed locally
- GitHub account connected to Azure

```powershell
# Login to Azure
az login

# List subscriptions
az account list --output table

# Set default subscription
az account set --subscription "Your-Subscription-ID"
```

---

## **Step 1: Create Resource Group**

```bash
# Create resource group
az group create \
  --name wpp-rg \
  --location eastus

# Verify
az group show --name wpp-rg
```

---

## **Step 2: Create Container Registry (ACR)**

```bash
# Create Azure Container Registry
az acr create \
  --resource-group wpp-rg \
  --name wppdigitaltwin \
  --sku Basic

# Save login credentials
az acr credential show \
  --name wppdigitaltwin \
  --resource-group wpp-rg

# Login to ACR
az acr login --name wppdigitaltwin
```

---

## **Step 3: Build and Push Docker Image**

```bash
# Build image in Azure
az acr build \
  --registry wppdigitaltwin \
  --image wpp-digital-twin:latest \
  .

# Verify image
az acr repository list --name wppdigitaltwin
```

---

## **Step 4: Create Azure Cosmos DB (NoSQL)**

```bash
# Create Cosmos DB account
az cosmosdb create \
  --resource-group wpp-rg \
  --name wpp-trading-db \
  --kind GlobalDocumentDB

# Create database
az cosmosdb sql database create \
  --resource-group wpp-rg \
  --account-name wpp-trading-db \
  --name trading_logs

# Create container
az cosmosdb sql container create \
  --resource-group wpp-rg \
  --account-name wpp-trading-db \
  --database-name trading_logs \
  --name auctions \
  --partition-key-path /hour

# Get connection string
az cosmosdb list-connection-strings \
  --resource-group wpp-rg \
  --name wpp-trading-db \
  --query 'connectionStrings[0].connectionString'
```

---

## **Step 5: Create App Service Plan & Web App**

```bash
# Create App Service Plan
az appservice plan create \
  --name wpp-appplan \
  --resource-group wpp-rg \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --resource-group wpp-rg \
  --plan wpp-appplan \
  --name wpp-dashboard \
  --deployment-container-image-name wppdigitaltwin.azurecr.io/wpp-digital-twin:latest

# Configure container settings
az webapp config container set \
  --resource-group wpp-rg \
  --name wpp-dashboard \
  --docker-custom-image-name wppdigitaltwin.azurecr.io/wpp-digital-twin:latest \
  --docker-registry-server-url https://wppdigitaltwin.azurecr.io \
  --docker-registry-server-user wppdigitaltwin \
  --docker-registry-server-password [PASSWORD]
```

---

## **Step 6: Create Key Vault (Secrets Management)**

```bash
# Create Key Vault
az keyvault create \
  --resource-group wpp-rg \
  --name wpp-vault

# Store database connection string
az keyvault secret set \
  --vault-name wpp-vault \
  --name cosmosdb-connection-string \
  --value "[YOUR-CONNECTION-STRING]"

# Store blockchain RPC URL
az keyvault secret set \
  --vault-name wpp-vault \
  --name blockchain-rpc-url \
  --value "https://mainnet.infura.io/v3/[YOUR-KEY]"

# Grant App Service access to Key Vault
az keyvault set-policy \
  --name wpp-vault \
  --spn $(az webapp identity show --resource-group wpp-rg --name wpp-dashboard --query principalId -o tsv) \
  --secret-permissions get list
```

---

## **Step 7: Configure App Service Settings**

```bash
# Set environment variables
az webapp config appsettings set \
  --resource-group wpp-rg \
  --name wpp-dashboard \
  --settings \
    COSMOSDB_CONNECTION_STRING="@Microsoft.KeyVault(SecretUri=https://wpp-vault.vault.azure.net/secrets/cosmosdb-connection-string/)" \
    GANACHE_RPC="http://127.0.0.1:8545" \
    FLASK_ENV="production" \
    PORT=8501

# Enable logging
az webapp log config \
  --resource-group wpp-rg \
  --name wpp-dashboard \
  --docker-container-logging filesystem \
  --level verbose
```

---

## **Step 8: Create Azure Functions for Trading Orchestrator**

```bash
# Create Function App
az functionapp create \
  --resource-group wpp-rg \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name wpp-trading-orchestrator

# Deploy trading_orchestrator.py as trigger
az functionapp deployment source config-zip \
  --resource-group wpp-rg \
  --name wpp-trading-orchestrator \
  --src-path orchestrator-function.zip
```

---

## **Step 9: Setup Application Insights Monitoring**

```bash
# Create Application Insights
az monitor app-insights component create \
  --app wpp-insights \
  --location eastus \
  --resource-group wpp-rg \
  --application-type web

# Link to App Service
az webapp config appsettings set \
  --resource-group wpp-rg \
  --name wpp-dashboard \
  --settings \
    APPINSIGHTS_INSTRUMENTATION_KEY="[YOUR-KEY-FROM-ABOVE]"
```

---

## **Step 10: Create CI/CD Pipeline (GitHub → Azure)**

Create file: `.github/workflows/azure-deploy.yml`

```yaml
name: Deploy to Azure

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Log in to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Build and push image to ACR
        run: |
          az acr build \
            --registry wppdigitaltwin \
            --image wpp-digital-twin:${{ github.sha }} \
            --image wpp-digital-twin:latest \
            .
      
      - name: Update App Service
        uses: azure/webapps-deploy@v2
        with:
          app-name: wpp-dashboard
          images: wppdigitaltwin.azurecr.io/wpp-digital-twin:latest
      
      - name: Restart App Service
        run: |
          az webapp restart \
            --resource-group wpp-rg \
            --name wpp-dashboard
      
      - name: Health Check
        run: |
          az webapp show \
            --resource-group wpp-rg \
            --name wpp-dashboard \
            --query "state"
```

Add to GitHub Secrets:
```yaml
AZURE_CREDENTIALS: # Run: az ad sp create-for-rbac --name "WPP" --role contributor
AZURE_SUBSCRIPTION_ID: # Your subscription ID
```

---

## **Step 11: Access Your Deployed Application**

```bash
# Get app URL
az webapp show \
  --resource-group wpp-rg \
  --name wpp-dashboard \
  --query defaultHostName

# Output: wpp-dashboard.azurewebsites.net
# Access: https://wpp-dashboard.azurewebsites.net
```

---

## **Step 12: Setup Auto-Scaling**

```bash
# Create auto-scale rule
az monitor autoscale create \
  --resource-group wpp-rg \
  --resource wpp-appplan \
  --resource-type "Microsoft.Web/serverfarms" \
  --name wpp-autoscale \
  --count 1 \
  --min-count 1 \
  --max-count 3

# Add scale-up rule (CPU > 70%)
az monitor autoscale rule create \
  --resource-group wpp-rg \
  --autoscale-name wpp-autoscale \
  --condition "Percentage CPU > 70 avg 5m" \
  --scale out 1
```

---

## **Cost Estimation (Monthly)**

| Service | Tier | Est. Cost |
|---------|------|-----------|
| App Service Plan | B1 (Basic) | $12 |
| Azure Cosmos DB | Starter (400 RU/s) | $24 |
| Container Registry | Basic | $5 |
| Application Insights | 1 GB/day | $2.30 |
| Data Egress | 10 GB | $1.20 |
| **Total** | — | **~$44/month** |

---

## **Monitoring & Diagnostics**

```bash
# View logs
az webapp log download \
  --resource-group wpp-rg \
  --name wpp-dashboard

# Get real-time logs
az webapp log tail \
  --resource-group wpp-rg \
  --name wpp-dashboard

# View metrics in Application Insights
az monitor metrics list \
  --resource /subscriptions/[SUB-ID]/resourceGroups/wpp-rg/providers/Microsoft.Web/sites/wpp-dashboard \
  --metric RequestsCount \
  --interval PT1M \
  --start-time 2024-01-01T00:00:00Z
```

---

## **Troubleshooting**

### **App Service not starting**
```bash
# Check deployment logs
az webapp deployment log show --resource-group wpp-rg --name wpp-dashboard

# Restart the app
az webapp restart --resource-group wpp-rg --name wpp-dashboard
```

### **Cosmos DB connection failed**
```bash
# Verify connection string
az cosmosdb list-connection-strings \
  --resource-group wpp-rg \
  --name wpp-trading-db

# Check firewall rules
az cosmosdb network-rule list \
  --resource-group wpp-rg \
  --name wpp-trading-db
```

### **Application Insights not logging**
```bash
# Check instrumentation key
az webapp config appsettings list \
  --resource-group wpp-rg \
  --name wpp-dashboard \
  --query "[?name=='APPINSIGHTS_INSTRUMENTATION_KEY']"
```

---

## **Next Steps**

1. ✅ Enable HTTPS with Azure Front Door
2. ✅ Configure custom domain name
3. ✅ Setup backup for Cosmos DB
4. ✅ Enable Advanced Threat Protection
5. ✅ Configure DDoS protection

