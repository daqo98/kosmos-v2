#!/usr/bin/env python3
import kopf
import kubernetes.config as k8s_config
import kubernetes.client as k8s_client
from kubernetes.client.rest import ApiException
import logging
import os
from pprint import pprint
import requests
import datetime

# Load Kubernetes config file
try:
    k8s_config.load_kube_config()
except k8s_config.ConfigException:
    k8s_config.load_incluster_config()

# Create an instance of the API class
api_core_instance = k8s_client.CoreV1Api()
api_apps_instance = k8s_client.AppsV1Api()
pretty = 'pretty_example'
# TODO: Get App name either from a OS/env variable or using Kopf to detect updates on deployments and update the global vars
namespace_name = os.environ['MY_NS_NAME'] #"default"
deployment_name = os.environ['MY_DP_NAME'] #"prime-numbers" 
pod_name = os.environ['MY_POD_NAME'] #"prime-numbers-5bf844868b-kw7cf" # # Copy complete name of the pod e.g. prime-numbers-<pod-template-has>}-{}
app_name = os.environ['MY_APP_NAME'] #"prime-numbers"

logger = logging.getLogger("VerSca20_operator")
logging.getLogger("kubernetes.client.rest").setLevel(logging.ERROR)

class ResourcesState():
    def __init__(self, cpu_req, cpu_lim, **kwargs):
        self.cpu_req = cpu_req
        self.cpu_lim = cpu_lim

        for key, val in kwargs.items():
            if (key == "mem_req"): self.mem_req = val
            if (key == "mem_lim"): self.mem_lim = val
            if (key == "resp_time"): self.resp_time = val

def handlingException(api_call):
    try: 
        return(api_call)
    except ApiException as e:
        logger.error(f"Exception: {e}")

def updatePod(new_pod_data):
    return api_core_instance.patch_namespaced_pod(name=pod_name, namespace=namespace_name, body=new_pod_data)

def updateStatusResourcesPod(new_pod_data):
    api_response = api_core_instance.patch_namespaced_pod_status(name=pod_name, namespace=namespace_name, body=new_pod_data)
    return api_response


def createDictContainerResources(container_idx, cpu_req, cpu_lim, curr_rsrc, **kwargs):
    """
    Perform vertical scaling of the first container of the first pod in the global variable namespace_name
    Args:
        container_idx: Index of the container in the current pod
        cpu_req: cpu request
        cpu_lim: cpu limit
        Optional:
            mem_req: memory request
            mem_lim: memory limit
    Returns:
        Nothing
    """
    [current_cpu_req, current_cpu_lim, current_mem_req, current_mem_lim] = curr_rsrc

    dict_spec_container_resources = [{
            'op': 'replace', 'path': f'/spec/containers/{container_idx}/resources',
            'value': {
                        'limits': {'cpu': f'{cpu_lim}','memory': f"{kwargs.get('mem_lim', current_mem_lim)}"},
                        'requests': {'cpu': f'{cpu_req}','memory': f"{kwargs.get('mem_req', current_mem_req)}"}
                    }
        }]

    
    return dict_spec_container_resources


def createDictContainerStatusResources(container_status_idx, cpu_req, cpu_lim, mem_req, mem_lim):
    #TODO: Search of container index given app name. Not thinking that it is going to be always the container 0
    """ dict_status_container_resources = [{
                                    'op': 'replace', 'path': f'/status/containerStatuses/{container_status_idx}',
                                    'value': {
                                                'allocatedResources': {'cpu': f'{cpu_req}','memory': f'{mem_req}'},
                                                'resources': {
                                                    'limits': {'cpu': f'{cpu_lim}','memory': f'{mem_lim}'},
                                                    'requests': {'cpu': f'{cpu_req}','memory': f'{mem_req}'}
                                            }
                                        }}] """

    dict_status_container_resources = [{
                                    'op': 'replace', 'path': f'/status/containerStatuses/{container_status_idx}/allocatedResources',
                                    'value': {
                                                'cpu': f'{cpu_req}','memory': f'{mem_req}'
                                                }}]

    return dict_status_container_resources


def getPod():
    """
    Returns: First pod in the namespace specified in the global variable as a V1Pod object
    """
    pods = api_core_instance.list_namespaced_pod(namespace=namespace_name, pretty=pretty)
    pod_idx = getPodIdx(pods)
    return pods.items[pod_idx]

