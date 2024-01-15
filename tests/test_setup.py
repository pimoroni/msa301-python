from i2cdevice import MockSMBus


def test_setup():
    import msa301
    i2c_dev = MockSMBus(1, default_registers={0x11: 0b00000100})
    device = msa301.MSA301(i2c_dev=i2c_dev)

    device.reset()
    assert device.get_part_id() == 0x00
    device.set_power_mode('normal')
    device.set_range(2)
    device.set_resolution(14)
    device.disable_all_interrupts()

    device.enable_interrupt(['double_tap_interrupt', 'freefall_interrupt', 'y_active_interrupt', 'freefall_interrupt'])
    device.get_measurements()
    device.set_offsets(0.5, 0.5, 0.5)
    device.get_offsets()
    device.get_current_range_and_resolution()
    device.get_output_data_rate()
    device.get_interrupt()
    del device


def test_power_mode():
    import msa301
    i2c_dev = MockSMBus(1, default_registers={0x11: 0b00000100})
    device = msa301.MSA301(i2c_dev=i2c_dev)

    device.set_power_mode('low_power')
    assert i2c_dev.regs[0x11] == 0b01000100
    device.set_power_mode('suspend')
    assert i2c_dev.regs[0x11] == 0b10000100
    device.set_power_mode('normal')
    assert device.get_power_mode() == 'normal'
    del device
