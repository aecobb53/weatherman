import argparse
import requests
import json
import datetime
import sys
import yaml

sys.path.append("..")
# sys.path.append("../etc")
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
aparse = argparse.ArgumentParser(description='Task Warrior TMUX wrapper')
aparse.add_argument('-get_response',                action='store_true', help="url, args")
aparse.add_argument('-format_request_city_id_list', action='store_true', help="url, city_id_list, key")
aparse.add_argument('-format_response',             action='store_true', help="data")
aparse.add_argument('-poll',                        action='store_true', help="")
aparse.add_argument('args', nargs='*')

args = aparse.parse_args()
print(args)

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
