#!/bin/bash

# Init kubeAdm cluster
sudo kubeadm init --config=$HOME/kversca20/config/cluster-conf/ec2/kubeadm-cluster.yaml
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Install Flannel as CNI add-on
kubectl apply -f ~/kversca20/config/cluster-conf/ec2/kube-flannel.yml
sudo systemctl restart containerd.service

# Verify node is running
kubectl get nodes -o wide
