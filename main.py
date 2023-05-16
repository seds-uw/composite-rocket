import time
import sys
import logging
import board
import RPi.GPIO as GPIO
import adafruit_bmp3xx
import qwiic_kx13x
from csv import writer
from Adafruit_BNO055 import BNO055

# bno documentation https://docs.circuitpython.org/projects/bno055/en/latest/
def main():
    # set up GPIO
    output_voltage_pin = 0
    GPIO.setmode(GPIO.BCM)  # choose BCM or BOARD
    GPIO.setup(output_voltage_pin, GPIO.OUT)  # set a port/pin as an output
    # GPIO.output(output_voltage_pin, 1)  # set port/pin value to 1/GPIO.HIGH/True
    # GPIO.output(output_voltage_pin, 0)  # set port/pin value to 0/GPIO.LOW/False

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
    time.sleep(2)
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

    # Read the calibration status, 0=uncalibrated and 3=fully calibrated.
    sys, gyro, accel, mag = bno.get_calibration_status()

    with open('data.csv', 'w', newline='') as f:
        data_writer = writer(f)
        time_tracker = 0
        decreasing_count = 0
        prev_alt = []
        prev_alt_limit = 5
        prev_alt_avg = 0

        while True:
            # data: pressure, temp, alt, ax, ay, az,
            current_data = []
            # collect bmp data
            measured_pressure = bmp.pressure
            measured_temp = bmp.temperature
            measured_alt = bmp.altitude
            # append data
            current_data.append(measured_pressure)
            current_data.append(measured_temp)
            current_data.append(measured_alt)

            # collect qwiic data
            myKx.get_accel_data()
            measured_ax = myKx.kx134_accel.x
            measured_ay = myKx.kx134_accel.y
            measured_az = myKx.kx134_accel.z
            # append data
            current_data.append(measured_ax)
            current_data.append(measured_ay)
            current_data.append(measured_az)

            # collect BNO data
            # Read the Euler angles for heading, roll, pitch (all in degrees).
            heading, roll, pitch = bno.read_euler()
            bno_accel_x, bno_accel_y, bno_accel_z = bno.read_accelerometer()
            bno_gyro_x, bno_gyro_y, bno_gyro_z = bno.read_gyroscope()
            # append data
            current_data.append(heading)
            current_data.append(roll)
            current_data.append(pitch)
            current_data.append(bno_accel_x)
            current_data.append(bno_accel_y)
            current_data.append(bno_accel_z)
            current_data.append(bno_gyro_x)
            current_data.append(bno_gyro_y)
            current_data.append(bno_gyro_z)



            prev_alt.append(measured_alt)
            if len(prev_alt) > prev_alt_limit:
                prev_alt.pop(0)
            curr_alt_avg = sum(prev_alt) / len(prev_alt)

            if prev_alt_avg > curr_alt_avg:  # TODO: floating point threshold
                decreasing_count += 1
            else:
                decreasing_count = 0

            if decreasing_count > 5: # TODO: determine appropriate value
                GPIO.output(output_voltage_pin, 1)
                break  # TODO: remove break; continue data collection

            prev_alt_avg = curr_alt_avg

            print(current_data)
            print("Decreasing Count: ", decreasing_count)
            print()

            data_writer.writerow(current_data)
            time_tracker += 0.1
            time.sleep(0.1)


if __name__ == '__main__':
    main()
