# Todo Phase5 - Kubernetes Deployment

Production-ready Kubernetes deployment with Dapr, Kafka, and PostgreSQL.

## 🚀 Quick Start (3 Commands)

```powershell
# 1. Install prerequisites
.\kubernetes\deploy.ps1 -InstallPrerequisites

# 2. Create cluster and install Dapr
.\kubernetes\deploy.ps1 -CreateCluster

# 3. Deploy all components
.\kubernetes\deploy.ps1 -DeployAll
```

**Total Time**: ~15-20 minutes

---

## 📋 What Gets Deployed

### Infrastructure
- ✅ **Minikube Cluster** (4 CPUs, 8GB RAM)
- ✅ **Dapr** (Service mesh for microservices)
- ✅ **PostgreSQL** (Production database with persistent storage)
- ✅ **Kafka Cluster** (3 brokers, 3 Zookeeper nodes via Strimzi)

### Application
- ✅ **FastAPI Backend** (2 replicas with autoscaling)
- ✅ **Kafka Consumer** (Event processing)
- ✅ **WebSocket Support** (Real-time updates)

### Topics
- `task-events` - Task lifecycle events
- `task-updates` - Task modification events
- `reminders` - Task reminder notifications

---

## 📁 Directory Structure

```
kubernetes/
├── deploy.ps1                  # PowerShell deployment script
├── DEPLOYMENT_GUIDE.md         # Detailed step-by-step guide
├── README.md                   # This file
├── postgres/                   # PostgreSQL manifests
│   ├── postgres-secret.yaml
│   ├── postgres-pvc.yaml
│   ├── postgres-deployment.yaml
│   └── postgres-service.yaml
├── kafka/                      # Kafka manifests
│   ├── kafka-cluster.yaml
│   └── kafka-topics.yaml
└── dapr/                       # Dapr components
    ├── kafka-pubsub.yaml
    ├── statestore.yaml
    └── configuration.yaml

helm/
└── todo-phase5/                # Helm chart
    ├── Chart.yaml
    ├── values.yaml
    └── templates/
        ├── deployment.yaml
        ├── service.yaml
        ├── hpa.yaml
        ├── serviceaccount.yaml
        └── _helpers.tpl
```

---

## 🎯 Accessing the Application

### Backend API
```powershell
kubectl port-forward -n todo-phase5 svc/todo-phase5-app 8000:8000
```
Then open: http://localhost:8000/docs

### Dapr Dashboard
```powershell
dapr dashboard -k
```
Then open: http://localhost:8080

### PostgreSQL
```powershell
kubectl port-forward -n todo-phase5 svc/postgres 5432:5432
```
Connection: `postgresql://todouser:todopass123@localhost:5432/todo_phase5`

### Kafka
```powershell
kubectl port-forward -n todo-phase5 svc/todo-kafka-kafka-bootstrap 9092:9092
```

---

## 🔍 Monitoring & Debugging

### Check All Resources
```powershell
kubectl get all -n todo-phase5
```

### View Backend Logs
```powershell
$POD = kubectl get pods -n todo-phase5 -l app=todo-backend -o jsonpath="{.items[0].metadata.name}"
kubectl logs -n todo-phase5 $POD -f
```

### View Kafka Logs
```powershell
kubectl logs -n todo-phase5 todo-kafka-kafka-0 -f
```

### Check Dapr Status
```powershell
dapr status -k
```

### List Kafka Topics
```powershell
kubectl get kafkatopics -n todo-phase5
```

---

## 🧪 Testing

### Test API
```powershell
# Health check
curl http://localhost:8000/health

# API documentation
Start-Process http://localhost:8000/docs
```

### Send Kafka Event
```powershell
kubectl run kafka-producer -n todo-phase5 --rm -it --restart=Never `
  --image=quay.io/strimzi/kafka:latest-kafka-3.6.0 -- `
  bin/kafka-console-producer.sh --bootstrap-server todo-kafka-kafka-bootstrap:9092 --topic task-events
```

