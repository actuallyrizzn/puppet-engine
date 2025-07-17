# Deployment Guide

## Overview

This guide covers deploying Puppet Engine in various environments, from development to production. The system supports multiple deployment strategies including Docker, PM2, and cloud platforms.

## Prerequisites

### System Requirements

- **Python**: 3.11 or higher
- **Memory**: Minimum 2GB RAM (4GB+ recommended)
- **Storage**: 10GB+ available disk space
- **Network**: Stable internet connection for API calls
- **Operating System**: Linux, macOS, or Windows

### Dependencies

- **SQLite**: Built-in (no external database required)
- **Docker**: 20.10+ (for containerized deployment)

## Environment Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```env
# Core Configuration
DATABASE_URL=sqlite:///puppet_engine.db
LOG_LEVEL=INFO
ENABLE_METRICS=true
ENVIRONMENT=production

# API Keys
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret

# LLM Providers
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4-turbo
GROK_API_KEY=your_grok_api_key
GROK_API_ENDPOINT=https://api.grok.x.com/v1/chat/completions
GROK_MODEL=grok-1

# Solana Configuration
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_PRIVATE_KEY_AGENT_ID=your_agent_specific_private_key

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Security
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Monitoring
ENABLE_HEALTH_CHECKS=true
HEALTH_CHECK_INTERVAL=30
```

### Configuration Validation

Validate your configuration before deployment:

```bash
# Check configuration
python -c "from src.core.settings import Settings; Settings().validate()"

# Test database connection
python -c "import asyncio; from src.memory.sqlite_store import SQLiteStore; asyncio.run(SQLiteStore(Settings()).initialize())"
```

## Development Deployment

### Local Development

1. **Clone and Setup**:
   ```bash
   git clone https://github.com/username/puppet-engine.git
   cd puppet-engine
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run Development Server**:
   ```bash
   # Development mode with auto-reload
   python -m src.main --dev
   
   # Or with specific configuration
   python -m src.main --config .env --dev
   ```

### Development with Hot Reload

For development with automatic reloading:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run with auto-reload
python -m src.main --dev --reload

# Or use uvicorn directly
uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8000
```

## Production Deployment

### Method 1: Direct Python Deployment

1. **Prepare Production Environment**:
   ```bash
   # Install production dependencies
   pip install -r requirements.txt
   
   # Set production environment
   export ENVIRONMENT=production
   export LOG_LEVEL=INFO
   ```

2. **Run Production Server**:
   ```bash
   # Production mode
   python -m src.main --production
   
   # With specific configuration
   python -m src.main --config /path/to/production.env --production
   ```

3. **Process Management**:
   ```bash
   # Using nohup (basic)
   nohup python -m src.main --production > puppet_engine.log 2>&1 &
   
   # Using screen
   screen -S puppet-engine
   python -m src.main --production
   # Ctrl+A, D to detach
   ```

### Method 2: Systemd Service (Recommended for Linux)

Systemd provides process management, auto-restart, and monitoring for Linux systems.

1. **Create Service File**:
   ```ini
   # /etc/systemd/system/puppet-engine.service
   [Unit]
   Description=Puppet Engine AI Agent System
   After=network.target
   
   [Service]
   Type=simple
   User=puppet-engine
   Group=puppet-engine
   WorkingDirectory=/opt/puppet-engine
   Environment=PATH=/opt/puppet-engine/venv/bin
   Environment=ENVIRONMENT=production
   Environment=LOG_LEVEL=INFO
   ExecStart=/opt/puppet-engine/venv/bin/python -m src.main --production
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

2. **Setup and Start Service**:
   ```bash
   # Create user
   sudo useradd -r -s /bin/false puppet-engine
   
   # Set permissions
   sudo chown -R puppet-engine:puppet-engine /opt/puppet-engine
   
   # Enable and start service
   sudo systemctl daemon-reload
   sudo systemctl enable puppet-engine
   sudo systemctl start puppet-engine
   
   # Check status
   sudo systemctl status puppet-engine
   
   # View logs
   sudo journalctl -u puppet-engine -f
   ```

3. **Service Management**:
   ```bash
   # Start the service
   sudo systemctl start puppet-engine
   
   # Stop the service
   sudo systemctl stop puppet-engine
   
   # Restart the service
   sudo systemctl restart puppet-engine
   
   # Check status
   sudo systemctl status puppet-engine
   ```

### Method 3: Docker Deployment

Docker provides consistent deployment across environments.

1. **Create Dockerfile**:
   ```dockerfile
   FROM python:3.11-slim
   
   # Set working directory
   WORKDIR /app
   
   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       gcc \
       && rm -rf /var/lib/apt/lists/*
   
   # Copy requirements and install Python dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy application code
   COPY src/ ./src/
   COPY docs/ ./docs/
   COPY README.md .
   COPY LICENSE .
   
   # Create non-root user
   RUN useradd --create-home --shell /bin/bash app
   USER app
   
   # Expose port
   EXPOSE 8000
   
   # Health check
   HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
     CMD curl -f http://localhost:8000/health || exit 1
   
   # Start command
   CMD ["python", "-m", "src.main", "--production"]
   ```

