#!/usr/bin/env python

import msa301
import time

print("""accelerometer.py - read XYZ data
        
Press Ctrl+C to exit.

""")

accel = msa301.MSA301()
accel.set_power_mode('normal')

try:
    while True:
        readings = accel.get_measurements()

        print(("{:+06.2f}g : {:+06.2f}g : {:+06.2f}g").format(*readings))
        time.sleep(0.2)

except KeyboardInterrupt:
    pass
