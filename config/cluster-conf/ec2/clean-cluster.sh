#!/bin/bash
read -p "Is this the master node? [y/n]" answer
if [[ $answer = y ]] ; then
  # Drain nodes
  for nodename in $(kubectl get nodes | awk '{print $1}')
  do
    kubectl drain $nodename --ignore-daemonsets --delete-emptydir-data --force
  done
  # Reset cluster
  sudo kubeadm reset --cri-socket=unix:///var/run/containerd/containerd.sock
  #sudo kubeadm reset --cri-socket=unix:///var/run/cri-dockerd.sock
fi

# If device or resource busy
umount_times=$(mount | grep /var/lib/kubelet/ | wc -l)
echo $umount_times
if [[ $umount_times -ge 1 ]] ; then
  for i in `seq 1 $umount_times`
  do
    sudo umount -lf tmpfs
  done
fi

sudo rm -rf /etc/kubernetes /var/lib/kubelet /var/lib/etcd /etc/cni/net.d

# Kill kubelet processes pending
for kubelet_pid in $(ps aux | grep kubelet | grep -v grep| awk '{print $2}')
do
  sudo kill -9 $kubelet_pid
done

sudo iptables -F
sudo iptables -t nat -F
sudo iptables -t mangle -F
sudo iptables -X