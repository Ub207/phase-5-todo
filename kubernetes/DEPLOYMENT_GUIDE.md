# Kubernetes Deployment Guide - Todo Phase5

## Phase 1: Prerequisites Installation

### Step 1.1: Install Chocolatey (Package Manager for Windows)

Open PowerShell as Administrator and run:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

Verify installation:
```powershell
choco --version
```

### Step 1.2: Install kubectl

```powershell
choco install kubernetes-cli -y
```

Verify:
```powershell
kubectl version --client
```

### Step 1.3: Install Helm

```powershell
choco install kubernetes-helm -y
```

Verify:
```powershell
helm version
```

### Step 1.4: Install Minikube

```powershell
choco install minikube -y
```

Verify:
```powershell
minikube version
```

### Step 1.5: Install Dapr CLI

```powershell
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
```

Verify:
```powershell
dapr --version
```

### Step 1.6: Verify Docker Desktop

```powershell
docker version
docker ps
```

**Expected Output**: Docker should be running without errors.

---

## Phase 2: Kubernetes Cluster Setup

### Step 2.1: Start Minikube

```powershell
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable necessary addons
minikube addons enable ingress
minikube addons enable metrics-server
```

**Wait Time**: ~2-5 minutes

### Step 2.2: Verify Cluster

```powershell
# Check cluster status
kubectl cluster-info

# Check nodes
kubectl get nodes

# Check namespaces
kubectl get namespaces
```

**Expected Output**:
```
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   1m    v1.28.3
```

### Step 2.3: Configure kubectl Context

```powershell
# Set context
kubectl config use-context minikube

# Verify current context
kubectl config current-context
```

---

## Phase 3: Dapr Installation

### Step 3.1: Install Dapr on Kubernetes

```powershell
# Initialize Dapr on Kubernetes
dapr init --kubernetes --wait

# This installs:
# - dapr-operator
# - dapr-sidecar-injector
# - dapr-placement-server
# - dapr-sentry (for mTLS)
```

**Wait Time**: ~3-5 minutes

### Step 3.2: Verify Dapr Installation

```powershell
# Check Dapr pods
kubectl get pods -n dapr-system

# Check Dapr version
dapr status -k
```

**Expected Output**:
```
NAME                                     READY   STATUS    RESTARTS   AGE
dapr-dashboard-xxxxx                     1/1     Running   0          2m
dapr-operator-xxxxx                      1/1     Running   0          2m
dapr-placement-server-0                  1/1     Running   0          2m
dapr-sentry-xxxxx                        1/1     Running   0          2m
dapr-sidecar-injector-xxxxx             1/1     Running   0          2m
```

### Step 3.3: Access Dapr Dashboard (Optional)

```powershell
# Forward port to access dashboard
kubectl port-forward svc/dapr-dashboard -n dapr-system 8080:8080
```

Open browser: http://localhost:8080

---

## Phase 4: PostgreSQL Database Setup

SQLite is not suitable for production. We'll use PostgreSQL.

### Step 4.1: Create Namespace

```powershell
kubectl create namespace todo-phase5
```

### Step 4.2: Deploy PostgreSQL

See `kubernetes/postgres/postgres-deployment.yaml`

```powershell
kubectl apply -f kubernetes/postgres/postgres-secret.yaml
kubectl apply -f kubernetes/postgres/postgres-pvc.yaml
kubectl apply -f kubernetes/postgres/postgres-deployment.yaml
kubectl apply -f kubernetes/postgres/postgres-service.yaml
```

### Step 4.3: Verify PostgreSQL

```powershell
# Check pod
kubectl get pods -n todo-phase5 | findstr postgres

# Check service
kubectl get svc -n todo-phase5 | findstr postgres
```

### Step 4.4: Initialize Database

```powershell
# Get pod name
$POSTGRES_POD = kubectl get pods -n todo-phase5 -l app=postgres -o jsonpath="{.items[0].metadata.name}"

# Create database
kubectl exec -n todo-phase5 $POSTGRES_POD -- psql -U todouser -c "CREATE DATABASE todo_phase5;"

# Verify
kubectl exec -n todo-phase5 $POSTGRES_POD -- psql -U todouser -c "\l"
```

---

## Phase 5: Kafka Deployment with Strimzi

### Step 5.1: Install Strimzi Operator

```powershell
# Add Strimzi Helm repo
helm repo add strimzi https://strimzi.io/charts/
helm repo update

# Install Strimzi operator
helm install strimzi-operator strimzi/strimzi-kafka-operator `
  --namespace todo-phase5 `
  --set watchNamespaces="{todo-phase5}"
```

