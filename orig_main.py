import datetime
import time
import json
import os
import yaml
import threading

from fastapi import FastAPI, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from typing import Optional, List  # noqa

# from weatherman import *
from weatherman import weather_butler
from weatherman import data_validator
from bin import setup_weatherman
from weatherman import sql_butler
from bin import logger

appname = 'weatherman'
master_config_path = 'etc/weatherman.yml'

# Logging
"""
I init the logger so i can use it for the api calls.
Because i dont want it to log to the main log i use a startup log that should forever be empy
"""
logger = logger.Logger(appname, app_name_in_file=True, log_suffix='startup')
logit = logger.return_logit()
default_log_file = logger.log_file

logit.debug('logging the this thingy here')


class WeatherMan:
    """
    Historic weather data is hard to comeby. There is Weatherunderground but it would just
    be easier to gather the data and generate our own reports.
    I gather my weather data from https://openweathermap.org.
    """

    def __init__(self):

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
        self.set_logging()
        logger.update_file_level(
            self.config['environments'][self.environment]['log_parameters']['f_level'])
        logger.update_consol_level(
            self.config['environments'][self.environment]['log_parameters']['c_level'])

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
        self.update_state({'timing_intervul': self.setup})
        self.update_state({'testing': self.testing})
        self.update_state({'db_name': self.db_name})
        self.update_state({'working_directory': os.getcwd()})

        # Wrapping up
        logit.info(f"Starting in {self.environment}")
        logit.info(f"logging levels set to fh:{self.state['f_level']} \
            ch:{self.state['c_level']} testing:{self.testing}")
        logit.debug(f'State: {self.state}')

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
            return self.set_timing_intervul()
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

    def set_logging(self, logging_dct=None):
        """
        Set or reset the logging parameters.
        """
        if logging_dct is None:
            logging_dct = self.config['environments'][self.environment]['log_parameters']
        for k, v in logging_dct.items():
            if v == 'None':
                logging_dct[k] = None
        logger.update_file(
            appname,
            f_level=logging_dct['f_level'],
            c_level=logging_dct['c_level'],
            log_rolling=logging_dct['log_rolling'],
            maxBytes=logging_dct['maxBytes'],
            backupCount=logging_dct['backupCount'],
            log_directory=logging_dct['log_directory'],
            log_prefix=logging_dct['log_prefix'],
            log_suffix=logging_dct['log_suffix'],
            app_name_in_file=logging_dct['app_name_in_file'],
            date_in_file=logging_dct['date_in_file'],
            time_in_file=logging_dct['time_in_file'],
            utc_in_file=logging_dct['utc_in_file'],
            short_datetime=logging_dct['short_datetime']
        )
        if logger.state['log_rolling'] is not None:
            logger.add_rotation()
        self.update_state({
            'f_level': logging_dct['f_level'],
            'c_level': logging_dct['c_level'],
            'log_rolling': logging_dct['log_rolling'],
            'maxBytes': logging_dct['maxBytes'],
            'backupCount': logging_dct['backupCount'],
            'log_file': logger.log_file,
        })

    def poll_weather(self):
        """
        Using the weather butler to grabb data from the weather website.
        """
        data = self.weather_butler.poll()
        logit.debug(f"request: {self.weather_butler.request}")
        logit.debug(f"request: {self.weather_butler.request.json()}")
        self.last_poll = datetime.datetime.now(tz=datetime.timezone.utc)
        return data

    def manage_polling(self):
        """
        I used to have a use case for needing two functions to do this...
        now i just have two functions...
        """
        logit.debug('managing polling?')
        data = self.poll_weather()
        self.db.multi_add(data)
        logit.debug('data added to db')

    def weather_dump(self, parameters):
        """
        Takes the parameters to filter out results from the database.
        """
        logit.debug(f'weather dump based on parameters {parameters}')
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
                    # memory = {
                    #     'sky_id': []
                    # }
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
        logit.debug('Created a weather report')
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
                    # new_start = storm[0]['time'].strftime("%Y-%m-%dT%H:%M:%SZ")
                    # new_end = storm[-1]['time'].strftime("%Y-%m-%dT%H:%M:%SZ")
                else:
                    if self.config['single_storm_event_flag']:
                        """
                        If the single_storm_event_flag is true the single event storms
                        will be added. else they will be skipped.
                        """
                        storm_durration = '0'
                        # new_start = storm[0]['time'].strftime("%Y-%m-%dT%H:%M:%SZ")
                        # new_end = storm[0]['time'].strftime("%Y-%m-%dT%H:%M:%SZ")
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
        logit.debug(f'Wrote a weatehr report to a file {file_name}')

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
        try:
            if intervul == 'auto':
                calls_made = len(self.state['cities'].keys())
                month_minute_converion = 60 * 24 * self.config['estemated_days_per_month']
                minimum_intervul = month_minute_converion / \
                    self.config['max_calls_per_month'] * calls_made
                intervul = minimum_intervul
            self.timing_intervul = max(intervul, self.config['minimum_poll_time'])
            self.state['timing_intervul'] = self.timing_intervul
        except:
            self.timing_intervul = self.config['minimum_poll_time']
            self.auto_polling = False
        self.state['auto_polling'] = self.auto_polling
        return self.timing_intervul


