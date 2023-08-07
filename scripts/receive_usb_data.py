import os
import sys
from datetime import datetime

import pandas as pd
import usb.core
import time

from monitor_intensity import check_intensity, calculate_vibration_intensity

vid = 0x0482
pid = 0x5749
basepath = os.getcwd()


class Data:
    def __init__(self, datetime, vibration_intensity) -> None:
        self.datetime = datetime
        self.vibration_intensity = vibration_intensity


def receive_usb_data(storage_queue):
    print("run receive_usb_data")
    # detect device
    device = usb.core.find(idVendor=vid, idProduct=pid)
    if device is None:
        raise ValueError("Device not found")

    # Claim the interface
    cfg = device.get_active_configuration()
    interface_number = cfg[(0, 0)].bInterfaceNumber

    if device.is_kernel_driver_active(interface_number):
        try:
            device.detach_kernel_driver(interface_number)
        except usb.core.USBError as e:
            sys.exit(
                "Could not detach kernel driver from interface({0}): {1}".format(interface_number, str(e)))

    usb.util.claim_interface(device, interface_number)

    # Receive data from the USB device
    endpoint = device[0][(0, 0)][0]

    sensor_data = pd.DataFrame()

    while True:
        # data only fetch vibratoin records at this stage. wait at most 100 milliseconds for one read, else system booms
        data = device.read(endpoint.bEndpointAddress,
                           endpoint.wMaxPacketSize, timeout=100)

        current_datetime = datetime.today()
        vibration_intensity = calculate_vibration_intensity(
            data=data)

        sensor_data = Data(datetime=current_datetime,
                           vibration_intensity=vibration_intensity)

        check_intensity(sensor_data=sensor_data)

        # add data to queue
        try:
            storage_queue.append(sensor_data)
        # if queue size == 1000, pop the left most (old data) and append latest
        except IndexError:
            storage_queue.popleft()
            storage_queue.append(sensor_data)

        # tune this for time interval, depends on how fast the machine runs
        time.sleep(0.02)  # Pause for 20 milliseconds (0.02 seconds)
