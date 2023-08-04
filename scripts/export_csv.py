import logging
import base64
import requests
import pandas
import os
from dotenv import load_dotenv
import yaml
load_dotenv()
logging.basicConfig(level=logging.DEBUG)

with open('./scripts/setting.yaml', 'r') as file:
    setting_yaml = yaml.safe_load(file)

'''
    function name: format_data(data: deque(maxlen=1000))
    return: csv_data => { [datetime, vibration_intensity, lasor_intensity(optional)] }
    set columns' name
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
            print('##############################')
            print(temp_row)
            print('##############################')
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


'''
    export data as csv
    set csv name to BerthingSection_{datetime}_out.csv
    store at {yaml.output.directory}BerthingSection_{datetime}_out.csv
'''


def export_csv(csv_data, datetime):
    filename = f'BerthingSection_{datetime}_out.csv'
    # change the export_path in order to store the file in other director
    export_path = setting_yaml['sensor']['output']['directory']
    export_path += f'{filename}'
    csv_data.to_csv(filename, sep=',', encoding='utf-8', index=False)
    post_csv(csv_path=export_path,
             filename=filename, pierId=setting_yaml['pierId'])
    export_path = setting_yaml['sensor']['output']['directory']


'''
    POST function:
        get endpoint from setting.yaml
        convert csv to json
        send to endpoint

        result:
            200 -> success
                server receives, but server will determine whether to accept it or not
            xxx -> fail
                refer to 'return_status' in log
'''


def post_csv(csv_path, filename, pierId):
    url = setting_yaml['server']['url']
    record = open(csv_path, 'rb').read()
    record = base64.b64encode(record)
    record = record.decode('utf-8')
    jsonObj = {'pierId': pierId, 'csvName': filename, '__csvfile': record}
    try:
        x = requests.post(url, json=jsonObj)
    except:
        return_status = x.status_code
        logging.error(f'POST failed, Error Status {return_status}')
    else:
        logging.error(f'POST succeded {return_status}')
