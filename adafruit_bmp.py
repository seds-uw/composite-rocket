import time
import board
import adafruit_bmp3xx

# https://learn.adafruit.com/adafruit-bmp388-bmp390-bmp3xx/python-circuitpython
# I2C setup
i2c = board.I2C()  # uses board.SCL and board.SDA
bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c)

# SPI setup
# from digitalio import DigitalInOut, Direction
# spi = board.SPI()
# cs = DigitalInOut(board.D5)
# bmp = adafruit_bmp3xx.BMP3XX_SPI(spi, cs)

bmp.pressure_oversampling = 8
bmp.temperature_oversampling = 2

while True:
    print(
        "Pressure: {:6.4f}  Temperature: {:5.2f}  Altitude: {} meters".format(bmp.pressure, bmp.temperature, bmp.altitude)
    )
    time.sleep(1)