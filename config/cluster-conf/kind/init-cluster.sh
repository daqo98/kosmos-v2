#!/bin/bash

cluster_name=k8s-playground
# Create kind cluster with its config
kind create cluster --name $cluster_name --image=kindest/node:v1.27.3@sha256:3966ac761ae0136263ffdb6cfd4db23ef8a83cba8a463690e98317add2c9ba72 \
    --config "config/cluster-conf/kind/development-cluster.yaml"
