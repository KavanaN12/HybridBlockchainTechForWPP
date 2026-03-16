# 🆓 Deploy to Fly.io (Free Forever)

**Platform**: Fly.io  
**Cost**: $0/month forever  
**Uptime**: 24/7 (no spin-down)  
**Setup Time**: 25 minutes  

---

## **Why Fly.io?**

✅ **100% FREE Forever**
- No credit card required
- No time limit
- Generous free resources

✅ **Always Running**
- Unlike Render, doesn't spin down
- 24/7 uptime

✅ **Easy Setup**
- Simple CLI
- 2 commands to deploy

---

## **Step 1: Install Fly.io CLI**

```powershell
# Using Chocolatey (recommended)
choco install flyctl

# OR: Manual from https://fly.io/docs/hands-on/install-flyctl/
```

Verify installation:
```powershell
fly --version
# Output: Fly CLI v0.x.x
```

---

## **Step 2: Create Fly.io Account**

```powershell
# Sign up via GitHub (free)
fly auth signup

# Or use email
fly auth signup --email your-email@example.com

# Verify email, then login
fly auth login
```

---

## **Step 3: Create fly.toml (Config File)**

Create file: `d:\WPPDigitalTwin\fly.toml`

```toml
# fly.toml file for WPP Digital Twin
app = "wpp-digital-twin"
primary_region = "iad"

[build]
dockerfile = "Dockerfile"

[env]
  GANACHE_RPC = "http://localhost:8545"
  FLASK_ENV = "production"

[http_service]
  internal_port = 8501
  force_https = true
  auto_stop_machines = false
  auto_start_machines = false

[[vm]]
  memory = "256mb"
  cpu_kind = "shared"
  cpus = 1

[checks]
  [checks.status]
    type = "http"
    interval = 30000
    timeout = 10000
    grace_period = 5000
    method = "get"
    path = "/"
```

---

## **Step 4: Create Dockerfile (if not exists)**

Check if you have one:
```powershell
Test-Path d:\WPPDigitalTwin\Dockerfile
```

If YES → Great! Skip to Step 5

If NO → Create: `d:\WPPDigitalTwin\Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501 || exit 1

# Run Streamlit
CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## **Step 5: Deploy to Fly.io**

From your project directory:

```powershell
cd d:\WPPDigitalTwin

# Launch the app (creates app if doesn't exist)
fly launch

# You'll be prompted:
# - App name: wpp-digital-twin (press Enter)
# - Region: Choose iad (Virginia, US) - fastest
# - Copy Postgres? No (press N)
# - Deploy now? Yes (press Y)

# Then it builds and deploys!
```

Wait for deployment (5-10 minutes):
```
Deploying...
✓ App deployed to https://wpp-digital-twin.fly.dev
```

---

## **Step 6: Access Your Live Dashboard**

```
https://wpp-digital-twin.fly.dev
```

**Share this URL** - it works forever for FREE! 🎉

---

## **Step 7: View Logs**

```powershell
# Real-time logs
fly logs --follow

# Or: View in dashboard
fly open /logs
```

---

## **Step 8: Update Deployed App**

Every time you update code:

```powershell
cd d:\WPPDigitalTwin
git add .
git commit -m "Update dashboard"

fly deploy
```

Automatically redeploys! ✨

---

## **Fly.io Free Tier Limits**

| Resource | Free Tier |
|----------|-----------|
| **Memory** | 3 GB shared |
| **CPU** | 3 shared CPUs |
| **Bandwidth** | 160 GB/month |
| **IPs** | 1 shared IPv4 + IPv6 |
| **Databases** | 0 (PostgreSQL not free) |
| **Cost** | $0 |

**For your dashboard**: Plenty! ✅

---

## **Free vs Paid Comparison**

| Feature | Free | Pro |
|---------|------|-----|
| Apps | Unlimited | Unlimited |
| Shared CPU | ✅ | CPUs |
| Memory | 256-512MB | More |
| Uptime | 99% | 99.9% |
| Cost | $0 | $5+/month |

**Recommendation**: Start FREE, upgrade only if needed!

---

## **Combining Ngrok + Fly.io**

### **Option 1: Just Fly.io (Simpler)**
- Deploy to fly.io
- Get public URL
- Done!
- Cost: $0

### **Option 2: Local + Ngrok**
- Keep on your machine
- Ngrok tunnels it
- Better for development
- Cost: $0

### **Option 3: Both (Backup)**
- Fly.io for public
- Local for testing
- Ngrok for sharing local version
- Cost: $0

**Choose ONE for simplicity** - Fly.io is easiest!

---

## **Troubleshooting Fly.io**

### **Build fails?**
```powershell
# Check logs
fly logs --follow

# Rebuild
fly deploy --force
```

### **Can't access app?**
```powershell
# Check status
fly status

# Restart
fly restart
```

### **App crashes?**
```powershell
# View detailed logs
fly logs

# Show recent errors
fly logs | grep ERROR
```

---

## **Update DNS/Domain (Optional)**

If you buy a domain later:

```powershell
# Add to fly.toml
fly certs add yourdomain.com

# Then setup DNS at your domain provider
```

Now: `https://wpp-digital-twin.fly.dev` (FREE!)  
Later: `https://yourdomain.com` (if you buy domain)

---

## **Quick Comparison: All FREE Options**

| Method | Cost | Setup | Uptime | Best For |
|--------|------|-------|--------|----------|
| **Fly.io** | $0 ♾️ | 25 min | 99% 24/7 | ⭐Production-ready |
| **Ngrok** | $0 ♾️ | 5 min | 100% (local) | Demos & sharing |
| **Render** | $0 ♾️ | 20 min | 50% (spins down) | Testing |

---

## **Complete Fly.io Deployment (Step-by-Step)**

```powershell
# 1. Install Fly CLI
choco install flyctl

# 2. Sign up
fly auth signup

# 3. Go to project
cd d:\WPPDigitalTwin

# 4. Launch app
fly launch

# 5. Deploy
fly deploy

# 6. Open in browser
fly open

# Result: https://wpp-digital-twin.fly.dev ✅
```

**Time: 25 minutes | Cost: $0 | Uptime: 24/7**

---

## **Next: Add Your GitHub Repo**

```powershell
# So changes auto-deploy:

# First, push to GitHub
git add .
git commit -m "Ready for Fly.io"
git push origin main

# Then setup auto-deployment
fly dashboard # Opens browser
# Settings → Deploy → Connect GitHub
# Select your repo
# Auto-deploy on push!
```

Now every `git push` auto-deploys! 🚀

---

## **You're Live!**

✅ Dashboard: `https://wpp-digital-twin.fly.dev`  
✅ Cost: $0/month forever  
✅ Uptime: 24/7  
✅ Deployment: 25 minutes  

**Share the link with anyone!** It works globally, free forever! 🌍

---

**Your WPP Digital Twin is now LIVE on the internet for $0!** 🎉

