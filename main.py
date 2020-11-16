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

        self.master_config = 'etc/weatherman.yml'
        with open(self.master_config) as ycf:
            self.config = yaml.load(ycf, Loader=yaml.FullLoader)

        logit.info(f"lines of the config")
        logit.info(f"Yml config {json.dumps(self.config)}")
        # logit.info(f"{json.dumps(self.config, indent=4)}")

        self.name = self.config['name']
        self.private_config_path = self.config['private_config_path']
        self.public_config_path = 'etc/weather_api_public.json'
        self.db_name = self.config['db_name'] # The type will be appended in the db
        self.weather_butler = weather_butler.WeatherButler(
            self.config['private_config_path'],
            self.config['owma_url']
        )

        self.state = self.config['starting_state']


        with open(self.private_config_path) as configfile:
            self.config.update(json.load(configfile))
            # self.config = json.load(configfile)
        self.state['cities'] = self.config['locations']

        """
        If the IS_IN_DOCKER env variable is set then it imports and sets up the SQL database.
        If not then it sets up a text file. I did this for testing because I couldnt get
        SQL on my VDI at first and in case this ever needs to be bruit forced down the road.
        """

        # Setup
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
        self.state['log_file'] = logger.update_file(
            self.name,
            app_name_in_file=True,
            log_suffix=self.config['environments'][environment]['log_parameters']['log_suffix']
        )
        # self.state['log_file'] = logger.update_file(self.name, app_name_in_file=True, log_suffix=None)
        self.state['db_name'] += '.sql'
        self.state['working_directory'] = self.config['environments'][environment]['docker_working_dir']
        self.state['in_docker'] = True

        logit.info(f"Starting in {environment}")
        logit.info(f"logging levels set to fh:{self.state['fh_logging']} ch:{self.state['ch_logging']} testing:{self.testing}")
        logit.debug(f'State: {self.state}')


    def poll_weather(self):
        """
        Using the weather butler to grabb data from the weather website.
        """
        data = self.weather_butler.poll()
        logit.debug(f"request: {self.weather_butler.request}")
        logit.debug(f"request: {self.weather_butler.request.json()}")
        return data


    def manage_polling(self):
        """
        I used to have a use case for needing two functions to do that...
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
        Bad weather dump grabs any weather between 200 and 899. 800+ is generally good
        weather (800 being "clear").
        """
        data = self.db.query_database(parameters)
        logit.debug(f'weather dump based on parameters {parameters}')
        return data


    def bad_weather_dump(self):
        """
        Bad weather dump grabs any weather between 200 and 899. 800+ is generally good
        weather (800 being "clear").
        """
        data = self.db.get_bad_data()
        logit.debug('Created bad weather dump')
        return data

    # def ica_dump(self):
    #     """
    #     ICA dump takes the bad weather dump and refines it for weather that could cause
    #     bad signal. The reason its so general is to grab the full scope of a storm if it rolls in.
    #     """
    #     data = self.bad_weather_dump()
    #     dump = []
    #     for line in data:
    #         if line['sky_id'] >= 200 and line['sky_id'] < 300 or \
    #         line['sky_id'] >= 310 and line['sky_id'] < 400 or \
    #         line['sky_id'] >= 500 and line['sky_id'] < 600 or \
    #         line['sky_id'] >= 601 and line['sky_id'] < 700 or \
    #         line['sky_id'] in [731, 751, 762, 771, 781]:
    #             dump.append(line)
    #     logit.debug('Created ica weather dump')
    #     return dump

    # def rain_dump(self):
    #     """Rain"""
    #     data = self.bad_weather_dump()
    #     dump = []
    #     for line in data:
    #         if line['sky_id'] >= 300 and line['sky_id'] < 600:
    #             dump.append(line)
    #     logit.debug('Created rain weather dump')
    #     return dump

    # def snow_dump(self):
    #     """Snow"""
    #     data = self.bad_weather_dump()
    #     dump = []
    #     for line in data:
    #         if line['sky_id'] >= 600 and line['sky_id'] < 700:
    #             dump.append(line)
    #     logit.debug('Created snow weather dump')
    #     return dump

    # def wind_dump(self):
    #     """wind"""
    #     data = self.bad_weather_dump()
    #     dump = []
    #     for line in data:
    #         if line['wind'] > 5:
    #             dump.append(line)
    #     logit.debug('Created wind weather dump')
    #     return dump

    """
    End of the dump secion and start of the report secion
    """

    def weather_report(self, data):
        report1 = {}
        report2 = {}
        for name, city in self.config['locations'].items():
            report1[name] = []
            for line in data:
                if line['city'] == city:
                    report1[name].append(line)
        for name, reports in report1.items():
            report2[name] = [[]]
            report_index = 0
            for index, line in enumerate(reports):
                if index == 0:
                    report2[name][0].append(line)
                else:
                    if reports[index - 1]['time'] <= line['time'] - datetime.timedelta(minutes=35):
                        report2[name].append([])
                        report_index += 1
                report2[name][report_index].append(line)
        report = {}
        for name, reports in report2.items():
            report[name] = []
            for index, event in enumerate(reports):
                if len(event) == 0:
                    continue
                elif len(event) == 1:
                    report[name].append([event])
                else:
                    report[name].append([event[0], event[-1]])
        logit.debug('Created a weather report')
        return report


    def write_report(self, report, file_name=None):
        json_report = {}
        first_last = self.db.get_first_and_last()
        json_report['data_start'] = datetime.datetime.strftime(first_last[0]['time'], '%Y-%m-%dT%H:%M:%SZ')
        json_report['data_end'] = datetime.datetime.strftime(first_last[-1]['time'], '%Y-%m-%dT%H:%M:%SZ')
        for name, storms in report.items():
            json_report[name] = []
            for storm in storms:
                storm_durration = str(storm[-1]['time'] - storm[0]['time'])
                new_start = storm[0]['time'].strftime("%Y-%m-%dT%H:%M:%SZ")
                new_end = storm[-1]['time'].strftime("%Y-%m-%dT%H:%M:%SZ")
                storm[0]['time'] = new_start
                storm[-1]['time'] = new_end
                entry = {
                    'storm_start':storm[0]['time'],
                    'storm_end':storm[-1]['time'],
                    'storm_durration':storm_durration,
                    'start_dct':storm[0],
                    'end_dct':storm[-1],
                }
                json_report[name].append(entry)
        if file_name == None:
            file_name = self.reports_dir + \
                'Weather_report_' + \
                datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%dT%H:%M:%SZ') + \
                '.json'
        with open(file_name, 'w') as new_report:
            json.dump(json_report, new_report, indent=2)
        logit.debug(f'Wrote a weatehr report to a file {file_name}')



    def bad_weather_report(self):
        report = self.weather_report(self.bad_weather_dump())
        self.write_report(report)
        logit.debug('Created a bad weather report')
        return report


    def ica_report(self):
        report = self.weather_report(self.ica_dump())
        self.write_report(report)
        logit.debug('Created an ica weather report')
        return report


    def rain_report(self):
        report = self.weather_report(self.rain_dump())
        self.write_report(report)
        logit.debug('Created a rain weather report')
        return report


    def snow_report(self):
        report = self.weather_report(self.snow_dump())
        self.write_report(report)
        logit.debug('Created a snow weather report')
        return report


    def wind_report(self):
        report = self.weather_report(self.wind_dump())
        self.write_report(report)
        logit.debug('Created a wind weather report')
        return report



