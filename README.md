# Weatherman

Historic weather data is surprisingly hard to come by. 
Thus the Weather man was born. 
(His backstory is is ***REALLY*** lame). 
Really what you need to know is it would be nice to have a way to capture weather data. 
Then use this weather data to determine if images for the ICAs were lost due to weather or not. 
It currently runs in a SQL or csv database and Docker or terminal configurations. 
I highly reccomend running it in Docker as SQL but i kept the other forms mostly up to date just in case. 

> Release:  0.4.0-beta

> Point of contact:  Andrew

> Last modified:  2020-10-09

## Table of Contents

 - [Weatherman API](#weatherman-api)
 - [Open Weather Map API](#open-weather-map-api)
 - [Docker setup](#docker-setup)
 - [Terminal setup](#terminal-setup)
 - [SQL setup](#sql-setup)
 - [CSV setup](#csv-setup)
 - [Crontab](#crontab)
 - [Docker](#docker)
 - [Terminal](#terminal)
 - [SQL](#sql)
 - [CSV](#csv)
 - [Logging](#logging)
 - [TODO](#todo)
 - [Links](#links)

 [Behave testing README](/README_behave.md)

## Weatherman API

You can reach the service from any web gui by going to 

```http
http://0.0.0.0:8000/

or

0.0.0.0:8000

or

localhost:8000
```

Going to any of the above addresses will bring you to a makeshift menu i created. 
This will give you a list of all url extentions and a brief description of what they do. 
In general 
- `/state` is for general system stuff like is it in Docker or not. 
- `/*dump` is for returning a list of dicts for all data matching the weather type.
- `/*report` returnsthe folowing nested data and creates a json report with the same data
  but formatted a bit better. 

```text
list of cities
    list of storms two elements long
        dict of first element is the start of the storm
        dict of second element is the last of the storm
```

###### `/`	            

Menu

###### `/state`	        

The state is an instance variable that keeps track of useful info such as: 

- working_directory - The directory in Docker (or terminal) being used. 
- in_docker - Boolean representing in Docker?
- env - Env is more for human understanding between prod/dev/test
- testing - Boolean representing are unit/feature tests being run?
- reports - If a report was generated where would it be placed? 
- log_file - Where is the app logging to?
- cities - A list of dicts {cities:city_id} being polled
- fh_logging - What is the file log level 
- ch_logging - What is the commandline log level 

###### `/poll`	        

Poll data from Open Weather Map based on the list of cities

###### `/full_dump`	    

"Return a list of all bad weather in db"

###### `/ica_dump`	    

"Return bad weather for ICAs"

###### `/rain_dump`	    

"Return rain data"

###### `/snow_dump`	    

"Return snow data"

###### `/wind_dump`	    

"Return wind data"

###### `/full_report`	

"File of bad data in report"

###### `/ica_report`	

"File of bad weather for ICAs"

###### `/rain_report`	

"File of rain data"

###### `/snow_report`	

"File of snow data"

###### `/wind_report`	

"File of wind data"

---

### Open Weather Map api

I am using the Free calls:

```
60 calls/minute
1,000,000 calls/month
Curent Weather
Minute Forecast 1 hour*
Hourly Forecast 2 days*
Daily Forecast 7 days*
Government Weather alerts*
Historical weather 5 days*
Basic weather maps
Weather triggers
Weather widgets
Uptime 95%

* - 1,000 API calls per day by using One Call API
** - 2,000 API calls per day by using One Call API
```

Note: I read somewhere the polling type i am using maxes out at 20. 
I cant find where that was again so maybe that changed. 
It appears i can call for current weather up to 60/min or 1M/month. 
If that is the case i can poll up to 22 cities every minute. 
Currently i only get 11 cities data every 15 minutes. 
I plan to increase to every 5 minutes.


| calls/attempt          | 10        | 11      | 20      | 23        |
| ----------------------:| ---------:| -------:| -------:| ---------:|
| calls/min              | 10        | 11      | 20      | 23        |
| calls/hour             | 600       | 660     | 1,200   | 1,380     |
| calls/day              | 14,400    | 15,840  | 28,800  | 33,120    |
| calls/week             | 100,800   | 110,880 | 201,600 | 231,840   |
| calls/month            | 446,400   | 491,040 | 892,800 | 1,026,720 |
| calls every 5  minutes | 89,280    | 98,208  | 178,560 | 205,344   |
| calls every 10 minutes | 44,640    | 49,104  | 89,280  | 102,672   |
| calls every 15 minutes | 29,760    | 32,736  | 59,520  | 68,448    |
| calls every 30 minutes | 14,880    | 16,368  | 29,760  | 34,224    |
| calls every 60 minutes | 7,440     | 8,184   | 14,880  | 17,112    |

## What you need

All configurations will need the repo downloaded locally, and an "openweathermap.org" API key. 
To set up a key add the folowing to a file in the repo called `key.ignore`. 

```json
{"Weather_Key": "<key>"}
```

The config is also not added to protect the locations i look at. 
Copy the config example below. 
The shorthand abbreviations are only used for human reference. 
The app looks exclusivly at the location ID. 

Config:

```json
{
    "locations": {
        "shorthand abreviation": 00000,
    },
    "url":"https://api.openweathermap.org/data/2.5/"
}
```

##### Docker setup

 - Ensure Docker is installed.

##### Terminal setup

 - Kepler. I dont think this will run in MCS Gold.
 - python3. I am currently using python3.7 but it _should_ work with any python3.

##### SQL setup

 - Docker will take care of this but if you need to install it yourself on Kepler.
   good luck! If you succeed i would be very interested in knowing how. 

##### CSV setup

 - Nothing... 

## Crontab

Right now i have a cron set up to tell the service to get weather from the api every 15 minutres. 
I have some groundwork for an internal clock but that gets into some problems with the innerowrking 
stuff that i havnt gotten working at yet. 
One day I will and it will be great. 
Currently I have a `run.sh` script that runs a `run.py` script that hits the apps endpoints. 
Both run scripts take and pass arguments but by default poll for weather data. 
you could for instance run `run.sh -ica_report` to run the `/ica_report` endpoint. 
I added the `-ica_reports` to run every day to make sure the reports look right. 
I currenly only have the minimal arugment parsing to get the job done. 

```crontab
*/15 * * * * /<path to>/run.sh

0 0 * * * /home/acobb/git/gold_scripts/scripts/weather/run.sh -ica_report
```

In the future I intend to add a crontab to generage a weekly weather report and then email it off. 

```crontab
0 1 * * 5 /<path to>/run.sh -ica_report

0 2 * * 5 /<path to>/email_script.py
```

## Docker

Again I **highly** encourage it to be run in Docker as SQL because the dockerfile will spin
up the appropriate python and docker instances. The only drawback is SQL is hard to install on
Kepler environments. 
I added the dup endpoints to make getting the data easy so there would not be any issues with
using it in the configuration. 
I will admit it does require some basic knowledge about Docker which i will not be adding
to this markdown but may add to another Readme somewhere in the toolbox. 
The name of the docker image created is `weather` or `weather-dev` depending on what you run. 
The name of the docker container is `weather:latest` or `weather-dev:latest` depending on what you run. 

---

Different run commands to run out of the git repo (descriptions underneith):


`docker-compose up [-d] [--build] weather`

The super basic run docker. 
By default this will spin it up in terminal. 
If you want it headless use the `-d` and if you want the image rebuilt run `--build`. 


`docker logs <container id> [--follow]`

Print recent logges or tail the logs


`docker-compose up [--build] dev`

If you want to spin up the dev instance run the above command. 
Note that the port for the dev instance is `8100` not `8000`.


`docker-compose up [--build] test`

I added this for unit/feature testing. 
I have some of the feature testing working but still need to finish and start the unit testing. 
there is more info in the behave readme mentioned after the table of contents. 

##### Dockerfile

The base is python3:latest, I set the working directory to `/usr/src/` and `COPY . .`. 
It feels like im cheating doing that but its totoly fine. 
I then set two ENV variables which i explain later. 
I dont fully understand what the first two ENV variables do but i think it errors if they arent there. 
I commented out the update steps and things seem to run fine. It doesnt hurt anything to uncomment 
them but I was playing with what the minimum setup needed was. 

ENVs set:

- PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disc (equivalent to python -B option). 
- PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr (equivalent to python -u option). 
- IS_IN_DOCKER: The main.py reads this variable to determin if its in Docker or not. 
- TESTING: Used to set logging on app startup. 

Notable Dockerfile events:

```Dockerfile
FROM python:3
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV IS_IN_DOCKER=True
```

##### docker-compose.yml

I grab version 3 because you are supposed to. 
I could move the timing from cron to another script to keep the main script polling on time. 
Here i have the command that is run and the volumne `.` is maped to the working directory. 
I expose port 8000 right now but it might change if i have multiple projects going. 
Either way the internal port will always be 8000. 
I set some more dynamic variables depending on the container spun up. 
The weather container has `ENVIRONMENT=prod`, `TESTING=False`, and no `--reset` on uvicorn. 
For ENVIRONMENT prod is intended to be stable weather gathering. 
dev changes the name of the log file to `dev_weatherman.log`. 
For TESTING True sets all log levels to DEBUG while False sets the logfile to DEBUG and commandline to INFO. 
I plan to set the command line to INFO/WARNING enventually but for testing it works well. 
All internal ports are set to 8000 but the external ports will be `8000` or prod and `8100` for dev. 
`--reset` in uvicorn sets uvicorn to stop/start if any file in the directory updates. 
This is SUPER useful for developing but not for a stable product. 

Notable docker-compose.xml events:

```Docker
version: '3'
services:
  weather:
    command: uvicorn main:app --workers 1 --host 0.0.0.0 --port 8000
    ports:
        - 8000:8000
    environment:
      - ENVIRONMENT=prod
      - TESTING=False

  dev:
    command: uvicorn main:app --reload --workers 1 --host 0.0.0.0 --port 8000
    ports:
        - 8100:8000
    environment:
      - ENVIRONMENT=dev
      - TESTING=True
  
  test:
    command: behave
    ports:
      - 8200:8000
    environment:
      - ENVIRONMENT=test
      - TESTING=True
```

---

Right now using Docker will use SQL and not will use txt... i dont have a great way to switch 
between the two. 

## Terminal

You can use uvicorn to spin up the service in terminal. 
Make sure you are in the repo and run the folowing command. 

`uvicorn main:app [--reload] --host 0.0.0.0 --port 8000`. 

You will know it has spun up when you see these lines

```txt
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## SQL

One downside to SQL is its hard to get installed on Kepler. 
Outside of that its perfect for this project. 
It is super easy to use once you get over the iniital hurdle and it is very adaptable. 
This link is gold... but hard to read at first https://www.sqlite.org/lang_expr.html#cosub.
Docker spins up SQL very easily and python comes with sql installed by default so it works great. 

## CSV

I added it for testing and if people wanted it.  

## Logging

I added a lot of features to the `logger.py` class. 
The setup is a bit weird because there are two parts. 
The first one is initing the logging object with `Logger('<app_name>', [<kwargs>])`. 
The **kwargs as displayed below. 
Half the list is provided strings to use directly the other needs boolean. 
The boolean is explicit so `True/False` or `1/0`.
`'False'` is considered a string and returns `True`. 

| kwarg | What it does | input type |
| --- | --- | --- |
| `f_level`          | Update the file logging level                | string |
| `c_level`          | Update the commandline logging level         | string |
| `log_rolling`      | Set log rotating (not working yet)           | string |
| `log_directory`    | Set a logging directory (default is `logs/`) | string |
| `log_prefix`       | Set a prefix in the log file name            | string |
| `log_suffix`       | Set a suffix in the log file name            | string |
| `app_name_in_file` | Use the app name in the log file             | boolean |
| `date_in_file`     | Add the date to the log file name            | boolean |
| `time_in_file`     | Add the tiem to the log file name            | boolean |
| `utc_in_file`      | Switch the file name timestamps to utc       | boolean |
| `short_datetime`   | Shorten the dates                            | boolean |

An example of how to set up the logfile in the init phase:

```python
logger = Logger('<app_name>',\
    app_name_in_file=True,\
    date_in_file=True,\
    time_in_file=True,\
    utc_in_file=True,\
    short_datetime=True,\
    log_prefix='dev')
```

The log file will end up looking like this `logs/app_name_dev_200926-174000Z`. 
I chose to have the prefix come after the app name. 
I figured this would be easiest if there were multiple programs logging to the same directory. 

The next part of seting up logger is to set up the part that actually logs. 
This is done with something like this: `logit = logger.return_logit()`.
There are a bunch of different objects and this was the easiest way to allow me to update the 
logging class after it had been spun up. 
To log you would run something like `logit.info('<something to log>')`. 
There are three objects being used here. 
The module `logging`, the handler `logger`, and the thing that sends the logs `logit`. 
When you are updating logging its against the `logger` object and when you are logging its 
against the `logit` object (or whatever you called it). 
In the rest of the markdown I will be refering to them by those names. 
Alltogether this is how i have my logging set up:

```python
logger = logger.Logger('weatherman', app_name_in_file=True)
logit = logger.return_logit()
logit.debug('logger and logit are set up')
```

---

Because of the difference between logit and logger you can update waht the logger does at any time. 
If you need to update the log level you can run `logger.update_file_level('DEBUG')`. 
Logger expects `debug`, `info`, `warning`, `error`, `critical` (case insensitive). 
You can also update the filename at any time with `logger.update_file('<app_name>', <kwargs>)`. 
When you update the file it appends a list so set it to `None` if you want it to unset something. 
Example Use cases are updateing the logger based on env variables as I have or switch the log levels 
and file names if you receive an error and want to capture more data about it. 
Currently if behave testing is being run I update the suffix to 'test' and all log levels to debug. 
If the environment is dev or test (not prod) I add that as a suffix. 
If the script is spun up outside of docker "text" is added to the scriptname. 

---

In a nutshell weatherman logs to `logs/weatherman.log` if we are in prod, `logs/weatherman_dev.log` if 
tweaking in dev, and `logs/weatherman_dev_test.log` if running behave testing. 

## TODO

- ~~Build out more run.* arguments.~~
- better error handling. 
- verify the run scripts error silently and capture all returns so the cront does not get full. 
- logging in the readme. 
- reports in the readme. 
- db structure in the readme. 
- update Dockerfile or docker-compose itteration numbers. 
- log rotating.
- Add to report the worst conditions of a storm. 
- Add CICD daily testing. pull changes, run tests, send results. 
- Change all backends to be `async`
- Eventually set the main app logging to file only

## Links

- [prod api](http://0.0.0.0:8000/state)
- [dev api](http://0.0.0.0:8100/state)
- [test api](http://0.0.0.0:8200/state)


- [SQL help](https://www.sqlite.org/lang_expr.html#cosub)
- [Open Weather Map (OWM)](https://openweathermap.org)
- [Open Weather Map Api](https://openweathermap.org/current#format). 
  This is the link to the main OWM api info. 
- [OWM weather conditions](https://openweathermap.org/weather-conditions). 
  This is where the weather codes, icons, and brief descriptions are. 
- [OWM FAQ](https://openweathermap.org/faq)
- [OWM Pricing](https://openweathermap.org/price)
  
