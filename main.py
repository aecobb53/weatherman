import argparse
import datetime
import time
import json
import os
import yaml

from fastapi import FastAPI, Request, Form, Query
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import PlainTextResponse, RedirectResponse
from typing import Optional, List

import weather_butler
import data_validator
import setup_weatherman


# Logging
import logger
logger = logger.Logger('weatherman', app_name_in_file=True, log_suffix='startup')
logit = logger.return_logit()
default_log_file = logger.log_file



class WeatherMan:
    """
    Historic weather data is hard to comeby. There is Weatherunderground but it would just
    be easier to gather the data and generate our own reports.
    I gather my weather data from https://openweathermap.org.
    Its free but you need to have an account an API key which i chose not to upload.

    Another useful link https://openweathermap.org/weather-conditions.
    It has all the weather codes and descriptions.
    2XX Thunderstorm
    3XX Drizzle
    5XX Rain
    6XX Snow
    7XX Atmosphere
    800 Clear
    80X Clouds
    Yep Rain and Drizzle are different... and after 399 comes 500... logic.

    There is not a good way to archive things right now. I am considering adding a cron
    to archve the databases and stop/start the container to reset everyting...I havnt tested
    what happens if you just move the database after the script thinks its spun up...
    Maybe I should add a try loop... << Note to self
    """


    def __init__(self):

        # Load config file and set some parameters
        self.master_config = 'etc/weatherman.yml'
        with open(self.master_config) as ycf:
            self.config = yaml.load(ycf, Loader=yaml.FullLoader)

        logit.info(f"lines of the config")
        logit.info(f"Yml config {json.dumps(self.config)}")

        self.name = self.config['name']
        self.private_config_path = self.config['private_config_path']
        self.db_name = self.config['db_name'] # The type will be appended in the db
        self.setup = False
        try:
            self.weather_butler = weather_butler.WeatherButler(
                self.config['private_config_path'],
                self.config['owma_url'],
                self.config['key_path']
            )
        except FileNotFoundError:
            logit.warning('setup files not found. Need to set up to use')
            self.setup = True

        self.state = self.config['starting_state']
        try:
            with open(self.private_config_path) as configfile:
                self.config.update(yaml.load(configfile, Loader=yaml.FullLoader))
            self.state['cities'] = self.config['locations']
        except FileNotFoundError:
            logit.warning('setup files not found. Need to set up to use')
            self.setup = True

        self.state['setup_needed'] = self.setup

        # Setup and more state setting
        import sql_butler
        if os.environ.get('ENVIRONMENT') == 'prod':
            environment = 'prod'
        elif os.environ.get('ENVIRONMENT') == 'dev':
            environment = 'dev'
        elif os.environ.get('ENVIRONMENT') == 'test':
            environment = 'test'
        else:
            raise TypeError('The environment is not recognized. App closing')

        logger.update_file_level(self.config['environments'][environment]['file_handler_level'])
        logger.update_consol_level(self.config['environments'][environment]['consol_handler_level'])
        self.environment = environment
        self.testing = self.config['environments'][environment]['testing_flag']
        self.working_directory = self.config['environments'][environment]['docker_working_dir']
        self.db_name += self.config['environments'][environment]['db_addition']
        self.db = sql_butler.SQLButler(self.db_name)
        self.db.create_database()

        self.state['env'] = environment
        self.state['testing'] = self.config['environments'][environment]['testing_flag']
        self.state['db_name'] += self.config['environments'][environment]['db_addition']
        self.state['fh_logging'] = self.config['environments'][environment]['file_handler_level']
        self.state['ch_logging'] = self.config['environments'][environment]['consol_handler_level']
        if self.config['environments'][environment]['log_parameters']['log_suffix'] == 'None':
            log_suffix = None
        else:
            log_suffix = self.config['environments'][environment]['log_parameters']['log_suffix']
        self.state['log_file'] = logger.update_file(
            self.name,
            app_name_in_file=True,
            log_suffix=log_suffix
        )
        self.state['db_name'] += '.sql'
        self.state['working_directory'] = self.config['environments'][environment]['docker_working_dir']
        self.state['in_docker'] = True

        logit.info(f"Starting in {environment}")
        logit.info(f"logging levels set to fh:{self.state['fh_logging']} ch:{self.state['ch_logging']} testing:{self.testing}")
        logit.debug(f'State: {self.state}')

        # Data holders
        self.dump_list = []
        self.report = {}
        self.last_poll = None


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
        data = self.poll_weather()
        self.db.multi_add(data)
        logit.debug('data added to db')


    def update_logging(self, log, terminal):
        """
        If i ever need to update the logging once the services is spun up I can run this
        function to do so. There should be endpoints to achieve this eventually.
        """
        logit.info(f'Updating logging levels to: {log},{terminal}')
        if log.upper() in ['DEBUG', '0']:
            fh.setLevel(logging.DEBUG)
        elif log.upper() in ['INFO', '1']:
            fh.setLevel(logging.INFO)
        elif log.upper() in ['WARN', 'WARNING', '2']:
            fh.setLevel(logging.WARNING)

        if terminal.upper() in ['DEBUG', '0']:
            ch.setLevel(logging.DEBUG)
        elif terminal.upper() in ['INFO', '1']:
            ch.setLevel(logging.INFO)
        elif terminal.upper() in ['WARN', 'WARNING', '2']:
            ch.setLevel(logging.WARNING)
        logit.info(f'Updated logging levels to: {log},{terminal}')


    def next_time(self, new_hours, new_minutes, new_seconds):
        """
        If an internal timer is needed this will set intervuls to run.
        For example if you give it (0,15,0) it will take time=now and add one
        minute at a time until the minutes are 15m intervuls so 0,15,30,45.
        you can do the same for hours or seconds.
        Im not sure why you would but you can set all three and get some weird time
        offsets...
        """
        now = datetime.datetime.now()
        later = datetime.datetime.now()

        """
        These if loops try to null out info not provided.
        For example, if you give (5,0,0) but run it at 06:23:45 it should grab the time
        10:00:00 not 10:23:45.
        """
        if new_minutes != 0 and new_seconds == 0:
            later = later.replace(second=self.config['time_increment']['replace_seconds'])
        if new_hours != 0 and new_minutes == 0 and new_seconds == 0:
            later = later.replace(minute=self.config['time_increment']['replace_minutes'])

        if new_hours == 0:
            pass
        else:
            inch = datetime.timedelta(hours=self.config['time_increment']['hours'])
            later = later + inch
            while later.hour not in [i for i in range(24) if i % new_hours == 0]:
                later = later + inch

        if new_minutes == 0:
            pass
        else:
            incm = datetime.timedelta(minutes=self.config['time_increment']['minutes'])
            later = later + incm
            while later.minute not in [i for i in range(60) if i % new_minutes == 0]:
                later = later + incm

        if new_seconds == 0:
            pass
        else:
            incs = datetime.timedelta(seconds=self.config['time_increment']['seconds'])
            later = later + incs
            while later.second not in [i for i in range(60) if i % new_seconds == 0]:
                later = later + incs
        return later


    def run(self):
        """
        If the script polls on its own this does that. There is a while loop that
        runs and sleeps until it needs to run again. It does a long and a short
        timer depending on how far away the timer is. If the timer is set to every
        15 minutes, the major sleep will wait 12 minutes and then sleep 1 minute
        at a time until the next timer is hit.
        """

        """
        It works but does not cut down on the processor time quite like i wanted so
        it is currently not used.
        """

        timer = self.next_time(
            self.config['timer']['default_hours'],
            self.config['timer']['default_minutes'],
            self.config['timer']['default_seconds']
        )
        timer_intervul = self.config['timer']['intervul']
        timer_delta = int(timer_intervul * self.config['timer']['intervul_multiplier'])
        logit.debug(f"Starting run loop with intervuls of {timer_intervul} and {timer_delta}")
        while True:
            logit.info(datetime.datetime.now())
            if datetime.datetime.now() > timer:
                timer = self.next_time(0,timer_intervul,0)
                minortimer = timer - datetime.timedelta(minutes=timer_delta)
                self.manage_polling()
            if datetime.datetime.now() > minortimer:
                sleeptime = self.config['timer']['sleep']
            else:
                sleeptime = minortimer * self.config['timer']['sleep']
            time.sleep(sleeptime)


    """
    Dumps just return a list of the dicts from the database. Useful as an intermediate
    step or if you just need the straight data.

    Reports take the dump data and creates a list where each element is a list of the start
    and the end of the storm. Each report takes the dump data and runs it through the
    weather_report funciton and returns the result. This is intended to make things
    easier... we will see if it actually works.

    I may add even more specilty reports below but for now there is one for each of the
    dump cases.
    """

    def weather_dump(self, parameters):
        """
        Takes the parameters to filter out results from the database.
        """
        logit.debug(f'weather dump based on parameters {parameters}')
        data = self.db.query_database(parameters)
        self.dump_list = []
        for weatherdata in data:
            new_dct = {i:None for i in self.config['dump_webpage_list']}
            dct = dict(weatherdata)
            for i,j in dct.items():
                if i == 'time':
                    dct[i] = datetime.datetime.strftime(j, self.config['datetime_str'])
                if i == 'name':
                    for x,y in self.config['locations'].items():
                        if int(dct['city']) == int(y):
                            j = x
                            break
                if i in self.config['dump_webpage_list']:
                    new_dct[i] = j
            self.dump_list.append(new_dct)
        return self.dump_list


    def bad_weather_dump(self):
        """
        Bad weather dump grabs any weather between 200 and 899. 800+ is generally good
        weather (800 being "clear").

        This is being depreciated
        """
        data = self.db.get_bad_data()
        logit.debug('Created bad weather dump')
        return data


    """
    End of the dump secion and start of the report secion
    """


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
            # Itterates through the new lists of weather data and places similar times together in to storms
            report2[name] = [[]]
            report_index = 0
            for index, line in enumerate(reports):
                if index == 0:
                    report2[name][0].append(line)
                else:
                    if reports[index - 1]['time'] <= line['time'] - datetime.timedelta(minutes=int(self.config['storm_difference_time'])):
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
                    memory = {
                        'sky_id':[]
                    }
                    for itterate, line in enumerate(event):
                        if itterate in [0, len(event)-1]:
                            continue
                        if not recursive_search(line['sky_id'], 'sky_id', itterate, event, self.config['storm_difference_itteration']):
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
                    new_start = storm[0]['time'].strftime("%Y-%m-%dT%H:%M:%SZ")
                    new_end = storm[-1]['time'].strftime("%Y-%m-%dT%H:%M:%SZ")
                else:
                    if self.config['single_storm_event_flag']:
                        # If the single_storm_event_flag is true the single event storms will be added. else they will be skipped.
                        storm_durration = '0'
                        new_start = storm[0]['time'].strftime("%Y-%m-%dT%H:%M:%SZ")
                        new_end = storm[0]['time'].strftime("%Y-%m-%dT%H:%M:%SZ")
                    else:
                        continue
                for line in storm:
                    if not isinstance(line['time'], str):
                        line['time'] = datetime.datetime.strftime(line['time'], self.config['datetime_str'])
                entry = {
                    'storm_start':storm[0]['time'],
                    'storm_end':storm[-1]['time'],
                    'storm_durration':storm_durration,
                    'start_dct':storm[0],
                    'end_dct':storm[-1],
                    'storm_events':storm,
                }
                json_report[name].append(entry)
        if file_name == None:
            file_name = self.config['weather_reports_dir'] + \
                'Weather_report_' + \
                datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%dT%H:%M:%SZ') + \
                '.json'
        self.report = json_report
        with open(file_name, 'w') as new_report:
            json.dump(json_report, new_report, indent=2)
        logit.debug(f'Wrote a weatehr report to a file {file_name}')

    def clear_search(self):
        self.dump_list = []
        self.report = {}



