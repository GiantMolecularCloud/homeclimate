"""
Home Climate Monitoring

author: GiantMolecularCloud

This script is part of a collection of scripts to log climate information in python and send them
to influxdb and graphana for plotting.

This script is purely python way to gather the most relevant metrics of the Raspberry Pi that
homeclimate is running one.
Deprecated in favor of a full TIG stack with system monitoring through telegraf.
"""

####################################################################################################
# Import modules
####################################################################################################

import time
import datetime
import os
import psutil
from influxdb import InfluxDBClient
import influxdb.exceptions as inexc


####################################################################################################
# Sensor Definition
####################################################################################################

sample_time = 30        # seconds
machine     = 'pi3'


####################################################################################################
# Initialize connection to influxdb
####################################################################################################

# if influxdb server is up and accessible
# TDB: test connection

client = InfluxDBClient(host='localhost', port=8086, username='root', password='root', database='homeclimate')


####################################################################################################
# Read data
####################################################################################################

def read_sensor():
    """
    Aquires several machine statistics of the localhost and formats them in a way that influxdb
    understands.
    """

    try:
        time = datetime.datetime.utcnow().isoformat()
        cpu_load = psutil.cpu_percent()
        cpu_freq = psutil.cpu_freq()[0]*1000
        cpu_temp = psutil.sensors_temperatures()['cpu-thermal'][0].current
        mem = psutil.virtual_memory()
        mem_load = mem.percent
        mem_used = mem.used

        if cpu_load==0.0:
            cpu_load = None
        if cpu_freq<0. or cpu_freq>2000.:
            cpu_freq = None
        if cpu_temp<0. or cpu_temp>120.:
            cpu_temp = None
        if mem_load<0. or mem_load>100.:
            mem_load = None

    except Exception:
        print(datetime.datetime.now(), "  Error reading system info. Passing dummy data.")
        time = datetime.datetime.utcnow().isoformat()
        cpu_load = None
        cpu_freq = None
        cpu_temp = None
        mem_load = None
        mem_used = None

    data = [{'measurement': 'system',
             'tags': {'machine': machine},
             'time': time,
             'fields': {'cpu_load': cpu_load, 'cpu_freq': cpu_freq, 'cpu_temp': cpu_temp, 'mem_load': mem_load, 'mem_used': mem_used}
            }]

    return data


####################################################################################################
# Send data to influxdb
####################################################################################################

def write_database(client, data):
    """
    Writes a given data record to the database and prints unexpected results. Successful writes are
    not printed to keep the logs simple.
    """

    try:
        iresponse  = client.write_points(data)
        if not iresponse:
            print("Sending data to database failed. Response: ", iresponse)
    except inexc.InfluxDBServerError:
        print(datetime.datetime.now(), "  Sending data to database failed due to timeout.")
        pass
    except Exception:
        print(datetime.datetime.now(), "  Encountered unknown error.")
        pass



####################################################################################################
# Continuously take data
####################################################################################################

try:
    while True:

        write_database(client = client,
                       data   = read_sensor()
                      )

        time.sleep(sample_time)

except KeyboardInterrupt:
    print (datetime.datetime.now(), "  Program stopped by keyboard interrupt [CTRL_C] by user. ")


####################################################################################################
