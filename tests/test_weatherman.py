from weatherman import weatherman
import pytest
from datetime import datetime
import yaml
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
    assert wm.setup == False
    wm.setup = True
    assert wm.setup == True
    wm.setup = None

def testing_auto_polling(setup_wm):
    wm = setup_wm
    assert wm.auto_polling == False
    wm.auto_polling = True
    assert wm.auto_polling == True
    wm.auto_polling = None

def testing_timing_intervul(setup_wm):
    wm = setup_wm
    assert wm.timing_intervul == 5
    wm.timing_intervul = 10
    assert wm.timing_intervul == 10
    wm.timing_intervul = None

def tesing_last_poll(setup_wm):
    wm = setup_wm
    assert isinstance(wm.last_poll, datetime)
    wm.last_poll = 10
    assert wm.last_poll == 10

def tesing_db_name(setup_wm):
    wm = setup_wm
    assert wm.db_name == config['db_name']
    wm.db_name = 'newname'
    assert wm.db_name == 'newname'


# def tesing_dump_list(setup_wm):
# def tesing_append_dump_list(setup_wm):
# def tesing_clear_dump_list(setup_wm):
# def tesing_report(setup_wm):
# def tesing_update_report(setup_wm):
# def tesing_clear_report(setup_wm):
# def tesing_state(setup_wm):
# def tesing_update_state(setup_wm):
# def tesing_load_config(setup_wm):
# def tesing_poll_weather(setup_wm):
# def tesing_manage_polling(setup_wm):
# def tesing_weather_dump(setup_wm):
# def tesing_weather_report(setup_wm):
# def tesing_recursive_search(setup_wm):
# def tesing_write_report(setup_wm):
# def tesing_clear_search(setup_wm):
# def tesing_set_timing_intervul(setup_wm):

