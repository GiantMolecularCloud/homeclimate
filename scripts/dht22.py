"""
Home Climate Monitoring

author: GiantMolecularCloud

This script is part of a collection of scripts to log climate information in python and send them
to influxdb and graphana for plotting.

Read data from a DHT22 sensor and write them a local unsecured influxdb.
"""

####################################################################################################
# Import modules
####################################################################################################

import time
import datetime
import Adafruit_DHT as dht
from influxdb import InfluxDBClient
import influxdb.exceptions as inexc


####################################################################################################
# Sensor Definition
####################################################################################################

pin         = 17
sensor      = dht.DHT22
sample_time = 30        # seconds


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
    Uses dht22 sensors to read the current temperature and humidity. The results are formated such
    that influxdb understands data.
    """

    try:
        time = datetime.datetime.utcnow().isoformat()
        humidity, temperature = dht.read_retry(sensor, pin)
        humidity    = int(round(humidity,0))
        temperature = round(temperature,2)
        if humidity<0 or humidity>100:
            humidity = None
        if temperature<-20 or temperature>40:
            temperature = None
    except Exception:
        print(datetime.datetime.now(), "  Error reading DHT22 at pin "+str(pin)+". Passing dummy data.")
        time = datetime.datetime.utcnow().isoformat()
        humidity    = None
        temperature = None

    data = [{'measurement': 'live logging',
             'tags': {'room': 'pin'+str(pin), 'sensor': 'DHT22'},
             'time': time,
             'fields': {'temperature': temperature, 'humidity': humidity}
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