"""
Spin up the app using fastapp and uvicorn. See the docker-compose file for whats
actually run
"""


app = FastAPI()  # noqa
global WM
WM = WeatherMan()
validator = data_validator.DataValidator()
SW = setup_weatherman.SetupWeatherman()

templates = Jinja2Templates(directory="templates/")
app.mount("/static", StaticFiles(directory="static"), name="static")
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def return_state():
    # state_list = []
    # for i,j in WM.state.items():
    #     if i == 'cities':
    #         state_list.append(i + ':')
    #         for x,y in j.items():
    #             state_list.append('-' + x + ' : ' + str(y))
    #     elif i == 'fh_logging':
    #         state_list.append('file_logging' + ' : ' + j)
    #     elif i == 'ch_logging':
    #         state_list.append('consol_logging' + ' : ' + j)
    #     else:
    #         state_list.append(i + ' : ' + str(j))
    #     logit.info(f"{i} : {j}")
    return WM.state.items()
    # return state_list


def generage_parameters(
    thunderstorm=False,
    drizzle=False,
    rain=False,
    snow=False,
    atmosphere=False,
    clouds=False,
    clear=False,
    exact_list=None,
    start_time=None,
    end_time=None
):

    if exact_list is None:
        exact_list = ''
    if start_time is None:
        start_time = ''
    if end_time is None:
        end_time = ''

    if thunderstorm:
        for num in WM.config['accepted_owma_codes']['thunderstorm']:
            exact_list += f",{str(num)}"

    if drizzle:
        for num in WM.config['accepted_owma_codes']['drizzle']:
            exact_list += f",{str(num)}"

    if rain:
        for num in WM.config['accepted_owma_codes']['rain']:
            exact_list += f",{str(num)}"

    if snow:
        for num in WM.config['accepted_owma_codes']['snow']:
            exact_list += f",{str(num)}"

    if atmosphere:
        for num in WM.config['accepted_owma_codes']['atmosphere']:
            exact_list += f",{str(num)}"

    if clouds:
        for num in WM.config['accepted_owma_codes']['clouds']:
            exact_list += f",{str(num)}"

    if clear:
        for num in WM.config['accepted_owma_codes']['clear']:
            exact_list += f",{str(num)}"

    try:
        logit.debug('validating exact_list')
        exact_list = validator.is_exact_list(exact_list)
    except:
        exact_list = None

    try:
        logit.debug('validating start_time')
        start_time = validator.is_datetime(start_time)
    except:
        start_time = None

    try:
        logit.debug('validating wnd_time')
        end_time = validator.is_datetime(end_time)
    except:
        end_time = None

    parameters = {
        'exact_list': exact_list,
        'start_time': start_time,
        'end_time': end_time,
    }
    return parameters


