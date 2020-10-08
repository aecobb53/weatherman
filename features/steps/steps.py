import datetime
import json
from behave import given, when, then
import weather_butler
import sql_butler
import csv_butler

# Logging
import steps_logging
logit, logger = steps_logging.setup()

# Weather bulter
WB = weather_butler.WeatherButler()


@given('I create an empty {database_type}')
def database_setup(context, database_type):
    if database_type == 'sql_database':
        context.db = sql_butler.SQLButler('db/weatherman_behave')
        context.db.create_database()
        db_type = 'sql'
    elif database_type == 'csv_database':
        context.db = csv_butler.CSVButler('db/weatherman_behave')
        context.db.create_database()
        db_type = 'csv'
    else:
        raise ValueError(f'The provided database {database_type} is not one supported')
    logit.debug(f'Created or connected to {db_type}')
    return context.db

@when('I load the weather data in {json_file}')
def load_weather_data_from_file(context, json_file):
    """
    Load in the data in the provided json file
    """
    json_file = 'features/support/' + json_file
    logit.debug(f"loading data from {json_file}")
    with open(json_file, 'r') as read_file:
        context.data = json.load(read_file)
    for index, line in enumerate(context.data):
        context.data[index]['time'] = datetime.datetime.strptime(line['time'], '%Y-%m-%dT%H:%M:%SZ')
    logit.info(f"the json that was loaded: {context.data}")
    return context.data

@when('I load the example response data in {json_file}')
def load_weather_response_data(context, json_file):
    """
    Load an example response from the website
    """
    json_file = 'features/support/' + json_file
    logit.debug(f"loading response data from {json_file}")
    with open(json_file, 'r') as read_file:
        raw_data = json.load(read_file)
    context.data = WB.format_response(raw_data['list'])
    logit.debug(f"context formatted data {context.data}")

@when('I try to select element(s) {number} from the database return')
def selecting_element_from_db_response(context, number):
    """
    Selecting the nth element of the list that was returned
    """
    numbers = number.split(',')
    context.selection = []
    for num in numbers:
        context.selection.append(context.db_response[int(num)])
    logit.debug(f"Indexes used {numbers}")
    logit.debug(f"selected data {context.selection}")

@when('I try to write the data to the database')
def database_write(context):
    """
    The json file must be a list of dicts to be able to add to the db
    """
    logit.debug(f'writing {context.data} to database type {type(context.db)}')
    context.db.multi_add(context.data)
    # context.db

@when('I try to get all data from the database')
def get_all_data_from_database(context):
    context.db_response = context.db.get_all_data()
    logit.debug(f"database response: {context.db_response}")

@then('I verify the database response matches {json_file}')
def compare_to_json_data(context, json_file):
    comparer = load_weather_data_from_file(context, json_file)
    logit.debug('comparing responses')
    logit.debug(f"{context.selection}")
    logit.debug(f"{comparer}")
    if len(context.selection) != len(comparer):
        logit.warning(f"The lenght of the two lists are not the same " +
            f"{len(context.selection)} does not equal {len(comparer)}")
        raise ValueError('The examplefile and the database do not match')
    for index in range(max(len(context.selection), len(comparer))):
        if any([k for k in context.selection[index].keys() if k not in comparer[index].keys()]) or \
            any([k for k in comparer[index].keys() if k not in context.selection[index].keys()]):
            logit.warning("The keys do not match")
            raise ValueError('The examplefile and the database do not match')
        context.selection[index]['time'] = ''
        comparer[index]['time'] = ''
        for key in context.selection[index].keys():
            if context.selection[index][key] != comparer[index][key]:
                logit.warning(f"not equal values {context.selection[index][key]}, {comparer[index][key]}")
                logit.warning(f"\n{context.selection[index]} \n{comparer[index]}")
                raise ValueError('The examplefile and the database do not match')
    logit.info(f"The comparison matches")

features/