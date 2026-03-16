# AWS Deployment Guide for WPP Digital Twin

**Status**: Production-Ready  
**Platform**: AWS (ECS, RDS, EC2)  
**Estimated Deployment Time**: 30 minutes  

---

## **Architecture Overview**

```
┌─────────────────────────────────────────────────────────┐
│                      AWS DEPLOYMENT                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Application Load Balancer (ALB)          │   │
│  │              (Port 80/443)                       │   │
│  └────────────────────┬─────────────────────────────┘   │
│                       │                                   │
│       ┌───────────────┴──────────────┬──────────────┐    │
│       │                              │              │    │
│  ┌────▼──────┐  ┌──────────────┐  ┌─▼──────────┐  │    │
│  │ Dashboard │  │   Trading    │  │  Blockchain│  │    │
│  │  Container│  │  Orchestrator│  │  Sync      │  │    │
│  │ (Streamlit)  │   Container  │  │  Container │  │    │
│  └────┬──────┘  └────┬─────────┘  └─┬──────────┘  │    │
│       │              │               │             │    │
│       └──────────────┼───────────────┘             │    │
│                      │                             │    │
│  ┌───────────────────▼─────────────────────────┐  │    │
│  │         RDS PostgreSQL / MySQL              │  │    │
│  │      (Trading Log + Configuration)          │  │    │
│  └─────────────────────────────────────────────┘  │    │
│                                                    │    │
│  ┌─────────────────────────────────────────────┐  │    │
│  │  AWS Secrets Manager                        │  │    │
│  │  (API Keys, Smart Contract Addresses)       │  │    │
│  └─────────────────────────────────────────────┘  │    │
│                                                    │    │
└─────────────────────────────────────────────────────┘   
```

---

## **Prerequisites**

- AWS Account with billing enabled
- AWS CLI installed: `pip install awscli`
- Docker installed locally
- GitHub account connected to AWS

```powershell
# Configure AWS credentials
aws configure
# Then enter:
# AWS Access Key ID: [your-key]
# AWS Secret Access Key: [your-secret]
# Default region: us-east-1 (or your region)
# Default output format: json
```

---

## **Step 1: Create ECR Repository for Docker Images**

```bash
# Create ECR repo for WPP Digital Twin
aws ecr create-repository \
  --repository-name wpp-digital-twin \
  --region us-east-1

# Output will show:
# "repositoryUri": "123456789.dkr.ecr.us-east-1.amazonaws.com/wpp-digital-twin"
# Save this URI - you'll need it
```

---

## **Step 2: Push Docker Image to ECR**

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t wpp-digital-twin:latest .

# Tag image
docker tag wpp-digital-twin:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/wpp-digital-twin:latest

# Push to ECR
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/wpp-digital-twin:latest
```

---

## **Step 3: Create RDS Database for Trading Logs**

```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier wpp-trading-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YourSecurePassword123! \
  --allocated-storage 20 \
  --publicly-accessible true \
  --region us-east-1

# Wait ~5 minutes for creation
aws rds describe-db-instances \
  --db-instance-identifier wpp-trading-db \
  --region us-east-1 \
  --query 'DBInstances[0].DBInstanceStatus'
```

**Save the endpoint**: `wpp-trading-db.abc123.us-east-1.rds.amazonaws.com`

---

## **Step 4: Create ECS Cluster**

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name wpp-cluster --region us-east-1

# Output: "clusterArn": "arn:aws:ecs:us-east-1:123456789:cluster/wpp-cluster"
```

---

## **Step 5: Create Task Definition for Dashboard**

Create file: `aws-task-definition.json`

```json
{
  "family": "wpp-dashboard",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "dashboard",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/wpp-digital-twin:latest",
      "portMappings": [
        {
          "containerPort": 8501,
          "hostPort": 8501,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "GANACHE_RPC",
          "value": "http://localhost:8545"
        },
        {
          "name": "DB_HOST",
          "value": "wpp-trading-db.abc123.us-east-1.rds.amazonaws.com"
        },
        {
          "name": "DB_USER",
          "value": "admin"
        }
      ],
      "secrets": [
        {
          "name": "DB_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:wpp/db-password"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/wpp-dashboard",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Register task definition:

```bash
aws ecs register-task-definition \
  --cli-input-json file://aws-task-definition.json \
  --region us-east-1
