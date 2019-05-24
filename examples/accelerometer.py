#!/usr/bin/env python

import msa301
import time

accel = msa301.MSA301()
accel.set_power_mode('normal')
while 1:
    readings = accel.get_measurements()

    print(("{:+06.2f}g : {:+06.2f}g : {:+06.2f}g").format(*readings))
    time.sleep(0.2)
