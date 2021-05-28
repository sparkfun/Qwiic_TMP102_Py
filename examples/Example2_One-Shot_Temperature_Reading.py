#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Example2_One-Shot_Temperature_Reading.py
# 
# Example for the TMP102 I2C Temperature Sensor
# Written byAlex Wende @ SparkFun Electronics
# April 29th 2016
# 
# This sketch connects to the TMP102 temperature sensor and enables the
# one-shot temperature measurement mode using the one_shot() function.
# The function returns 0 until the temperature measurement is ready to
# read (takes around 25ms). After the measurment is read, the TMP102 is
# placed back into sleep mode before the loop is repeated. This can be 
# useful to save power or increase the continuous conversion rate from
# 8Hz up to a maximum of 40Hz.
# 
#==================================================================================
# Copyright (c) 2021 SparkFun Electronics
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.
#==================================================================================
# Example 2
#-----------------------------------------------------------------------------

from __future__ import print_function
import qwiic_tmp102
import time
import sys

# Connections
# VCC = 3.3V
# GND = GND
# SDA = A4
# SCL = A5

# Sensor address can be changed with an external jumper to:
# ADD0 - Address
# VCC - 0x49
# SDA - 0x4A
# SCL - 0x4B


def runExample():

	print("\nSparkFun Qwiic TMP102 Sensor Example 2\n")
	myTmpSensor = qwiic_tmp102.QwiicTmp102Sensor()

	if myTmpSensor.is_connected == False:
		print("The Qwiic TMP102 Sensor device isn't connected to the system. Please check your connection", \
			file=sys.stderr)
		return

	myTmpSensor.begin()

	print("Initialized.")

	while True:
		myTmpSensor.one_shot(1)
		while(myTmpSensor.one_shot() == 0):
			time.sleep(1)
		print ("TempC = ", myTmpSensor.read_temp_c())
		myTmpSensor.sleep()
		time.sleep(1)


if __name__ == '__main__':
	try:
		runExample()
	except (KeyboardInterrupt, SystemExit) as exErr:
		print("\nEnding Example 1")
		sys.exit(0)