```

---

## **Step 6: Create Application Load Balancer**

```bash
# Create security group for ALB
aws ec2 create-security-group \
  --group-name wpp-alb-sg \
  --description "Security group for WPP ALB" \
  --region us-east-1

# Allow HTTP/HTTPS
aws ec2 authorize-security-group-ingress \
  --group-name wpp-alb-sg \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0 \
  --region us-east-1

# Create ALB
aws elbv2 create-load-balancer \
  --name wpp-alb \
  --subnets subnet-12345678 subnet-87654321 \
  --security-groups sg-12345678 \
  --scheme internet-facing \
  --type application \
  --region us-east-1
```

---

## **Step 7: Create ECS Service**

```bash
# Create ECS service
aws ecs create-service \
  --cluster wpp-cluster \
  --service-name wpp-dashboard-service \
  --task-definition wpp-dashboard:1 \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345678],securityGroups=[sg-12345678],assignPublicIp=ENABLED}" \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=dashboard,containerPort=8501 \
  --region us-east-1
```

---

## **Step 8: Access Your Deployed Dashboard**

```bash
# Get ALB DNS name
aws elbv2 describe-load-balancers \
  --names wpp-alb \
  --region us-east-1 \
  --query 'LoadBalancers[0].DNSName'

# Open in browser:
# http://wpp-alb-123456-us-east-1.elb.amazonaws.com
```

---

## **Step 9: Setup Auto-Scaling**

```bash
# Create auto-scaling group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name wpp-dashboard-asg \
  --min-size 1 \
  --max-size 3 \
  --desired-capacity 2 \
  --launch-configuration-name wpp-dashboard-lc \
  --availability-zones us-east-1a us-east-1b \
  --region us-east-1

# Create scaling policy (scale up if CPU > 70%)
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name wpp-dashboard-asg \
  --policy-name scale-up \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration "TargetValue=70,PredefinedMetricSpecification={PredefinedMetricType=ASGAverageCPUUtilization}" \
  --region us-east-1
```

---

## **Step 10: Enable CI/CD Pipeline (GitHub Actions → AWS)**

Create file: `.github/workflows/aws-deploy.yml`

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Build and push to ECR
        run: |
          aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
          docker build -t wpp-digital-twin:${{ github.sha }} .
          docker tag wpp-digital-twin:${{ github.sha }} 123456789.dkr.ecr.us-east-1.amazonaws.com/wpp-digital-twin:latest
          docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/wpp-digital-twin:latest
      
      - name: Update ECS service
        run: |
          aws ecs update-service \
            --cluster wpp-cluster \
            --service wpp-dashboard-service \
            --force-new-deployment \
            --region us-east-1
```

---

## **Cost Estimation (Monthly)**

| Service | Tier | Est. Cost |
|---------|------|-----------|
| ECS (Fargate) | 256 CPU, 512 MB | $30 |
| ALB | 1 x ALB | $16 |
| RDS PostgreSQL | db.t3.micro | $15 |
| Data Transfer | 10 GB/month | $1 |
| ECR Storage | 5 GB | $0.50 |
| **Total** | — | **~$62/month** |

---

## **Monitoring & Logging**

```bash
# View ECS logs
aws logs tail /ecs/wpp-dashboard --follow --region us-east-1

# Get service status
aws ecs describe-services \
  --cluster wpp-cluster \
  --services wpp-dashboard-service \
  --region us-east-1

# View CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=wpp-dashboard-service \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 300 \
  --statistics Average \
  --region us-east-1
```

---

## **Troubleshooting**

### **Dashboard not accessible**
```bash
# Check service status
aws ecs describe-services --cluster wpp-cluster --services wpp-dashboard-service --region us-east-1

# Check task logs
aws ecs describe-tasks --cluster wpp-cluster --tasks <task-arn> --region us-east-1
```

### **Database connection failed**
```bash
# Check RDS status
aws rds describe-db-instances --db-instance-identifier wpp-trading-db --region us-east-1

# Check security group rules
aws ec2 describe-security-groups --group-names wpp-alb-sg --region us-east-1
```

---

## **Next Steps**

1. ✅ Monitor dashboard via CloudWatch
2. ✅ Set up auto-scaling alerts
3. ✅ Enable backup for RDS database
4. ✅ Configure HTTPS with ACM certificate

