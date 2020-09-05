"""
Home Climate Monitoring

author: GiantMolecularCloud

This script is part of a collection of scripts to log climate information in python and send them
to influxdb and graphana for plotting.

Development script to gather data from influxdb and analysize them statistically. This script does
the work of getting data, treating them and finally plotting.
This code uses hourly averages created by influxdb. Requires setting up a CONTINOUS QUERY
(https://docs.influxdata.com/influxdb/v1.8/guides/downsample_and_retain/) to not overwhelm the system
with the precision of thousands of records from every 30 seconds.
"""

####################################################################################################
# Import modules
####################################################################################################

import os
from datetime import datetime
import pickle
import numpy as np
from influxdb import InfluxDBClient
import influxdb.exceptions as inexc
import matplotlib.pyplot as plt

import sys
sys.path.append('/home/pi/homeclimate/scripts/')
from homeclimate_statistics import plot_hist2d



####################################################################################################
# STATISTICS CLASS # STATISTICS CLASS # STATISTICS CLASS # STATISTICS CLASS # STATISTICS CLASS #
####################################################################################################

class homeclimate_statistics:

    def __init__():
        self.client = None
        self.colors = {'temperature': 'crimson',
                       'CO2':         'darkorange',
                       'brightness':  'seagreen',
                       'humidity':    'dodgerblue',
                       'pressure':    'darkmagenta'
                      }
        self.hsetup = {'temperature': {'min': 15,  'max': 35,   'step': 0.5, 'label': 'temperature [C]'},
                       'CO2':         {'min': 300, 'max': 2500, 'step': 25,  'label': 'CO2 concentration [ppm]'},
                       'brightness':  {'min': 0.1, 'max': 1000, 'step': 10,  'label': 'brightness [lux]'},
                       'humidity':    {'min': 0,   'max': 100,  'step': 5,   'label': 'humidity [%]'},
                       'pressure':    {'min': 980, 'max': 1030, 'step': 1,   'label': 'pressure [hPa]'}
                      }
        self.ranges = {'total': {'range': '1000d', 'alpha': 1.00},
                       'month': {'range': '30d',   'alpha': 0.75},
                       'week':  {'range': '7d',    'alpha': 0.50},
                       'day':   {'range': '1d',    'alpha': 0.25},
                      }
        print("Initializing statistics plotting ...")

    def connect_influx():
        self.client = InfluxDBClient(host='localhost', port=8086, username='root', password='root', database='homeclimate_hourly')

    def get_values(time_range):
        results = client.query('SELECT * FROM "live logging" WHERE time > now() - '+time_range)
        USBmonitor = list(results.get_points('live logging', tags={'room':'living room', 'sensor':'USB CO2 monitor'}))
        TSL2561    = list(results.get_points('live logging', tags={'room':'living room', 'sensor':'TSL2561'}))
        DHT22      = list(results.get_points('live logging', tags={'room':'pin17',       'sensor':'DHT22'}))
        BMP180     = list(results.get_points('live logging', tags={'room':'outdoor',     'sensor':'BMP180'}))
        values = {'CO2':         [x['mean_co2'] for x in USBmonitor if not x['mean_co2']==None],
                  'temperature': [x['mean_temperature'] for x in USBmonitor if not x['mean_temperature']==None],
                  'brightness':  [x['mean_lux'] for x in TSL2561 if not x['mean_lux']==None],
                  'humidity':    [x['mean_humidity'] for x in DHT22 if not x['mean_humidity']==None],
                  'pressure':    [x['mean_pressure'] for x in BMP180 if not x['mean_pressure']==None]}
        return time_range, values



####################################################################################################
# connect to influxdb
####################################################################################################

# connect to influxdb
client = InfluxDBClient(host='localhost', port=8086, username='root', password='root', database='homeclimate_hourly')



####################################################################################################
# HISTOGRAM PLOTTING # HISTOGRAM PLOTTING # HISTOGRAM PLOTTING # HISTOGRAM PLOTTING #
####################################################################################################


####################################################################################################
# define influxdb and data functions
####################################################################################################

