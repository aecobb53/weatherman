from weatherman import data_validator
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
def setup_dv():
    dv = data_validator.DataValidator()
    return dv

testdata = [
    ('2020-01-01T00:00:00.000000Z', '2020-01-01T00:00:00Z'),
    ('2020-01-01T00:00:00.000000L', '2020-01-01T00:00:00Z'),
    ('2020-01-01T00:00:00.000000', '2020-01-01T00:00:00Z'),
    ('2020-01-01T00:00:00.000Z', '2020-01-01T00:00:00Z'),
    ('2020-01-01T00:00:00.000L', '2020-01-01T00:00:00Z'),
    ('2020-01-01T00:00:00.000', '2020-01-01T00:00:00Z'),
    ('2020-01-01T00:00:00Z', '2020-01-01T00:00:00Z'),
    ('2020-01-01T00:00:00L', '2020-01-01T00:00:00Z'),
    ('2020-01-01T00:00:00', '2020-01-01T00:00:00Z'),
    ('2020-01-01T00:00Z', '2020-01-01T00:00:00Z'),
    ('2020-01-01T00:00L', '2020-01-01T00:00:00Z'),
    ('2020-01-01T00:00', '2020-01-01T00:00:00Z'),
    ('2020-01-01T00Z', '2020-01-01T00:00:00Z'),
    ('2020-01-01T00L', '2020-01-01T00:00:00Z'),
    ('2020-01-01T00', '2020-01-01T00:00:00Z'),
    ('2020-01-01', '2020-01-01T00:00:00Z')
]

@pytest.mark.parametrize("test, expected", testdata)
def test_is_datetime(setup_dv, test, expected):
    dv = setup_dv
    date_obj = dv.is_datetime(test)
    expected_obj = datetime.strptime(expected, config['datetime_str'])
    assert date_obj == expected_obj


testdata = [
    ('500', '500'),
    ('500,501', '500,501'),
    ('500 , 501', '500,501'),
    ('500-505', '500,501,502,503,504'),
    ('500 - 505', '500,501,502,503,504'),
    ('500-505,300,301', '500,501,502,503,504,300,301'),
    ('500-505,300-306', '500,501,502,503,504,300,301,305'),
]

@pytest.mark.parametrize("test, expected", testdata)
def test_is_exact_list(setup_dv, test, expected):
    dv = setup_dv
    new_values = dv.is_exact_list(test)
    assert new_values == [int(n) for n in expected.split(',')]
