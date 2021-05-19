import datetime
# import time
import json
import os
import yaml

from weatherman import weather_butler
from weatherman import sql_butler
from bin import logger

appname = 'weatherman'
master_config_path = 'etc/weatherman.yml'

# Logging
"""
I init the logger so i can use it for the api calls.
Because i dont want it to log to the main log i use a startup log that should forever be empy
"""
# logger = logger.Logger(appname, app_name_in_file=True, log_suffix='startup')
# logit = self.logger.return_self.logit()
# default_log_file = self.logger.log_file


class WeatherMan:
    """
    Historic weather data is hard to comeby. There is Weatherunderground but it would just
    be easier to gather the data and generate our own reports.
    I gather my weather data from https://openweathermap.org.
    """

    def __init__(self, passed_logger=None, passed_logit=None):

        # Variables
        self.environment = None
        self.testing = None
        self.autopolling = None
        self.config = None
        self._state = None
        self._setup = None
        self._auto_polling = None
        self._dump_list = None
        self._report = None
        self._last_poll = None
        self._timing_intervul = None
        self._db_name = None

        # ENV
        self.environment = os.environ.get('ENVIRONMENT')

        if os.environ.get('TESTING').upper() == 'TRUE':
            self.testing = True
        elif os.environ.get('TESTING').upper() == 'FALSE':
            self.testing = False
        else:
            raise ValueError('TESTING variable not set')

        if os.environ.get('AUTOPOLLING').upper() == 'TRUE':
            self.auto_polling = True
        elif os.environ.get('AUTOPOLLING').upper() == 'FALSE':
            self.auto_polling = False
        else:
            raise ValueError('AUTOPOLLING variable not set')

        # Config
        self.load_config()
        self.setup = False

        # Logging
        logging_dct = self.config['environments'][self.environment]['log_parameters']
        if passed_logit is None:
            self.logger = logger.Logger(
                appname,
                f_level=logging_dct['f_level'],
                c_level=logging_dct['c_level'],
                log_directory=logging_dct['log_directory'],
                log_prefix=logging_dct['log_prefix'],
                log_suffix=logging_dct['log_suffix'],
                app_name_in_file=logging_dct['app_name_in_file'],
                date_in_file=logging_dct['date_in_file'],
                time_in_file=logging_dct['time_in_file'],
                utc_in_file=logging_dct['utc_in_file'],
                short_datetime=logging_dct['short_datetime'],
                maxBytes=logging_dct['maxBytes'],
                backupCount=logging_dct['backupCount'],
                create_ch=logging_dct['create_ch'],
                create_sh=logging_dct['create_sh'])
            self.logit = self.logger.return_logit()
            default_log_file = self.logger.file_name
        else:
            self.logger = passed_logger
            self.logit = passed_logit

        # Variables
        try:
            self.weather_butler = weather_butler.WeatherButler(
                self.config['private_config_path'],
                self.config['owma_url'],
                self.config['key_path']
            )
            self.config['locations'] = self.weather_butler.config['locations']
            self.update_state(self.config['locations'])
        except FileNotFoundError:
            self.setup = True

        self.db_name = self.config['db_name'] + \
            self.config['environments'][self.environment]['db_addition']
        self.db = sql_butler.SQLButler(self.db_name)
        self.db.create_database()

        self.update_state({'env': self.environment})
        self.update_state({'db_name': self.db_name})
        self.update_state({'setup_needed': self.setup})
        self.update_state({'timing_intervul': self.timing_intervul})
        self.update_state({'testing': self.testing})
        self.update_state({'db_name': self.db_name})
        self.update_state({'working_directory': os.getcwd()})

        # Wrapping up
        self.logit.info(f"Starting in {self.environment}")
        self.logit.debug(f'State: {self.state}')

    # Getters/Setters
    # Setup
    @property
    def setup(self):
        if self._setup is None:
            return False
        return self._setup

    @setup.setter
    def setup(self, value):
        self._setup = value
        self.update_state({'setup': self.setup})

    # Auto Polling
    @property
    def auto_polling(self):
        if self._auto_polling is None:
            return False
        return self._auto_polling

    @auto_polling.setter
    def auto_polling(self, value):
        self._auto_polling = value
        self.update_state({'auto_polling': self.auto_polling})

    # Timing Intervul
    @property
    def timing_intervul(self):
        if self._timing_intervul is None:
            return self.set_timing_intervul(self.config['minimum_poll_time'])
            """
            If you want to run this as often as possible for a free acount,
            remove the set_timing_intervul arguments so it runs 'auto'
            """
            # return self.set_timing_intervul()
        return self._timing_intervul

    @timing_intervul.setter
    def timing_intervul(self, value):
        self._timing_intervul = value
        self.update_state({'timing_intervul': self.timing_intervul})

    # Last Poll
    @property
    def last_poll(self):
        if self._last_poll is None:
            return datetime.datetime.strftime(
                self.db.get_first_and_last()[-1],
                self.config['datetime_str'])
        return self._last_poll

    @last_poll.setter
    def last_poll(self, value):
        self._last_poll = value
        self.update_state({'last_poll': self.last_poll})

    # DB Name
    @property
    def db_name(self):
        if self._db_name is None:
            return self.config['db_name']
        return self._db_name

    @db_name.setter
    def db_name(self, value):
        self._db_name = value
        self.update_state({'db_name': self.db_name})

    # Dump List
    @property
    def dump_list(self):
        if self._dump_list is None:
            return []
        return self._dump_list

    def append_dump_list(self, values):
        if not isinstance(values, list):
            values = [values]
        if self._dump_list is None:
            self._dump_list = []
        for value in values:
            self._dump_list.append(value)

    def clear_dump_list(self):
        self._dump_list = None

    # Report
    @property
    def report(self):
        if self._report is None:
            return {}
        return self._report

    def update_report(self, dct):
        if self._report is None:
            self._report = {}
        for key, value in dct.items():
            self._report[key] = value

    def clear_report(self):
        self._report = None

    # State
    @property
    def state(self):
        if self._state is None:
            return {}
        return self._state

    def update_state(self, dct):
        if self._state is None:
            self._state = {}
        for key, value in dct.items():
            self._state[key] = value

    # Config
    def load_config(self, path=master_config_path):
        with open(path) as ycf:
            self.config = yaml.load(ycf, Loader=yaml.FullLoader)
        try:
            self.config['locations'] = self.weather_butler.config['locations']
            self.update_state({'locations': self.config['locations']})
        except:
            pass
        return self.config

    # def set_logging(self, logging_dct=None):
    #     """
    #     Set or reset the logging parameters.
    #     """
    #     if logging_dct is None:
    #         logging_dct = self.config['environments'][self.environment]['log_parameters']
    #     for k, v in logging_dct.items():
    #         if v == 'None':
    #             logging_dct[k] = None
    #     self.logger.update_file(
    #         appname,
    #         f_level=logging_dct['f_level'],
    #         c_level=logging_dct['c_level'],
    #         log_rolling=logging_dct['log_rolling'],
    #         maxBytes=logging_dct['maxBytes'],
    #         backupCount=logging_dct['backupCount'],
    #         log_directory=logging_dct['log_directory'],
    #         log_prefix=logging_dct['log_prefix'],
    #         log_suffix=logging_dct['log_suffix'],
    #         app_name_in_file=logging_dct['app_name_in_file'],
    #         date_in_file=logging_dct['date_in_file'],
    #         time_in_file=logging_dct['time_in_file'],
    #         utc_in_file=logging_dct['utc_in_file'],
    #         short_datetime=logging_dct['short_datetime']
    #     )
    #     if self.logger.state['log_rolling'] is not None:
    #         self.logger.add_rotation()
    #     self.update_state({
    #         'f_level': logging_dct['f_level'],
    #         'c_level': logging_dct['c_level'],
    #         'log_rolling': logging_dct['log_rolling'],
    #         'maxBytes': logging_dct['maxBytes'],
    #         'backupCount': logging_dct['backupCount'],
    #         'log_file': self.logger.log_file,
    #     })

    def poll_weather(self):
        """
        Using the weather butler to grabb data from the weather website.
        """
        data = self.weather_butler.poll()
        self.logit.debug(f"request: {self.weather_butler.request}")
        self.logit.debug(f"request: {self.weather_butler.request.json()}")
        self.last_poll = datetime.datetime.now(tz=datetime.timezone.utc)
        return data

    def manage_polling(self):
        """
        I used to have a use case for needing two functions to do this...
        now i just have two functions...
        """
        self.logit.debug('managing polling?')
        data = self.poll_weather()
        self.db.multi_add(data)
        self.logit.debug('data added to db')

    def weather_dump(self, parameters):
        """
        Takes the parameters to filter out results from the database.
        """
        self.logit.debug(f'weather dump based on parameters {parameters}')
        data = self.db.query_database(parameters)
        for weatherdata in data:
            new_dct = {i: None for i in self.config['dump_webpage_list']}
            dct = dict(weatherdata)
            for i, j in dct.items():
                if i == 'time':
                    dct[i] = datetime.datetime.strftime(j, self.config['datetime_str'])
                if i == 'name':
                    for x, y in self.config['locations'].items():
                        if int(dct['city']) == int(y):
                            j = x
                            break
                if i in self.config['dump_webpage_list']:
                    new_dct[i] = j
            self.append_dump_list(new_dct)
        return self.dump_list

    def weather_report(self, data):
        """
        This takes a list of dumped weather data and saves off the important bits for a report
        """

        def recursive_search(value, key, index, lst, itterations):
            # Is this a duplicate weather response?

            dex = 0
            for thingy, el in enumerate(reversed(lst[:index])):
                if value == el[key]:
                    return True
                dex += 1
                if dex >= itterations:
                    return False
            return False

        report1 = {}
        report2 = {}
        for name, city in self.config['locations'].items():
            # create dict with the city names as the keys to keep all weather data together
            report1[name] = []
            for line in data:
                if line['name'] == name:
                    report1[name].append(line)
        for name, reports in report1.items():
            """
            Itterates through the new lists of weather data and
            places similar times together in to storms
            """
            report2[name] = [[]]
            report_index = 0
            for index, line in enumerate(reports):
                if index == 0:
                    report2[name][0].append(line)
                else:
                    if reports[index - 1]['time'] <= line['time'] - \
                        datetime.timedelta(
                            minutes=int(
                                self.config['storm_difference_time']
                            )):

                        report2[name].append([])
                        report_index += 1
                report2[name][report_index].append(line)
        report = {}
        for name, reports in report2.items():
            # Adds the first and last element into the final storm list
            # This is where i will add extra data such as notable weather fluxuations
            report[name] = []
            for index, event in enumerate(reports):
                if len(event) == 0:
                    continue
                elif len(event) == 1:
                    report[name].append(event)
                else:
                    report[name].append([event[0], event[-1]])
                    for itterate, line in enumerate(event):
                        if itterate in [0, len(event) - 1]:
                            continue
                        if not recursive_search(
                            line['sky_id'],
                            'sky_id',
                            itterate,
                            event,
                            self.config['storm_difference_itteration']
                        ):

                            report[name][index].insert(-1, line)
        self.logit.debug('Created a weather report')
        return report

    def write_report(self, report, file_name=None):
        """
        Takes the list of data, updates the datetime objects to strings and saves to a file.
        """
        json_report = {}
        for name, storms in report.items():
            json_report[name] = []
            for storm in storms:
                if len(storm) > 1:
                    storm_durration = str(storm[-1]['time'] - storm[0]['time'])
                else:
                    if self.config['single_storm_event_flag']:
                        """
                        If the single_storm_event_flag is true the single event storms
                        will be added. else they will be skipped.
                        """
                        storm_durration = '0'
                    else:
                        continue
                for line in storm:
                    if not isinstance(line['time'], str):
                        line['time'] = datetime.datetime.strftime(
                            line['time'],
                            self.config['datetime_str'])
                entry = {
                    'storm_start': storm[0]['time'],
                    'storm_end': storm[-1]['time'],
                    'storm_durration': storm_durration,
                    'start_dct': storm[0],
                    'end_dct': storm[-1],
                    'storm_events': storm,
                }
                json_report[name].append(entry)
        if file_name is None:
            file_name = self.config['weather_reports_dir'] + \
                'Weather_report_' + \
                datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%dT%H:%M:%SZ') + \
                '.json'
        self.update_report(json_report)
        with open(file_name, 'w') as new_report:
            json.dump(self.report, new_report, indent=2)
        self.logit.debug(f'Wrote a weatehr report to a file {file_name}')

    def clear_search(self):
        self.clear_dump_list()
        self.clear_report()

    def set_timing_intervul(self, intervul='auto'):
        """
        Set the amount of time between data pulls.
        If it is auto, it will calculate the minimum number of minutes
        between polls and take the largest value
        between that and the minimum poll timer in the config.
        """

        if intervul == 'auto' or not isinstance(intervul, int):
            try:
                calls_made = len(self.config['locations'])
                # calls_made = len(self.state['cities'].keys())
                month_minute_converion = 60 * 24 * self.config['estemated_days_per_month']
                minimum_intervul = month_minute_converion / \
                    self.config['max_calls_per_month'] * calls_made
                intervul = round(minimum_intervul * 10) / 10
            except KeyError:
                self.logit.debug('key error when trying to set timing intervul for auto or non int')
                intervul = int(self.config['minimum_poll_time'])
        self.timing_intervul = intervul
        return intervul

        # try:
        #     pass
        #     # if intervul == 'auto':
        #     #     calls_made = len(self.state['cities'].keys())
        #     #     month_minute_converion = 60 * 24 * self.config['estemated_days_per_month']
        #     #     minimum_intervul = month_minute_converion / \
        #     #         self.config['max_calls_per_month'] * calls_made
        #     #     intervul = minimum_intervul
        #     # self.timing_intervul = max(intervul, self.config['minimum_poll_time'])
        #     # self.state['timing_intervul'] = self.timing_intervul
        # except:
        #     self.timing_intervul = self.config['minimum_poll_time']
        #     self.auto_polling = False
        # self.timing_intervul
        # self.state['auto_polling'] = self.auto_polling # State should be updated when self.auto_polling is updated, if not this needs to be fixed!
        # return self.timing_intervul
        # return 10