**Wait Time**: ~2 minutes

### Step 5.2: Verify Strimzi Operator

```powershell
kubectl get pods -n todo-phase5 | findstr strimzi
```

**Expected Output**:
```
strimzi-cluster-operator-xxxxx   1/1   Running   0   1m
```

### Step 5.3: Deploy Kafka Cluster

See `kubernetes/kafka/kafka-cluster.yaml`

```powershell
kubectl apply -f kubernetes/kafka/kafka-cluster.yaml
```

**Wait Time**: ~5-10 minutes (Kafka takes time to start)

### Step 5.4: Monitor Kafka Deployment

```powershell
# Watch Kafka pods starting
kubectl get pods -n todo-phase5 -w | findstr kafka

# Check Kafka cluster status
kubectl get kafka -n todo-phase5
```

**Expected Output**:
```
NAME         DESIRED KAFKA REPLICAS   DESIRED ZK REPLICAS   READY
todo-kafka   3                        3                     True
```

### Step 5.5: Create Kafka Topics

See `kubernetes/kafka/kafka-topics.yaml`

```powershell
kubectl apply -f kubernetes/kafka/kafka-topics.yaml
```

### Step 5.6: Verify Topics

```powershell
# List topics
kubectl get kafkatopics -n todo-phase5
```

**Expected Output**:
```
NAME           CLUSTER      PARTITIONS   REPLICATION FACTOR   READY
task-events    todo-kafka   3            2                    True
reminders      todo-kafka   3            2                    True
task-updates   todo-kafka   3            2                    True
```

---

## Phase 6: Backend Containerization

### Step 6.1: Create Dockerfile

See `Dockerfile` in project root.

### Step 6.2: Build Docker Image

```powershell
# Build image
docker build -t todo-phase5-backend:v1.0 .

# Tag for Minikube
docker tag todo-phase5-backend:v1.0 todo-phase5-backend:latest

# Push to Minikube's Docker daemon
minikube image load todo-phase5-backend:latest
```

### Step 6.3: Verify Image

```powershell
# Check image in Minikube
minikube ssh docker images | findstr todo-phase5
```

---

## Phase 7: Helm Chart Deployment

### Step 7.1: Create Helm Chart Structure

See `helm/todo-phase5/` directory.

### Step 7.2: Configure values.yaml

Edit `helm/todo-phase5/values.yaml` with your settings.

### Step 7.3: Install Helm Chart

```powershell
# Lint the chart first
helm lint helm/todo-phase5

# Dry run to check
helm install todo-phase5-app helm/todo-phase5 `
  --namespace todo-phase5 `
  --dry-run --debug

# Install for real
helm install todo-phase5-app helm/todo-phase5 `
  --namespace todo-phase5 `
  --wait --timeout 10m
```

**Wait Time**: ~2-5 minutes

### Step 7.4: Verify Deployment

```powershell
# Check all resources
kubectl get all -n todo-phase5

# Check pods
kubectl get pods -n todo-phase5

# Check services
kubectl get svc -n todo-phase5
```

---

## Phase 8: Dapr Component Configuration

### Step 8.1: Configure Kafka Pub/Sub

See `kubernetes/dapr/kafka-pubsub.yaml`

```powershell
kubectl apply -f kubernetes/dapr/kafka-pubsub.yaml
```

### Step 8.2: Configure State Store

See `kubernetes/dapr/statestore.yaml`

```powershell
kubectl apply -f kubernetes/dapr/statestore.yaml
```

### Step 8.3: Verify Dapr Components

```powershell
kubectl get components -n todo-phase5
```

---

## Phase 9: Verification & Testing

### Step 9.1: Check Backend Logs

```powershell
# Get backend pod name
$BACKEND_POD = kubectl get pods -n todo-phase5 -l app=todo-backend -o jsonpath="{.items[0].metadata.name}"

# View logs
kubectl logs -n todo-phase5 $BACKEND_POD -c todo-backend

# Follow logs
kubectl logs -n todo-phase5 $BACKEND_POD -c todo-backend -f
```

### Step 9.2: Port Forward to Backend

```powershell
# Forward backend port
kubectl port-forward -n todo-phase5 svc/todo-backend 8000:8000
```

Open browser: http://localhost:8000/health

### Step 9.3: Test API Endpoints

```powershell
# Health check
curl http://localhost:8000/health

# API docs
Start-Process http://localhost:8000/docs
```

### Step 9.4: Test Kafka Events

