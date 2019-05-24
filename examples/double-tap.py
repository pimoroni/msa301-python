#!/usr/bin/env python

import msa301
import time

print("""double-tap.py - detect a double tap.

Double-tap firmly on or near the sensor.

Press Ctrl+C to exit.

""")

accel = msa301.MSA301()
accel.reset()
accel.set_power_mode('normal')
accel.enable_interrupt(['double_tap_interrupt'])

try:
    while True:
        print (' {0} Detected '.format(accel.wait_for_interrupt(
            'double_tap_interrupt', polling_delay=0.05)))
        time.sleep(0.5)

except KeyboardInterrupt:
    pass
