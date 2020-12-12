from weatherman import weatherman
import pytest
# import datetime
# import sqlite3
import yaml
# import json
import os
import unittest
mock = unittest.mock.Mock()

master_copnfig = 'etc/weatherman.yml'
with open(master_copnfig) as ycf:
    config = yaml.load(ycf, Loader=yaml.FullLoader)
environment = os.environ.get('ENVIRONMENT')

@pytest.fixture(scope="function")
def setup_wm():
    wm = weatherman.WeatherMan()
    return wm

def test_setup(setup_wm):
    wm = setup_wm
    # assert wm._setup == None
    # assert wm.setup == False
    # wm.setup = True
    # assert wm.setup == True




# def test_auto_polling():
# def test_timing_intervul():
# def test_last_poll():

# def test_db_name():
# def test_dump_list():
# def test_append_dump_list():
# def test_clear_dump_list():
# def test_report():
# def test_update_report():
# def test_clear_report():
# def test_state():
# def test_update_state():

# def test_load_config():
# def test_set_logging():

# def test_poll_weather():
# def test_manage_polling():
# def test_weather_dump():
# def test_weather_report():
# def test_write_report():
# def test_clear_search():
# def test_set_timing_intervul():






# def setup(self, value):
# def auto_polling(self, value):
# def timing_intervul(self, value):
# def last_poll(self, value):
# def db_name(self, value):

# def dump_list(self):
# def append_dump_list(self, values):
# def clear_dump_list(self):
# def report(self):
# def update_report(self, dct):
# def clear_report(self):
# def state(self):
# def update_state(self, dct):

# def load_config(self, path=master_config_path):
# def set_logging(self, logging_dct=None):

# def poll_weather(self):
# def manage_polling(self):
# def weather_dump(self, parameters):
# def weather_report(self, data):
#     def recursive_search(value, key, index, lst, itterations):
# def write_report(self, report, file_name=None):
# def clear_search(self):
# def set_timing_intervul(self, intervul='auto'):