```powershell
# Send test event to Kafka
kubectl run kafka-producer -n todo-phase5 --rm -it --restart=Never `
  --image=quay.io/strimzi/kafka:latest-kafka-3.6.0 -- `
  bin/kafka-console-producer.sh --bootstrap-server todo-kafka-kafka-bootstrap:9092 --topic task-events

# Then type a JSON event:
# {"event_type":"task_created","data":{"id":999,"title":"Test Task","user_id":1}}
```

### Step 9.5: Monitor Kafka Consumer

```powershell
# View consumer logs
kubectl logs -n todo-phase5 -l app=kafka-consumer -f
```

### Step 9.6: Test WebSocket

```powershell
# Forward WebSocket port
kubectl port-forward -n todo-phase5 svc/todo-backend 8000:8000

# Use a WebSocket client to connect to:
# ws://localhost:8000/ws/tasks?token=YOUR_TOKEN
```

---

## Phase 10: Production Readiness Checklist

### Step 10.1: Enable Monitoring

```powershell
# Install Prometheus
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack `
  --namespace monitoring --create-namespace

# Forward Grafana port
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

Access Grafana: http://localhost:3000 (admin/prom-operator)

### Step 10.2: Configure Autoscaling

```powershell
# Apply HPA
kubectl apply -f kubernetes/backend/hpa.yaml

# Check HPA
kubectl get hpa -n todo-phase5
```

### Step 10.3: Set Resource Limits

Ensure all pods have resource requests/limits in Helm values.

### Step 10.4: Enable TLS

See `kubernetes/ingress/tls-secret.yaml` for HTTPS setup.

---

## Common Commands Reference

### Cluster Management
```powershell
# Start cluster
minikube start

# Stop cluster
minikube stop

# Delete cluster
minikube delete

# Get cluster IP
minikube ip
```

### Application Management
```powershell
# Restart deployment
kubectl rollout restart deployment/todo-backend -n todo-phase5

# Scale deployment
kubectl scale deployment/todo-backend --replicas=3 -n todo-phase5

# Update Helm release
helm upgrade todo-phase5-app helm/todo-phase5 -n todo-phase5

# Uninstall Helm release
helm uninstall todo-phase5-app -n todo-phase5
```

### Debugging
```powershell
# Describe pod
kubectl describe pod POD_NAME -n todo-phase5

# Get events
kubectl get events -n todo-phase5 --sort-by='.lastTimestamp'

# Shell into pod
kubectl exec -it POD_NAME -n todo-phase5 -- /bin/bash
```

---

## Troubleshooting Guide

### Issue: Pods in Pending State

**Cause**: Insufficient resources

**Solution**:
```powershell
# Increase Minikube resources
minikube delete
minikube start --cpus=6 --memory=12288
```

### Issue: ImagePullBackOff

**Cause**: Image not found in Minikube

**Solution**:
```powershell
# Load image again
minikube image load todo-phase5-backend:latest

# Or use imagePullPolicy: Never in deployment
```

### Issue: Kafka Not Starting

**Cause**: Insufficient resources or slow startup

**Solution**:
```powershell
# Wait longer (Kafka needs 5-10 minutes)
kubectl get pods -n todo-phase5 -w

# Check Kafka logs
kubectl logs -n todo-phase5 todo-kafka-kafka-0
```

### Issue: Database Connection Failed

**Cause**: Wrong DATABASE_URL

**Solution**:
```powershell
# Update secret
kubectl delete secret todo-secrets -n todo-phase5
kubectl create secret generic todo-secrets -n todo-phase5 `
  --from-literal=database-url='postgresql://todouser:todopass@postgres:5432/todo_phase5'

# Restart backend
kubectl rollout restart deployment/todo-backend -n todo-phase5
```

### Issue: Dapr Sidecar Not Injecting

**Cause**: Missing annotations

**Solution**:
Ensure deployment has:
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "todo-backend"
  dapr.io/app-port: "8000"
```

---

## Next Steps

1. **Set up CI/CD**: GitHub Actions or GitLab CI
2. **Configure Ingress**: External access via domain
3. **Add SSL/TLS**: Let's Encrypt certificates
4. **Implement Secrets Management**: HashiCorp Vault
5. **Set up Logging**: ELK Stack or Loki
6. **Deploy to Cloud**: AWS EKS, GCP GKE, or Azure AKS

---

## Summary

✅ Kubernetes cluster running
✅ Dapr installed and configured
✅ PostgreSQL database deployed
✅ Kafka cluster with Strimzi
✅ Backend deployed with Helm
✅ Event consumers running
✅ WebSocket endpoints available
✅ Monitoring enabled

**Your Todo Phase5 application is now production-ready on Kubernetes!**
