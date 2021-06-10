import argparse
import requests
import json
import datetime
import sys
import yaml

# Argparse
aparse = argparse.ArgumentParser(description='Task Warrior TMUX wrapper')
aparse.add_argument('-state',           action='store_true', help='state of app')
aparse.add_argument('-update_state',    action='append',     help='update the state')
aparse.add_argument('-poll',            action='store_true', help='poll data now')
aparse.add_argument('-dump',            action='store_true', help='database data dump')
aparse.add_argument('-report',          action='store_true', help='database refined dump')
aparse.add_argument('-setup',           action='store_true', help='set up the app. \
    run -setup help for more info')
aparse.add_argument('-bug',             action='store_true', help='create a bug report')
aparse.add_argument('-port',            default='8000',      help='create a bug report')
aparse.add_argument('args',             nargs='*')
args = aparse.parse_args()

url = 'http://localhost:' + args.port + '/api'
tab = '    '
app_no_setup = 'App is not set up yet! run the setup endpoint to finish setup'

# url = url + '/api/state'

print(f"args: {args}")
print(f"url:{url}")
print('')


def get(url, args=None):
    print(f"url: {url}")
    print(f"args: {args}")
    if args is None:
        print('running no args')
        responses = requests.get(url)
    else:
        print('running args')
        responses = requests.get(url, args)

    try:
        data = responses.json()
    except:
        data = {}

    return responses, data

def post(url, args=None):
    print(f"url: {url}")
    print(f"args: {args}")
    if args is None:
        print('running no args')
        responses = requests.post(url)
    else:
        print('running args')
        responses = requests.post(url, args)

    try:
        data = responses.json()
    except:
        data = {}

    return responses, data


def run_setup():
    # if response.status_code == 501 and response.content.decode('utf-8') == 'App not setup!':
    print('Run setup endpoint api/setup to finish setting up the app!')
    exit()


if args.state:
    response, data = get(url + '/state')
    print(f"Return code -- {response.status_code}")
    # if response.content.decode('utf-8') == app_no_setup:
    if data == app_no_setup:
        run_setup()
    for k, v in data.items():
        if k == 'cities':
            print(f"{tab}Cities:")
            for k2, v2 in v.items():
                print(f"{tab*2}-{k2}: {v2}")
        else:
            print(f"{tab}{k}: {v}")

if args.update_state:
    print('updating state')
    new_states = {}
    for arg in args.update_state:
        updatable = arg.split('=')
        if len(updatable) != 2:
            raise ValueError('there needs to be an "=" to seporate key/values')
        new_states[updatable[0]] = updatable[1]
    print(new_states)
    response, data = post(url + '/state/update', new_states)
        

if args.poll:
    arg_dct = {}
    if args.args:
        arg_dct = {
            'city_id_list': ','.join(args.args)
        }
    if arg_dct:
        print(f"polling for this city id list: {arg_dct['city_id_list']}")
        response, data = get(url + '/poll', arg_dct)
    else:
        print(f"polling with for all cities")
        response, data = get(url + '/poll')
    print(f"Return code -- {response.status_code}")
    if data == app_no_setup:
        run_setup()


# dump
if args.dump:
    # response, data = get(url + '/dump/search')
    arg_dct = {}
    for item in args.args:
        key = ''
        if '=' in item:
            key, value = item.split('=')

        if item == 'thunderstorm':
            arg_dct['thunderstorm'] = True

        if item == 'drizzle':
            arg_dct['drizzle'] = True

        if item == 'rain':
            arg_dct['rain'] = True

        if item == 'snow':
            arg_dct['snow'] = True

        if item == 'atmosphere':
            arg_dct['atmosphere'] = True

        if item == 'clouds':
            arg_dct['clouds'] = True

        if item == 'clear':
            arg_dct['clear'] = True

        if key == 'exact_list':
            arg_dct['exact_list'] = value

        if key == 'start_time':
            arg_dct['start_time'] = value

        if key == 'end_time':
            arg_dct['end_time'] = value

    response, data = get(url + '/dump/search', arg_dct)
    print(f"Return code -- {response.status_code}")
    if data == app_no_setup:
        run_setup()
    for line in data:
        print(line)


