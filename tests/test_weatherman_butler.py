from weather_butler import WeatherButler
import pytest
import datetime # noqa
import sqlite3 # noqa
import yaml
import json # noqa
import os
import unittest
mock = unittest.mock.Mock()

master_copnfig = 'etc/weatherman.yml'
with open(master_copnfig) as ycf:
    config = yaml.load(ycf, Loader=yaml.FullLoader)
environment = os.environ.get('ENVIRONMENT')

@pytest.fixture(scope="function")
def setup_wb():
    wb = WeatherButler('db/weatherman_unit')
    return wb

# def test_get_response():

# def test_format_request_city_id_list():

# def test_format_response():

# def test_poll():