"""
Spin up the app using fastapp and uvicorn. See the docker-compose file for whats
actually run
"""
app = FastAPI()
WM = WeatherMan()
validator = data_validator.DataValidator()
templates = Jinja2Templates(directory="templates/")
app.mount("/static", StaticFiles(directory="static"), name="static")

# origins = [
#     "http://localhost.tiangolo.com",
#     "https://localhost.tiangolo.com",
#     "http://localhost",
#     "http://localhost:8080",
#     "http://localhost:8000",
#     "http://127.0.0.1:8000",
# ]

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def reat_root(request: Request):
    logit.debug('home endpoint hit')
    info = {
        '/':'list of extentions',
        '/state':'Info about the instance',
        '/poll':'Get data from Open Weather Map',
        'Dump format':'is all data gathered matching search',
        '/full_dump':'Return a list of all bad weather in db',
        '/ica_dump':'Return bad weather for ICAs',
        '/rain_dump':'Return rain data',
        '/snow_dump':'Return snow data',
        '/wind_dump':'Return wind data',
        'Report format':'is the start and end of bad data in a csv file',
        '/full_report':'File of bad data in report',
        '/ica_report':'File of bad weather for ICAs',
        '/rain_report':'File of rain data',
        '/snow_report':'File of snow data',
        '/wind_report':'File of wind data',
    }

    new_l = [i+' : '+j for i,j in info.items()]
    return templates.TemplateResponse("main.html", {"request": request, 'list':new_l})



@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    # This is here to remind myself how to pass data and to make things async
    return templates.TemplateResponse("item.html", {"request": request, "id": id})

@app.get("/about-weatherman", response_class=HTMLResponse)
async def about_weatherman(request: Request):
    return templates.TemplateResponse("about_weatherman.html", {"request": request})


