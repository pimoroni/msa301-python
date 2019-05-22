import time
import math
from i2cdevice import Device, Register, BitField
from i2cdevice.adapter import Adapter, LookupAdapter, U16ByteSwapAdapter


class SensorDataAdapter(Adapter):

    def __init__(self , bit_resolution = 14):

        self.bit_resolution = bit_resolution


    def _encode(self, value):
        return value



    def _decode(self, value):
        LSB = (value & 0xFF00) >> 10
        MSB = (value & 0x00FF) << 6
        #print (bin(MSB),bin(LSB))
        return MSB + LSB     
        

class InteruptLookupAdapter(Adapter):
    """Special version of the look up adapter that allows for multipule values to be set at once
    """
    def __init__(self, lookup_table):
        self.lookup_table = lookup_table
      

    def _decode(self, value):
        index = list(self.lookup_table.values()).index(value)
        return list(self.lookup_table.keys())[index]

    def _encode(self, value):

        return self.lookup_table[value]



class MSA301:
    def __init__(self, i2c_addr=0x26, i2c_dev=None):
        self._i2c_addr = i2c_addr
        self._i2c_dev = i2c_dev
        self._is_setup = False
        # Device definition
        self._msa301 = Device([0x26], i2c_dev=self._i2c_dev, bit_width=8, registers=(
            Register('SOFT_RESET', 0x00, fields=(
                BitField('soft_reset',  0b00100000),
                BitField('seft_reset_alt', 0b00000100)
            )),

            Register('PARTID', 0x01, fields=([BitField('id', 0xFF)])),
                





            Register('ACCEL_X', 0x02, fields=(
                [BitField('reading',   0xFFFF, adapter=SensorDataAdapter(bit_resolution))]), bit_width=16, read_only=True),
            
            Register('ACCEL_Y', 0x04, fields=(
                [BitField('reading',   0xFFFF, adapter=SensorDataAdapter())]), bit_width=16, read_only=True),

            Register('ACCEL_Z', 0x06, fields=(
                [BitField('reading',   0xFFFF, adapter=SensorDataAdapter())]), bit_width=16, read_only=True),

            Register('MOTION_INTERUPT', 0x09, fields=(
                BitField('orientation_interrupt',  0b01000000, read_only=True),
                BitField('single_tap_interrupt',   0b00100000, read_only=True),
                BitField('double_tap_interrupt',   0b00010000, read_only=True),
                BitField('active_interrupt',       0b00000100, read_only=True),
                BitField('freefall_interrupt',     0b00000001, read_only=True)
                )),

            Register('DATA_INTERUPT', 0x0A, fields=(
                [BitField('new_data_interrupt', 0b00000001, read_only=True)])),

            Register('TAP_ACTIVE_STATUS', 0x0B, fields=(
                BitField('tap_sign',           0b10000000, read_only=True),             
                BitField('tap_triggered_x',    0b01000000, read_only=True),
                BitField('tap_triggered_y',    0b00100000, read_only=True),
                BitField('tap_triggered_z',    0b00010000, read_only=True),
                BitField('active_sign',        0b00001000, read_only=True),
                BitField('active_triggered_x', 0b00000100, read_only=True),
                BitField('active_triggered_y', 0b00000010, read_only=True),
                BitField('active_triggered_z', 0b00000001, read_only=True)
                )),

            Register('ORIENTATION_STATUS', 0x0C, fields=(
                BitField('z_orientation',   0b10000000, read_only=True),
                BitField('x_y_orientation', 0b01100000, read_only=True, adapter=LookupAdapter(
                    {
                    'portrait_upright':    0b00, 
                    'portrait_upsidedown': 0b01, 
                    'landscape_left':      0b10, 
                    'landscape_right':     0b11
                    }))
            )),

            Register('RESOLUTION_RANGE', 0x0F, fields=(
                BitField('resolution', 0b00001100, adapter=LookupAdapter(
                    {
                    14: 0b00, 
                    12: 0b01, 
                    10: 0b10, 
                    8:  0b11
                    },snap = False)),
                BitField('range', 0b00000011,  adapter=LookupAdapter(
                    {
                    2:  0b00, 
                    4:  0b01, 
                    8:  0b10, 
                    16: 0b11
                    },snap = False))

            )),

            Register('DISABLE_AXIS_ODR', 0x10, fields=(
                BitField('disable_x_axis',   0b10000000),
                BitField('disable_y_axis',   0b01000000),
                BitField('disable_z_axis',   0b00100000),
                BitField('output_data_rate', 0b00001111,  adapter=LookupAdapter(
                    {
                    '1Hz':    0b0000,   #Not Available in Normal Mode 
                    '1.95Hz': 0b0001,   #Not Available in Normal Mode
                    '3.9Hz':  0b0010,
                    '7.81Hz': 0b0011, 
                    '15.63Hz': 0b0100, 
                    '31.25Hz': 0b0101, 
                    '62.5Hz': 0b0110, 
                    '125Hz':  0b0111,
                    '250Hz':  0b1000,
                    '500Hz':  0b1001,   #Not Available in Low Power Mode 
                    '1000Hz': 0b1010    #Not Available in Low Power Mode 
                    }))
            )),

            Register('POWER_MODE_BANDWIDTH', 0x11, fields=(
                BitField('power_mode', 0b11000000,  adapter=LookupAdapter(
                    {
                    'normal':    0b00,  
                    'low_power': 0b01,  
                    'suspend':   0b10   
                    })),
                BitField('low_power_bandwidth', 0b00011110,  adapter=LookupAdapter(
                    {'1.95Hz': 0b0010,
                    '3.9Hz':  0b0011,
                    '7.81Hz': 0b0100, 
                    '15.63Hz': 0b0101, 
                    '31.25Hz': 0b0110, 
                    '62.5Hz': 0b0111, 
                    '125Hz':  0b1000,
                    '250Hz':  0b1001,
                    '500Hz':  0b1010
                    }))
            )),

            Register('SWAP_POLARITY', 0x12, fields=(
                BitField('x_polariy', 0b00001000),
                BitField('y_polariy', 0b00000100),
                BitField('z_polariy', 0b00000010),
                BitField('x_z_swap',  0b00000001)
                )),

            Register('INTERUPT_ENABLE_0', 0x16, fields=(
            	BitField('interupt',  0xFF, adapter=LookupAdapter({
                	'orientation_interrupt':0b01000000,              
                	'single_tap_interrupt': 0b00100000,
                	'double_tap_interrupt': 0b00010000,
                	'z_active_interupt':    0b00000100,
                	'y_active_interupt':    0b00000010,
                	'x_active_interupt':    0b00000001
                }))
            )),

            Register('INTERUPT_ENABLE_1', 0x17, fields=(
				BitField('interrupt', 0xFF, adapter=LookupAdapter({
					'data_interrupt':     0b00010000,
					'freefall_interrupt': 0b00001000
					}))
                )),

            Register('INT1_MAPPING_0', 0x19, fields=(
                BitField('map_orientation_int1', 0b01000000),               
                BitField('map_single_tap_int1',  0b00100000),
                BitField('map_double_tap_int1',  0b00010000),
                BitField('map_active_int1',      0b00000100),
                BitField('map_freefall_int1',    0b00000001)
                )),

            Register('INT1_MAPPING_1', 0x1A, fields=(
                [BitField('map_new_data_int1',    0b00000001)]
                )),

            Register('INT1_OUTPUT_MODE', 0x20, fields=(
                BitField('mode', 0b00000010,  adapter=LookupAdapter(
                    {
                    'push_pull':  0b0,  
                    'open_drain': 0b1   
                    })),
                BitField('active_level', 0b00000010,  adapter=LookupAdapter(
                    {
                    'low':  0b0,    
                    'high': 0b1 
                    })),

             )),

            Register('INT1_LATCH', 0x21, fields=(
                BitField('latch_reset',      0b10000000),
                BitField('latch_setting', 0b00001111,  adapter=LookupAdapter(
                    {
                    'non_latched':      0b0000,     
                    'temp_latch_250ms': 0b0001,     
                    'temp_latch_500ms': 0b0010,
                    'temp_latch_1s':    0b0011, 
                    'temp_latch_2s':    0b0100, 
                    'temp_latch_4s':    0b0101, 
                    'temp_latch_8s':    0b0110, 
                    'latched':          0b0111,
                    'non_latched':      0b1000,
                    'temp_latch_1ms':   0b1001, 
                    'temp_latch_1ms':   0b1010,
                    'temp_latch_2ms':   0b1011, 
                    'temp_latch_25ms':  0b1100, 
                    'temp_latch_50ms':  0b1101,
                    'temp_latch_100ms': 0b1110,         
                    'latched':          0b1111  
                    }))
            )),

            Register('FREEFALL_DURATION', 0x22, fields=(
                [BitField('duration', 0xFF)]

            )),

            Register('FREEFALL_THRESHOLD', 0x23, fields=(
                [BitField('threshold', 0xFF)]  
            )),

            Register('FREEFALL_HYSTERESIS', 0x24, fields=(
                BitField('mode', 0x00000100, adapter=LookupAdapter(
                    {
                    'single': 0b0,  
                    'sum':    0b1
                    })),
                BitField('hysteresis_time',    0b00000011) 
            )),

            Register('ACTIVE_DURATION', 0x27, fields=(
                [BitField('duration',    0b00000011)] 
            )),



            Register('ACTIVE_THRESHOLD', 0x21, fields=(
                [BitField('threshold', 0xFF)]
            )),

            Register('TAP_DURATION', 0x28, fields=(
                BitField('tap_quiet', 0x10000000, adapter=LookupAdapter(
                    {
                    '30ms': 0b0,
                    '20ms': 0b1
                    })),
                BitField('tap_shock', 0x01000000, adapter=LookupAdapter(
                    {
                    '50ms': 0b0,    
                    '70ms': 0b1
                    })),
                BitField('double_tap_window', 0b00000111,  adapter=LookupAdapter(
                    {
                    '50ms':  0b000,
                    '100ms': 0b001,
                    '150ms': 0b010,
                    '200ms': 0b011, 
                    '250ms': 0b100, 
                    '375ms': 0b101, 
                    '500ms': 0b110, 
                    '700ms': 0b111
                    }))
            )),

            Register('TAP_THRESHOLD', 0x2B, fields=(
                [BitField('threshold', 0b00011111)]
            )),

            Register('ORIENTATION_HYSTERESIS', 0x2C, fields=(
                BitField('hysteresis', 0b01110000), #set the hysteresis of the orientation interrupt, 1LSB is 62.5mg
                BitField('orientation_blocking', 0b00001100,  adapter=LookupAdapter(
                    {
                    'non_blocking':                   0b00, 
                    'z_axis_blocking':                0b01, 
                    'z_axis_any_0.2_slope_blocking':  0b10, 
                    'non_blocking':                   0b11
                    })),
                BitField('orientation_mode', 0b00000011,  adapter=LookupAdapter(
                    {
                    'symmetrical':       0b00, 
                    'high_asymmetrical': 0b01, 
                    'low_asymmetrical':  0b10, 
                    'symmetrical':       0b11
                    }))


            )),

            Register('Z_BLOCK', 0x2D, fields=(
                BitField('setting', 0b00001111), #defines the block acc_z between 0g to 0.9375g
            )),

            Register('X_OFFSET', 0x38, fields=(
                [BitField('offset', 0xFF)] #the offset compensation value for X axis, 1LSB is 3.9mg
            )),

            Register('Y_OFFSET', 0x39, fields=(
                [BitField('offset', 0xFF)] #the offset compensation value for Y axis, 1LSB is 3.9mg
            )),

            Register('Z_OFFSET', 0x3A, fields=(
                [BitField('offset', 0xFF)] #the offset compensation value for Z axis, 1LSB is 3.9mg
            ))
            ))
        self._resolution = self._msa301.RESOLUTION_RANGE.get_resolution()
        self._range = self._msa301.RESOLUTION_RANGE.get_range()

        print( "Sensor initialized with reading range of {0} and resolution of {1}".format(self._range, self._resolution))


            


    def twos_comp_conversion(self, val, bits):
        if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)        # compute negative value
        return val    

    
    

    def reset(self):
        self._msa301.SOFT_RESET.set_soft_reset(True)
        time.sleep(0.01)

    def get_part_id(self):
        return self._msa301.PARTID.get_id()

    def set_range(self, range):
        valid_ranges = [2, 4, 8, 16]
        if (range in valid_ranges):
            self._range = range 
            self._msa301.RESOLUTION_RANGE.set_range(range)
        else:
            print('Invalid range value ', range)

    def set_resolution(self, resolution):
        valid_resolutions = [14 , 12 , 10 ,8]
        if (resolution in valid_resolutions):
            self._resolution = resolution
            self._msa301.RESOLUTION_RANGE.set_resolution(resolution)
        else:
            print('Invalid resolution Value  ', resolution)




    def get_current_range_and_resolution(self):
        return self._range , self._resolution

    def set_output_data_rate(self, rate):
        self._msa301.DISABLE_AXIS_ODR.set_output_data_rate(rate)

    def get_output_data_rate(self):
        return self._msa301.DISABLE_AXIS_ODR.get_output_data_rate()

    def get_power_mode(self):
        return self._msa301.POWER_MODE_BANDWIDTH.get_power_mode()

    def set_power_mode(self, mode):
        self._msa301.POWER_MODE_BANDWIDTH.set_power_mode(mode)

    def get_interupt(self):
    	return None

    def set_interupt(self, interrupts):
    	if interrupts is tuple:

    	for interrupt in interupts:
    		if(interupt != 'data_interrupt' or 'freefall_interrupt'):
    			self._msa301.INTERUPT_ENABLE_1.set_interrupt(interupt)

    		elif(interupt):

    




    def get_raw_measurements(self):


        x = self.twos_comp_conversion(self._msa301.ACCEL_X.get_reading(), self._resolution)
        y = self.twos_comp_conversion(self._msa301.ACCEL_Y.get_reading(), self._resolution)
        z = self.twos_comp_conversion(self._msa301.ACCEL_Z.get_reading(), self._resolution)

        return x , y , z

    def get_measurements(self):

        x = 0.0
        y = 0.0
        z = 0.0
        range = 0.0
        range =+ self._range

        x = float(self.twos_comp_conversion(self._msa301.ACCEL_X.get_reading(), self._resolution))  * (self._range / float(math.pow( 2 , (self._resolution - 1)))) 
        y = float(self.twos_comp_conversion(self._msa301.ACCEL_Y.get_reading(), self._resolution))  * (self._range / float(math.pow( 2 , (self._resolution - 1)))) 
        z = float(self.twos_comp_conversion(self._msa301.ACCEL_Z.get_reading(), self._resolution))  * (self._range / float(math.pow( 2 , (self._resolution - 1)))) 

        return x, y, z






if __name__ == "__main__":
    import smbus

    bus = smbus.SMBus(1)
    accel = MSA301(i2c_dev=bus)
    
    accel.reset()
    print (hex(accel.get_part_id()))
    accel.set_power_mode('normal')
    #accel.set_range(345)
    #accel.set_resolution(14)
    accel.set_power_mode('normal')
    while (1):
        print (accel.get_raw_measurements())
        time.sleep(0.2)
    