import os
import time

from waveshare_TSL2591 import TSL2591

import utils

sensor = TSL2591.TSL2591()


def lux():
    """
    Returns the lux light level of the room
    :return: lux level of the room
    """
    try:
        return sensor.Lux
    except KeyboardInterrupt:
        sensor.Disable()
        exit()


def save_lux():
    """
    Saves the lux value to the drive
    :return: None
    """
    # If images folder does not exist, create it
    with open("lux/lux_" + utils.est_time_now() + ".txt", "w") as file:
        # Write the integer value to the file
        file.write(str(lux()))


if __name__ == '__main__':
    # Take an image every minute
    if not os.path.exists("lux"):
        os.makedirs("lux")
    while True:
        save_lux()
        time.sleep(60)
