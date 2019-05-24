#!/usr/bin/env python

import msa301
import time

accel = msa301.MSA301()
accel.reset()
accel.set_power_mode('normal')
accel.enable_interrupt(['freefall_interrupt'])

while 1:
    print('Gently throw sensor upwards and catch it')
    print('Ctrl + c when you are done')
    print (' {0} Detected '.format(accel.wait_for_interrupt(
        'freefall_interrupt', polling_delay=0.05)))
    time.sleep(0.5)
