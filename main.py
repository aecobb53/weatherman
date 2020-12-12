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
# from weatherman import weather_butler
from weatherman import weatherman
from weatherman import data_validator
from bin import setup_weatherman
# from weatherman import sql_butler
from bin import logger

appname = 'weatherman'
master_config_path = 'etc/weatherman.yml'

# Logging
"""
I init the logger so i can use it for the api calls.
Because i dont want it to log to the main log i use a startup log that should forever be empy
"""
logger = logger.Logger(appname, app_name_in_file=True, log_suffix='api')
logit = logger.return_logit()
default_log_file = logger.log_file

with open(master_config_path) as ycf:
    config = yaml.load(ycf, Loader=yaml.FullLoader)

environment = os.environ.get('ENVIRONMENT')

logging_dct = config['environments'][environment]['log_parameters']
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
logger.update_file_level(
    config['environments'][environment]['log_parameters']['f_level'])
logger.update_consol_level(
    config['environments'][environment]['log_parameters']['c_level'])

app = FastAPI()  # noqa
global WM
WM = weatherman.WeatherMan()
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