2. **Create Docker Compose Configuration**:
   ```yaml
   # docker-compose.yml
   version: '3.8'
   
   services:
     puppet-engine:
       build: .
       ports:
         - "8000:8000"
       environment:
         - ENVIRONMENT=production
         - LOG_LEVEL=INFO
       env_file:
         - .env
       volumes:
         - ./data:/app/data
         - ./logs:/app/logs
       restart: unless-stopped
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
         interval: 30s
         timeout: 10s
         retries: 3
         start_period: 40s
   
     nginx:
       image: nginx:alpine
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx.conf:/etc/nginx/nginx.conf
         - ./ssl:/etc/nginx/ssl
       depends_on:
         - puppet-engine
       restart: unless-stopped
   ```

3. **Build and Run**:
   ```bash
   # Build the image
   docker build -t puppet-engine .
   
   # Run with Docker Compose
   docker-compose up -d
   
   # View logs
   docker-compose logs -f puppet-engine
   
   # Stop services
   docker-compose down
   ```

### Method 3: Systemd Service

For Linux systems, use systemd for service management.

1. **Create Service File**:
   ```ini
   # /etc/systemd/system/puppet-engine.service
   [Unit]
   Description=Puppet Engine AI Agent System
   After=network.target
   
   [Service]
   Type=simple
   User=puppet-engine
   Group=puppet-engine
   WorkingDirectory=/opt/puppet-engine
   Environment=PATH=/opt/puppet-engine/venv/bin
   Environment=ENVIRONMENT=production
   Environment=LOG_LEVEL=INFO
   ExecStart=/opt/puppet-engine/venv/bin/python -m src.main --production
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and Start Service**:
   ```bash
   # Create user
   sudo useradd -r -s /bin/false puppet-engine
   
   # Set permissions
   sudo chown -R puppet-engine:puppet-engine /opt/puppet-engine
   
   # Enable and start service
   sudo systemctl daemon-reload
   sudo systemctl enable puppet-engine
   sudo systemctl start puppet-engine
   
   # Check status
   sudo systemctl status puppet-engine
   
   # View logs
   sudo journalctl -u puppet-engine -f
   ```

## Cloud Deployment

### AWS Deployment

#### EC2 Deployment

1. **Launch EC2 Instance**:
   ```bash
   # Launch Ubuntu 22.04 instance
   aws ec2 run-instances \
     --image-id ami-0c02fb55956c7d316 \
     --instance-type t3.medium \
     --key-name your-key-pair \
     --security-group-ids sg-12345678 \
     --subnet-id subnet-12345678
   ```

2. **Configure Instance**:
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python and dependencies
   sudo apt install -y python3.11 python3.11-venv python3-pip nginx
   
   # Clone repository
   git clone https://github.com/username/puppet-engine.git
   cd puppet-engine
   
   # Setup virtual environment
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Nginx**:
   ```nginx
   # /etc/nginx/sites-available/puppet-engine
   server {
       listen 80;
       server_name your-domain.com;
   
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

4. **Enable Site**:
   ```bash
   sudo ln -s /etc/nginx/sites-available/puppet-engine /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

#### ECS Deployment

1. **Create Task Definition**:
   ```json
   {
     "family": "puppet-engine",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "512",
     "memory": "1024",
     "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "puppet-engine",
         "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/puppet-engine:latest",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "ENVIRONMENT",
             "value": "production"
           }
         ],
         "secrets": [
           {
             "name": "TWITTER_API_KEY",
             "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:twitter-api-key"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/puppet-engine",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

2. **Deploy to ECS**:
   ```bash
   # Create ECR repository
   aws ecr create-repository --repository-name puppet-engine
   
   # Build and push image
   docker build -t puppet-engine .
   docker tag puppet-engine:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/puppet-engine:latest
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
   docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/puppet-engine:latest
   
   # Create service
   aws ecs create-service \
     --cluster your-cluster \
     --service-name puppet-engine \
     --task-definition puppet-engine:1 \
     --desired-count 1
   ```

### Google Cloud Platform

#### Compute Engine Deployment

1. **Create Instance**:
   ```bash
   gcloud compute instances create puppet-engine \
     --zone=us-central1-a \
     --machine-type=e2-medium \
     --image-family=ubuntu-2204-lts \
     --image-project=ubuntu-os-cloud \
     --tags=http-server,https-server
   ```

2. **Configure Instance**:
   ```bash
   # SSH into instance
   gcloud compute ssh puppet-engine --zone=us-central1-a
   
   # Install dependencies
   sudo apt update && sudo apt install -y python3.11 python3.11-venv nginx
   
   # Deploy application
   git clone https://github.com/username/puppet-engine.git
   cd puppet-engine
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Setup Service**:
   ```bash
   # Create systemd service
   sudo nano /etc/systemd/system/puppet-engine.service
   
   # Enable and start
   sudo systemctl enable puppet-engine
   sudo systemctl start puppet-engine
   ```

#### Cloud Run Deployment

1. **Create Dockerfile** (see Docker section above)

2. **Deploy to Cloud Run**:
   ```bash
   # Build and push image
   gcloud builds submit --tag gcr.io/your-project/puppet-engine
   
   # Deploy to Cloud Run
   gcloud run deploy puppet-engine \
     --image gcr.io/your-project/puppet-engine \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars ENVIRONMENT=production
   ```

### Azure Deployment

#### Azure Container Instances

1. **Build and Push Image**:
   ```bash
   # Login to Azure Container Registry
   az acr login --name yourregistry
   
   # Build and push
   docker build -t yourregistry.azurecr.io/puppet-engine:latest .
   docker push yourregistry.azurecr.io/puppet-engine:latest
   ```

2. **Deploy Container**:
   ```bash
   az container create \
     --resource-group your-rg \
     --name puppet-engine \
     --image yourregistry.azurecr.io/puppet-engine:latest \
     --dns-name-label puppet-engine \
     --ports 8000 \
     --environment-variables ENVIRONMENT=production
   ```

## Monitoring and Observability

### Health Checks

The application provides built-in health checks:

```bash
# Health check endpoint
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/status
```

### Logging

Configure logging for production:

```python
# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/puppet-engine/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "json"
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["file", "console"]
    }
}
```

### Metrics

Enable metrics collection:

```bash
# Install metrics dependencies
pip install prometheus-client