def verticalScale(cpu_req, cpu_lim, **kwargs):
    """
    Perform vertical scaling of the first container of the first pod in the global variable namespace_name
    Args:
        cpu_req: cpu request
        cpu_lim: cpu limit
        Optional:
            mem_req: memory request
            mem_lim: memory limit
    Returns:
        Nothing
    """
    pod = getPod()
    container_idx = getContainerIdx(pod, getAppName())
    # Update pod's spec
    curr_rsrc = getContainerResources(pod) # current resources
    dict_container_resources = createDictContainerResources(container_idx, cpu_req, cpu_lim, curr_rsrc, **kwargs)
    updatePod(dict_container_resources)

    mem_req = kwargs.get("mem_req", curr_rsrc[2])
    mem_lim = kwargs.get("mem_lim", curr_rsrc[3])

    logger.info("App container resources modified")
    logger.info(f"New resources: cpu_req: {cpu_req}, cpu_lim: {cpu_lim}, mem_req: {mem_req}, and mem_lim: {mem_lim}")

def getContainersPort(container_name):
    pod = getPod()
    container_idx = getContainerIdx(pod, container_name)
    port = pod.spec.containers[container_idx].ports[0].container_port
    logger.info(f"Container port is: {port}")
    return port

def deletePod():
    # TODO: Not used so far. Maybe is useful in the future.
    pod = getPod()
    podName = pod.metadata.name
    api_core_instance.delete_namespaced_pod(name=podName, namespace=namespace_name, body=k8s_client.V1DeleteOptions(), pretty=pretty)

def getContainerResources(pod):
    container_idx = getContainerIdx(pod, getAppName())
    pod_resources = pod.spec.containers[container_idx].resources
    cpu_req = pod_resources.requests['cpu']
    cpu_lim = pod_resources.limits['cpu']
    mem_req = pod_resources.requests['memory']
    mem_lim = pod_resources.limits['memory']
    resources = [cpu_req, cpu_lim, mem_req, mem_lim]
    return resources

def isInZeroState(zeroStateDef):
    [cpu_req, cpu_lim, mem_req, mem_lim] = getContainerResources(getPod())

    if (hasattr(zeroStateDef, "mem_req") and hasattr(zeroStateDef, "mem_lim")):
        if (cpu_req == zeroStateDef.cpu_req and cpu_lim == zeroStateDef.cpu_lim and mem_req == zeroStateDef.mem_req and mem_lim == zeroStateDef.mem_lim):
            return True
        else: 
            return False
    else:
        if (cpu_req == zeroStateDef.cpu_req and cpu_lim == zeroStateDef.cpu_lim):
            return True
        else: 
            return False

def isContainerReady():
    pod = getPod()
    container_status = getContainerStatus(pod)
    return container_status.ready

def getDefaultConfigContainer():
    deployment = api_apps_instance.read_namespaced_deployment(deployment_name, namespace_name, pretty=pretty)
    pod = deployment.spec.template
    return getContainerResources(pod)

def getContainerStatus(pod):
    container_status_idx = getContainerStatusIdx(pod, getAppName())
    return pod.status.container_statuses[container_status_idx]

def getContainerStatusResources(pod):
    status_resources = dict()
    status_resources["resources"] = dict()
    container_status = getContainerStatus(pod)
    status_resources["allocated_resources"] = container_status.allocated_resources
    status_resources["resources"]["limits"] = container_status.resources.limits
    status_resources["resources"]["requests"] = container_status.resources.requests
    return status_resources

def getAppName():
    #deployment = api_apps_instance.read_namespaced_deployment(deployment_name, namespace_name, pretty=pretty)
    #app_name = deployment.spec.template.metadata.labels["app"]
    return app_name

def getContainerIdx(pod, container_name):
    for idx, container in enumerate(pod.spec.containers):
        if container.name == container_name:
            container_idx = idx
            break
    return container_idx

def getContainerStatusIdx(pod, container_name):
    for idx, container in enumerate(pod.status.container_statuses):
        if container.name == container_name:
            container_status_idx = idx
            break
    return container_status_idx

def getContainerRestartCount():
    container_status = getContainerStatus()
    return container_status.restart_count

def getPodIdx(pods):
    for idx, pod in enumerate(pods.items):
        if pod_name == pod.metadata.name:
            pod_idx = idx
            break
    return pod_idx

def modifyLabel(key,value):
    pod = getPod()
    dict_entry = [{'op': 'replace', 'path': f'/metadata/labels/{key}',
                                    'value': value
                                    }]
    updatePod(dict_entry)
    logger.info(f"Label updated: '{key}: {value}'")

def getPodLabel(label):
    value = getPod().metadata.labels[f"{label}"]
    logger.info(f"'{label}: {value}'")
    return value

