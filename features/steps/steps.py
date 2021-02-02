import datetime
import json
import yaml
from behave import given, when, then

from weatherman import weather_butler
from weatherman import sql_butler

# Logging
import steps_logging
logit, logger = steps_logging.setup()

# # Main app
# import main

# @given('I init the main app')
# def init_main_app(context):
#     """
#     Init the main app. 
#     """
#     context.main = main.WeatherMan()
#     logit.debug('initing the main app')

