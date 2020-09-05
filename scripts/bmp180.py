"""
Home Climate Monitoring

author: GiantMolecularCloud

This script is part of a collection of scripts to log climate information in python and send them
to influxdb and graphana for plotting.

Read data from a BMP085 sensor and write them a local unsecured influxdb.
"""

####################################################################################################
# Import modules
####################################################################################################

import time
import datetime
import Adafruit_BMP.BMP085 as BMP085
from influxdb import InfluxDBClient
import influxdb.exceptions as inexc


####################################################################################################
# Sensor Definition
####################################################################################################

bmp         = BMP085.BMP085()
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
    Uses BMP180 sensors to read the current temperature and humidity. The results are formated such
    that influxdb understands data.
    """

    try:
        time = datetime.datetime.utcnow().isoformat()

        temperature = bmp.read_temperature()
        pressure    = bmp.read_pressure()/100        # Pa -> hPa
        # altitude    = bmp.read_altitude()

        temperature = round(temperature,2)
        pressure    = int(round(pressure,0))
        if pressure<900 or pressure>1100:
            humidity = None
        if temperature<-20 or temperature>40:
            temperature = None
    except Exception:
        print(datetime.datetime.now(), "  Error reading BMP180 over I2C. Passing dummy data.")
        time = datetime.datetime.utcnow().isoformat()
        humidity    = None
        temperature = None

    data = [{'measurement': 'live logging',
             'tags': {'room': 'outdoor', 'sensor': 'BMP180'},
             'time': time,
             'fields': {'temperature': temperature, 'pressure': pressure}
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
