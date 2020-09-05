"""
Home Climate Monitoring

author: GiantMolecularCloud

This script is part of a collection of scripts to log climate information in python and send them
to influxdb and graphana for plotting.

Attach a physical button to a Raspberry Pi and shut the Pi down when the button is pressed for at
least one second.
"""

####################################################################################################
# Import modules
####################################################################################################

import os
import time
from gpiozero import Button


####################################################################################################
# Sensor Definition
####################################################################################################

pin        = 4
stopButton = Button(pin, hold_time=1.0)

def shutdown_raspi():
    print("Shutdown button pressed. Shutting down now.")
    os.system("shutdown now -h")

stopButton.when_held = shutdown_raspi


####################################################################################################
# monitor shutdown button
####################################################################################################

# dummy loop to keep script running and waiting for button press
# the shutdown is configured in stopButton.when_held and not in this loop
while True:
    stopButton.wait_for_press()



####################################################################################################
