import requests
import argparse

# Argparse
aparse = argparse.ArgumentParser(description='Runs different posts')
aparse.add_argument('-soh', action='store_true', help='state of health')
aparse.add_argument('-p', '-poll', action='store_true', help='poll')
aparse.add_argument('-r', '-report', action='store_true', help='full report')
aparse.add_argument('-ica_report', action='store_true', help='ica report')
args = aparse.parse_args()

"""
This takes arguments probably passed by the run.sh file and passes them to the app. 
"""

app_url = 'http://0.0.0.0:8000'

def server_soh():
    url = app_url
    try:
        request = requests.get(url)
        if request.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.ConnectionError:
        return False

def gather_weather():
    url = app_url + '/poll'
    request = requests.get(url)
    
def full_report():
    url = app_url + '/bad_weather'
    request = requests.get(url)

def ica_report():
    url = app_url + '/ica_report'
    request = requests.get(url)

if args.soh:
    server_soh()

if args.p:
    if server_soh():
        gather_weather()
    else:
        print('server not started or 200 code')

if args.r:
    if server_soh():
        full_report()
    else:
        print('server not started or 200 code')

if args.ica_report:
    if server_soh():
        ica_report()
    else:
        print('server not started or 200 code')

    