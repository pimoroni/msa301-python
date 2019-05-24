#!/usr/bin/env python

import msa301
import time

print("""detect-axis-move.py - Detect movement and print delta.

Press Ctrl+C to exit.

""")

accel = msa301.MSA301()
accel.reset()
accel.set_power_mode('normal')
accel.enable_interrupt([
    'x_active_interrupt',
    'z_active_interrupt',
    'y_active_interrupt'
    ])

try:
    while True:
        first_x, first_y, first_z = accel.get_measurements()
        print('Move sensor to trigger axis move detect.')
        print (' {0} Detected '.format(
            accel.wait_for_interrupt(
                'active_interrupt')))

        last_x, last_y, last_z = accel.get_measurements()
        print('Movement delta : {:+06.2f}g : {:+06.2f}g : {:+06.2f}g\n'.format(
            first_x-last_x,
            first_y-last_y,
            first_z-last_z))

        time.sleep(0.5)

except KeyboardInterrupt:
    pass
