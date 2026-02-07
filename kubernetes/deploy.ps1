# Todo Phase5 - Kubernetes Deployment Script
# Run this script in PowerShell as Administrator

param(
    [switch]$InstallPrerequisites,
    [switch]$CreateCluster,
    [switch]$DeployAll,
    [switch]$CleanUp
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param($Message)
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
}

function Write-Success {
    param($Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Error {
    param($Message)
    Write-Host "[FAIL] $Message" -ForegroundColor Red
}

# Install Prerequisites
if ($InstallPrerequisites) {
    Write-Step "Installing Prerequisites"

    # Check if Chocolatey is installed
    if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
        Write-Host "Installing Chocolatey..."
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    }

    Write-Host "Installing kubectl, helm, and minikube..."
    choco install kubernetes-cli kubernetes-helm minikube -y

    Write-Host "Installing Dapr CLI..."
    powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"

    Write-Success "Prerequisites installed successfully"
}

# Create Cluster
if ($CreateCluster) {
    Write-Step "Creating Minikube Cluster"

    # Start Minikube
    minikube start --cpus=4 --memory=8192 --driver=docker

    # Enable addons
    minikube addons enable ingress
    minikube addons enable metrics-server

    # Set kubectl context
    kubectl config use-context minikube

    # Create namespace
    kubectl create namespace todo-phase5

    # Install Dapr
    Write-Step "Installing Dapr on Kubernetes"
    dapr init --kubernetes --wait

    Write-Success "Cluster created and Dapr installed"
}

# Deploy All Components
if ($DeployAll) {
    Write-Step "Deploying PostgreSQL"
    kubectl apply -f kubernetes/postgres/postgres-secret.yaml
    kubectl apply -f kubernetes/postgres/postgres-pvc.yaml
    kubectl apply -f kubernetes/postgres/postgres-deployment.yaml
    kubectl apply -f kubernetes/postgres/postgres-service.yaml

    Write-Host "Waiting for PostgreSQL to be ready..."
    kubectl wait --for=condition=ready pod -l app=postgres -n todo-phase5 --timeout=300s
    Write-Success "PostgreSQL deployed"

    Write-Step "Deploying Kafka with Strimzi"
    helm repo add strimzi https://strimzi.io/charts/
    helm repo update
    helm install strimzi-operator strimzi/strimzi-kafka-operator `
        --namespace todo-phase5 `
        --set watchNamespaces="{todo-phase5}"

    Write-Host "Waiting for Strimzi operator..."
    Start-Sleep -Seconds 30

    kubectl apply -f kubernetes/kafka/kafka-cluster.yaml
    kubectl apply -f kubernetes/kafka/kafka-topics.yaml

    Write-Host "Waiting for Kafka cluster (this takes 5-10 minutes)..."
    kubectl wait kafka/todo-kafka --for=condition=Ready --timeout=600s -n todo-phase5
    Write-Success "Kafka deployed"

    Write-Step "Deploying Dapr Components"
    kubectl apply -f kubernetes/dapr/kafka-pubsub.yaml
    kubectl apply -f kubernetes/dapr/statestore.yaml
    kubectl apply -f kubernetes/dapr/configuration.yaml
    Write-Success "Dapr components deployed"

    Write-Step "Building and Loading Backend Image"
    docker build -t todo-phase5-backend:latest .
    minikube image load todo-phase5-backend:latest
    Write-Success "Backend image built and loaded"

    Write-Step "Deploying Backend with Helm"
    helm lint helm/todo-phase5
    helm install todo-phase5-app helm/todo-phase5 `
        --namespace todo-phase5 `
        --wait --timeout 10m
    Write-Success "Backend deployed"

    Write-Step "Deployment Summary"
    kubectl get all -n todo-phase5

    Write-Success "All components deployed successfully!"
    Write-Host "`nTo access the backend, run:"
    Write-Host "kubectl port-forward -n todo-phase5 svc/todo-phase5-app 8000:8000" -ForegroundColor Yellow
}

# Clean Up
if ($CleanUp) {
    Write-Step "Cleaning Up Resources"

    $response = Read-Host "Are you sure you want to delete everything? (yes/no)"
    if ($response -eq "yes") {
        helm uninstall todo-phase5-app -n todo-phase5 2>$null
        helm uninstall strimzi-operator -n todo-phase5 2>$null
        kubectl delete namespace todo-phase5
        dapr uninstall --kubernetes
        minikube delete
        Write-Success "Cleanup complete"
    } else {
        Write-Host "Cleanup cancelled"
    }
}

# Show help if no parameters
if (-not ($InstallPrerequisites -or $CreateCluster -or $DeployAll -or $CleanUp)) {
    Write-Host @"
Todo Phase5 - Kubernetes Deployment Script

Usage:
    .\deploy.ps1 -InstallPrerequisites   Install kubectl, helm, minikube, dapr
    .\deploy.ps1 -CreateCluster          Create Minikube cluster and install Dapr
    .\deploy.ps1 -DeployAll              Deploy all components (PostgreSQL, Kafka, Backend)
    .\deploy.ps1 -CleanUp                Clean up all resources

Example - Full deployment:
    .\deploy.ps1 -InstallPrerequisites
    .\deploy.ps1 -CreateCluster
    .\deploy.ps1 -DeployAll

"@ -ForegroundColor Cyan
}
