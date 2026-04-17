# QAlytics Deployment Guide

## 📋 Pre-Deployment Checklist

- [ ] All tests passing locally (`pytest automation/ -v`)
- [ ] Environment variables configured
- [ ] Database backups taken
- [ ] API documentation reviewed
- [ ] Security scan passed
- [ ] Performance benchmarks met

---

## 🐳 Quick Start with Docker

### Local Development with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

**Services:**

- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- API Docs: `http://localhost:8000/docs`

### Build Backend Image Only

```bash
# Build image
docker build -t qalytics:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=sqlite:///./backend/qalytics.db \
  -e BOOTSTRAP_ADMIN_USERNAME=admin \
  -e BOOTSTRAP_ADMIN_PASSWORD=admin \
  --name qalytics-api \
  qalytics:latest

# View logs
docker logs -f qalytics-api

# Stop container
docker stop qalytics-api
docker rm qalytics-api
```

---

## 🚀 Production Deployment

### AWS EC2 Deployment

```bash
# 1. Launch EC2 instance
# - Ubuntu 22.04 LTS
# - t3.medium or larger
# - Security group: allow 22, 80, 443

# 2. Connect and install dependencies
ssh -i key.pem ubuntu@your-instance.com

sudo apt update && sudo apt install -y \
  docker.io \
  docker-compose \
  git

# 3. Clone repository
git clone https://github.com/yourusername/qalytics.git
cd qalytics

# 4. Configure environment
cp .env.production .env
# Edit .env with production values

# 5. Start with Docker Compose
docker-compose -f docker-compose.yml up -d

# 6. Setup SSL with Let's Encrypt
# Use Nginx reverse proxy + Certbot

# 7. Setup monitoring
# Configure CloudWatch or DataDog
```

### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qalytics
spec:
  replicas: 3
  selector:
    matchLabels:
      app: qalytics
  template:
    metadata:
      labels:
        app: qalytics
    spec:
      containers:
      - name: backend
        image: qalytics:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: qalytics-secrets
              key: db-url
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

Deploy with:

```bash
kubectl apply -f deployment.yaml
kubectl expose deployment qalytics --type=LoadBalancer --port=80 --target-port=8000
```

---

## 🔒 Environment Configuration

### Production `.env` Template

```env
# Server
SECRET_KEY=your-very-secret-key-change-this
QA_ENV=production

# Database
DATABASE_URL=postgresql://user:pass@db.example.com/qalytics

# Authentication
BOOTSTRAP_ADMIN_ENABLED=false  # Disable after setup
BOOTSTRAP_ADMIN_USERNAME=admin_user
BOOTSTRAP_ADMIN_PASSWORD=strong_password_here

# CORS
CORS_ALLOWED_ORIGINS=https://qalytics.example.com,https://app.example.com

# Logging
LOG_LEVEL=INFO

# Allure Reports
ALLURE_BIN=/usr/local/bin/allure
```

---

## 📊 Monitoring & Logging

### Setup Log Aggregation

```bash
# Using ELK Stack (Elasticsearch, Logstash, Kibana)
docker-compose -f docker-compose.monitoring.yml up -d
```

### Health Checks

```bash
# API health
curl http://localhost:8000/api/health

# Database connectivity
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/suites
```

---

## 🔄 Database Migrations

### Generate Migration

```bash
# Generate new migration
alembic revision --autogenerate -m "Add new column to users"

# Review generated migration
cat alembic/versions/001_add_column.py
```

### Apply Migrations

```bash
# Upgrade database
alembic upgrade head

# Downgrade (careful!)
alembic downgrade -1
```

---

## 🛠️ Troubleshooting

### Container won't start

```bash
# Check logs
docker logs qalytics-api

# Check image exists
docker images | grep qalytics

# Rebuild image
docker build --no-cache -t qalytics:latest .
```

### Database connection error

```bash
# Test connection string
python -c "from backend.database import SessionLocal; SessionLocal()"

# Check SQLite file permissions
ls -la backend/qalytics.db
chmod 666 backend/qalytics.db
```

### Port already in use

```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

---

## 📈 Performance Tuning

### Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_suite_name ON suites(name);
CREATE INDEX idx_case_suite_id ON test_cases(suite_id);
CREATE INDEX idx_run_status ON test_runs(status);
```

### Enable Caching

```python
# Add Redis caching
from redis import Redis
cache = Redis(host='localhost', port=6379)
```

---

## 🔐 Security Hardening

### SSL/TLS Setup

```bash
# Generate self-signed cert for testing
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365

# Use nginx to serve with SSL
```

### Firewall Rules

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable
```

---

## 📋 Backup & Recovery

### Backup Database

```bash
# SQLite backup
cp backend/qalytics.db backup/qalytics.db.$(date +%s)

# PostgreSQL backup (if using PG)
pg_dump dbname > backup/qalytics.sql

# Automate daily backups
0 2 * * * cp backend/qalytics.db /backups/qalytics.db.$(date +\%Y\%m\%d)
```

### Restore from Backup

```bash
# Restore SQLite
cp backup/qalytics.db.TIMESTAMP backend/qalytics.db

# Restore PostgreSQL
psql dbname < backup/qalytics.sql
```

---

## 🚨 Incident Response

### API is down

1. Check service status: `docker ps`
2. View logs: `docker logs qalytics-api`
3. Restart service: `docker restart qalytics-api`
4. If persistent, redeploy: `docker-compose up -d --force-recreate`

### Database is corrupted

1. Backup current database
2. Stop application
3. Restore from backup: `cp backup/qalytics.db backup/qalytics.db`
4. Restart application
5. Verify data integrity

---

## 📞 Support

For issues, check:

1. Application logs in Docker
2. Database connectivity
3. Environment variables
4. Firewall/networking rules
5. Disk space and resources
