"""
Home Climate Monitoring

author: GiantMolecularCloud

This script is part of a collection of scripts to log climate information in python and send them
to influxdb and graphana for plotting.

Read data from a USB CO2 monitor and write them a local unsecured influxdb.
Requires https://github.com/vfilimonov/co2meter to be installed.
"""

####################################################################################################
# Import modules
####################################################################################################

import time
import datetime
import co2meter as co2
from influxdb import InfluxDBClient
import influxdb.exceptions as inexc


####################################################################################################
# Sensor Definition
####################################################################################################

sample_time = 30        # seconds


####################################################################################################
# Set up co2monitor
####################################################################################################

mon = co2.CO2monitor()


####################################################################################################
# Initialize connection to influxdb
####################################################################################################

# if influxdb server is up and accessible
# TDB: test connection

client = InfluxDBClient(host='localhost', port=8086, username='root', password='root', database='homeclimate')


####################################################################################################
# Read data
####################################################################################################

def read_monitor():
    """
    Uses co2monitor to read the current temperature and co2 level. The results are formated such
    that influxdb understands data.
    """

    try:
        time, co2, temperature = mon.read_data()
        time        = time.utcnow().isoformat()
        temperature = round(temperature,2)
    except Exception:
        print(datetime.datetime.now(), "  Error reading co2 monitor. Passing dummy data.")
        time = datetime.datetime.utcnow().isoformat()
        co2  = None
        temperature = None

    data = [{'measurement': 'live logging',
             'tags': {'room': 'living room', 'sensor': 'USB CO2 monitor'},
             'time': time,
             'fields': {'temperature': temperature, 'co2': co2}
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
                       data   = read_monitor()
                      )

        time.sleep(sample_time)

except KeyboardInterrupt:
    print (datetime.datetime.now(), "  Program stopped by keyboard interrupt [CTRL_C] by user. ")


####################################################################################################
