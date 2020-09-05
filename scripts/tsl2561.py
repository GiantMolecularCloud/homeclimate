"""
Home Climate Monitoring

author: GiantMolecularCloud

This script is part of a collection of scripts to log climate information in python and send them
to influxdb and graphana for plotting.

Read data from a TSL2561 sensor and write them a local unsecured influxdb.
"""

####################################################################################################
# Import modules
####################################################################################################

import time
import datetime
import board
import busio
import adafruit_tsl2561
from influxdb import InfluxDBClient
import influxdb.exceptions as inexc


####################################################################################################
# Sensor Definition
####################################################################################################

i2c = busio.I2C(board.SCL, board.SDA)
tsl = adafruit_tsl2561.TSL2561(i2c)
sample_time = 30                        # seconds


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
        time      = datetime.datetime.utcnow().isoformat()
        lux       = tsl.lux
        broadband = tsl.broadband
        infrared  = tsl.infrared

    except Exception:
        print(datetime.datetime.now(), "  Error reading co2 monitor. Passing dummy data.")
        time = datetime.datetime.utcnow().isoformat()
        lux       = None
        broadband = None
        infrared  = None

    data = [{'measurement': 'live logging',
             'tags': {'room': 'living room', 'sensor': 'TSL2561'},
             'time': time,
             'fields': {'lux': lux, 'broadband': broadband, 'infrared': infrared}
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
