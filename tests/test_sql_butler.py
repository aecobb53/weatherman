from sql_butler import SQLButler
import pytest
import datetime
import sqlite3
import yaml
import json
import os

master_copnfig = 'etc/weatherman.yml'
with open(master_copnfig) as ycf:
    config = yaml.load(ycf, Loader=yaml.FullLoader)
environment = os.environ.get('ENVIRONMENT')
# db_name = config['db_name'] + config['environments'][environment]['db_addition']

@pytest.fixture(scope="function")
def setup_sqlb():
    sqlb = SQLButler('db/weatherman_unit')
    # sqlb = SQLButler(db_name)
    return sqlb

@pytest.fixture(scope="function")
def simulate_database_data(path_to_data):
    with open(path_to_data) as jf:
        data = json.load(jf)
    return data

def str_to_datetime(datetiemstr):
    return datetime.datetime.strptime(datetiemstr, config['datetime_str'])


def test_set_up_sqlb(setup_sqlb):
    sqlb = setup_sqlb
    assert isinstance(sqlb.headers, dict)
    assert isinstance(sqlb.config['datetime_str'], str)
    assert sqlb.database_name == 'db/weatherman_unit.sql'

def test_create_database(setup_sqlb):
    sqlb = setup_sqlb
    c = sqlb.create_database()
    assert isinstance(c, sqlite3.Cursor)
    assert isinstance(sqlb.conn, sqlite3.Connection)

def test_format_for_insert(setup_sqlb):
    sqlb = setup_sqlb
    insert_data = sqlb.format_for_insert({
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
    assert isinstance(insert_data, list)
    assert len(insert_data) == 12
    assert isinstance(insert_data[0], str)
    assert isinstance(insert_data[1], int)
    assert isinstance(insert_data[2], str)
    assert isinstance(insert_data[3], int)
    assert isinstance(insert_data[4], str)
    assert isinstance(insert_data[5], str)
    assert isinstance(insert_data[6], (float, int))
    assert isinstance(insert_data[7], int)
    assert isinstance(insert_data[8], int)
    assert isinstance(insert_data[9], int)
    assert isinstance(insert_data[10], (float, int))
    assert isinstance(insert_data[11], (float, int))

def test_negative_format_for_insert_too_many(setup_sqlb):
    sqlb = setup_sqlb
    insert_data = sqlb.format_for_insert({
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
        'notes': 'this is a note to be ignored',
        'favorite_number': 123456789
    })
    assert isinstance(insert_data, list)
    assert len(insert_data) == 12
    assert isinstance(insert_data[0], str)
    assert isinstance(insert_data[1], int)
    assert isinstance(insert_data[2], str)
    assert isinstance(insert_data[3], int)
    assert isinstance(insert_data[4], str)
    assert isinstance(insert_data[5], str)
    assert isinstance(insert_data[6], (float, int))
    assert isinstance(insert_data[7], int)
    assert isinstance(insert_data[8], int)
    assert isinstance(insert_data[9], int)
    assert isinstance(insert_data[10], (float, int))
    assert isinstance(insert_data[11], (float, int))

def test_negative_format_for_insert_too_few(setup_sqlb):
    sqlb = setup_sqlb
    insert_data = sqlb.format_for_insert({
        'time': str_to_datetime('2020-01-01T00:00:00Z'),
        'city': 5419384,
        'sky_id': 800,
        'sky': 'Clear',
        'sky_desc': 'Clear',
        'temp': 60.0,
        'humidity': 20,
    })
    assert isinstance(insert_data, list)
    assert len(insert_data) == 12
    assert isinstance(insert_data[0], str)
    assert isinstance(insert_data[1], int)
    assert isinstance(insert_data[2], str)
    assert isinstance(insert_data[3], int)
    assert isinstance(insert_data[4], str)
    assert isinstance(insert_data[5], str)
    assert isinstance(insert_data[6], (float, int))
    assert isinstance(insert_data[7], int)
    assert isinstance(insert_data[8], int)
    assert isinstance(insert_data[9], int)
    assert isinstance(insert_data[10], (float, int))
    assert isinstance(insert_data[11], (float, int))

# def test_format_for_insert_as_str():
#     sqlb = setup_sqlb()
#     insert_data = sqlb.format_for_insert({
#         'time': str_to_datetime('2020-01-01T00:00:00Z'),
#         'city': '5419384',
#         'name': 'Denver',
#         'sky_id': '800',
#         'sky': 'Clear',
#         'sky_desc': 'Clear',
#         'temp': '60.0',
#         'humidity': '20',
#         'wind': '0',
#         'cover': '5',
#         'rain': '0.0',
#         'snow': '0.0',
#     })
#     assert isinstance(insert_data, list)
#     assert len(insert_data) == 12
#     assert isinstance(insert_data[0], str)
#     assert isinstance(insert_data[1], int)
#     assert isinstance(insert_data[2], str)
#     assert isinstance(insert_data[3], int)
#     assert isinstance(insert_data[4], str)
#     assert isinstance(insert_data[5], str)
#     assert isinstance(insert_data[6], (float, int))
#     assert isinstance(insert_data[7], int)
#     assert isinstance(insert_data[8], int)
#     assert isinstance(insert_data[9], int)
#     assert isinstance(insert_data[10], (float, int))
#     assert isinstance(insert_data[11], (float, int))
#     # Add extra values to verify it still works
#     # Add too few vales to verify it still works
#     # Add values all in str?

# add_data

# commit_table

# multi_add(self, data_list):

def test_tuple_to_dict(setup_sqlb):
    sqlb = setup_sqlb
    return_data = sqlb.tuple_to_dict((
        '2020-01-01T00:00:00Z',
        5419384,
        'Denver',
        800,
        'Clear',
        'Clear',
        60.0,
        20,
        0,
        5,
        0.0,
        0.0,
    ))
    assert isinstance(return_data, dict)


def test_list_tuple_to_list_dict(setup_sqlb):
    sqlb = setup_sqlb
    return_data = sqlb.list_tuple_to_list_dict([(
        '2020-01-01T00:00:00Z',
        5419384,
        'Denver',
        800,
        'Clear',
        'Clear',
        60.0,
        20,
        0,
        5,
        0.0,
        0.0,
    )])
    assert isinstance(return_data, list)
    assert isinstance(return_data[0], dict)

def test_query_database(setup_sqlb):
    sqlb = setup_sqlb
    return_data = sqlb.query_database({
        'start_time': None,
        'end_time': None,
        'exact_list': None,
    })
    assert isinstance(return_data, list)

def test_get_all_data(setup_sqlb):
    sqlb = setup_sqlb
    return_data = sqlb.get_all_data()
    assert isinstance(return_data, list)

def test_get_first_and_last(setup_sqlb):
    sqlb = setup_sqlb
    mocker.patch('sql_butler.tuple_to_dict', return_value=[1, 2])
    return_data = sqlb.get_first_and_last()
    assert isinstance(return_data, list)



def test_negative_set_up_sql():
    with pytest.raises(TypeError) as exp:
        SQLButler(123456)
    assert str(exp.value) == 'The provided database name is not a string'



# When building for main, use a parametrize ability for the getters/setters so it can test multiple cases quickly
# If you are using the same functions or parameters you can set them in