# report
if args.report:
    # response, data = get(url + '/dump/search')
    arg_dct = {}
    for item in args.args:
        key = ''
        if '=' in item:
            key, value = item.split('=')

        if item == 'thunderstorm':
            arg_dct['thunderstorm'] = True

        if item == 'drizzle':
            arg_dct['drizzle'] = True

        if item == 'rain':
            arg_dct['rain'] = True

        if item == 'snow':
            arg_dct['snow'] = True

        if item == 'atmosphere':
            arg_dct['atmosphere'] = True

        if item == 'clouds':
            arg_dct['clouds'] = True

        if item == 'clear':
            arg_dct['clear'] = True

        if key == 'exact_list':
            arg_dct['exact_list'] = value

        if key == 'start_time':
            arg_dct['start_time'] = value

        if key == 'end_time':
            arg_dct['end_time'] = value

    response, data = get(url + '/report/search', arg_dct)
    print(f"Return code -- {response.status_code}")
    if data == app_no_setup:
        run_setup()
    for city, storms in data.items():
        print('')
        for index, storm in enumerate(storms):
            print(f"{tab}{city} storm:{index}")
            for line in storm:
                print(tab*2 + str(line))


def print_setup_help():
    print('Args for setup:')
    print('The action types define if it is retreiving data or setup data.')
    print(tab + 'action - either refresh or setup (can also call those two directly) \
        by default it will refresh')
    print(tab + 'Example: action=refresh or refresh')

    print('The key/value pairs use an "=" to designate them')
    print(tab + 'key - sets the OWMA key')
    print(tab + 'citySearch - The search parameter for the city name')
    print(tab + 'cityId - The search parameter for the city id number')
    print(tab + 'stateAbbr - The search parameter for the state abbreviation')
    print(tab + 'countryAbbr - The search parameter for the country abbreviation')
    print(tab + 'lat - The search parameter for the lattitude')
    print(tab + 'lon - The search parameter for the longitued')
    print(tab + 'Example: citySearch=Denver')

    print('The type/key/value pairs use two "=" to designate the info. weird i know')
    print(tab + 'city - Add a name and a city id to the list of cities')
    print(tab + tab + 'Example: city=Denver=123456')
    print(tab + 'newname - Update the list of cities -- currently turned off')
    print(tab + tab + "Example: newname='Old City Name'='New City Name'")
    print(tab + 'delete - Delete a city by its id number')
    print(tab + tab + 'Example: delete=123456')

    print('No arguments returns the current state of the setup')


# setup
if args.setup:
    if 'help' in args.args:
        print_setup_help()
        exit()
    print_setup_help()
    arg_dct = {}
    for item in args.args:

        key = ''
        value = ''
        if '=' in item:
            newls = item.split('=')
            key = newls[0]
            value = '='.join(newls[1:])
        print(f"{item},  -{key}-, -{value}-")

        if any([True for i in ['action', 'refresh', 'setup'] if item.startswith(i)]):
            if key == 'action':
                arg_dct['action'] = value
            if item == 'refresh':
                arg_dct['action'] = 'refresh'
            if item == 'setup':
                arg_dct['action'] = 'setup'

        if any([True for i in [
            'key',
            'citySearch',
            'cityId',
            'stateAbbr',
            'countryAbbr',
            'lat',
            'lon'] if item.startswith(i)]):
            if key == 'key':
                arg_dct['key'] = value
            if key == 'citySearch':
                arg_dct['citySearch'] = value
            if key == 'cityId':
                arg_dct['cityId'] = value
            if key == 'stateAbbr':
                arg_dct['stateAbbr'] = value
            if key == 'countryAbbr':
                arg_dct['countryAbbr'] = value
            if key == 'lat':
                arg_dct['lat'] = value
            if key == 'lon':
                arg_dct['lon'] = value

        if any([True for i in ['delete', 'newname', 'city'] if item.startswith(i)]):
            if key == 'delete':
                if 'delete' not in arg_dct.keys():
                    arg_dct['delete'] = []
                arg_dct['delete'].append(value)
            if key == 'newname':
                value = value[1:-1].split(',')
                arg_dct['newname'] = value
            if key == 'city':
                if 'city' not in arg_dct.keys():
                    arg_dct['city'] = []
                arg_dct['city'].append(value)

    response, data = get(url + '/setup', arg_dct)

    for category, values in data.items():
        if category == 'key':
            print(f"{tab}key: {values}")

        if category == 'locations':
            print(f"{tab}locations:")
            for k, v in values.items():
                print(f"{tab*2}-{k}: {v}")

        if category == 'parameters':
            pass

        if category == 'results':
            print(f"{tab}results:")
            for thing in values:
                print(f"{tab*2}{thing}")

    print('')
    print('Here is the list of elements to replace to make copy/paste/replace \
        easier if you need to')
    newstr = "'" + "','".join([item for item in data['locations'].keys()]) + "'"
    print(f"newname=[{newstr}]")

    print('')
    print("To rename a city from the locations list above add newname=<ID>")
    print("To remove a city from the locations list above add delete=<ID>")
    print("To add a city from the results list above add city=<name>=<ID>")

# # bug report
# @app.get("/api/bug-report/entry", response_class=HTMLResponse)
# @app.get("/bug-report", response_class=HTMLResponse)
# @app.get("/bug-report/entry", response_class=HTMLResponse)
