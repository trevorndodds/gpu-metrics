#!/usr/bin/env python
#Collect metrics from NVIDIA GPUs using nvidia-smi tool and send to Elasticsearch

import datetime
import time
import urllib
import json
import urllib2
import os
import socket
import sys
import pprint
import subprocess

# ElasticSearch Cluster to Send Metrics
elasticIndex = os.environ.get('GPU_METRICS_INDEX_NAME', 'gpu_metrics')
elasticMonitoringCluster = os.environ.get('GPU_METRICS_CLUSTER_URL', 'http://192.168.1.151:9200')
interval = int(os.environ.get('GPU_METRICS_INTERVAL', '10'))

def get_gpu_data():
    query = ["timestamp","gpu_name","pci.bus_id","driver_version","pstate","pcie.link.gen.max","pcie.link.gen.current",
             "temperature.gpu","utilization.gpu","utilization.memory","memory.total","memory.free","memory.used","power.draw",
             "gpu_serial","clocks.current.graphics","clocks.current.sm","clocks.current.memory","ecc.errors.corrected.aggregate.total",
             "ecc.errors.uncorrected.aggregate.total","gpu_uuid","clocks.max.mem","clocks.max.sm","clocks.max.graphics"]
    #example Output:
    #'2018/08/01 17:58:35.632', 'TeslaP100 - PCIE - 16GB', '00000000:06:00.0', 390.46, 'P0', 3, 3, 25, 3, 0, 16280, 16280, 0, 27.00
    #set the DataType here
    dType = [str, str, str, float, str, int, int, int, int, int, int, int, int, float, int, int, int, int, int, int, str, int, int, int]
    try:
        output = subprocess.check_output(["nvidia-smi", "--query-gpu=timestamp,name,pci.bus_id,driver_version,pstate,"
                                                        "pcie.link.gen.max,pcie.link.gen.current,temperature.gpu,"
                                                        "utilization.gpu,utilization.memory,memory.total,memory.free,"
                                                        "memory.used,power.draw,gpu_serial,clocks.current.graphics,"
                                                        "clocks.current.sm,clocks.current.memory,"
                                                        "ecc.errors.corrected.aggregate.total,"
                                                        "ecc.errors.uncorrected.aggregate.total,gpu_uuid,"
                                                        "clocks.max.mem,clocks.max.sm,clocks.max.graphics",
                                          "--format=csv,nounits,noheader"]).rstrip()
        list_strings = output.split(", ")
        list_values = [t(x) for t, x in zip(dType, list_strings)]
        zipped = dict(zip(query, list_values))
        zipped['@timestamp'] = str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3])
        zipped['node'] = socket.gethostname().lower()
        zipped['pstate'] = int((zipped['pstate']).replace('P',''))
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(zipped)
        post_data(zipped)
    except Exception as e:
        print "Error:  {0}".format(str(e))
        pass

def post_data(data):
    utc_datetime = datetime.datetime.utcnow()
    url_parameters = {'cluster': elasticMonitoringCluster, 'index': elasticIndex,
        'index_period': utc_datetime.strftime("%Y.%m"), }
    url = "%(cluster)s/%(index)s-%(index_period)s/message" % url_parameters
    headers = {'content-type': 'application/json'}
    try:
        req = urllib2.Request(url, headers=headers, data=json.dumps(data))
        response = urllib2.urlopen(req)
        print response.read()
    except Exception as e:
        print "Error:  {0}".format(str(e))


def main():
    get_gpu_data()


if __name__ == '__main__':
    try:
        nextRun = 0
        while True:
            if time.time() >= nextRun:
                nextRun = time.time() + interval
                now = time.time()
                main()
                elapsed = time.time() - now
                print "Total Elapsed Time: %s" % elapsed
                timeDiff = nextRun - time.time()

                # Check timediff , if timediff >=0 sleep, if < 0 send metrics to es
                if timeDiff >= 0:
                    time.sleep(timeDiff)

    except KeyboardInterrupt:
        print 'Interrupted'
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
