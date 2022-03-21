# uncompyle6 version 3.8.0
# Python bytecode 3.6 (3379)
# Decompiled from: Python 3.6.4 (v3.6.4:d48eceb, Dec 19 2017, 06:54:40) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: read_data_json.py
import json, global_var as gvar

def write():
    numbers = {'sql':{'host':'163.18.69.14',
      'name':'pdal-measurement',
      'user':'root',
      'charset':'utf8',
      'password':'rsa+0414018'},
     'measure_tool':{'number':3,
      'id':{'COM1':'',
       'COM2':'',
       'COM3':''}}}
    filename = 'system.json'
    with open(filename, 'w') as (file):
        json.dump(numbers, file)


def read_data(file_name):
    file = file_name
    with open(file) as (file_origin):
        data = json.load(file_origin)
        return data


def system_data_input_global_var(data):
    pass
# okay decompiling read_data_json.pyc