def submit_bug(
    prod=None,
    dev=None,
    test=None,
    unit_test=None,
    website=None,
    home=None,
    reports=None,
    dump=None,
    realtime=None,
    state=None,
    poll=None,
    about=None,
    report=None,
    event_time=None,
    description=None
):
    entry_time = datetime.datetime.strftime(
        datetime.datetime.now(tz=datetime.timezone.utc),
        WM.config['datetime_str']
    )

    valid = False
    none_list = [
        prod,
        dev,
        test,
        unit_test,
        website,
        home,
        reports,
        dump,
        realtime,
        state,
        poll,
        about,
        report]
    if event_time == '' and description == '':
        for check in none_list:
            if check is not None:
                valid = True
                break
    else:
        valid = True

    bug_info = {
        'env': [],
        'tab': [],
        'datetime': [],
        'description': '',
    }

    bug_info['env'] += ['prod'] if prod is not None else []
    bug_info['env'] += ['dev'] if dev is not None else []
    bug_info['env'] += ['test'] if test is not None else []
    bug_info['env'] += ['unit_test'] if unit_test is not None else []
    bug_info['env'] += ['website'] if website is not None else []

    bug_info['tab'] += ['home'] if home is not None else []
    bug_info['tab'] += ['reports'] if reports is not None else []
    bug_info['tab'] += ['dump'] if dump is not None else []
    bug_info['tab'] += ['realtime'] if realtime is not None else []
    bug_info['tab'] += ['state'] if state is not None else []
    bug_info['tab'] += ['poll'] if poll is not None else []
    bug_info['tab'] += ['about'] if about is not None else []
    bug_info['tab'] += ['report'] if report is not None else []

    if event_time is None or event_time == '':
        bug_info['datetime'] = entry_time
    else:
        bug_info['datetime'] = event_time

    if description is None or description == '':
        bug_info['description'] = ''
    else:
        bug_info['description'] = description

    logit.info(f"bug report submitted {bug_info}")

    if valid:
        filename = 'bug_report_' + entry_time + '.json'
        with open(WM.config['bug_report_dir'] + filename, 'w') as br:
            json.dump(bug_info, br, indent=4)
        return True
    else:
        logit.info('Invalid entry, skipping')
        return False


def execute_setup(
    action: str = None,
    key: str = None,
    delete: List[str] = Query([]),
    newname: List[str] = Query([]),
    city: List[str] = Query([]),
    citySearch: str = None,
    cityId: str = None,
    stateAbbr: str = None,
    countryAbbr: str = None,
    lat: str = None,
    lon: str = None
):

    # Key
    if key is not None and key != '':
        SW.key = key

    # Search parameterse
    if citySearch is not None and citySearch != '':
        SW.update_parameters('name', citySearch)
    if cityId is not None and cityId != '':
        SW.update_parameters('id', cityId)
    if stateAbbr is not None and stateAbbr != '':
        SW.update_parameters('state', stateAbbr)
    if countryAbbr is not None and countryAbbr != '':
        SW.update_parameters('country', countryAbbr)
    if lat is not None and lat != '':
        SW.update_parameters('lat', lat)
    if lon is not None and lon != '':
        SW.update_parameters('lon', lon)

    # Modifying to list
    # Updating
    location_lst = [(k, v) for k, v in SW.locations.items()]
    for index, element in enumerate(newname):
        if element != '':
            SW.update_locations(location_lst[index][0], element)
    # Removing
    location_lst = [(k, v) for k, v in SW.locations.items()]
    if delete != ['']:
        for tup in location_lst:
            if tup[1] in delete:
                SW.remove_location(tup[0])
    # Adding
    for element in city:
        element_info = element.split('=')
        SW.add_locations(element_info[0], element_info[1])

    if action == 'refresh':
        print('Refreshing ')
    elif action == 'setup':
        print('Setting up app')
        SW.verify_directories()
        SW.create_key_file()
        SW.create_locations_file()
        try:
            WM.__init__()
            WM.setup = False
            WM.state['setup_needed'] = WM.setup
            try:
                SW.cleanup_setup_files()
            except:
                pass
            return True
        except FileNotFoundError:
            WM.setup = True
            logit.warning('app not set up yet! setting setup flag to {setup}')
            return False

