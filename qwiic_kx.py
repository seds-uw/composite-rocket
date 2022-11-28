from __future__ import print_function
import qwiic_kx13x
import time
import sys

def runExample():
    myKx = qwiic_kx13x.QwiicKX134()

    # Check for connection
    if myKx.connected == False:
            print("The Qwiic KX13X Accelerometer device isn't connected to the system. Please check your connection", \
                    file=sys.stderr)
            return

    # Check for sensor number
    if myKx.begin():
        print("Ready.")
    else:
        print("Make sure you're using the KX132 and not the KX134")

    # Prepare sensor
    myKx.set_range(myKx.KX134_RANGE16G) # Update the range of the data output.(8, 16, 32, 64)
    myKx.initialize() # Load default settings

    # Print data
    while True:
        myKx.get_accel_data()
        print("X: {0}g Y: {1}g Z: {2}g".format(myKx.kx134_accel.x,
                                               myKx.kx134_accel.y,
                                               myKx.kx134_accel.z))
        time.sleep(1) #Set delay to 1/Output Data Rate which is by default 50Hz 1/50 = .02


if __name__ == '__main__':
    try:
        runExample()
    except (KeyboardInterrupt, SystemExit) as exErr:
        print("\nEnding Example 1")
        sys.exit(0)