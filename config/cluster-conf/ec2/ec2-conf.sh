#!/bin/bash
# #Install cri-dockerd container runtime: 
# sudo su
# apt-get update && apt install docker.io -y
	
# #Docker requires the additional service cri-dockerd:
# #For Ubuntu 22.04 (Jammy Jellyfish): 
# wget https://github.com/Mirantis/cri-dockerd/releases/download/v0.3.4/cri-dockerd_0.3.4.3-0.ubuntu-jammy_amd64.deb
# sudo dpkg -i cri-dockerd_0.3.4.3-0.ubuntu-jammy_amd64.deb

# Kubernetes pkg repos:
sudo apt-get update
# apt-transport-https may be a dummy package; if so, you can skip that package
sudo apt-get install -y apt-transport-https ca-certificates curl
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.27/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

# This overwrites any existing configuration in /etc/apt/sources.list.d/kubernetes.list
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.27/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
# Install kubelet, kubeadm and kubectl:
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

# Disable swap for kubelet to work properly: 
sudo swapoff -a
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab

# Installing KVerSca20 related files
cd $HOME
git clone https://github.com/daqo98/versca20.git
git clone https://github.com/daqo98/kversca20.git
sudo apt install -y pip
pip install pipenv
echo "export PATH=$PATH:$HOME/.local/bin" >> ~/.bashrc
source ~/.bashrc

# Install containerd
wget https://github.com/containerd/containerd/releases/download/v1.7.5/containerd-1.7.5-linux-amd64.tar.gz 
sudo tar Cxzvf /usr/local containerd-1.7.5-linux-amd64.tar.gz 
wget https://raw.githubusercontent.com/containerd/containerd/main/containerd.service
sudo mkdir -p /usr/local/lib/systemd/system
sudo mv containerd.service /usr/local/lib/systemd/system/containerd.service
sudo systemctl daemon-reload
sudo systemctl enable --now containerd
rm -f containerd-1.7.5-linux-amd64.tar.gz

# Creating conf.toml config file:
sudo mkdir /etc/containerd
# sudo touch /etc/containerd/config.toml
# sudo chmod 666 /etc/containerd/config.toml
# containerd config default > /etc/containerd/config.toml
# nano /etc/containerd/config.toml
wget https://raw.githubusercontent.com/daqo98/versca20/main/config/cluster-conf/ec2/config.toml
sudo mv config.toml /etc/containerd/
sudo systemctl restart containerd

# Install runc
wget https://github.com/opencontainers/runc/releases/download/v1.1.9/runc.amd64
sudo install -m 755 runc.amd64 /usr/local/sbin/runc
rm -f runc.amd64

# Install CNI
wget https://github.com/containernetworking/plugins/releases/download/v1.3.0/cni-plugins-linux-amd64-v1.3.0.tgz
sudo mkdir -p /opt/cni/bin
sudo tar Cxzvf /opt/cni/bin cni-plugins-linux-amd64-v1.3.0.tgz
rm -f cni-plugins-linux-amd64-v1.3.0.tgz

# Install crictl
VERSION="v1.27.1" # check latest version in /releases page
wget https://github.com/kubernetes-sigs/cri-tools/releases/download/$VERSION/crictl-$VERSION-linux-amd64.tar.gz
sudo tar zxvf crictl-$VERSION-linux-amd64.tar.gz -C /usr/local/bin
rm -f crictl-$VERSION-linux-amd64.tar.gz

# Create a conf file to set the container runtime endpoint:
cat <<EOF | sudo tee /etc/crictl.yaml
runtime-endpoint: unix:///run/containerd/containerd.sock
image-endpoint: unix:///run/containerd/containerd.sock
timeout: 2
debug: true
pull-image-on-create: false
EOF

# Forwarding IPv4 and letting iptables see bridged traffic
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

sudo modprobe overlay
sudo modprobe br_netfilter

# sysctl params required by setup, params persist across reboots
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

# Apply sysctl params without reboot
sudo sysctl --system

# k9s
sudo snap install k9s --channel=stable
echo "export PATH=$PATH:/snap/bin" >> ~/.bashrc
source ~/.bashrc
sudo ln -s /snap/k9s/current/bin/k9s /snap/bin/k9s