# WM.setup = True


def is_api_setup():
    if WM.setup:
        logit.warning('app not set up, redirecting to setup')
        return 'App is not set up yet! run the setup endpoint to finish setup'
        # response = RedirectResponse(url='/api/setup')
        # return response
    else:
        return False


def is_setup():
    if WM.setup:
        logit.warning('app not set up, redirecting to setup')
        response = RedirectResponse(url='/setup')
        return response
    else:
        return False


# Internal Cron
def timing_of_app(time_to_poll=WM.timing_intervul):
    """
    If auto polling is active it will poll on the designated time interul.
    """
    print(WM.auto_polling)
    while True:
        try:
            if WM.auto_polling:
                WM.manage_polling()
        except:
            pass
        time.sleep(time_to_poll * 60)


auto_poller = threading.Thread(target=timing_of_app)
auto_poller.daemon = True
auto_poller.start()


# Root
@app.get('/')
async def root(request: Request):
    """
    The home page has some explanation of what each tab does.
    Eventually it would be great to have picutres of the tabs here as well.
    """
    logit.debug('home endpoint hit')
    return templates.TemplateResponse("main.html", {"request": request})


# About
@app.get("/about-weatherman", response_class=HTMLResponse)
async def about_weatherman(request: Request):
    """
    If people had more questions I wanted to have a place to answer some of them.
    """
    logit.debug('about-weatherman endpoint hit')
    return templates.TemplateResponse("about_weatherman.html", {"request": request})


# State
@app.get('/api/state')
async def return_api_args(request: Request):
    """
    The api endpoint for state.
    """
    logit.debug('api state endpoint hit')
    logit.warning(f"Setup is {WM.setup}")
    resp = is_api_setup()
    if resp:
        return resp
    state_response = return_state()
    return state_response


@app.get('/state')
async def return_args(request: Request):
    """
    This returns the state of the app.
    Useful for some debugging.
    """
    logit.debug('state endpoint hit')
    state_list = []
    logit.warning(f"Setup is {WM.setup}")
    resp = is_setup()
    if resp:
        return resp
    for i, j in return_state():
        if i == 'cities':
            state_list.append(i + ':')
            for x, y in j.items():
                state_list.append('-' + x + ' : ' + str(y))
        elif i == 'fh_logging':
            state_list.append('file_logging' + ' : ' + j)
        elif i == 'ch_logging':
            state_list.append('consol_logging' + ' : ' + j)
        else:
            state_list.append(i + ' : ' + str(j))
        logit.info(f"{i} : {j}")
    return templates.TemplateResponse("state.html", {"request": request, 'list': state_list})


# Poll
@app.get('/api/poll')
async def poll_api_data(request: Request):
    """
    This fires off a poll to the app.
    """
    logit.debug('api poll endpoint hit')
    resp = is_api_setup()
    if resp:
        return resp
    WM.manage_polling()


@app.get('/poll')
async def poll_data(request: Request):
    """
    Poll OWMA for new weather data.
    """
    logit.debug('about to poll data')
    resp = is_setup()
    if resp:
        return resp

    if WM.environment == 'dev':
        logit.warning('While auto pulling is defaulted to off, \
            running poll will toggle it for the tiem being')
        if WM.auto_polling:
            WM.auto_polling = False
            WM.state['auto_polling'] = WM.auto_polling
        else:
            WM.auto_polling = True
            WM.state['auto_polling'] = WM.auto_polling

    logit.debug('passed the setup check')
    WM.manage_polling()
    timestamp = datetime.datetime.strftime(WM.last_poll, WM.config['datetime_str'])
    return templates.TemplateResponse("poll.html", {"request": request, "last_poll": timestamp})


