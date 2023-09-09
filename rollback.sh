#!/bin/bash

# Deleting old resources
kubectl delete -f "examples/benchmark/system-autoscaler"
kubectl delete -f "examples/benchmark/metrics"
kubectl delete -f "examples/benchmark/application2"
kubectl delete -f "config/storage"
kubectl delete -f "config/permissions"
kubectl delete -f "config/crd/bases"
kubectl delete -f config/cluster-conf/e2e-namespace.yaml