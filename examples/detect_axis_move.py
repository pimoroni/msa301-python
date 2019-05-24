#!/usr/bin/env python

import msa301
import time

accel = msa301.MSA301()
accel.reset()
accel.set_power_mode('normal')
accel.enable_interrupt([
    'x_active_interrupt',
    'z_active_interrupt',
    'y_active_interrupt'
    ])
while 1:
    first_x, first_y, first_z = accel.get_measurements()
    print('Move sensor to trigger axis move detect. Ctrl+c to exit')
    print (' {0} Detected '.format(
        accel.wait_for_interrupt(
            'active_interrupt')))

    last_x, last_y, last_z = accel.get_measurements()
    print('Movement delta : {:+06.2f}g : {:+06.2f}g : {:+06.2f}g '.
          format(first_x-last_x, first_y-last_y, first_z-last_z))

    time.sleep(0.5)
