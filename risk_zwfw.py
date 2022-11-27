# -*- coding: utf-8 -*-
"""
Created on Sun Nov 27 09:09:50 2022
@author: gitoscc
"""

import os
import json
import time
import hashlib
import requests
from datetime import datetime

# Location of Json files
PATHS = 'Archive'

ABS_PATH = os.path.dirname(os.path.abspath(__file__))
PATHS = os.path.join(ABS_PATH, PATHS)


def fetch_new():
    """
    Fetch the latest risk data from the API
    :return: json data
    """
    # Send get requests
    url = 'http://app.gjzwfw.gov.cn/fwmhapp3/yhzx/app/xzqh.do'
    Params={}
    Headers={}
    r = requests.get(url=url,params=Params,headers=Headers)
    risk_json = r.json()
    return risk_json

def save_json(file_path, json_data):
    # Save Json file
    with open(file_path, 'w', encoding="utf-8") as outfile:
        json.dump(json_data, outfile, ensure_ascii=False)

def get_json(file_path):
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r', encoding="utf-8") as outfile:
        json_data = json.load(outfile)
    return json_data


def get_info_by_list():
    file_list = os.listdir(PATHS)
    file_list.sort()
    info = {'file_count': 0, 'file_list': []}
    for file in file_list:
        if '-' in file:
            update_time = file.split('-')[0]
            update_time += '+0800'
            update_time = datetime.strptime(update_time, "%Y%m%d%H%z")
            update_time = int(update_time.timestamp())
            info_dict = {
                'file_name': file,
                'update_time': update_time,
                'save_time': int(time.time())
            }
            info['file_list'].append(info_dict)
            info['file_count'] += 1
    return info


def main():
    force_update = os.environ.get('FORCE_UPDATE', '')
    force_update = force_update.lower() == 'true'

    if not os.path.exists(PATHS):
        os.makedirs(PATHS)

    data = fetch_new()
    update_time = data['params']['high'][0]['gxsj']
    update_time += '+0800'
    update_time = datetime.strptime(update_time, "%Y-%m-%d %H:%M:%S%z")
    update_timestamp = int(update_time.timestamp())
    update_time = datetime.strftime(update_time, "%Y%m%d%H")
    data_hash = hashlib.md5(json.dumps(data, sort_keys=True).encode('utf-8')).hexdigest()
    data_hash = data_hash[:8]
    time_file_name = f'{update_time}-{data_hash}.json'
    time_file_path = os.path.join(PATHS, time_file_name)
    if os.path.exists(time_file_path) and not force_update:
        print('File %s already exists' % time_file_name)
        return False
    save_json(time_file_path, data)
    print('File %s saved' % time_file_name)
    save_json(os.path.join(PATHS, 'latest.json'), data)
    print('File latest.json updated')

    info_path = os.path.join(PATHS, 'info.json')
    info = get_json(info_path)
    if info is None or force_update:
        info = get_info_by_list()
    else:
        info['file_count'] += 1
        info['file_list'].append({
            'file_name': time_file_name,
            'update_time': update_timestamp,
            'save_time': int(time.time()),
        })
    save_json(info_path, info)
    print('File info.json updated')
    return True


if __name__ == '__main__':
    if main():
        exit(0)
    else:
        exit(1)
