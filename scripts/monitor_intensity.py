# monitor_intensity.py
import logging
from datetime import datetime

import yaml

from export_csv import format_data, export_csv

logging.basicConfig(level=logging.DEBUG)


with open('./scripts/setting.yaml', 'r') as file:
    setting_yaml = yaml.safe_load(file)

vibration_starttime = datetime.now()
lsenable = False
vibration_detected = False
vibration_lock = False

'''
    This is just a data class
'''


class Data:
    def __init__(self, datetime, vibration_intensity, lasor_intensity=None) -> None:
        self.datetime = datetime
        self.vibration_intensity = vibration_intensity
        self.lasor_intensity = lasor_intensity


'''
    control function:
        when the vibration is received, it locks the period +-{20}seconds preventing to create a new csv within this time period 
'''


def check_vibration_intensity(sensor_data):
    if sensor_data.vibration_intensity > setting_yaml['sensor']['threshold']['vibration_threshold']:
        logging.debug(
            f"======== Vibration detected: {sensor_data.vibration_intensity} ========")
        global vibration_detected, vibration_starttime
        if not vibration_detected:
            vibration_detected = True
            vibration_starttime = sensor_data.datetime
    return


# formula for calculating vibration intensity
def calculate_vibration_intensity(data):
    return (data[4] * 65536 + data[5] * 256 + data[6]) * 9.83 / 8388607


# formula for calculating lasor intensity
def calculate_lasor_intensity(data):
    return (data[7] * 65536 + data[8] * 256 + data[9]) * 2.95 / 8388607 + 0.05


'''
    called by receive_usb_data function when vibrations are received
    if vibration is received within the first {5 / 10} seconds that the program starts,
        fill the first part with epoc and vibration_intensity=0
    append the remaining {15 / 20} seconds after the first vibration is recieved
'''


def monitor_intensity(storage_queue):
    while True:
        global vibration_detected, vibration_starttime, vibration_lock
        if vibration_detected and not vibration_lock:
            vibration_lock = True
            logging.info("======== Start recording vibration ========")

            # only keep the latest 250 data
            if len(storage_queue) > 250:
                for _ in range(1, len(storage_queue) - 250):
                    storage_queue.popleft()
            elif len(storage_queue) < 250:
                logging.warning(
                    "======= Not enough data for prior 5 seconds =======")
                for _ in range(1, 250 - len(storage_queue)):
                    storage_queue.appendleft(Data(datetime=datetime(1970, 1, 1),
                                                  vibration_intensity=0))

        if vibration_detected and vibration_lock and len(storage_queue) == 1000:
            copy_queue = storage_queue.copy()
            if len(copy_queue) > 1000:
                # only keep the latest 250 data
                for _ in range(1, len(copy_queue) - 1000):
                    copy_queue.pop()
            export_csv(format_data(copy_queue), vibration_starttime)
            storage_queue.clear()
            logging.debug("########### queue cleared ###########")
            vibration_detected = False
            vibration_lock = False
