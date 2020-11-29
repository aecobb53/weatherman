from behave import given, when, then
import datetime
import json
import yaml

import weather_butler

# Logging
import steps_logging
logit, logger = steps_logging.setup()

# Config
import steps_config
config = steps_config.load_config()

@given('I start with a new url from {private_path} and {public_path}')
def new_url(context, private_path, public_path):
    """
    Right now I have two instances of weather bulter floating around. 
    I might consolidate them but for the time being the one attached to context is the only 
    one used for polling. 
    """
    context.WB = weather_butler.WeatherButler(
        config['support_path'] + config['private_config_name'],
        config['url'],
        config['etc_path'] + config['key_name'],
    )
    logit.debug('weather butler inited')

@when('I map the url')
def map_url(context):
    """
    Whats the current url
    """
    context.url, context.args = context.WB.format_request_city_id_list(
        config['url'],
        config['locations'].values(),
        context.WB.key['Weather_Key']
    )
    logit.debug(f"url mapped: url:{context.url}, args:{context.args}")

@then('I verify the url matches {example_file} {json_key}')
def compare_urls(context, example_file, json_key):
    """
    Comparing the url to make sure its correct
    """
    example_file = config['support_path'] + example_file
    logit.debug(f"looking for {json_key}")
    with open(example_file, 'r') as eyf:
        json_data = yaml.load(eyf, Loader=yaml.FullLoader)
    if any([True for k in json_data['group_arguments'].keys() if k not in context.args.keys()]):
        logit.warning(f"The context keys are: {context.args.keys()}")
        logit.warning(f"The compare keys are: {json_data['group_arguments'].keys()}")
        logit.error(f'there are missing keys in the url that show up in the json file')
        raise IndexError('There are missing keys')
    for k in json_data['group_arguments'].keys():
        if json_data['group_arguments'][k] != context.args[k]:
            logit.warning(f"The current key: {k}")
            logit.warning(f"The context data: {context.args[k]}")
            logit.warning(f"Does not match")
            logit.warning(f"The compare data: {json_data['group_arguments'][k]}")
            logit.error(f"the url args dont match the json file")
            raise ValueError('The data does not match')
    logit.info('The url is correct')

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
        for item in report:
            if not isinstance(item, dict):
                logit.error(f'not proper date format. Expected a dict {type(item)}')
                raise TypeError('The data was the wrong type')

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
        context.request, context.request_list = context.WB.get_response(
            context.url, 
            context.args
        )
        if context.request.status_code != 200:
            logit.warn(f"url used: {context.url}")
            logit.warn(f"args used: {context.args}")
            logit.error(f'The api return a wrong code of {context.request.status_code}')
            raise ValueError(f'An eronius code was returned {context.request.status_code}')
        logit.info('The GET was succesful')
