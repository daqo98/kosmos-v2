![pipelines](https://github.com/lterrac/system-autoscaler/workflows/base-pipeline/badge.svg)

# KOSMOS

<p align="center">
  <img width="100%" src="https://i.imgur.com/tm9mSuM.png" alt="Politecnico di Milano" />
</p>

## Overview

KOSMOS is an autoscaling solution, developed at the Politecnico di Milano, for Kubernetes. Pods are individually controlled by control-theoretical planners that manage container resources on-the-fly (vertical scaling). A dedicated component is in charge of handling resource contention scenarios among containers deployed in the same node (a physical or virtual machine). Finally, at the cluster-level a heuristic-based controller is in charge of the horizontal scaling of each application.

## Controller

The controllers are freely inspired from [sample-controller](https://github.com/kubernetes/sample-controller)

- [Pod Autoscaler](pkg/pod-autoscaler/README.md)
- [Pod Resource Updater](pkg/pod-resource-updater/README.md)
- [PodScale Controller](pkg/podscale-controller/README.md)


## Getting started


### Requirements
* **Kubectl v1.27.4 (client version)**.
* **Kind v0.20.0**.

### Platform setup

In the root folder of the Kosmos repo:

1. Create Cluster with its config:
   ```
   kind create cluster --name k8s-playground --image=kindest/node:v1.27.3@sha256:3966ac761ae0136263ffdb6cfd4db23ef8a83cba8a463690e98317add2c9ba72 --config "config/cluster-conf/development-cluster.yaml"
   ```
2. Create namespace: `kubectl apply -f config/cluster-conf/e2e-namespace.yaml`
3. Install Kosmos Custom Resource Definitions (CRDs): `kubectl apply -f "config/crd/bases"`
4. Install RBACs: kubectl apply -f "config/permissions"
5. To be able to schedule pods on the Kubernetes control-plane node, you need to remove a taint on the master or control-plane nodes:
    - `kubectl taint nodes --all node-role.kubernetes.io/master-`
    - `kubectl taint nodes --all  node-role.kubernetes.io/control-plane-`
6. Deploy app:  `kubectl apply -f "examples/benchmark/application2"`
7. Deploy metrics: `kubectl apply -f "examples/benchmark/metrics"`
8. Deploy system autoscaler: `kubectl apply -f "examples/benchmark/system-autoscaler"`
9. If nginx-admission-patch is failing:
    - `kubectl delete -A validatingWebhookConfiguration ingress-nginx-admission`
    - `kubectl apply -f "examples/benchmark/metrics"`
10. Port-forward the prime-numbers app: `kubectl port-forward service/prime-numbers 8000:8000`

When everything is working:
1. `kubectl cp kube-system/pod-autoscaler-574d6c9f7f-dwxj8:var/podscale.json podscale.json -c pod-autoscaler` **(DOESN'T WORK)**
2. `kubectl exec postgres-statefulset-0 -- psql -d awesomedb -U amazinguser -c "\copy response_information to /response.csv delimiter ',' csv header;"`
3. `kubectl cp postgres-statefulset-0:response.csv response.csv`

### Run Kosmos Controllers:
```
kubectl apply -f examples/benchmark/system-autoscaler
```
By deploying `examples/benchmark/system-autoscaler`, 4 controllers will be run: `MetricsExposer`, `PodAutoscaler`, `PodReplicaUpdater`, and `PodScaleController`.

## CRDs code generation

Since the API code generator used in [hack/update-codegen.sh](hack/update-codegen.sh) was not designed to work with Go modules, it is mandatory to recreate the entire module path in order to make the code generation work.  
This gives you two options:  
1) Create the folders `github.com/deib-polimi` and clone this repository in any location of your filesystem.
2) Clone the repository inside the `GOPATH` directory.

In the end there is no choice other than to preserve the module hierarchy.

## Citation
If you use this code for evidential learning as part of your project or paper, please cite the following work:  

    @article{baresi2021kosmos,
      title={{KOSMOS:} Vertical and Horizontal Resource Autoscaling for Kubernetes},
      author={Baresi, Luciano and Hu, Davide Yi Xian and Quattrocchi, Giovanni and Terracciano, Luca},
      journal={ICSOC},
      volume={13121},
      pages={821--829},
      year={2021}
    }

## Contributors
* **[Davide Yi Xian Hu](https://github.com/DragonBanana)**
* **[Luca Terracciano](https://github.com/lterrac)**
