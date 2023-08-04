import os
import sys
from datetime import datetime

import pandas as pd
import usb.core
import yaml

from monitor_intensity import check_vibration_intensity, calculate_vibration_intensity

basepath = os.getcwd()

with open('./scripts/setting.yaml', 'r') as file:
    setting_yaml = yaml.safe_load(file)


class Data:
    def __init__(self, datetime, vibration_intensity, lasor_intensity=None) -> None:
        self.datetime = datetime
        self.vibration_intensity = vibration_intensity
        self.lasor_intensity = lasor_intensity


'''
    This is just some setup to receive usb signals and format the signal with date to form a Data object
'''


def receive_usb_data(storage_queue):
    print("run receive_usb_data")
    # detect device
    device = usb.core.find(
        idVendor=setting_yaml['sensor']['vid'], idProduct=setting_yaml['sensor']['pid'])
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
        # data only fetch vibratoin records at this stage
        data = device.read(endpoint.bEndpointAddress,
                           endpoint.wMaxPacketSize, timeout=1000)

        current_datetime = datetime.today()
        vibration_intensity = calculate_vibration_intensity(
            data=data)

        sensor_data = Data(datetime=current_datetime,
                           vibration_intensity=vibration_intensity)

        check_vibration_intensity(sensor_data=sensor_data)

        try:
            storage_queue.append(sensor_data)
        except IndexError:
            storage_queue.popleft()
            storage_queue.append(sensor_data)
