#!/usr/bin/env python3
import kopf
import kubernetes.config as k8s_config
import kubernetes.client as k8s_client
from kubernetes.client.rest import ApiException
import logging
import os
from pprint import pprint
import requests

# Load Kubernetes config file
try:
    k8s_config.load_kube_config()
except k8s_config.ConfigException:
    k8s_config.load_incluster_config()

# Create an instance of the API class
#api_core_instance = k8s_client.CoreV1Api()
#api_apps_instance = k8s_client.AppsV1Api()
api_ext_instance = k8s_client.ApiextensionsV1Api()
api_custom_obj_instance = k8s_client.CustomObjectsApi()
pretty = 'pretty_example'

logger = logging.getLogger("KVerSca20_operator")
logging.getLogger("kubernetes.client.rest").setLevel(logging.ERROR)

group = 'systemautoscaler.polimi.it'
version = 'v1beta1'
namespace = 'default'
plural = 'servicelevelagreements'
name = 'prime-numbers'

def listCRDs():
    try: 
        return api_ext_instance.list_custom_resource_definition(pretty=pretty)
    except ApiException as e:
        print("Exception when calling ApiextensionsV1beta1Api->read_custom_resource_definition: %s\n" % e)

def getCRD():
    crd_name = "servicelevelagreements.systemautoscaler.polimi.it"
    try: 
        return api_ext_instance.read_custom_resource_definition(crd_name, pretty=pretty)
    except ApiException as e:
        print("Exception when calling ApiextensionsV1beta1Api->read_custom_resource_definition: %s\n" % e)

def getSLA():
    try:
        return api_custom_obj_instance.get_namespaced_custom_object(group, version, namespace, plural, name)
    except ApiException as e:
        print("Exception when calling CustomObjectsApi->get_namespaced_custom_object: %s\n" % e)

def modifySLA(sla, cpu_req, cpu_lim, mem_req, mem_lim, resp_time):
    sla['spec']['defaultResources'] = {'cpu': f'{cpu_req}', 'memory': f'{mem_req}'}
    sla['spec']['maxResources'] = {'cpu': f'{cpu_lim}', 'memory': f'{mem_lim}'}
    sla['spec']['minResources'] = {'cpu': f'{cpu_req}', 'memory': f'{mem_req}'}
    sla['spec']['metric'] = {'responseTime': f'{resp_time}'}
    return sla

def patchSLA(body):
    try:
        return api_custom_obj_instance.patch_namespaced_custom_object(group, version, namespace, plural, name, body)
    except ApiException as e:
        print("Exception when calling CustomObjectsApi->patch_namespaced_custom_object: %s\n" % e)

def updateSLA(cpu_req, cpu_lim, mem_req, mem_lim, resp_time):
    sla = getSLA()
    partial_new_sla = modifySLA(sla, cpu_req, cpu_lim, mem_req, mem_lim, resp_time)
    patchSLA(partial_new_sla)

#pprint(getCRD())
#pprint(getSLA())
#updateSLA(resp_time="1000000m", cpu_req="10m", cpu_lim="10m", mem_req="10Mi", mem_lim="10Mi") # To zero
#pprint(getSLA())