def get_values(time_range):
    results = client.query('SELECT * FROM "live logging" WHERE time > now() - '+time_range)
    USBmonitor = list(results.get_points('live logging', tags={'room':'living room', 'sensor':'USB CO2 monitor'}))
    TSL2561    = list(results.get_points('live logging', tags={'room':'living room', 'sensor':'TSL2561'}))
    DHT22      = list(results.get_points('live logging', tags={'room':'pin17',       'sensor':'DHT22'}))
    BMP180     = list(results.get_points('live logging', tags={'room':'outdoor',     'sensor':'BMP180'}))
    values = {'CO2':         [x['mean_co2'] for x in USBmonitor if not x['mean_co2']==None],
              'temperature': [x['mean_temperature'] for x in USBmonitor if not x['mean_temperature']==None],
              'brightness':  [x['mean_lux'] for x in TSL2561 if not x['mean_lux']==None],
              'humidity':    [x['mean_humidity'] for x in DHT22 if not x['mean_humidity']==None],
              'pressure':    [x['mean_pressure'] for x in BMP180 if not x['mean_pressure']==None]}
    return time_range, values


####################################################################################################
# plot histograms
####################################################################################################

# colors setup
colors = {'temperature': 'crimson',
          'CO2':         'darkorange',
          'brightness':  'seagreen',
          'humidity':    'dodgerblue',
          'pressure':    'darkmagenta'
         }

# histogram setup
hsetup = {'temperature': {'min': 15,  'max': 35,   'step': 0.5, 'label': 'temperature [C]'},
          'CO2':         {'min': 300, 'max': 2500, 'step': 25,  'label': 'CO2 concentration [ppm]'},
          'brightness':  {'min': 0.1, 'max': 1000, 'step': 10,  'label': 'brightness [lux]'},
          'humidity':    {'min': 0,   'max': 100,  'step': 5,   'label': 'humidity [%]'},
          'pressure':    {'min': 980, 'max': 1030, 'step': 1,   'label': 'pressure [hPa]'}
         }
ranges = {'total': {'range': '1000d', 'alpha': 1.00},
          'month': {'range': '30d',   'alpha': 0.75},
          'week':  {'range': '7d',    'alpha': 0.50},
          'day':   {'range': '1d',    'alpha': 0.25},
         }

# query influxdb and get measurements
values = {r: get_values(v['range']) for r,v in ranges.items()}

# histgram data
bins = {k: np.arange(v['min'],v['max']+v['step'],v['step']) for k,v in hsetup.items()}
histograms   = {k: {r: {'histogram': None, 'edges': None} for r in ranges.keys()} for k in hsetup.keys()}
histograms2D = {'temperature CO2':      {'x': 'temperature', 'y': 'CO2',      'histogram': None, 'xedges': None, 'yedges': None},
                'temperature humidity': {'x': 'temperature', 'y': 'humidity', 'histogram': None, 'xedges': None, 'yedges': None}
               }

# calculate histograms
for k,v in histograms.items():
    for r in v.keys():
        histograms[k][r]['histogram'], histograms[k][r]['edges'] = np.histogram(values[r][k], bins=bins[k])

# calculate 2D histograms
for k,v in histograms2D.items():
    histograms2D[k]['histogram'], histograms2D[k]['xedges'], histograms2D[k]['yedges'] = np.histogram2d(values['total'][v['x']], values['total'][v['y']], bins=[bins[v['x']],bins[v['y']]])

# plot 2D histogram
plot_hist2d('temperature','CO2')
plot_hist2d('temperature','humidity')








####################################################################################################
# HOUR STATS PLOTTING # HOUR STATS PLOTTING # HOUR STATS PLOTTING # HOUR STATS PLOTTING #
####################################################################################################


####################################################################################################
# load old statistics or initialize new statistics
####################################################################################################

# mean value per hour of the day
try:
    hour_mean = pickle.load(open('/home/pi/homeclimate/statistics/hour_mean.pickle', 'rb'))
except:
    hour_mean = {'hour':        list(range(24)),
                 'temperature': [{'#': 0, 'mean': 0} for i in range(24)],
                 'co2':         [{'#': 0, 'mean': 0} for i in range(24)],
                 'pressure':    [{'#': 0, 'mean': 0} for i in range(24)],
                 'brightness':  [{'#': 0, 'mean': 0} for i in range(24)],
                 'humidity':    [{'#': 0, 'mean': 0} for i in range(24)]}


####################################################################################################
# load new data
####################################################################################################

# check when program last ran
    # write either log or timestamp file
    # parse through datetime if necessary