# Dump
@app.get('/api/dump/search')
def read_items(
        thunderstorm=False,
        drizzle=False,
        rain=False,
        snow=False,
        atmosphere=False,
        clouds=False,
        clear=False,
        exact_list=None,
        start_time=None,
        end_time=None):
    """
    Takes a query and tells the app to grab data.
    """

    logit.debug('api dump/search endpoint hit')
    logit.debug(f"thunderstorm: {thunderstorm}")
    logit.debug(f"drizzle: {drizzle}")
    logit.debug(f"rain: {rain}")
    logit.debug(f"snow: {snow}")
    logit.debug(f"atmosphere: {atmosphere}")
    logit.debug(f"clouds: {clouds}")
    logit.debug(f"clear: {clear}")
    logit.debug(f"exact_list: {exact_list}")
    logit.debug(f"start_time: {start_time}")
    logit.debug(f"end_time: {end_time}")

    resp = is_api_setup()
    if resp:
        return resp

    parameters = generage_parameters(
        thunderstorm,
        drizzle,
        rain,
        snow,
        atmosphere,
        clouds,
        clear,
        exact_list,
        start_time,
        end_time,
    )
    WM.weather_dump(parameters)
    data = WM.dump_list
    WM.clear_search()
    return data


@app.get('/dump')
async def data_dump(request: Request):
    """
    This returns the html to load the results from the database dump.
    """
    logit.debug('dump endpoint hit')
    resp = is_api_setup()
    if resp:
        return resp
    data = WM.dump_list
    WM.clear_search()
    return templates.TemplateResponse("dump.html", {"request": request, 'list': data})


@app.get('/dump/search/')
def read_items_search(
        request: Request,
        thunderstorm=False,
        drizzle=False,
        rain=False,
        snow=False,
        atmosphere=False,
        clouds=False,
        clear=False,
        exact_list=None,
        start_time=None,
        end_time=None):
    """
    Takes a query and tells the app to grab data.
    """

    logit.debug('dump/search endpoint hit')
    logit.debug(f"thunderstorm: {thunderstorm}")
    logit.debug(f"drizzle: {drizzle}")
    logit.debug(f"rain: {rain}")
    logit.debug(f"snow: {snow}")
    logit.debug(f"atmosphere: {atmosphere}")
    logit.debug(f"clouds: {clouds}")
    logit.debug(f"clear: {clear}")
    logit.debug(f"exact_list: {exact_list}")
    logit.debug(f"start_time: {start_time}")
    logit.debug(f"end_time: {end_time}")

    resp = is_setup()
    if resp:
        return resp

    parameters = generage_parameters(
        thunderstorm,
        drizzle,
        rain,
        snow,
        atmosphere,
        clouds,
        clear,
        exact_list,
        start_time,
        end_time,
    )
    WM.weather_dump(parameters)
    response = RedirectResponse(url='/dump')
    return response


# Bug
@app.get("/api/bug-report/entry", response_class=HTMLResponse)
async def api_read_items(
        prod=None,
        dev=None,
        test=None,
        unit_test=None,
        website=None,
        home=None,
        reports=None,
        dump=None,
        realtime=None,
        state=None,
        poll=None,
        about=None,
        report=None,
        event_time=None,
        description=None):
    """
    Receive bug-report.
    """

    logit.debug('api bug-report endpoint hit')
    logit.debug(f"prod: {prod}")
    logit.debug(f"dev: {dev}")
    logit.debug(f"test: {test}")
    logit.debug(f"unit-test: {unit_test}")
    logit.debug(f"website: {website}")
    logit.debug(f"home: {home}")
    logit.debug(f"reports: {reports}")
    logit.debug(f"dump: {dump}")
    logit.debug(f"realtime: {realtime}")
    logit.debug(f"state: {state}")
    logit.debug(f"poll: {poll}")
    logit.debug(f"about: {about}")
    logit.debug(f"report: {report}")
    logit.debug(f"event_time: {event_time}")
    logit.debug(f"description: {description}")

    resp = is_api_setup()
    if resp:
        return resp

    if submit_bug(
        prod,
        dev,
        test,
        unit_test,
        website,
        home,
        reports,
        dump,
        realtime,
        state,
        poll,
        about,
        report,
        event_time,
        description,
    ):
        return 'Successful'
    else:
        return 'Failed'


