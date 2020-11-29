from behave import given, when, then
import datetime
import json
import yaml

import data_validator

# Logging
import steps_logging
logit, logger = steps_logging.setup()

# Config
import steps_config
config = steps_config.load_config()
main_config = steps_config.load_config('weatherman.yml', 'etc/')

@given('I set up a new datetime validator')
def new_validator(context):
    """
    Spin up a new validator. 
    """
    logit.debug('setting up data validator')
    context.validator = data_validator.DataValidator()

@when('I run {data} through the datetime validator')
def run_data(context, data):
    """
    Data checked for validation. 
    """
    logit.debug(f'checking data {data} which is a {type(data)} datatype')
    context.data_returned = context.validator.is_datetime(data)

@when('I run {data} through the exact list validator')
def exact_list_data(context, data):
    """
    Data checked for validation. 
    """
    logit.debug(f'checking data {data} which is a {type(data)} datatype')
    context.data_returned = context.validator.is_exact_list(data)

@then('I verify the exact match data matches {result}')
def check_exact_list_data(context, result):
    """
    Verify data matches. 
    """
    comparer = [int(r) for r in result.split(',')]
    if context.data_returned != comparer:
        logit.warning(f"The data returned does not matche the comparrer")
        logit.warning(f"The data: {context.data_returned}")
        logit.warning(f"The comparer: {comparer}")
        raise ValueError('exact list value error')
    logit.info(f"Data matches")

@then('I verify the datetime data matches {result}')
def check_datetime_data(context, result):
    """
    Verify data matches. 
    """
    comparer = datetime.datetime.strptime(result, config['datetime_str'])
    if context.data_returned != comparer:
        logit.warning(f"The data returned does not matche the comparrer")
        logit.warning(f"The data: {context.data_returned}")
        logit.warning(f"The comparer: {comparer}")
        raise ValueError('datetime value error')
    logit.info(f"Data matches")

