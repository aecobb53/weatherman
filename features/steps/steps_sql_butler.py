from behave import given, when, then
import datetime
import json
import yaml

import sql_butler
import data_validator
validator = data_validator.DataValidator()


# Logging
import steps_logging
logit, logger = steps_logging.setup()

# Config
import steps_config
config = steps_config.load_config()
main_config = steps_config.load_config('weatherman.yml', 'etc/')

@given('I create an empty database')
def database_setup(context):
    """
    Depending on a SQL or CSV database I want them to be run the same. 
    They need to be set up though. 
    """
    context.db = sql_butler.SQLButler(config['database_name'])
    context.db.create_database()
    logit.debug(f"Created or connected to database called {config['database_name']}")

@when('I load the weather data in {json_file}')
def load_weather_data_from_file(context, json_file):
    """
    Load in the data in the provided json file
    """
    json_file = config['support_path'] + json_file
    logit.debug(f"loading data from {json_file}")
    with open(json_file, 'r') as read_file:
        context.data = json.load(read_file)
    for index, line in enumerate(context.data):
        context.data[index]['time'] = datetime.datetime.strptime(line['time'], config['datetime_str'])
    logit.info(f"the json that was loaded: {context.data}")
    return context.data

@when('I try to write the data to the database')
def database_write(context):
    """
    The json file must be a list of dicts to be able to add to the db
    """
    logit.debug(f'writing {context.data} to database type {type(context.db)}')
    context.db.multi_add(context.data)

@when('I try to get all data from the database')
def get_all_data_from_database(context):
    context.db_response = context.db.get_all_data()
    logit.debug(f"database response: {context.db_response}")

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

@when('I load the example response data in {json_file}')
def load_weather_response_data(context, json_file):
    """
    Load an example response from the website
    """
    json_file = config['support_path'] + json_file
    logit.debug(f"loading response data from {json_file}")
    with open(json_file, 'r') as read_file:
        raw_data = json.load(read_file)
    context.data = context.WB.format_response(raw_data['list'])
    logit.debug(f"context formatted data {context.data}")

@when('I try to set up a {change_datatype} from {json_file}')
def setup_raw_database_return(context, change_datatype, json_file):
    """
    This will set up a json to look like a tuple or a list of tuples to verify the database interprets the data correctly. 
    """
    json_file = config['support_path'] + json_file
    with open(json_file, 'r') as read_file:
        raw_data = json.load(read_file)
    if change_datatype == 'tuple':
        raw_data = tuple(raw_data['tuple'])
        logit.debug(f"Data loaded into a tuple")
        context.return_data = [context.db.tuple_to_dict(raw_data),]
    elif change_datatype == 'list':
        raw_data = [tuple(raw_data['tuple']),]
        logit.debug(f"Data loaded into a list of tuples")
        context.return_data = context.db.list_tuple_to_list_dict(raw_data)
    logit.debug(f"returned data: {context.return_data}")

@when('I set up a parameters search')
def setup_parameters_search(context):
    """
    Set up a parameter search
    """
    context.parameters = {
        'exact_list': None,
        'start_time': None,
        'end_time': None
    }
    logit.debug('New parameter search set up')

@when('I add {parameter}={argument}')
def update_parameter_search(context, parameter, argument):
    """
    Given parameter and argument, update the context.parameter search
    """
    if parameter not in context.parameters.keys():
        logit.warning(f"Parameter {parameter} not found in {context.parameters.keys()}")
        raise KeyError('parameter not in list of parameters available')
    if parameter == 'exact_list':
        if context.parameters['exact_list'] == None:
            context.parameters['exact_list'] = []
        logit.debug(f"added numbers {validator.is_exact_list(argument)}")
        context.parameters['exact_list'].extend(validator.is_exact_list(argument))
    elif parameter in ['start_time', 'end_time']:
        context.parameters[parameter] = validator.is_datetime(argument)
        logit.debug(f"updating {parameter} {validator.is_exact_list(argument)}")
    else:
        logit.warning(f'The provided parameter is not in the context parameters')
        raise KeyError('parameter not in list of parameters available')
    logit.debug(f"parameters updated {parameter}:{argument}")

@when('I use the parameters to get data from the database')
def database_parameter_search(context):
    """
    Based on the parameters updated before, grab results from the database. 
    """
    logit.info(f"using parameters to get data from the database {context.parameters}")
    context.selection = context.db.query_database(context.parameters)
    logit.debug(f"data from the database {context.selection}")

@then('I verify the database response matches {json_file}')
def compare_to_json_data(context, json_file):
    """
    Verify the database matches what was supposed to be saved.
    """
    comparer = load_weather_data_from_file(context, json_file)
    logit.debug('comparing responses')
    logit.debug(f"context data: {context.selection}")
    logit.debug(f"comparer data: {comparer}")
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

@then('I verify the interpreted data matches {json_file}')
def compare_database_returned_data(context, json_file):
    """
    Verify the database transitional files were altered the way they are supposed to. 
    """
    comparer = load_weather_data_from_file(context, json_file)
    logit.debug('comparing responses')
    logit.debug(f"context data: {context.return_data}")
    logit.debug(f"comparer data: {comparer}")
    if any([True for key in context.return_data[0].keys() if key not in comparer[0].keys()]):
        logit.warning(f"There is a key in context that is not in comparer")
        logit.warning(f"Context keys: {context.return_data[0].keys()}")
        logit.warning(f"Compare keys: {comparer.keys()}")
        raise KeyError("There are missing keys between context and comparer")
    if any([True for key in comparer[0].keys() if key not in context.return_data[0].keys()]):
        logit.warning(f"There is a key in comparer that is not in context")
        logit.warning(f"Context keys: {context.return_data[0].keys()}")
        logit.warning(f"Compare keys: {comparer.keys()}")
        raise KeyError("There are missing keys between context and comparer")
    for key, value in comparer[0].items():
        if value != context.return_data[0][key]:
            logit.warning(f"Data does not match for {key} {context.return_data[0][key]} {value}")
            raise ValueError('The data run through the database does not match the comparer data')
    logit.info(f"The comparison matches")