"""
Spin up the app using fastapp and uvicorn. See the docker-compose file for whats
actually run
"""
app = FastAPI()
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


@app.get('/')
async def root(request: Request):
    """
    The home page has some explanation of what each tab does.
    Eventually it would be great to have picutres of the tabs here as well.
    """
    logit.debug('home endpoint hit')
    return templates.TemplateResponse("main.html", {"request": request})


@app.get("/about-weatherman", response_class=HTMLResponse)
async def about_weatherman(request: Request):
    """
    If people had more questions I wanted to have a place to answer some of them.
    """
    logit.debug('about-weatherman endpoint hit')
    return templates.TemplateResponse("about_weatherman.html", {"request": request})


@app.get('/api/state')
async def return_api_args(request: Request):
    """
    The api endpoint for state.
    """
    logit.debug('api state endpoint hit')
    return WM.state


@app.get('/state')
async def return_args(request: Request):
    """
    This returns the state of the app.
    Useful for some debugging.
    """
    logit.debug('state endpoint hit')
    state_list = []
    logit.warning(f"Setup is {WM.setup}")
    if WM.setup:
        logit.warning('app not set up, redirecting to setup')
        response = RedirectResponse(url='/setup')
        return response
    for i,j in WM.state.items():
        if i == 'cities':
            state_list.append(i + ':')
            for x,y in j.items():
                state_list.append('-' + x + ' : ' + str(y))
        elif i == 'fh_logging':
            state_list.append('file_logging' + ' : ' + j)
        elif i == 'ch_logging':
            state_list.append('consol_logging' + ' : ' + j)
        else:
            state_list.append(i + ' : ' + str(j))
        logit.info(f"{i} : {j}")
    return templates.TemplateResponse("state.html", {"request": request, 'list':state_list})


