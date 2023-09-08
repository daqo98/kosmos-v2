#!/bin/bash

cluster_name=k8s-playground
# Delete Kind cluster with its config
kind delete cluster --name $cluster_name