#!/bin/bash

# Deleting old resources
kubectl delete -f "examples/benchmark/system-autoscaler"
kubectl delete -f "examples/benchmark/metrics"

# Delete app
echo "Choose the configuration to delete:"
echo "1. App"
echo "2. App + KVerSca20"
read -p "Choice: " answer

if [[ $answer = 1 ]]; then
    kubectl delete -f "examples/benchmark/app_alone"
elif [[ $answer = 2 ]]; then
    kubectl delete -f "examples/benchmark/app_and_kversca20"
else
     echo "Run again the script and choose one of the options"
fi

kubectl delete -f "config/storage"
kubectl delete -f "config/permissions"
kubectl delete -f "config/crd/bases"
kubectl delete -f config/cluster-conf/e2e-namespace.yaml