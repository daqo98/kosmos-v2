#!/bin/bash

# Create namespace
kubectl apply -f config/cluster-conf/e2e-namespace.yaml

# Install Kosmos Custom Resource Definitions (CRDs)
kubectl apply -f "config/crd/bases"

# Install RBACs
kubectl apply -f "config/permissions"

# Install PV and PVC to store .csv of metrics-logger
kubectl apply -f "config/storage"

# Remove taint on the master or control-plane nodes to schedule pods on the Kubernetes control-plane node:
kubectl taint nodes --all node-role.kubernetes.io/master-
kubectl taint nodes --all  node-role.kubernetes.io/control-plane-

# Deploy app
kubectl apply -f "examples/benchmark/application2"

# Deploy metrics
kubectl apply -f "examples/benchmark/metrics"

# Deploy system-autoscaler
kubectl apply -f "examples/benchmark/system-autoscaler" #/pod-replica-updater.yaml"

# Deleting podscales since the pod-autoscaler doesn't detect them at first
kubectl delete podscales --all

kubectl port-forward service/prime-numbers 8080:80
# kubectl port-forward service/http-metrics 8000:8000
# Try a request: curl http://localhost:8080/prime/12 or curl http://<Node's_Public_IP>:31512/prime/12
## Locust workload: 
# cd $HOME/kversca20
# pipenv install
# pipenv shell
# locust -f ~/kversca20/locust_workload.py --headless --host=http://localhost:8080/prime/12