Then paste:
```json
{"event_type":"task_created","data":{"id":999,"title":"Test Task","user_id":1}}
```

---

## 🔧 Configuration

### Scale Backend
```powershell
kubectl scale deployment/todo-phase5-app --replicas=5 -n todo-phase5
```

### Update Configuration
Edit `helm/todo-phase5/values.yaml` and run:
```powershell
helm upgrade todo-phase5-app helm/todo-phase5 -n todo-phase5
```

### Change Database Password
1. Edit `kubernetes/postgres/postgres-secret.yaml`
2. Apply: `kubectl apply -f kubernetes/postgres/postgres-secret.yaml`
3. Restart pods: `kubectl rollout restart deployment -n todo-phase5`

---

## 🚨 Troubleshooting

### Pods Not Starting
```powershell
# Check pod status
kubectl get pods -n todo-phase5

# Describe pod to see events
kubectl describe pod POD_NAME -n todo-phase5

# View events
kubectl get events -n todo-phase5 --sort-by='.lastTimestamp'
```

### Image Pull Errors
```powershell
# Rebuild and reload image
docker build -t todo-phase5-backend:latest .
minikube image load todo-phase5-backend:latest

# Restart deployment
kubectl rollout restart deployment/todo-phase5-app -n todo-phase5
```

### Kafka Not Ready
```powershell
# Kafka takes 5-10 minutes to start
# Check Kafka cluster status
kubectl get kafka -n todo-phase5

# Check Kafka pods
kubectl get pods -n todo-phase5 | findstr kafka

# View Kafka broker logs
kubectl logs -n todo-phase5 todo-kafka-kafka-0
```

### Database Connection Failed
```powershell
# Verify PostgreSQL is running
kubectl get pods -n todo-phase5 -l app=postgres

# Test connection
$POSTGRES_POD = kubectl get pods -n todo-phase5 -l app=postgres -o jsonpath="{.items[0].metadata.name}"
kubectl exec -n todo-phase5 $POSTGRES_POD -- psql -U todouser -c "\l"
```

---

## 🧹 Cleanup

### Delete Everything
```powershell
.\kubernetes\deploy.ps1 -CleanUp
```

### Partial Cleanup
```powershell
# Uninstall app only
helm uninstall todo-phase5-app -n todo-phase5

# Delete namespace (keeps cluster running)
kubectl delete namespace todo-phase5

# Stop cluster
minikube stop
```

---

## 📚 Additional Resources

- **Detailed Guide**: See `DEPLOYMENT_GUIDE.md` for step-by-step instructions
- **Dapr Docs**: https://docs.dapr.io/
- **Strimzi Docs**: https://strimzi.io/docs/
- **Helm Docs**: https://helm.sh/docs/
- **Minikube Docs**: https://minikube.sigs.k8s.io/docs/

---

## ✅ Success Indicators

After deployment, you should see:
```
NAME                                    READY   STATUS    AGE
pod/postgres-xxx                        1/1     Running   5m
pod/strimzi-cluster-operator-xxx        1/1     Running   5m
pod/todo-kafka-kafka-0                  1/1     Running   5m
pod/todo-kafka-kafka-1                  1/1     Running   5m
pod/todo-kafka-kafka-2                  1/1     Running   5m
pod/todo-kafka-zookeeper-0              1/1     Running   5m
pod/todo-kafka-zookeeper-1              1/1     Running   5m
pod/todo-kafka-zookeeper-2              1/1     Running   5m
pod/todo-phase5-app-xxx                 2/2     Running   5m
```

**Note**: `2/2` means both the app container and Dapr sidecar are running.

---

## 🎉 You're Ready!

Your Todo Phase5 application is now running on Kubernetes with:
- Production-grade database (PostgreSQL)
- Event streaming (Kafka)
- Service mesh (Dapr)
- Auto-scaling (HPA)
- Real-time updates (WebSocket)

**Happy deploying!** 🚀