@app.get('/api/poll')
async def poll_api_data(request: Request):
    """
    This fires off a poll to the app.
    """
    logit.debug('api poll endpoint hit')
    WM.manage_polling()


@app.get('/poll')
async def poll_data(request: Request):
    """
    Poll OWMA for new weather data.
    """
    logit.debug('about to poll data')
    if WM.setup:
        logit.warning('app not set up, redirecting to setup')
        response = RedirectResponse(url='/setup')
        return response
    WM.manage_polling()
    timestamp = datetime.datetime.strftime(WM.last_poll, WM.config['datetime_str'])
    return templates.TemplateResponse("poll.html", {"request": request, "last_poll":timestamp})


@app.get('/dump')
async def data_dump(request: Request):
    """
    This returns the html to load the results from the database dump.
    """
    logit.debug('dump endpoint hit')
    if WM.setup:
        logit.warning('app not set up, redirecting to setup')
        response = RedirectResponse(url='/setup')
        return response
    data = WM.dump_list
    WM.clear_search()
    return templates.TemplateResponse("dump.html", {"request": request, 'list':data})


@app.get('/dump/search/')
def read_items(
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

    logit.debug(f"dump/search endpoint hit")
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

    if WM.setup:
        logit.warning('app not set up, redirecting to setup')
        response = RedirectResponse(url='/setup')
        return response

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
        logit.debug(f"validating exact_list")
        exact_list = validator.is_exact_list(exact_list)
    except ValueError:
        exact_list = None

    try:
        logit.debug(f"validating start_time")
        start_time = validator.is_datetime(start_time)
    except ValueError:
        start_time = None

    try:
        logit.debug(f"validating wnd_time")
        end_time = validator.is_datetime(end_time)
    except ValueError:
        end_time = None

    parameters = {
        'exact_list': exact_list,
        'start_time': start_time,
        'end_time': end_time,
    }
    WM.weather_dump(parameters)
    response = RedirectResponse(url='/dump')
    return response


@app.get("/bug-report", response_class=HTMLResponse)
async def submit_bug_report(request: Request):
    return templates.TemplateResponse("bug_report.html", {"request": request})


@app.get("/bug-report/entry", response_class=HTMLResponse)
async def read_items(
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

    if WM.setup:
        logit.warning('app not set up, redirecting to setup')
        response = RedirectResponse(url='/setup')
        return response

    entry_time = datetime.datetime.strftime(
            datetime.datetime.now(tz=datetime.timezone.utc),
            WM.config['datetime_str']
        )

    valid = False
    none_list = [prod, dev, test, unit_test, website, home, reports, dump, realtime, state, poll, about, report]
    if event_time == '' and description == '':
        for check in none_list:
            if check is not None:
                valid = True
                break
    else:
        valid = True

    bug_info = {
        'env':[],
        'tab':[],
        'datetime':[],
        'description':'',
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
    else:
        logit.info(f"Invalid entry, skipping")
    response = RedirectResponse(url='/')
    return response


@app.get("/report", response_class=HTMLResponse)
async def report(request: Request):
    """
    Saves a report to the out/ direcotry.
    Eventually it may return the report but i dont have that working yet.
    """
    logit.debug('report endpoint hit')
    if WM.setup:
        logit.warning('app not set up, redirecting to setup')
        response = RedirectResponse(url='/setup')
        return response
    data = WM.report
    WM.clear_search()
    return templates.TemplateResponse("report.html", {"request": request, 'dict':data})

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

    logit.debug(f"report/search endpoint hit")
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

    if WM.setup:
        logit.warning('app not set up, redirecting to setup')
        response = RedirectResponse(url='/setup')
        return response

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
        logit.debug(f"validating exact_list")
        exact_list = validator.is_exact_list(exact_list)
    except ValueError:
        exact_list = None

    # If there are no dates provided, set them to one week starting on Monday
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    while now.weekday() != 0:
        now = now - datetime.timedelta(days=1)
    end = now
    start = now - datetime.timedelta(days=7)

    new_start_time = validator.is_datetime(
        datetime.datetime.strftime(start, '%Y-%m-%d')
        )
    new_end_time = validator.is_datetime(
        datetime.datetime.strftime(end, '%Y-%m-%d')
        )

    try:
        logit.debug(f"validating start_time")
        start_time = validator.is_datetime(start_time)
        if start_time is None:
            raise ValueError
    except ValueError:
        start_time = new_start_time

    try:
        logit.debug(f"validating wnd_time")
        end_time = validator.is_datetime(end_time)
        if end_time is None:
            raise ValueError
    except ValueError:
        end_time = new_end_time

    parameters = {
        'exact_list': exact_list,
        'start_time': start_time,
        'end_time': end_time,
    }
    report = WM.weather_report(WM.weather_dump(parameters))
    WM.write_report(report)
    response = RedirectResponse(url='/report')
    return response

@app.get("/api/setup", response_class=HTMLResponse)
async def report(request: Request):
    return "Dont forget to build this out. should run the setup stuff"

@app.get("/setup", response_class=HTMLResponse)
# async def report(request: Request):
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
    lon: str = None

    ):

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


    # Key
    if key != None and key != '':
        SW.key = key

    # Search parameterse
    if citySearch != None and citySearch != '':
        SW.update_parameters('name', citySearch)
    if cityId != None and cityId != '':
        SW.update_parameters('id', cityId)
    if stateAbbr != None and stateAbbr != '':
        SW.update_parameters('state', stateAbbr)
    if countryAbbr != None and countryAbbr != '':
        SW.update_parameters('country', countryAbbr)
    if lat != None and lat != '':
        SW.update_parameters('lat', lat)
    if lon != None and lon != '':
        SW.update_parameters('lon', lon)

    # Modifying to list
    ## Updating
    location_lst = [(k,v) for k,v in SW.locations.items()]
    for index, element in enumerate(newname):
        if element != '':
            SW.update_locations(location_lst[index][0], element)
    ## Removing
    location_lst = [(k,v) for k,v in SW.locations.items()]
    if delete != ['']:
        for tup in location_lst:
            if tup[1] in delete:
                SW.remove_location(tup[0])
    ## Adding
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
            response = RedirectResponse(url='/')
            return response
        except FileNotFoundError:
            WM.setup = True
            logit.warning('app not set up yet! setting setup flag to {setup}')

    return templates.TemplateResponse("setup.html", {"request": request, 'dict':SW.setup_dct()})