# Configure metrics
export ENABLE_METRICS=true
export METRICS_PORT=9090
```

### Monitoring Stack

#### Prometheus + Grafana

1. **Prometheus Configuration**:
   ```yaml
   # prometheus.yml
   global:
     scrape_interval: 15s
   
   scrape_configs:
     - job_name: 'puppet-engine'
       static_configs:
         - targets: ['localhost:9090']
   ```

2. **Grafana Dashboard**:
   ```json
   {
     "dashboard": {
       "title": "Puppet Engine Metrics",
       "panels": [
         {
           "title": "Active Agents",
           "type": "stat",
           "targets": [
             {
               "expr": "puppet_engine_active_agents"
             }
           ]
         },
         {
           "title": "Posts per Hour",
           "type": "graph",
           "targets": [
             {
               "expr": "rate(puppet_engine_posts_total[1h])"
             }
           ]
         }
       ]
     }
   }
   ```

## Security Considerations

### API Security

1. **Authentication**:
   ```python
   # Add API key authentication
   from fastapi import Security, HTTPException
   from fastapi.security import APIKeyHeader
   
   api_key_header = APIKeyHeader(name="X-API-Key")
   
   async def get_api_key(api_key: str = Security(api_key_header)):
       if api_key != settings.api_key:
           raise HTTPException(status_code=403, detail="Invalid API key")
       return api_key
   ```

2. **Rate Limiting**:
   ```python
   # Add rate limiting
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
   ```

### Network Security

1. **Firewall Configuration**:
   ```bash
   # UFW firewall rules
   sudo ufw allow 22/tcp    # SSH
   sudo ufw allow 80/tcp    # HTTP
   sudo ufw allow 443/tcp   # HTTPS
   sudo ufw enable
   ```

2. **SSL/TLS Configuration**:
   ```nginx
   # Nginx SSL configuration
   server {
       listen 443 ssl http2;
       server_name your-domain.com;
   
       ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
   
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

### Data Security

1. **Environment Variables**:
   ```bash
   # Use secure environment variable management
   export TWITTER_API_KEY=$(aws secretsmanager get-secret-value --secret-id twitter-api-key --query SecretString --output text)
   ```

2. **Database Security**:
   ```python
   # Use encrypted database connections
   DATABASE_URL = "sqlite:///puppet_engine.db?check_same_thread=false"
   
   # For production, consider PostgreSQL with SSL
   DATABASE_URL = "postgresql://user:pass@host:5432/db?sslmode=require"
   ```

## Backup and Recovery

### Data Backup

1. **Database Backup**:
   ```bash
   # SQLite backup
   sqlite3 puppet_engine.db ".backup backup_$(date +%Y%m%d_%H%M%S).db"
   
   # Automated backup script
   #!/bin/bash
   BACKUP_DIR="/backups/puppet-engine"
   DATE=$(date +%Y%m%d_%H%M%S)
   
   mkdir -p $BACKUP_DIR
   sqlite3 puppet_engine.db ".backup $BACKUP_DIR/backup_$DATE.db"
   
   # Keep only last 7 days
   find $BACKUP_DIR -name "backup_*.db" -mtime +7 -delete
   ```

2. **Configuration Backup**:
   ```bash
   # Backup configuration files
   tar -czf config_backup_$(date +%Y%m%d).tar.gz .env agent_configs/
   ```

### Disaster Recovery

1. **Recovery Plan**:
   ```bash
   # Restore database
   sqlite3 puppet_engine.db ".restore backup_20241219_120000.db"
   
   # Restore configuration
   tar -xzf config_backup_20241219.tar.gz
   
   # Restart services
   sudo systemctl restart puppet-engine
   ```

2. **High Availability**:
   ```yaml
   # Docker Compose with multiple instances
   version: '3.8'
   services:
     puppet-engine-1:
       build: .
       environment:
         - INSTANCE_ID=1
       restart: unless-stopped
     
     puppet-engine-2:
       build: .
       environment:
         - INSTANCE_ID=2
       restart: unless-stopped
     
     nginx:
       image: nginx:alpine
       ports:
         - "80:80"
       volumes:
         - ./nginx.conf:/etc/nginx/nginx.conf
   ```

## Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```bash
   # Check what's using the port
   sudo netstat -tulpn | grep :8000
   
   # Kill the process
   sudo kill -9 <PID>
   ```

2. **Permission Issues**:
   ```bash
   # Fix file permissions
   sudo chown -R puppet-engine:puppet-engine /opt/puppet-engine
   sudo chmod -R 755 /opt/puppet-engine
   ```

3. **Database Issues**:
   ```bash
   # Check database integrity
   sqlite3 puppet_engine.db "PRAGMA integrity_check;"
   
   # Rebuild database
   sqlite3 puppet_engine.db ".dump" | sqlite3 puppet_engine_new.db
   ```

### Debug Mode

Enable debug mode for troubleshooting:

```bash
# Set debug environment
export LOG_LEVEL=DEBUG
export ENVIRONMENT=development

# Run with debug output
python -m src.main --debug --verbose
```

### Log Analysis

```bash
# View recent logs
tail -f /var/log/puppet-engine/app.log

# Search for errors
grep -i error /var/log/puppet-engine/app.log

# Monitor system resources
htop
iotop
```

## Performance Optimization

### System Tuning

1. **Python Optimization**:
   ```bash
   # Use optimized Python
   export PYTHONOPTIMIZE=2
   
   # Increase file descriptor limits
   ulimit -n 65536
   ```

2. **Database Optimization**:
   ```sql
   -- Enable WAL mode for better concurrency
   PRAGMA journal_mode=WAL;
   
   -- Optimize for read-heavy workloads
   PRAGMA cache_size=10000;
   PRAGMA temp_store=MEMORY;
   ```

3. **Memory Optimization**:
   ```python
   # Configure memory limits
   import gc
   gc.set_threshold(700, 10, 10)
   ```

### Scaling Strategies

1. **Horizontal Scaling**:
   ```yaml
   # Load balancer configuration
   upstream puppet_engine {
       server 127.0.0.1:8001;
       server 127.0.0.1:8002;
       server 127.0.0.1:8003;
   }
   ```

2. **Vertical Scaling**:
   ```bash
   # Increase worker processes
   export WORKERS=8
   
   # Increase memory limits
   export MAX_MEMORY=4G
   ```

## Maintenance

### Regular Maintenance

1. **Log Rotation**:
   ```bash
   # Configure logrotate
   sudo nano /etc/logrotate.d/puppet-engine
   
   /var/log/puppet-engine/*.log {
       daily
       missingok
       rotate 7
       compress
       delaycompress
       notifempty
       create 644 puppet-engine puppet-engine
   }
   ```

2. **Database Maintenance**:
   ```bash
   # Weekly database maintenance
   sqlite3 puppet_engine.db "VACUUM; ANALYZE;"
   ```

3. **Security Updates**:
   ```bash
   # Update dependencies
   pip install --upgrade -r requirements.txt
   
   # Update system packages
   sudo apt update && sudo apt upgrade
   ```

### Monitoring and Alerts

1. **Health Check Script**:
   ```bash
   #!/bin/bash
   HEALTH_URL="http://localhost:8000/health"
   
   response=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)
   
   if [ $response -ne 200 ]; then
       echo "Health check failed: $response"
       # Send alert
       curl -X POST -H 'Content-type: application/json' \
         --data '{"text":"Puppet Engine health check failed"}' \
         https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
   fi
   ```

2. **Automated Restart**:
   ```bash
   # Systemd service with auto-restart
   [Service]
   Restart=always
   RestartSec=10
   StartLimitInterval=60
   StartLimitBurst=3
   ``` 