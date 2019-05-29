import sys
from i2cdevice import MockSMBus
import mock


def test_setup():
    sys.modules['smbus'] = mock.Mock()
    sys.modules['smbus'].SMBus = MockSMBus
    import msa301
    device = msa301.MSA301()

    device.reset()
    print(hex(device.get_part_id()))
    device.set_power_mode('normal')
    device.set_range(2)
    device.set_resolution(14)
    device.disable_all_interrupts()
    device.set_power_mode('normal')
    device.enable_interrupt(['double_tap_interrupt', 'freefall_interrupt', 'y_active_interrupt', 'freefall_interrupt'])
    device.get_measurements()
    device.set_offsets(0.5, 0.5, 0.5)
    device.get_offsets()
    device.get_current_range_and_resolution()
    device.get_output_data_rate()
    device.get_interrupt()
    del device
