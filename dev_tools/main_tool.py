import argparse
import requests
import json
import datetime
import sys
import yaml

# sys.path.append("..")

# master_config = '../etc/weatherman.yml'
# with open(master_config) as ycf:
#     config = yaml.load(ycf, Loader=yaml.FullLoader)
# private_config_path = '../' + config['private_config_path']
# WB = weather_butler.WeatherButler(
#     '../' + config['private_config_path'],
#     config['owma_url'],
#     '../' + config['key_path']
# )

# url = config['owma_url']


# Argparse
aparse = argparse.ArgumentParser(description='Task Warrior TMUX wrapper')
aparse.add_argument('-state',   action='store_true', help='state of app')
aparse.add_argument('-poll',    action='store_true', help='poll data now')
aparse.add_argument('-dump',    action='store_true', help='database data dump')
aparse.add_argument('-report',  action='store_true', help='database refined dump')
aparse.add_argument('-setup',   action='store_true', help='set up the app')
aparse.add_argument('-bug',     action='store_true', help='create a bug report')
aparse.add_argument('-port',    default='8010',      help='create a bug report')
aparse.add_argument('args', nargs='*')
args = aparse.parse_args()

url = 'http://localhost:' + args.port + '/api'
tab = '    '

# url = url + '/api/state'

print(f"args: {args}")
print(f"url:{url}")
print('')


# response = requests.get(url + '/state')
# print(response)
# print(response.status_code)
# print(response.json())


def get(url, args=None):
    print(f"url: {url}")
    print(f"args: {args}")
    if args == None:
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

def run_setup():
    # if response.status_code == 501 and response.content.decode('utf-8') == 'App not setup!':
    print('Run setup')

if args.state:
    response, data = get(url + '/state')
    print(f"Return code -- {response.status_code}")
    if response.content.decode('utf-8') == 'App not setup!':
        run_setup()
    for k,v in data.items():
        if k == 'cities':
            print(f"{tab}Cities:")
            for k2, v2 in v.items():
                print(f"{tab*2}-{k2}: {v2}")
        else:
            print(f"{tab}{k}: {v}")

if args.poll:
    response, data = get(url + '/poll')
    print(f"Return code -- {response.status_code}")
    if response.content.decode('utf-8') == 'App not setup!':
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
    if response.content.decode('utf-8') == 'App not setup!':
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

    response, data = get(url + '/setup', arg_dct)
    print(f"Return code -- {response.status_code}")
    if response.content.decode('utf-8') == 'App not setup!':
        run_setup()
        print(data)
    # for location, storms in data.items():
    #     print(location)
    #     for line in storms:
    #         print(f"{tab}{line}")

# setup
if args.setup:
    arg_dct = {}
    for item in args.args:
        key = ''
        value = ''
        if '=' in item:
            newls = item.split('=')
            key = newls[0]
            value = '='.join(newls[1:])
        print(f"{item},  -{key}-, -{value}-")

        if any([True for i in ['action', 'refresh', 'submit'] if item.startswith(i)]):
            if key == 'action':
                arg_dct['action'] = value
            if item == 'refresh':
                arg_dct['action'] = 'refresh'
            if item == 'submit':
                arg_dct['action'] = 'submit'

        if any([True for i in ['key', 'citySearch', 'cityId', 'stateAbbr', 'countryAbbr', 'lat', 'lon'] if item.startswith(i)]):
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
                if 'newname' not in arg_dct.keys():
                    arg_dct['newname'] = []
                arg_dct['newname'].append(value)
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
            # print(f"{tab}Search parameters used:")
            # for k, v in values.items():
            #     print(f"{tab*2}{k}: {v}")

        if category == 'results':
            print(f"{tab}results:")
            for thing in values:
                print(f"{tab*2}{thing}")
    print('')
    print("To rename a city from the locations list above add newname=<ID>")
    print("To remove a city from the locations list above add delete=<ID>")
    print("To add a city from the results list above add city=<name>=<ID>")
        
    # response, data = get(url + '/report/search', arg_dct)
# @app.get("/api/setup", response_class=HTMLResponse)
# @app.get("/setup", response_class=HTMLResponse)

# # bug report
# @app.get("/api/bug-report/entry", response_class=HTMLResponse)
# @app.get("/bug-report", response_class=HTMLResponse)
# @app.get("/bug-report/entry", response_class=HTMLResponse)