@app.get('/state')
def return_args(request: Request):
    logit.debug('state endpoint hit')
    state_list = []
    for i,j in WM.state.items():
        if i == 'cities':
            state_list.append(i + ':')
            for x,y in j.items():
                state_list.append('    ' + x + ' : ' + str(y))
        elif i == 'fh_logging':
            state_list.append('file_logging' + ' : ' + j)
        elif i == 'ch_logging':
            state_list.append('consol_logging' + ' : ' + j)
        else:
            state_list.append(i + ' : ' + str(j))
        logit.info(f"{i} : {j}")
    return templates.TemplateResponse("state.html", {"request": request, 'list':state_list})
    # return WM.state

@app.get('/poll')
def poll_data():
    logit.debug('About to poll data')
    WM.manage_polling()
    return {'Success':True}

@app.get('/dump')
def data_dump(request: Request):
    logit.debug('Sending dump')
    dump_list = []
    for weatherdata in WM.bad_weather_dump():
        new_dct = {i:None for i in WM.config['dump_webpage_list']}
        dct = dict(weatherdata)
        for i,j in dct.items():
            if i == 'time':
                dct[i] = datetime.datetime.strftime(j, WM.config['datetime_str'])
            if i in WM.config['dump_webpage_list']:
                new_dct[i] = j
        dump_list.append(new_dct)
    # logit.debug(f"dump list{dump_list}")
    return templates.TemplateResponse("empty_dump.html", {"request": request, 'list':dump_list})
    # return templates.TemplateResponse("dump.html", {"request": request})

@app.get('/dump/search/')
# async def read_items(q: Optional[List[str]] = Query(None)):
# async def read_items(q: Optional[str] = Query(None)):
async def read_items(
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

    logit.info(f"thunderstorm: {thunderstorm}")
    logit.info(f"drizzle: {drizzle}")
    logit.info(f"rain: {rain}")
    logit.info(f"snow: {snow}")
    logit.info(f"atmosphere: {atmosphere}")
    logit.info(f"clouds: {clouds}")
    logit.info(f"clear: {clear}")
    logit.info(f"exact_list: {exact_list}")
    logit.info(f"start_time: {start_time}")
    logit.info(f"end_time: {end_time}")

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
        # start_time = datetime.datetime.strptime(
        #     WM.config['earliest_datetime'],
        #     WM.config['valid_datetimes']['day']
        # )
    try:
        logit.debug(f"validating wnd_time")
        end_time = validator.is_datetime(end_time)
    except ValueError:
        end_time = None
        # end_time = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1)

    parameters = {
        'exact_list': exact_list,
        'start_time': start_time,
        'end_time': end_time,
    }
    # logit.debug(f'Sending query with parameters {parameters}')
    dump_list = []
    for weatherdata in WM.weather_dump(parameters):
        new_dct = {i:None for i in WM.config['dump_webpage_list']}
        dct = dict(weatherdata)
        for i,j in dct.items():
            if i == 'time':
                dct[i] = datetime.datetime.strftime(j, WM.config['datetime_str'])
            if i in WM.config['dump_webpage_list']:
                new_dct[i] = j
        dump_list.append(new_dct)
    # logit.debug(f"dump list{dump_list}")
    return templates.TemplateResponse("dump.html", {"request": request, 'list':dump_list})
    # return templates.TemplateResponse("dump.html", {"request": request})
    
    
    # query_items = {"q": q}
    # return {query_items}




# @app.get('/full_dump')
# def full_data_dump():
#     logit.debug('Gathering full dump')
#     dump = WM.bad_weather_dump()
#     return dump

# @app.get('/ica_dump')
# def ica_dump():
#     logit.debug('Gathering ica dump')
#     dump = WM.ica_dump()
#     return dump

# @app.get('/rain_dump')
# def rain_dump():
#     logit.debug('Gathering rain dump')
#     dump = WM.rain_dump()
#     return dump

# @app.get('/snow_dump')
# def snow_dump():
#     logit.debug('Gathering snow dump')
#     dump = WM.snow_dump()
#     return dump

# @app.get('/wind_dump')
# def wind_dump():
#     logit.debug('Gathering wind dump')
#     dump = WM.wind_dump()
#     return dump

"""
Reports
"""

@app.get('/full_report')
def full_data_report():
    logit.debug('Gathering full report')
    report = WM.bad_weather_report()
    return report

@app.get('/ica_report')
def ica_report():
    logit.debug('Gathering ica report')
    report = WM.ica_report()
    return report

@app.get('/rain_report')
def rain_report():
    logit.debug('Gathering rain report')
    report = WM.rain_report()
    return report

@app.get('/snow_report')
def snow_report():
    logit.debug('Gathering snow report')
    report = WM.snow_report()
    return report

@app.get('/wind_report')
def wind_report():
    logit.debug('Gathering wind report')
    report = WM.wind_report()
    return report
