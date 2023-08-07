import logging
import base64
import requests
import pandas
import os
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(level=logging.DEBUG)

export_path = os.getcwd()
pierId = os.getenv("SERVER_ENDPOINT")

'''
    function name: format_data(data: deque(maxlen=1000))
    return: csv_data => { [datetime, vibration_intensity, lasor_intensity] }
'''


def format_data(data):
    logging.debug("======== Printing CSV ========")
    csv_data = pandas.DataFrame()

    # if data does not have lasor_intensity column
    if not hasattr(data, 'lasor_intensity'):
        while data:
            temp_data = data.popleft()
            temp_row = pandas.DataFrame(
                [pandas.Series([temp_data.datetime,
                               temp_data.vibration_intensity])]
            )
            csv_data = pandas.concat([csv_data, temp_row], ignore_index=True)
        csv_data.columns = ['STM32_DATETIME',
                            'Accelerometer z-axis/ms^-2']

    # if data has lasor_intensity column
    else:
        while data:
            temp_data = data.popleft()
            temp_row = pandas.DataFrame(
                [pandas.Series(
                    temp_data.datetime,
                    temp_data.vibration_intensity,
                    temp_data.lasor_intensity)]
            )
            csv_data = pandas.concat([csv_data, temp_row], ignore_index=True)
        csv_data.columns = ['STM32_DATETIME',
                            'Accelerometer z-axis/ms^-2',
                            'Laser Sensor /m']
    return csv_data


def export_csv(csv_data, datetime):
    global export_path
    filename = f'BerthingSection_{datetime}_out.csv'
    # change the export_path in order to store the file in other director
    export_path = f'{filename}'
    csv_data.to_csv(filename, sep=',', encoding='utf-8', index=False)
    post_csv(csv_path=export_path,
             filename=filename, pierId=pierId)
    export_path = os.getcwd()


def post_csv(csv_path, filename, pierId):
    url = os.getenv("SERVER_ENDPOINT")
    record = open(csv_path, 'rb').read()
    record = base64.b64encode(record)
    record = record.decode('utf-8')
    jsonObj = {'pierId': pierId, 'csvName': filename, '__csvfile': record, }
    try:
        x = requests.post(url, json=jsonObj)
        return_status = x.status_code
    except:
        logging.error(f'POST failed, Error Status {return_status}')
    else:
        if (x.status_code == 200):
            logging.error(f'POST succeded, Status {return_status}')
        else:
            logging.error(f'POST failed, Error Status {return_status}')
