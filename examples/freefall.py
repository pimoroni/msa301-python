#!/usr/bin/env python

import time

import msa301

print("""freefall.py - detect a freefall event.

Gently throw your sensor upwards and catch it.

Press Ctrl+C to exit.

""")

accel = msa301.MSA301()
accel.reset()
accel.set_power_mode('normal')
accel.enable_interrupt(['freefall_interrupt'])

try:
    while True:
        print (' {0} Detected '.format(accel.wait_for_interrupt(
            'freefall_interrupt', polling_delay=0.05)))
        time.sleep(0.5)

except KeyboardInterrupt:
    pass