@app.get("/bug-report", response_class=HTMLResponse)
async def submit_bug_report(request: Request):
    return templates.TemplateResponse("bug_report.html", {"request": request})


@app.get("/bug-report/entry", response_class=HTMLResponse)
async def read_bug(
        request: Request,
        prod=None,
        dev=None,
        test=None,
        unit_test=None,
        website=None,
        home=None,
        reports=None,
        dump=None,
        realtime=None,
        state=None,
        poll=None,
        about=None,
        report=None,
        event_time=None,
        description=None):
    """
    Receive bug-report.
    """

    logit.debug('bug-report endpoint hit')
    logit.debug(f"prod: {prod}")
    logit.debug(f"dev: {dev}")
    logit.debug(f"test: {test}")
    logit.debug(f"unit-test: {unit_test}")
    logit.debug(f"website: {website}")
    logit.debug(f"home: {home}")
    logit.debug(f"reports: {reports}")
    logit.debug(f"dump: {dump}")
    logit.debug(f"realtime: {realtime}")
    logit.debug(f"state: {state}")
    logit.debug(f"poll: {poll}")
    logit.debug(f"about: {about}")
    logit.debug(f"report: {report}")
    logit.debug(f"event_time: {event_time}")
    logit.debug(f"description: {description}")

    resp = is_setup()
    if resp:
        return resp

    if submit_bug(
        prod,
        dev,
        test,
        unit_test,
        website,
        home,
        reports,
        dump,
        realtime,
        state,
        poll,
        about,
        report,
        event_time,
        description,
    ):
        response = RedirectResponse(url='/')
        return response
    else:
        response = RedirectResponse(url='/bug-report')
        return response


# Report
@app.get('/api/report/search/')
def api_report_items(
        thunderstorm=False,
        drizzle=False,
        rain=False,
        snow=False,
        atmosphere=False,
        clouds=False,
        clear=False,
        exact_list=None,
        start_time=None,
        end_time=None):
    """
    Takes a query and tells the app to grab data.
    """

    logit.debug('api report/search endpoint hit')
    logit.debug(f"thunderstorm: {thunderstorm}")
    logit.debug(f"drizzle: {drizzle}")
    logit.debug(f"rain: {rain}")
    logit.debug(f"snow: {snow}")
    logit.debug(f"atmosphere: {atmosphere}")
    logit.debug(f"clouds: {clouds}")
    logit.debug(f"clear: {clear}")
    logit.debug(f"exact_list: {exact_list}")
    logit.debug(f"start_time: {start_time}")
    logit.debug(f"end_time: {end_time}")

    resp = is_api_setup()
    if resp:
        return resp

    parameters = generage_parameters(
        thunderstorm,
        drizzle,
        rain,
        snow,
        atmosphere,
        clouds,
        clear,
        exact_list,
        start_time,
        end_time,
    )
    report = WM.weather_report(WM.weather_dump(parameters))
    WM.clear_search()
    return report


@app.get("/report", response_class=HTMLResponse)
async def report(request: Request):
    """
    Saves a report to the out/ direcotry.
    Eventually it may return the report but i dont have that working yet.
    """
    logit.debug('report endpoint hit')
    resp = is_setup()
    if resp:
        return resp
    data = WM.report
    WM.clear_search()
    return templates.TemplateResponse("report.html", {"request": request, 'dict': data})


