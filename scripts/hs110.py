"""
Home Climate Monitoring

author: GiantMolecularCloud

This script is part of a collection of scripts to log climate information in python and send them
to influxdb and graphana for plotting.

Read data from a TP-Link HS110 smart plug and write them to a remote influxdb database.
"""

####################################################################################################
# Import modules
####################################################################################################

import time
import datetime
from influxdb import InfluxDBClient
import influxdb.exceptions as inexc


####################################################################################################
# Sensor Definition
####################################################################################################

ip   = '0.0.0.0'        # change to IP of your smart plug
port = 9999             # default port for HS110
sample_time = 30        # seconds


####################################################################################################
# Initialize connection to influxdb
####################################################################################################

# if influxdb server is up and accessible
# TDB: test connection

client = InfluxDBClient(host='0.0.0.0', port=8086, username='root', password='root', database='telegraf')


####################################################################################################
# Read data
####################################################################################################

def encrypt(string):
    """
    Encrypt the TP-Link Smart Home Protocoll: XOR Autokey Cipher with starting key = 171
    This follows: https://github.com/softScheck/tplink-smartplug
    """
    from struct import pack
    key = 171
    result = pack('>I', len(string))
    for i in string:
        a = key ^ ord(i)
        key = a
        result += bytes([a])
    return result

def decrypt(string):
    """
    Decrypt the TP-Link Smart Home Protocoll: XOR Autokey Cipher with starting key = 171
    This follows: https://github.com/softScheck/tplink-smartplug
    """
    key = 171
    result = ""
    for i in string:
        a = key ^ i
        key = i
        result += chr(a)
    return result

def poll_HS110(ip,port):
    """
    connect to HS110, send payload and receive power data
    """
    import socket
    try:
        sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_tcp.settimeout(int(10))
        sock_tcp.connect((ip, port))
        sock_tcp.settimeout(None)
        sock_tcp.send(encrypt('{"emeter":{"get_realtime":{}}}'))
        data = sock_tcp.recv(2048)
        sock_tcp.close()
        return data
    except:
        raise ConnectionError("Could not connect to HS110 at IP "+str(ip)+" on port "+str(port))

def decrypt_power(data):
    """
    decrypt power data and convert to Volts, Ampere, Watt, kWh
    """
    import json
    try:
        decrypted = decrypt(data[4:])
        decrypt_dict = json.loads(decrypted)
        return {'voltage':      decrypt_dict['emeter']['get_realtime']['voltage_mv']/1000,    # V
                'current':      decrypt_dict['emeter']['get_realtime']['current_ma']/1000,    # A
                'power':        decrypt_dict['emeter']['get_realtime']['power_mw']/1000,      # W
                'energy_total': decrypt_dict['emeter']['get_realtime']['total_wh']/1000,      # kWh
                'error_code':   decrypt_dict['emeter']['get_realtime']['err_code']
               }
    except:
        raise TypeError("Could not decrypt returned data.")

def read_sensor():
    """
    Uses dht22 sensors to read the current temperature and humidity. The results are formated such
    that influxdb understands data.
    """
    polltime = datetime.datetime.utcnow().isoformat()
    try:
        data = poll_HS110(ip, port)
        data = decrypt_power(data)
    except ConnectionError:
        print(polltime, "  Error contacting HS110. Passing dummy data.")
        voltage, current, power, energy_total = None, None, None, None
        error_code = 9999
    except TypeError:
        print(polltime, "  Error decrypting data. Passing dummy data.")
        voltage, current, power, energy_total = None, None, None, None
        error_code = 9999
    except Exception:
        print(polltime, "  Unknown error. Passing dummy data.")
        voltage, current, power, energy_total = None, None, None, None
        error_code = 9999                                                           # I assume such a high error code 9999 is not used by TP-Link, so I highjack this metric.

    return [{'measurement': 'power',
             'tags': {'sensor': 'HS110'},
             'time': polltime,
             'fields': data
            }]


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
