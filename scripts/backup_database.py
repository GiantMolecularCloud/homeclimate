"""
Home Climate Monitoring

author: GiantMolecularCloud

This script is part of a collection of scripts to log climate information in python and send them
to influxdb and graphana for plotting.

Manually back up the homeclimate directory to someothermachine. This simply copies over the current
version including all scripts, services and the influxdb that are all placed in the homeclimate
directory.
Development script! Database backups should be done through the appropriate influxdb functions to
e.g. export a JSON record of the database, instead of copying the hundreds of small files that make
up the database.
"""

####################################################################################################
# Import modules
####################################################################################################

import sys
import subprocess
import time
import datetime
from influxdb import InfluxDBClient
import influxdb.exceptions as inexc


####################################################################################################
# Initialize connection to influxdb
####################################################################################################

# if influxdb server is up and accessible
# TDB: test connection

client = InfluxDBClient(host='localhost', port=8086, username='root', password='root', database='homeclimate')


####################################################################################################
# Read data
####################################################################################################

def copy_data():
    """
    Backups data to another machine or raises exception if not successful.
    """

    result = subprocess.call('sudo rsync -rvzhc /home/pi/homeclimate/ -e "ssh -i /home/pi/.ssh/id_rsa" homeclimate@someothermachine:/volume1/data/homeclimate/ --progress', shell=True)

    time    = datetime.datetime.utcnow().isoformat()
    if result==0:
        success = "successful"
    else:
        print(datetime.datetime.now(), "  rsync to someothermachine failed.")
        success = "rsync failed"

    data = [{'measurement': 'backup',
             'tags': {'target': 'someothermachine'},
             'time': time,
             'fields': {'success': success}
            }]

    return success,data


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
        else:
            print("Backup successful.")
    except inexc.InfluxDBServerError:
        print(datetime.datetime.now(), "  Sending data to database failed due to timeout.")
        pass
    except Exception:
        print(datetime.datetime.now(), "  Encountered unknown error.")
        pass



####################################################################################################
# Try backup up to five times
####################################################################################################

for i in range(5):
    success, data = copy_data()
    write_database(client = client,
                   data   = data
                  )
    if success=='successful':
        sys.exit(0)
    else:
        print('try '+str(i)+': sleeping for 60, then try again')
        time.sleep(60)

sys.exit(1)

####################################################################################################
