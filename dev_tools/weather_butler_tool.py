import argparse
import requests
import json
import datetime
import sys
import yaml

sys.path.append("..")
import weather_butler

master_config = '../etc/weatherman.yml'
with open(master_config) as ycf:
    config = yaml.load(ycf, Loader=yaml.FullLoader)
private_config_path = '../' + config['private_config_path']
WB = weather_butler.WeatherButler(
    '../' + config['private_config_path'],
    config['owma_url'],
    '../' + config['key_path']
)

url = config['owma_url']


# Argparse
aparse = argparse.ArgumentParser(description='weather butler tool')
aparse.add_argument('-get_response',                action='store_true', help="url, args")
aparse.add_argument('-format_request_city_id_list', action='store_true', help="url, city_id_list, key")
aparse.add_argument('-format_response',             action='store_true', help="data")
aparse.add_argument('-poll',                        action='store_true', help="")
aparse.add_argument('-versions',                    action='store_true', help="")
aparse.add_argument('args', nargs='*')

args = aparse.parse_args()
print(args)

# Functions
def str_sizer(string, length, add_char=' '):
    while len(string) < length:
        string += add_char
    return string

# get_response

if args.get_response:
    print(f"running get_response")
    # for arg in args.args:
    #     print(arg)
    url, arguments = WB.format_request_city_id_list(
        WB.config['url'], 
        WB.config['locations'].values(), 
        WB.key['Weather_Key']
    )
    response, response_list = WB.get_response(
        url,
        arguments
    )
    # print("responsestuff")
    print(response)
    print(response.status_code)
    # print(response_list)


# format_request_city_id_list


if args.format_request_city_id_list:
    url, arguments = WB.format_request_city_id_list(
        WB.config['url'], 
        WB.config['locations'].values(), 
        WB.key['Weather_Key']
    )
    print(url, arguments)

# format_response


# poll
if args.poll:
    print(f"running poll")
    for arg in args.args:
        print(arg)
    for k,v in WB.__dict__.items():
        print(k,v)
    weather_response = WB.poll()
    print(weather_response)
    # print(weather_response.json())
    # print(weather_response.code)

# Versions
if args.versions:
    import os
    print(f"running versions")
    modules = {}
    with open('../requirements.txt') as rtf:
        for line in rtf:
            name, current = line[:-1].split('==')
            modules[name] = current
    mod_str_size = 0
    for mod, old_version in modules.items():
        mod_str_size = max(mod_str_size, len(mod))

    for mod, old_version in modules.items():
        # print(f"{str_sizer(mod, mod_str_size + 2, '.')}{old_version}")
        print('')
        print(f"Module: {mod}")
        print(f"Current version: {old_version}")
        # pip search mod | grep mod
        # output = os.system(f'pip search {mod} | grep {mod}')
        # print(output)

