import time
import board
import adafruit_bmp3xx
from __future__ import print_function
import qwiic_kx13x
import time
import sys
import logging

def main():
    # set up bmp
    i2c = board.I2C()  # uses board.SCL and board.SDA
    bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c)
    bmp.pressure_oversampling = 8
    bmp.temperature_oversampling = 2

    # set up qwiic
    myKx = qwiic_kx13x.QwiicKX134()
    # check qwiic sensor number
    if myKx.begin():
        print("Ready.")
    else:
        print("Make sure you're using the KX132 and not the KX134")

    # prepare qwiic sensor
    myKx.set_range(myKx.KX134_RANGE16G)  # Update the range of the data output.(8, 16, 32, 64)
    myKx.initialize()  # Load default settings

    # BNO
    # Create and configure the BNO sensor connection.
    # Raspberry Pi configuration with serial UART and RST connected to GPIO 18:
    bno = BNO055.BNO055(serial_port='/dev/serial0', rst=18)
    # Initialize the BNO055 and stop if something went wrong.
    if not bno.begin():
        raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')
    # Print system status and self test result.
    status, self_test, error = bno.get_system_status()
    print('System status: {0}'.format(status))
    print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
    # Print out an error if system status is in error mode.
    if status == 0x01:
        print('System error: {0}'.format(error))
        print('See datasheet section 4.3.59 for the meaning.')

    # collect bmp data
    measured_pressure = bmp.pressure
    measured_temp = bmp.temperature
    measured_alt = bmp.altitude

    # collect qwiic data
    myKx.get_accel_data()
    measured_ax = myKx.kx134_accel.x
    measured_ay = myKx.kx134_accel.y
    measured_az = myKx.kx134_accel.z

    # collect BNO data
    # Read the Euler angles for heading, roll, pitch (all in degrees).
    heading, roll, pitch = bno.read_euler()
    # Read the calibration status, 0=uncalibrated and 3=fully calibrated.
    sys, gyro, accel, mag = bno.get_calibration_status()


if __name__ == '__main__':
    main()