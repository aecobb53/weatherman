from sql_butler import SQLButler
import pytest
import datetime
import sqlite3
import yaml
import os

master_copnfig = 'etc/weatherman.yml'
with open(master_copnfig) as ycf:
    config = yaml.load(ycf, Loader=yaml.FullLoader)
environment = os.environ.get('ENVIRONMENT')
# db_name = config['db_name'] + config['environments'][environment]['db_addition']

def setup_sqlb():
    sqlb = SQLButler('db/weatherman_unit')
    # sqlb = SQLButler(db_name)
    return sqlb

def str_to_datetime(datetiemstr):
    return datetime.datetime.strptime(datetiemstr, config['datetime_str'])


def test_set_up_sqlb():
    sqlb = setup_sqlb()
    assert isinstance(sqlb.headers, dict)
    assert isinstance(sqlb.config['datetime_str'], str)
    assert sqlb.database_name == 'db/weatherman_unit.sql'

def test_create_database():
    sqlb = setup_sqlb()
    c = sqlb.create_database()
    assert isinstance(c, sqlite3.Cursor)
    assert isinstance(sqlb.conn, sqlite3.Connection)

def test_format_for_insert():
    sqlb = setup_sqlb()
    sqlb.format_for_insert({
        'time': str_to_datetime('2020-01-01T00:00:00Z'),
        'city': 5419384,
        'name': 'Denver',
        'sky_id': 800,
        'sky': 'Clear',
        'sky_desc': 'Clear',
        'temp': 60.0,
        'humidity': 20,
        'wind': 0,
        'cover': 5,
        'rain': 0.0,
        'snow': 0.0,
    })

    # Add extra values to verify it still works
    # Add too few vales to verify it still works
    # Add values all in str?

def test_negative_set_up_sql():
    with pytest.raises(TypeError) as exp:
        SQLButler(123456)
    assert str(exp.value) == 'The provided database name is not a string'