@app.get('/report/search/')
def report_items(
        request: Request,
        thunderstorm=False,
        drizzle=False,
        rain=False,
        snow=False,
        atmosphere=False,
        clouds=False,
        clear=False,
        exact_list=None,
        start_time=None,
        end_time=None):
    """
    Takes a query and tells the app to grab data.
    """

    logit.debug('report/search endpoint hit')
    logit.debug(f"thunderstorm: {thunderstorm}")
    logit.debug(f"drizzle: {drizzle}")
    logit.debug(f"rain: {rain}")
    logit.debug(f"snow: {snow}")
    logit.debug(f"atmosphere: {atmosphere}")
    logit.debug(f"clouds: {clouds}")
    logit.debug(f"clear: {clear}")
    logit.debug(f"exact_list: {exact_list}")
    logit.debug(f"start_time: {start_time}")
    logit.debug(f"end_time: {end_time}")

    resp = is_setup()
    if resp:
        return resp

    parameters = generage_parameters(
        thunderstorm,
        drizzle,
        rain,
        snow,
        atmosphere,
        clouds,
        clear,
        exact_list,
        start_time,
        end_time,
    )
    report = WM.weather_report(WM.weather_dump(parameters))
    WM.write_report(report)
    response = RedirectResponse(url='/report')
    return response


# Setup
@app.get("/api/setup")
async def api_setup(
        action: str = None,
        key: str = None,
        delete: List[str] = Query([]),
        newname: List[str] = Query([]),
        city: List[str] = Query([]),
        citySearch: str = None,
        cityId: str = None,
        stateAbbr: str = None,
        countryAbbr: str = None,
        lat: str = None,
        lon: str = None):

    logit.debug('api /setup endpoint hit')
    logit.debug(f"action: {action}")
    logit.debug(f"key: {key}")
    logit.debug(f"delete: {delete}")
    logit.debug(f"newname: {newname}")
    logit.debug(f"city: {city}")
    logit.debug(f"citySearch: {citySearch}")
    logit.debug(f"cityId: {cityId}")
    logit.debug(f"stateAbbr: {stateAbbr}")
    logit.debug(f"countryAbbr: {countryAbbr}")
    logit.debug(f"lat: {lat}")
    logit.debug(f"lon: {lon}")

    execute_setup(
        action,
        key,
        delete,
        newname,
        city,
        citySearch,
        cityId,
        stateAbbr,
        countryAbbr,
        lat,
        lon,
    )
    return SW.setup_dct()


@app.get("/setup", response_class=HTMLResponse)
async def run_setup(
        request: Request,
        action: str = None,

        key: str = None,

        delete: List[str] = Query([]),
        newname: List[str] = Query([]),
        city: List[str] = Query([]),

        citySearch: str = None,
        cityId: str = None,
        stateAbbr: str = None,
        countryAbbr: str = None,
        lat: str = None,
        lon: str = None):

    logit.debug('/setup endpoint hit')
    logit.debug(f"action: {action}")
    logit.debug(f"key: {key}")
    logit.debug(f"delete: {delete}")
    logit.debug(f"newname: {newname}")
    logit.debug(f"city: {city}")
    logit.debug(f"citySearch: {citySearch}")
    logit.debug(f"cityId: {cityId}")
    logit.debug(f"stateAbbr: {stateAbbr}")
    logit.debug(f"countryAbbr: {countryAbbr}")
    logit.debug(f"lat: {lat}")
    logit.debug(f"lon: {lon}")

    if execute_setup(
        action,
        key,
        delete,
        newname,
        city,
        citySearch,
        cityId,
        stateAbbr,
        countryAbbr,
        lat,
        lon,
    ):
        response = RedirectResponse(url='/')
        return response

    return templates.TemplateResponse("setup.html", {"request": request, 'dict': SW.setup_dct()})
