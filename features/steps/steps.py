import datetime
import json
from behave import given, when, then
import weather_butler
import sql_butler
import csv_butler

# Logging
import steps_logging
logit, logger = steps_logging.setup()

# # Weather bulter
# WB = weather_butler.WeatherButler()


@given('I create an empty {database_type}')
def database_setup(context, database_type):
    """
    Depending on a SQL or CSV database I want them to be run the same. 
    They need to be set up though. 
    """
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

@given('I start with a new url from {private_path} and {public_path}')
def new_url(context, private_path, public_path):
    """
    Right now I have two instances of weather bulter floating around. 
    I might consolidate them but for the time being the one attached to context is the only 
    one used for polling. 
    """
    dir_path = 'features/support/'
    context.WB = weather_butler.WeatherButler(dir_path+private_path, dir_path+public_path)
    logit.debug('weather butler inited')
    logit.debug(f'weather butler config {context.WB.config}')

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
    context.data = context.WB.format_response(raw_data['list'])
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

@when('I map the url')
def map_url(context):
    """
    Whats the current url
    """
    # logit.debug(f"{context.WB.config}  {context.WB.key}")
    # logit.debug(f"{type(context.WB.config)}  {type(context.WB.key)}")
    # logit.debug(f"{context.WB.config.keys()}  {context.WB.key.keys()}")
    # logit.debug(f"{context.WB.config.values()}  {context.WB.key.values()}")
    # logit.debug(f"{context.WB.config['url']}  {context.WB.config['locations'].values()}  {context.WB.key['Weather_Key']}")
    context.url, context.args = context.WB.format_request_city_id_list(context.WB.config['url'], context.WB.config['locations'].values(), context.WB.key['Weather_Key'])
    logit.debug(f"url:{context.url}, args:{context.args}")

@when('I poll owma')
def weather_butler_poll(context):
    """
    Use the run module
    """
    try:
        if context.run == False:
            logit.info('poll turned off')
    except:
        context.run = True
    if context.run == True:
        report = context.WB.poll()
        # logit.debug(f'report {report}')
        for item in report:
            # logit.debug(f'{type(item)}')
            if not isinstance(item, dict):
                logit.error(f'not proper date format. Expected a dict {type(item)}')
                raise TypeError('The data was the wrong type')

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

@then('I verify the url matches {json_file} {json_key}')
def compare_urls(context, json_file, json_key):
    """
    Comparing the url to make sure its correct
    """
    json_file = 'features/support/' + json_file
    logit.debug(f"looking for {json_key}")
    with open(json_file, 'r') as read_file:
        json_data = json.load(read_file)
    # for k,v in context.args.items():
    #     logit.debug(f"-----ARGS:{k}  :  {v}")
    # for k,v in json_data['group_arguments'].items():
    #     logit.debug(f"-----JSON:{k}  :  {v}")
    if any([True for k in json_data['group_arguments'].keys() if k not in context.args.keys()]):
        logit.error(f'there are missing keys in the url that show up in the json file')
        raise IndexError('There are missing keys')
    for k in json_data['group_arguments'].keys():
        if json_data['group_arguments'][k] != context.args[k]:
            logit.error(f'the url args dont match the json file')
            raise ValueError('The data does not match')
    logit.info('The url is correct')

@then('I get a response from owma')
def weather_bulter_response(context):
    """
    Verify the response is expected from the api
    """
    try:
        if context.run == False:
            logit.info('response turned off')
    except:
        context.run = True
    if context.run == True:
        context.request, context.request_list = context.WB.get_response(context.url, context.args)
        if context.request.status_code != 200:
            logit.error(f'The api return a wrong code of {context.request.status_code}')
            raise ValueError(f'An eronius code was returned {context.request.status_code}')
        logit.info('The GET was succesful')
        # # logit.debug(f'request {context.request}')
        # logit.debug(f'list {context.request_list}')
        # logit.debug(f'list {len(context.request_list)}')
        # logit.debug(f'list {json.dumps(context.request_list, indent=4)}')
        # for item in context.request_list:
        #     logit.debug(f"item:::::{item}")
        #     logit.debug(f"keys: {item.keys()}")
        #     logit.debug(f"keys: {item.values()}")
        #     logit.debug(f"types {[type(i) for i in item.values()]}")
        #     logit.debug(f" ")