# load new time series data since last statistics run
results = client.query('SELECT * FROM "live logging" WHERE time > now() - 1d')
USBmonitor = list(results.get_points('live logging', tags={'room':'living room', 'sensor':'USB CO2 monitor'}))
TSL2561    = list(results.get_points('live logging', tags={'room':'living room', 'sensor':'TSL2561'}))
DHT22      = list(results.get_points('live logging', tags={'room':'pin17',       'sensor':'DHT22'}))
BMP180     = list(results.get_points('live logging', tags={'room':'outdoor',     'sensor':'BMP180'}))

# bring new data into readable format
quantities = {'co2':         [[x['time'],x['mean_co2']] for x in USBmonitor],
              'temperature': [[x['time'],x['mean_temperature']] for x in USBmonitor],
              'brightness':  [[x['time'],x['mean_lux']] for x in TSL2561],
              'humidity':    [[x['time'],x['mean_humidity']] for x in DHT22],
              'pressure':    [[x['time'],x['mean_pressure']] for x in BMP180]}


####################################################################################################
# update statistics with new data
####################################################################################################

# mean value per hour of the day
for key,quantity in quantities.items():
    for time,value in quantity:
        hour  = datetime.strptime(time, '%Y-%m-%dT%H:%M:%SZ').hour
        hour_mean[key][hour]['#']    += 1
        hour_mean[key][hour]['mean'] += value/hour_mean[key][hour]['#']


####################################################################################################
# save updated statistics
####################################################################################################

if not os.path.exists('/home/pi/homeclimate/statistics/'):
    os.system('mkdir /home/pi/homeclimate/statistics/')

pickle.dump(hour_mean, open('/home/pi/homeclimate/statistics/hour_mean.pickle', 'wb'))


####################################################################################################
# render statistics plot to show on homepage
####################################################################################################

# mean value per hour of the day
fig = plt.figure(figsize=(4,4))
ax1 = fig.subplots(1)
ax2 = ax1.twinx()

ax1.plot([x+0.5 for x in hour_mean['hour']],
        [x['mean'] for x in hour_mean['co2']],
        ls='-', lw=2, c='orange')
ax2.plot([x+0.5 for x in hour_mean['hour']],
        [x['mean'] for x in hour_mean['temperature']],
        ls='-', lw=2, c='red')

ax1.set_xlim([0,24])
ax2.set_xlim([0,24])
ax1.set_ylim([300,2500])
ax2.set_ylim([20,32])
ax1.set_xlabel('hour of the day')
ax1.set_ylabel('mean CO2 concentration')
ax2.set_ylabel('mean temperature')
fig.savefig('/home/pi/homeclimate/statistics/hour_mean.pdf', dpi=300, bbox_inches='tight')


# 2D hist plus overlays: time - temperature/co2/humidity/brightness/pressure
fig,axes = plt.subplots(nrows=5, ncols=1, squeeze=True, sharex='col', sharey='row', figsize=(10,6))

for ax,(key,quantity) in zip(axes, quantities.items()):
    ax.plot
    # background hist 2D
    # total/month/week/day mean

for ax in axes:
    ax.set_xlim(0,24)
    ax.set_axisbelow(True)
    ax.grid(axis='y')
    ax.set_xticks(np.arange(1,25))
for ax,[llim,ulim,label] in zip(axes, [[20,32,'temperature [C]'],[300,2500,'CO2 [ppm]'],[0,100,'humidity [%]'],[0.1,1000,'brightness [lux]'],[980,1030,'pressure [hPa]']]):
    ax.set_ylim(llim,ulim)
    ax.set_ylabel(label)
axes[3].set_yscale('log')
fig.tight_layout()
fig.savefig('/home/pi/homeclimate/statistics/time_stats.pdf', dpi=300, bbox_inches='tight')




####################################################################################################
# DEBUG CODE # DEBUG CODE # DEBUG CODE # DEBUG CODE # DEBUG CODE # DEBUG CODE # DEBUG CODE # DEBUG
####################################################################################################
# DEBUG CODE # DEBUG CODE # DEBUG CODE # DEBUG CODE # DEBUG CODE # DEBUG CODE # DEBUG CODE # DEBUG
####################################################################################################

# # list influxdb databases
# client.get_list_database()

# # list measurements
# client.get_list_measurements()
