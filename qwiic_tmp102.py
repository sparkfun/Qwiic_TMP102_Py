"""
qwiic_tmp102
============
Python module for the [SparkFun Qwiic TMP102 Sensor](https://www.sparkfun.com/products/16304)

This python package is a port of the existing [SparkFun Qwiic TMP102 Sensor Arduino Examples](https://github.com/sparkfun/SparkFun_TMP102_Arduino_Library/tree/master/examples)

This package can be used in conjunction with the overall [SparkFun qwiic Python Package](https://github.com/sparkfun/Qwiic_Py)

New to qwiic? Take a look at the entire [SparkFun qwiic ecosystem](https://www.sparkfun.com/qwiic).

"""
from __future__ import print_function, division

import qwiic_i2c

#======================================================================
# Basic setup of I2C commands and available I2C Addresses
#
#
# The name of this device - note this is private
_DEFAULT_NAME = "Qwiic TMP102 Sensor"

# Command addresses. These can be found on page 23 of the datasheet
TEMPERATURE_REGISTER = 0x00
CONFIG_REGISTER = 0x01
T_LOW_REGISTER = 0x02
T_HIGH_REGISTER = 0x03
TMP102_DEFAULT_ADDRESS = 0x48


TMP102_RESOLUTION = 0.0625                   # Resolution of the device, found on (page 1 of datasheet)

#Address can only be 0x48 (GND), 
#	0x49 (V+), 0x4A (SDA), and 0x4B (SCL)
_AVAILABLE_I2C_ADDRESS = [0x48, 0x49, 0x4A, 0x4B]

