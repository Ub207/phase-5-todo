# ⚡ Quick Start - Deploy in 3 Commands

## Prerequisites
- Windows 10/11
- Docker Desktop installed and running
- PowerShell (as Administrator)

---

## 🚀 Deploy Now (20 minutes)

### Command 1: Install Tools
```powershell
.\kubernetes\deploy.ps1 -InstallPrerequisites
```
**Installs**: kubectl, helm, minikube, dapr (~5 min)

### Command 2: Create Cluster
```powershell
.\kubernetes\deploy.ps1 -CreateCluster
```
**Creates**: Minikube + Dapr (~5 min)

### Command 3: Deploy App
```powershell
.\kubernetes\deploy.ps1 -DeployAll
```
**Deploys**: PostgreSQL, Kafka, Backend (~10 min)

---

## ✅ Verify It Works

```powershell
# Check everything is running
kubectl get pods -n todo-phase5

# Access backend
kubectl port-forward -n todo-phase5 svc/todo-phase5-app 8000:8000

# Open browser
Start-Process http://localhost:8000/docs
```

---

## 📁 What You Got

```
27 files created:
├── Documentation (3)
├── Deployment Script (1)
├── Dockerfile (1)
├── PostgreSQL Manifests (4)
├── Kafka Manifests (2)
├── Dapr Components (3)
└── Helm Chart (9 templates)
```

---

## 🔍 Useful Commands

```powershell
# View all resources
kubectl get all -n todo-phase5

# View logs
$POD = kubectl get pods -n todo-phase5 -l app=todo-backend -o jsonpath="{.items[0].metadata.name}"
kubectl logs -n todo-phase5 $POD -f

# Dapr dashboard
dapr dashboard -k

# Scale up
kubectl scale deployment/todo-phase5-app --replicas=5 -n todo-phase5

# Clean up
.\kubernetes\deploy.ps1 -CleanUp
```

---

## 📚 Full Documentation

- **Step-by-Step Guide**: `kubernetes/DEPLOYMENT_GUIDE.md`
- **Reference Manual**: `kubernetes/README.md`
- **Complete Summary**: `kubernetes/DEPLOYMENT_SUMMARY.md`

---

## 🎯 What's Deployed

| Component | Count | Status |
|-----------|-------|--------|
| Minikube Cluster | 1 | ✅ Running |
| PostgreSQL | 1 pod | ✅ Persistent |
| Kafka Brokers | 3 pods | ✅ Clustered |
| Zookeeper | 3 pods | ✅ Clustered |
| Backend API | 2 pods | ✅ Auto-scaling |
| Dapr Sidecars | Auto | ✅ Injected |

**Topics**: task-events, task-updates, reminders

---

## 🚨 Troubleshooting

**Pods pending?**
```powershell
# Increase resources
minikube delete
minikube start --cpus=6 --memory=12288
```

**Image not found?**
```powershell
# Reload image
docker build -t todo-phase5-backend:latest .
minikube image load todo-phase5-backend:latest
kubectl rollout restart deployment/todo-phase5-app -n todo-phase5
```

**Kafka slow to start?**
```
Wait 5-10 minutes. Kafka needs time to initialize.
Check: kubectl get kafka -n todo-phase5
```

---

## ✨ You're Done!

Your app is now running on Kubernetes with:
- Production database (PostgreSQL)
- Event streaming (Kafka)
- Service mesh (Dapr)
- Auto-scaling (HPA)

**Happy deploying!** 🚀
