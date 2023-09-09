import requests
from KVerSca20_operator import *
from pprint import pprint
import os
import datetime
import csv
import time
import sys
 
# pod_name = os.environ['MY_POD_NAME'] #"prime-numbers-5bf844868b-kw7cf" # Already declared in VerSca20_operator
zero_state = ResourcesState(cpu_req="10m", cpu_lim="10m")

def k8s_metrics_logger():
    # list of column names
    field_names = ["timestamp","spec_req_cpu","spec_lim_cpu","status_alloc_cpu","status_req_cpu","status_lim_cpu", "response_time","request_count","throughput"]

    pod = getPod()
 
    [cpu_req, cpu_lim, mem_req, mem_lim] = getContainerResources(pod) # spec
    container_status_resources = getContainerStatusResources(pod) # status

    metrics = dict()
    metrics["timestamp"] = str(datetime.datetime.now())
    metrics["spec_req_cpu"] = cpu_req
    metrics["spec_lim_cpu"] = cpu_lim
    metrics["status_alloc_cpu"] = container_status_resources["allocated_resources"]["cpu"]
    metrics["status_req_cpu"] = container_status_resources["resources"]["requests"]["cpu"]
    metrics["status_lim_cpu"] = container_status_resources["resources"]["limits"]["cpu"]

    container_name = "http-metrics"
    for idx, container in enumerate(pod.spec.containers):
        if container.name == container_name:
            http_metrics = http_metrics_logger()
            metrics["response_time"] = http_metrics['response_time']
            metrics["request_count"] = http_metrics['request_count']
            metrics["throughput"] = http_metrics['throughput']

    currentDir = os.path.dirname(__file__)
    absolutePath = os.path.join(currentDir, "data") # "mnt/data"
    filename = pod_name +'.csv'
    filepath = os.path.join(absolutePath, filename)
    file_exists = os.path.isfile(filepath)
    
    with open(filepath, 'a') as csv_file:
        dict_object = csv.DictWriter(csv_file,  delimiter=',', lineterminator='\n', fieldnames=field_names)
        if not file_exists:
            dict_object.writeheader()  # file doesn't exist yet, write a header
        dict_object.writerow(metrics)

    return metrics

def http_metrics_logger():
    # api-endpoint
    URL = "http://localhost:8000/metrics/"
    # sending get request and saving the response as response object
    r = requests.get(url = URL)
    # extracting data in json format
    data = r.json()

    return data
    
def main():
    ctr = 0
    lim_rows_zero_state = 5
    while True:
        # if (getPodLabel('logger') == "on" and ctr < lim_rows_zero_state):
        # if (getPodLabel('logger') == "on" and not isInZeroState(zero_state)):
        if (getPodLabel('logger') == "on"):
            k8s_metrics_logger()
            
        """ if isInZeroState(zero_state): 
            ctr = ctr + 1
        else: 
            ctr = 0 """

        time.sleep(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Ctrl C - Stopping server")
        sys.exit(1)