###############################################################################
###############################################################################
# Some devices have multiple available addresses - this is a list of these addresses.
# NOTE: The first address in this list is considered the default I2C address for the
# device.
class QwiicTmp102Sensor(object):
    """
    QwiicTmp102Sensor

        :param address: The I2C address to use for the device.
                        If not provided, the default address is used.
        :param i2c_driver: An existing i2c driver object. If not provided
                        a driver object is created.
        :return: The TMP102 Sensor device object.
        :rtype: Object
    """
    device_name         = _DEFAULT_NAME
    available_addresses = _AVAILABLE_I2C_ADDRESS

    # Constructor
    def __init__(self, address=None, i2c_driver=None):

        # Did the user specify an I2C address?
        self.address = self.available_addresses[0] if address is None else address

        # load the I2C driver if one isn't provided

        if i2c_driver is None:
            self._i2c = qwiic_i2c.getI2CDriver()
            if self._i2c is None:
                print("Unable to load I2C driver for this platform.")
                return
        else:
            self._i2c = i2c_driver


    # ----------------------------------
    # is_connected()
    #
    # Is an actual board connected to our system?

    def is_connected(self):
        """
            Determine if a Soil MoistureSensor device is conntected to the system..
            :return: True if the device is connected, otherwise False.
            :rtype: bool
        """        
        return qwiic_i2c.isDeviceConnected(self.address)

    connected = property(is_connected)

    # ----------------------------------
    # begin()
    #
    # Initialize the system/validate the board.
    def begin(self):
        """
            Initialize the operation of the Soil Moisture Sensor module
            :return: Returns true of the initialization was successful, otherwise False.
            :rtype: bool
        """
        # Set variables
        self.tempC = 0
        self.tempF = 0
        
        # Basically return True if we are connected...
        return self.is_connected()

    #****************************************************************************#
    #
    #   Sensor functions
    #
    # ****************************************************************************#
    def get_address(self):
        """
        Returns the device address
        """
        return self.address

    def read_temp_c(self):
        """
        Reads the results from the sensor
        :rtype: integer
        """
        data = self._i2c.readBlock(self.address, TEMPERATURE_REGISTER, 2)
        
        if (data[0] == 0xFF and data[1] == 0xFF):
                return NaN
                
        if(data[1]&0x01):	# 13 bit mode
                baseRead = ((data[0]) << 5) | (data[1] >> 3)
                if(baseRead > 0xFFF):
                        baseRead |= 0xE000
        else:
                #Combine bytes to create a signed int 
                baseRead = ((data[0]) << 4) | (data[1] >> 4)

        	#Temperature data can be + or -, if it should be negative,
                #convert 12 bit to 16 bit and use the 2s compliment.
                if(baseRead > 0x7FF):
                        baseRead |= 0xF000

        self.tempC = baseRead * 0.0625
        return self.tempC
        
    def read_temp_f(self):
        """
        Reads the results from the sensor
        :rtype: integer
        """

        self.tempF = self.read_temp_c() * 9.0 / 5.0 + 32.0
        return self.tempF
        
    def set_conversion_rate(self, rate):
        """
        // Set the conversion rate (0-3)
        // 0 - 0.25 Hz
        // 1 - 1 Hz
	// 2 - 4 Hz (default)
        // 3 - 8 Hz
        """
        
        configByte = self._i2c.readBlock(self.address, CONFIG_REGISTER, 2)
        rate = rate&0x03
                
        # Load new conversion rate
        configByte[1] &= 0x3F           # Clear CR0/1 (bit 6 and 7 of second byte)
        configByte[1] |= rate<<6        # Shift in new conversion rate
      
        self._i2c.writeBlock(self.address, CONFIG_REGISTER, configByte)
        
    def set_extended_mode(self, mode):
        """
        Enable or disable extended mode
	0 - disabled (-55C to +128C)
	1 - enabled  (-55C to +150C)
        """
        configByte = self._i2c.readBlock(self.address, CONFIG_REGISTER, 2)
        
        # Load new value for extention mode
        configByte[1] &= 0xEF		# Clear EM (bit 4 of second byte)
        configByte[1] |= mode<<4	# Shift in new exentended mode bit
        
        self._i2c.writeBlock(self.address, CONFIG_REGISTER, configByte)
    
    def sleep(self):
        """
        Switch sensor to low power mode
        """
        sleepValue = self._i2c.readByte(self.address, CONFIG_REGISTER)
        sleepValue |= 0x01	# Set SD (bit 0 of first byte)
        self._i2c.writeByte(self.address, CONFIG_REGISTER, sleepValue)

    def wakeup(self):
        """
        Wakeup and start running in normal power mode
        """
        wakeValue = self._i2c.readByte(self.address, CONFIG_REGISTER)
        wakeValue &= 0xFE	# Clear SD (bit 0 of first byte)
        self._i2c.writeByte(self.address, CONFIG_REGISTER, wakeValue)

    def set_alert_polarity(self, polarity):
        """
        Set the polarity of Alert
        0 - Active LOW
        1 - Active HIGH
        """
        configByte = self._i2c.readByte(self.address, CONFIG_REGISTER)
        
        # Load new value for polarity
        configByte &= 0xFB           # Clear POL (bit 2 of registerByte)
        configByte |= polarity<<2    # Shift in new POL bit

        self._i2c.writeByte(self.address, CONFIG_REGISTER, configByte)

    def alert(self):
        """
        Returns state of Alert register
        """
        alert = self._i2c.readByte(self.address, CONFIG_REGISTER)
        alert &= 0x20   #Clear everything but the alert bit (bit 5)
        return alert>>5;
        
    def one_shot(self, setOneShot = 0):
        """
        Sets the SingleShot Register. Returns 1 after the conversion is complete
        """
        registerByte = self._i2c.readByte(self.address, CONFIG_REGISTER)
        if(setOneShot == 1):
                registerByte |= (1<<7)
                self._i2c.writeByte(self.address, CONFIG_REGISTER, registerByte)
                return 0
        else:
                registerByte &= (1<<7)
                return (registerByte>>7)


    def set_low_temp_c(self, temperature):
        """
        Sets T_LOW (degrees C) alert threshold
        """
        if(temperature > 150.0):
                temperature = 150.0
        if(temperature < -55.0):
                temperature = -55.0
                
        registerByte = self._i2c.readBlock(self.address, CONFIG_REGISTER, 2)
        
        #Check if temperature should be 12 or 13 bits
        # 0 - temp data will be 12 bits
        # 1 - temp data will be 13 bits
        extendedMode = (registerByte[1]&0x10) >> 4	
                                                                
        #Convert analog temperature to digital value
        temperature = temperature/0.0625
        
        if(extendedMode):	#13-bit mode
                registerByte[0] = int(temperature)>>5
                registerByte[1] = (int(temperature)<<3)
        else:
                registerByte[0] = int(temperature)>>4
                registerByte[1] = int(temperature)<<4
              
        self._i2c.writeBlock(self.address, T_LOW_REGISTER, registerByte)

    def set_high_temp_c(self, temperature):
        """
        Sets T_LOW (degrees C) alert threshold
        """

        if(temperature > 150.0):
                temperature = 150.0
        if(temperature < -55.0):
                temperature = -55.0
        registerByte = self._i2c.readBlock(self.address, CONFIG_REGISTER, 2)
        
        #Check if temperature should be 12 or 13 bits
        # 0 - temp data will be 12 bits
        # 1 - temp data will be 13 bits
        extendedMode = (registerByte[1]&0x10) >> 4	
                                                                
        #Convert analog temperature to digital value
        temperature = temperature/0.0625
                
        if(extendedMode):	#13-bit mode
                registerByte[0] = int(temperature)>>5
                registerByte[1] = (int(temperature)<<3)
        else:
                registerByte[0] = int(temperature)>>4
                registerByte[1] = int(temperature)<<4
                
        self._i2c.writeBlock(self.address, T_HIGH_REGISTER, registerByte)

    def set_low_temp_f(self, temperature):
        """
        Sets T_LOW (degrees F) alert threshold
        """
        new_temp = (temperature - 32)*5/9    # Convert temperature to C
        self.set_low_temp_c(new_temp)           # Set T_LOW

        
    def set_high_temp_f(self, temperature):
        """
        Sets T_HIGH (degrees F) alert threshold
        """
        new_temp = (temperature - 32)*5/9    # Convert temperature to C
        self.set_high_temp_c(new_temp)           # Set T_HIGH


    def read_low_temp_c(self):
        """
        Gets T_LOW (degrees C) alert threshold
        """
        configByte = self._i2c.readBlock(self.address, CONFIG_REGISTER, 2)

        # 0 - temp data will be 12 bits
        # 1 - temp data will be 13 bits
        extendedMode = (configByte[1]&0x10)>>4	

        lowTempByte = self._i2c.readBlock(self.address, T_LOW_REGISTER, 2)

        if(lowTempByte[0] == 0xFF and lowTempByte[1] == 0xFF):
                return NAN

        if (extendedMode):
                digitalTemp = ((lowTempByte[0]) << 5) | (lowTempByte[1] >> 3)
                if(digitalTemp > 0xFFF):
                        digitalTemp |= 0xE000
        else:
                digitalTemp = ((lowTempByte[0]) << 4) | (lowTempByte[1] >> 4)
                if(digitalTemp > 0x7FF):
                        digitalTemp |= 0xF000
                        
        return digitalTemp*0.0625    
        
                    
    def read_high_temp_c(self):
        """
        Gets T_HIGH (degrees C) alert threshold
        """
        configByte = self._i2c.readBlock(self.address, CONFIG_REGISTER, 2)

        # 0 - temp data will be 12 bits
        # 1 - temp data will be 13 bits
        extendedMode = (configByte[1]&0x10)>>4	

        highTempByte = self._i2c.readBlock(self.address, T_HIGH_REGISTER, 2)

        if(highTempByte[0] == 0xFF and highTempByte[1] == 0xFF):
                return NAN

        if (extendedMode):
                digitalTemp = ((highTempByte[0]) << 5) | (highTempByte[1] >> 3)
                if(digitalTemp > 0xFFF):
                        digitalTemp |= 0xE000
        else:
                digitalTemp = ((highTempByte[0]) << 4) | (highTempByte[1] >> 4)
                if(digitalTemp > 0x7FF):
                        digitalTemp |= 0xF000
                        
        return digitalTemp*0.0625


    def read_low_temp_f(self):
        """
        Reads T_LOW register in F
        """
        return self.read_low_temp_c()*9.0/5.0 + 32.0
        
    def read_high_temp_f(self):
        """
        Reads T_HIGH register in F		
        """
        
        return self.read_high_temp_c()*9.0/5.0 + 32.0


    def set_fault(self, faultSetting):
        """
	Set the number of consecutive faults
	0 - 1 fault
	1 - 2 faults
	2 - 4 faults
	3 - 6 faults
        """
        faultSetting = faultSetting&3   #Make sure rate is not set higher than 3.

        configByte = self._i2c.readByte(self.address, CONFIG_REGISTER)
                
        #Load new conversion rate
        configByte &= 0xE7                   # Clear F0/1 (bit 3 and 4 of first byte)
        configByte |= faultSetting<<3        # Shift new fault setting
        
        self._i2c.writeByte(self.address, CONFIG_REGISTER, configByte)
        
    def set_alert_mode(self, mode):
        """
	// Set Alert type
        // 0 - Comparator Mode: Active from temp > T_HIGH until temp < T_LOW
        // 1 - Thermostat Mode: Active when temp > T_HIGH until any read operation occurs
	
        """
        configByte = self._i2c.readByte(self.address, CONFIG_REGISTER)
        
        #Load new conversion rate
        configByte &= 0xFD            # Clear old TM bit (bit 1 of first byte)
        configByte |= mode<<1	        # Shift in new TM bit

        self._i2c.writeByte(self.address, CONFIG_REGISTER, configByte)

 
